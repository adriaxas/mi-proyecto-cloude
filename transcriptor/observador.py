#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Observador de ~/procesar_libros  (versión 2)

Vigila la carpeta; cada PDF nuevo se transcribe a un Markdown estructurado dentro
de una carpeta con el nombre del libro, junto con el PDF original.

Qué hace distinto de la versión 1:
  * Usa la capa de texto del PDF cuando existe (conserva negritas, cursivas y
    tamaños reales) y recién usa OCR (Tesseract) en las páginas sin texto.
  * Títulos H1-H4 según tamaño de letra / negrita / mayúsculas, medidos sobre
    TODO el libro (no página por página).
  * Listas numeradas, con letras, con viñetas y anidadas (1, 1a, 1b, 2, a), ...).
  * Negritas, cursivas y superíndices (llamadas de nota) -> **x**, *x*, <sup>x</sup>.
  * Tablas con líneas (solo en PDFs con capa de texto) -> tablas Markdown.
  * Folio impreso: lo LEE de cada página (pie/cabecera), calibra el offset por
    votación y marca discrepancias. Soporta numeración romana y offset negativo
    (artículos o capítulos sueltos).
  * Páginas dobles (dos páginas impresas en una hoja) -> se separan en izq/der.
  * Cabeceras y pies corridos se conservan como comentario, fuera del cuerpo.
  * Imágenes como archivos .webp livianos en imagenes/ (no Base64 dentro del .md).
  * Frontmatter con metadatos, ISBN validado, estructura (esquema de títulos),
    páginas sin texto y páginas de OCR dudoso.
  * Si se corta, retoma desde la última página guardada (.trabajo/).

Uso:
  python observador.py              -> vigila ~/procesar_libros
  python observador.py libro.pdf    -> procesa ese PDF y termina

Variables opcionales: CARPETA_LIBROS, OCR_LANG (spa), FORZAR_OCR=1, DPI (200).
"""
import io
import os
import re
import sys
import json
import time
import glob
import queue
import shutil
import threading
import statistics
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
import pytesseract
from PIL import Image

try:
    import pymupdf as fitz
except ImportError:  # versiones viejas de PyMuPDF
    import fitz

CARPETA = Path(os.environ.get("CARPETA_LIBROS", str(Path.home() / "procesar_libros")))
OCR_LANG = os.environ.get("OCR_LANG", "spa")
DPI = int(os.environ.get("DPI", "200"))
FORZAR_OCR = os.environ.get("FORZAR_OCR", "") == "1"

MIN_CARACTERES_TEXTO = 30     # menos que esto en la capa de texto -> se prueba OCR
ZONA_MARGEN = 0.065           # franja superior/inferior donde buscamos cabecera/pie
RATIO_TITULO = 1.18           # tamaño mínimo (x cuerpo) para considerar título por tamaño
FACTOR_MAYUS = 0.9            # corrección del tamaño estimado por OCR en líneas en mayúsculas
FACTOR_BOLD_OCR = 1.28        # grosor de trazo (x mediana de la página) para llamar "negrita"
CONF_DUDOSA = 70              # confianza media de OCR bajo la cual la página se marca dudosa

# --------------------------------------------------------------------------------------
# Utilidades de texto
# --------------------------------------------------------------------------------------


def esc(t):
    """Escapa lo mínimo para que el texto literal no active formato Markdown."""
    t = t.replace("\\", "\\\\").replace("*", "\\*").replace("_", "\\_").replace("<", "\\<")
    return t.replace("[[", "\\[\\[")


def envolver(txt, b, i, sup):
    if not txt.strip():
        return txt
    pre = txt[:len(txt) - len(txt.lstrip())]
    post = txt[len(txt.rstrip()):]
    core = txt.strip()
    if sup:
        core = "<sup>%s</sup>" % core
    if b and i:
        core = "***%s***" % core
    elif b:
        core = "**%s**" % core
    elif i:
        core = "*%s*" % core
    return pre + core + post


def render_inline(sp, saltar=0, estilos=True):
    """sp: lista de [texto, negrita, cursiva, sup]. Salta los primeros `saltar` caracteres."""
    partes = []
    for texto, b, i, sup in sp:
        if saltar > 0:
            if saltar >= len(texto):
                saltar -= len(texto)
                continue
            texto = texto[saltar:]
            saltar = 0
        st = (bool(b) and estilos, bool(i) and estilos, bool(sup) and estilos)
        if partes and partes[-1][0] == st:
            partes[-1][1] += texto
        else:
            partes.append([st, texto])
    out = "".join(envolver(esc(t), *st) for st, t in partes)
    return out.strip()


def proteger_inicio(txt):
    """Evita que un párrafo común que empieza con '2014.' o '- ' se convierta en lista/cita."""
    m = re.match(r"^(\s*)(\d+)([\.\)])(\s)", txt)
    if m:
        return m.group(1) + m.group(2) + "\\" + m.group(3) + txt[m.end(3):]
    if re.match(r"^\s*[#>+\-]\s", txt) or re.match(r"^\s*#{1,6}\S", txt):
        i = len(txt) - len(txt.lstrip())
        return txt[:i] + "\\" + txt[i:]
    return txt


def a_romano(n):
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
            (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    s = ""
    for v, r in vals:
        while n >= v:
            s += r
            n -= v
    return s


def de_romano(s):
    s = s.lower()
    m = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    if not s or any(c not in m for c in s):
        return None
    tot = 0
    for k, c in enumerate(s):
        v = m[c]
        if k + 1 < len(s) and m[s[k + 1]] > v:
            tot -= v
        else:
            tot += v
    return tot if 0 < tot < 4000 and a_romano(tot) == s else None


def yaml_str(s):
    return json.dumps(s, ensure_ascii=False)


def mediana_ponderada(pares):
    pares = sorted(pares)
    total = sum(w for _, w in pares)
    if not total:
        return None
    acc = 0
    for v, w in pares:
        acc += w
        if acc >= total / 2.0:
            return v


def isbn_valido(s):
    d = re.sub(r"[^0-9Xx]", "", s)
    if len(d) == 13 and d.isdigit():
        tot = sum(int(c) * (1 if k % 2 == 0 else 3) for k, c in enumerate(d[:12]))
        return (10 - tot % 10) % 10 == int(d[12])
    if len(d) == 10:
        try:
            tot = sum((10 - k) * (10 if c in "xX" else int(c)) for k, c in enumerate(d[:9]))
            tot += 10 if d[9] in "xX" else int(d[9])
            return tot % 11 == 0
        except ValueError:
            return False
    return False


# --------------------------------------------------------------------------------------
# Extracción: capa de texto del PDF
# --------------------------------------------------------------------------------------


LIGATURAS = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",
             "\ufb05": "st", "\ufb06": "st", "\u00ad": ""}


def limpiar_texto(t):
    for k, v in LIGATURAS.items():
        if k in t:
            t = t.replace(k, v)
    return t


def estilo_span(s, tam_max):
    f = s.get("font", "")
    b = bool(s["flags"] & 16) or bool(re.search(r"bold|black|heavy|semibold|demi", f, re.I))
    i = bool(s["flags"] & 2) or bool(re.search(r"italic|oblique", f, re.I))
    sup = bool(s["flags"] & 1) or (s["size"] < 0.72 * tam_max and s["text"].strip().isdigit())
    return b, i, sup


def lineas_texto_pdf(page, clip):
    d = page.get_text("dict", clip=clip)
    out = []
    for bi, b in enumerate(d.get("blocks", [])):
        if b.get("type") != 0:
            continue
        for l in b.get("lines", []):
            dx, dy = l.get("dir", (1, 0))
            if abs(dy) > 0.5:
                continue  # texto vertical (sellos, márgenes)
            spans = [s for s in l.get("spans", []) if s["text"] != ""]
            for sp_ in spans:
                sp_["text"] = limpiar_texto(sp_["text"])
            spans = [s for s in spans if s["text"] != ""]
            plano = "".join(s["text"] for s in spans)
            if not plano.strip():
                continue
            tam_max = max(s["size"] for s in spans)
            sp = []
            n_b = n_i = tot = 0
            dom = {}
            for s in spans:
                bb, ii, sup = estilo_span(s, tam_max)
                n = len(s["text"].strip())
                tot += n
                n_b += n if bb else 0
                n_i += n if ii else 0
                dom[round(s["size"], 1)] = dom.get(round(s["size"], 1), 0) + n
                sp.append([s["text"], bb, ii, sup])
            tot = max(tot, 1)
            x0, y0, x1, y1 = l["bbox"]
            out.append({
                "k": "texto", "sp": sp, "p": plano,
                "s": max(dom, key=dom.get),
                "x0": x0 - clip.x0, "x1": x1 - clip.x0, "y0": y0 - clip.y0, "y1": y1 - clip.y0,
                "b": n_b / float(tot), "i": n_i / float(tot), "bl": "t%d" % bi,
            })
    return out


def unir_misma_linea(lineas):
    """Une fragmentos que están en la misma línea de base y pegados horizontalmente."""
    out = []
    for l in lineas:
        for m in out:
            tam = max(l["s"], m["s"])
            if (abs((l["y0"] + l["y1"]) / 2 - (m["y0"] + m["y1"]) / 2) < 0.35 * tam
                    and -1 <= l["x0"] - m["x1"] < 1.5 * tam):
                tot = max(1, len(m["p"].strip()) + len(l["p"].strip()))
                m["b"] = (m["b"] * len(m["p"].strip()) + l["b"] * len(l["p"].strip())) / float(tot)
                m["i"] = (m["i"] * len(m["p"].strip()) + l["i"] * len(l["p"].strip())) / float(tot)
                m["sp"] = m["sp"] + l["sp"]
                m["p"] = m["p"] + l["p"]
                m["x1"] = max(m["x1"], l["x1"])
                m["y0"], m["y1"] = min(m["y0"], l["y0"]), max(m["y1"], l["y1"])
                break
        else:
            out.append(l)
    return out


def tabla_md(filas):
    def celda(c):
        return esc((c or "").replace("\n", " ").strip()).replace("|", "\\|")
    ncol = max(len(r) for r in filas)
    filas = [list(r) + [""] * (ncol - len(r)) for r in filas]
    out = ["| " + " | ".join(celda(c) for c in filas[0]) + " |",
           "|" + "|".join(["---"] * ncol) + "|"]
    for r in filas[1:]:
        out.append("| " + " | ".join(celda(c) for c in r) + " |")
    return "\n".join(out)


def tablas_pdf(page, clip):
    """Tablas dibujadas con líneas (solo PDFs con capa de texto). Mejor esfuerzo."""
    try:
        tf = page.find_tables(clip=clip)
    except Exception:
        return []
    res = []
    for t in getattr(tf, "tables", []):
        try:
            filas = t.extract()
        except Exception:
            continue
        if len(filas) < 2 or max(len(r) for r in filas) < 2:
            continue
        res.append({"bbox": t.bbox, "md": tabla_md(filas)})
    return res


def integrar_tablas(lineas, tablas, clip):
    if not tablas:
        return lineas
    resto = []
    for l in lineas:
        cx = (l["x0"] + l["x1"]) / 2.0 + clip.x0
        cy = (l["y0"] + l["y1"]) / 2.0 + clip.y0
        dentro = any(t["bbox"][0] - 2 <= cx <= t["bbox"][2] + 2 and t["bbox"][1] - 2 <= cy <= t["bbox"][3] + 2
                     for t in tablas)
        if not dentro:
            resto.append(l)
    for n, t in enumerate(tablas):
        x0, y0, x1, y1 = t["bbox"]
        resto.append({"k": "tabla", "md": t["md"], "p": "", "sp": [], "s": 0,
                      "x0": x0 - clip.x0, "x1": x1 - clip.x0, "y0": y0 - clip.y0, "y1": y1 - clip.y0,
                      "b": 0, "i": 0, "bl": "tabla%d" % n})
    # orden de lectura: cada tabla va después de la última línea (en orden de flujo) que termina sobre ella
    base = [l for l in resto if l["k"] != "tabla"]
    tabs = [l for l in resto if l["k"] == "tabla"]
    for t in sorted(tabs, key=lambda l: l["y0"]):
        pos = 0
        for idx, l in enumerate(base):
            if l["y1"] <= t["y0"] + 2:
                pos = idx + 1
        base.insert(pos, t)
    return base


# --------------------------------------------------------------------------------------
# Extracción: OCR
# --------------------------------------------------------------------------------------


def otsu(gris):
    hist = np.bincount(gris.ravel(), minlength=256).astype(float)
    total = gris.size
    suma = float(np.dot(np.arange(256), hist))
    sb = wb = 0.0
    mejor, umbral = 0.0, 127
    for t in range(256):
        wb += hist[t]
        if wb == 0:
            continue
        wf = total - wb
        if wf == 0:
            break
        sb += t * hist[t]
        var = wb * wf * (sb / wb - (suma - sb) / wf) ** 2
        if var > mejor:
            mejor, umbral = var, t
    return umbral


def grosor_trazo(gris, umbral, x, y, w, h):
    rec = gris[max(0, y):y + h, max(0, x):x + w] < umbral
    if rec.size == 0:
        return 0.0
    tinta = int(rec.sum())
    if tinta == 0:
        return 0.0
    r8 = rec.astype(np.int8)
    cambios = int((np.diff(r8, axis=1) == 1).sum()) + int(r8[:, 0].sum())
    return (tinta / float(max(1, cambios))) / float(max(1, h))


NS = "{http://www.w3.org/1999/xhtml}"
RE_BBOX = re.compile(r"bbox (-?\d+) (-?\d+) (-?\d+) (-?\d+)")
RE_WCONF = re.compile(r"x_wconf (-?\d+)")
RE_XSIZE = re.compile(r"x_size ([\d.]+)")
CLASES_LINEA = ("ocr_line", "ocr_header", "ocr_caption", "ocr_textfloat")


def ocr_una_vez(img):
    """OCR con hOCR: da líneas con texto, posición, tamaño de letra (x_size) y confianza."""
    hocr = pytesseract.image_to_pdf_or_hocr(img, lang=OCR_LANG, extension="hocr", config="--psm 3")
    root = ET.fromstring(hocr)
    gris = np.asarray(img.convert("L"))
    umbral = otsu(gris)
    k = 72.0 / DPI
    grupos = []
    confs = []
    pares = [e for e in root.iter() if e.get("class") == "ocr_par"]
    for par_i, par in enumerate(pares):
        for ln in par.iter():
            if ln.get("class") not in CLASES_LINEA:
                continue
            palabras = []
            for w in ln.iter(NS + "span"):
                if w.get("class") != "ocrx_word":
                    continue
                txt = "".join(w.itertext()).strip()
                tt = w.get("title", "")
                bb = RE_BBOX.search(tt)
                if not txt or not bb:
                    continue
                x0, y0, x1, y1 = [int(v) for v in bb.groups()]
                wc = RE_WCONF.search(tt)
                if wc and int(wc.group(1)) >= 0:
                    confs.append(int(wc.group(1)))
                letras = sum(ch.isalpha() for ch in txt)
                g = grosor_trazo(gris, umbral, x0, y0, x1 - x0, y1 - y0) if letras >= 3 else 0.0
                tag_b = w.find(".//" + NS + "strong") is not None
                tag_i = w.find(".//" + NS + "em") is not None
                palabras.append((txt, x0, y0, x1, y1, g, tag_b, tag_i))
            if palabras:
                xs = RE_XSIZE.search(ln.get("title", ""))
                grupos.append((par_i, float(xs.group(1)) if xs else None, palabras))
    todos_g = [p[5] for _, _, ws in grupos for p in ws if p[5] > 0]
    g_med = statistics.median(todos_g) if todos_g else 0.0
    lineas = []
    for par_i, xsize, ws in grupos:
        flags = []
        for (t, x0, y0, x1, y1, g, tb, ti) in ws:
            if tb:
                flags.append(True)
            elif g_med and g > 0:
                flags.append(g > FACTOR_BOLD_OCR * g_med)
            else:
                flags.append(None)
        for n, f in enumerate(flags):  # palabras cortas entre dos negritas -> negrita
            if f is None:
                ant = next((flags[j] for j in range(n - 1, -1, -1) if flags[j] is not None), False)
                sig = next((flags[j] for j in range(n + 1, len(flags)) if flags[j] is not None), False)
                flags[n] = bool(ant and sig)
        n = 0
        while n < len(flags):  # una negrita aislada de una sola palabra se descarta (mucho ruido)
            if flags[n]:
                m = n
                while m < len(flags) and flags[m]:
                    m += 1
                if m - n < 2:
                    for j in range(n, m):
                        flags[j] = False
                n = m
            else:
                n += 1
        plano = " ".join(p[0] for p in ws)
        sp = []
        for n, (t, x0, y0, x1, y1, g, tb, ti) in enumerate(ws):
            sp.append([t + (" " if n < len(ws) - 1 else ""), flags[n], ti, False])
        alto = max(p[4] for p in ws) - min(p[2] for p in ws)
        s_px = xsize if xsize else alto
        s_pt = s_px * k * (1.0 if any(ch.islower() for ch in plano) else FACTOR_MAYUS)
        tot = max(1, sum(len(q[0].strip()) for q in sp))
        n_b = sum(len(q[0].strip()) for q in sp if q[1])
        n_i = sum(len(q[0].strip()) for q in sp if q[2])
        lineas.append({
            "k": "texto", "sp": sp, "p": plano, "s": s_pt,
            "x0": min(p[1] for p in ws) * k, "x1": max(p[3] for p in ws) * k,
            "y0": min(p[2] for p in ws) * k, "y1": max(p[4] for p in ws) * k,
            "b": n_b / float(tot), "i": n_i / float(tot), "bl": "o%d" % par_i,
        })
    conf = sum(confs) / float(len(confs)) if confs else 0.0
    return lineas, conf


def lineas_ocr(img):
    lineas, conf = ocr_una_vez(img)
    rotada = False
    if conf < 55:  # ¿página girada / cabeza abajo?
        try:
            from pytesseract import Output
            rot = pytesseract.image_to_osd(img, output_type=Output.DICT).get("rotate", 0)
        except Exception:
            rot = 0
        if rot in (90, 180, 270):
            img2 = img.rotate(-rot, expand=True)
            l2, c2 = ocr_una_vez(img2)
            if c2 > conf + 10:
                lineas, conf, rotada = l2, c2, True
                img = img2
    return lineas, conf, rotada, img


# --------------------------------------------------------------------------------------
# Extracción: imágenes
# --------------------------------------------------------------------------------------


def leer_franjas(img):
    """OCR aparte de la franja inferior y superior: Tesseract lee mal un número suelto en una página grande."""
    w, h = img.size
    res = {}
    for nombre, (a, b) in (("pie", (0.88, 1.0)), ("cab", (0.0, 0.12))):
        try:
            res[nombre] = pytesseract.image_to_string(
                img.crop((0, int(a * h), w, int(b * h))), lang=OCR_LANG, config="--psm 6").strip()
        except Exception:
            res[nombre] = ""
    return res


def extraer_figuras(doc, page, clip, hoja, lado, dir_img):
    figs = []
    try:
        infos = page.get_image_info(xrefs=True)
    except Exception:
        return figs
    area = float(clip.width * clip.height)
    vistos = set()
    for n, inf in enumerate(infos, 1):
        xref = inf.get("xref", 0)
        bb = fitz.Rect(inf["bbox"]) & clip
        if not xref or bb.is_empty or xref in vistos:
            continue
        vistos.add(xref)
        if bb.width * bb.height > 0.8 * area:
            continue  # es un escaneo de página, no una figura
        if inf.get("width", 0) < 120 or inf.get("height", 0) < 120:
            continue
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha >= 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        except Exception:
            continue
        dir_img.mkdir(parents=True, exist_ok=True)
        nombre = "fig_h%04d%s_%d.webp" % (hoja, lado[:1] if lado else "", n)
        im.save(str(dir_img / nombre), "WEBP", quality=60)
        figs.append({"archivo": nombre, "ancho": im.size[0], "alto": im.size[1],
                     "y0": bb.y0 - clip.y0})
    return figs


# --------------------------------------------------------------------------------------
# Extracción de una unidad de página (una página impresa)
# --------------------------------------------------------------------------------------


def lados(page):
    r = page.rect
    if r.width > 1.25 * r.height:
        mitad = r.x0 + r.width / 2.0
        return [("izq", fitz.Rect(r.x0, r.y0, mitad, r.y1)), ("der", fitz.Rect(mitad, r.y0, r.x1, r.y1))]
    return [("", r)]


def extraer_unidad(doc, page, hoja, lado, clip, pos, dir_img):
    u = {"pos": pos, "hoja": hoja, "lado": lado, "ancho": clip.width, "alto": clip.height,
         "fuente": "sin_texto", "conf": None, "lineas": [], "figuras": []}
    lineas = []
    if not FORZAR_OCR:
        lineas = unir_misma_linea(lineas_texto_pdf(page, clip))
        lineas = integrar_tablas(lineas, tablas_pdf(page, clip), clip) if lineas else lineas
    chars = sum(len(l["p"].strip()) for l in lineas)
    if chars:
        u["fuente"] = "texto_pdf"
    if chars < MIN_CARACTERES_TEXTO:
        pix = page.get_pixmap(dpi=DPI, clip=clip)
        img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        l_ocr, conf, rotada, img_ok = lineas_ocr(img)
        chars_ocr = sum(len(l["p"].strip()) for l in l_ocr)
        if chars_ocr > chars:
            lineas, chars = l_ocr, chars_ocr
            u["fuente"] = "ocr_rotada" if rotada else "ocr"
            u["conf"] = round(conf, 1)
            u["ancho"], u["alto"] = img_ok.size[0] * 72.0 / DPI, img_ok.size[1] * 72.0 / DPI
            u["franjas"] = leer_franjas(img_ok)
    u["lineas"] = lineas
    u["figuras"] = extraer_figuras(doc, page, clip, hoja, lado, dir_img)
    return u


# --------------------------------------------------------------------------------------
# Análisis global: cuerpo, márgenes, folios, niveles de título
# --------------------------------------------------------------------------------------

RE_NUM_PURO = re.compile(r"^[\-–—\s\.]*(\d{1,4})[\-–—\s\.]*$")
RE_ROM_PURO = re.compile(r"^[\-–—\s\.]*([ivxlcdmIVXLCDM]{1,7})[\-–—\s\.]*$")
RE_NUM_INI = re.compile(r"^(\d{1,3})\s+\S")
RE_NUM_FIN = re.compile(r"\S\s+(\d{1,3})$")

RE_LISTA = re.compile(r"""^\s*(
    (?P<num>\d{1,3}[\.\)])
  | (?P<comp>\d{1,2}(?:\.\d{1,2})+\.?)
  | (?P<numlet>\d{1,2}[a-z][\.\)])
  | (?P<let>[a-z][\.\)]|[A-Z]\))
  | (?P<rom>[ivx]{1,4}[\.\)]|[IVX]{2,5}[\.\)]|[IVX]\))
  | (?P<bul>[•·▪●■◦○\-–—\*])
)\s+(?=\S)""", re.X)


def calcular_cuerpo(unidades):
    pares = []
    for u in unidades:
        for l in u["lineas"]:
            if l["k"] == "texto" and len(l["p"].strip()) >= 25:
                pares.append((round(l["s"], 1), len(l["p"])))
    return mediana_ponderada(pares) or 10.0


def marcar_margenes(unidades, cuerpo):
    """Cabecera/pie corridos: cortos, chicos y (números de página, o separados del cuerpo)."""
    for u in unidades:
        alto = u["alto"]
        for l in u["lineas"]:
            l["z"] = None
        lins = [l for l in u["lineas"] if l["k"] == "texto"]
        cands = []
        for l in lins:
            if l["s"] > 1.15 * cuerpo or len(l["p"].split()) > 12:
                continue
            if l["y1"] < 0.12 * alto:
                cands.append((l, "cab"))
            elif l["y0"] > 0.88 * alto:
                cands.append((l, "pie"))
        ids = set(id(l) for l, _ in cands)
        for l, z in cands:
            p = l["p"].strip()
            pura = bool(RE_NUM_PURO.match(p) or RE_ROM_PURO.match(p))
            otros = [o for o in lins if id(o) not in ids]
            if z == "cab":
                sep = [o["y0"] - l["y1"] for o in otros if o["y0"] >= l["y1"] - 1]
                extremo = l["y1"] < ZONA_MARGEN * alto
            else:
                sep = [l["y0"] - o["y1"] for o in otros if o["y1"] <= l["y0"] + 1]
                extremo = l["y0"] > (1 - ZONA_MARGEN) * alto
            separado = bool(sep) and min(sep) >= 1.8 * cuerpo
            if pura or separado or extremo:
                l["z"] = z


def leer_folio(u):
    """Devuelve ('arabe', n) / ('romano', n) / None leído de cabecera o pie."""
    marg = [l for l in u["lineas"] if l.get("z")]
    marg.sort(key=lambda l: 0 if l["z"] == "pie" else 1)
    textos = [l["p"].strip() for l in marg]
    fr = u.get("franjas") or {}
    franja = [t.strip() for k in ("pie", "cab") for t in fr.get(k, "").splitlines() if t.strip()]
    for p in textos + franja:                      # 1) número arábigo solo
        m = RE_NUM_PURO.match(p)
        if m and 1 <= int(m.group(1)) <= 2500:
            return ("arabe", int(m.group(1)))
    for p in textos:                               # 2) romano solo: solo i, v, x (el OCR confunde l/c/d/m)
        m = RE_ROM_PURO.match(p)
        if m and re.fullmatch(r"[ivxIVX]+", m.group(1)):
            n = de_romano(m.group(1))
            if n and n <= 39:
                return ("romano", n)
    for p in textos + franja:                      # 3) "42 Título" o "Título 43"
        if len(p.split()) > 12:
            continue
        m = RE_NUM_INI.match(p) or RE_NUM_FIN.search(p)
        if m and 1 <= int(m.group(1)) <= 999:
            return ("arabe", int(m.group(1)))
    return None


def calibrar(unidades, explicito):
    votos, votos_r = Counter(), Counter()
    for u in unidades:
        f = u.get("leido")
        if not f:
            continue
        if f[0] == "arabe":
            votos[u["pos"] - f[1]] += 1
        else:
            votos_r[u["pos"] - f[1]] += 1
    n_ar = sum(votos.values())
    detectado, apoyo = None, 0
    if votos:
        detectado, apoyo = votos.most_common(1)[0]
    ok_det = detectado is not None and apoyo >= 3 and apoyo >= 0.5 * n_ar
    off_rom = None
    if votos_r:
        o, c = votos_r.most_common(1)[0]
        if c >= 2 and c >= 0.5 * sum(votos_r.values()):
            off_rom = o
    info = {"detectado": detectado if ok_det else None, "apoyo": apoyo, "leidas": n_ar,
            "off_rom": off_rom, "alerta": None}
    if explicito is not None:
        info["offset"] = explicito
        info["origen"] = "nombre_de_archivo"
        if ok_det and detectado != explicito:
            info["alerta"] = ("el offset del nombre (%d) no coincide con el leído en las páginas (%d, %d de %d)"
                              % (explicito, detectado, apoyo, n_ar))
    elif ok_det:
        info["offset"] = detectado
        info["origen"] = "detectada_en_paginas (%d de %d folios leídos coinciden)" % (apoyo, n_ar)
    else:
        info["offset"] = 0
        info["origen"] = "NO_CALIBRADA (sin folios legibles: folio = posición de página)"
    return info


def etiqueta_folio(pos, cal, leido=None):
    n = pos - cal["offset"]
    if n >= 1:
        return str(n)
    if cal["off_rom"] is not None and pos - cal["off_rom"] >= 1:
        return a_romano(pos - cal["off_rom"])
    if leido and leido[0] == "romano":
        return a_romano(leido[1])
    return "prel-%d" % pos


def info_titulo(l, cuerpo):
    p = l["p"].strip()
    if not p or len(p) > 160:
        return None
    palabras = len(p.split())
    letras = [c for c in p if c.isalpha()]
    if palabras > 22 or len(letras) < 3 or p[-1] in ",;" or re.search(r"[\[\]|{}]", p):
        return None
    if p.endswith(".") and palabras > 12:
        return None
    return {"ratio": l["s"] / cuerpo, "mayus": len(letras) >= 4 and p == p.upper(),
            "negrita": l["b"] >= 0.8, "palabras": palabras}


def construir_niveles(unidades, cuerpo):
    ratios = []
    for u in unidades:
        for l in u["lineas"]:
            if l["k"] == "texto" and not l.get("z"):
                it = info_titulo(l, cuerpo)
                if it and it["ratio"] >= RATIO_TITULO:
                    ratios.append(it["ratio"])
    if not ratios:
        return []
    ratios.sort(reverse=True)
    clusters = [[ratios[0]]]
    for r in ratios[1:]:
        if r >= 0.86 * clusters[-1][0]:   # mismo nivel si está a menos de ~14 % del mayor del grupo
            clusters[-1].append(r)
        else:
            clusters.append([r])
    medias = [(sum(c) / len(c), len(c)) for c in clusters]
    validos = [m for m in medias if m[1] >= 2 or m[0] >= 1.6]
    if not validos:
        validos = [medias[0]]
    return [m[0] for m in validos[:3]]


def nivel_de(ratio, niveles):
    mejor = min(range(len(niveles)), key=lambda k: abs(niveles[k] - ratio))
    return mejor + 1


# --------------------------------------------------------------------------------------
# Construcción del Markdown
# --------------------------------------------------------------------------------------


def comentario(txt):
    return txt.replace("--", "- -")


def render_unidad(u, ctx, cal):
    cuerpo, niveles = ctx["cuerpo"], ctx["niveles"]
    folio = etiqueta_folio(u["pos"], cal, u.get("leido"))
    marca = ["FOLIO_IMPRESO: %s" % folio, "HOJA_PDF: %d" % u["hoja"]]
    if u["lado"]:
        marca.append("LADO: %s" % u["lado"])
    marca.append("FUENTE: %s" % u["fuente"])
    if u["conf"] is not None:
        marca.append("OCR_CONF: %d" % round(u["conf"]))
    leido = u.get("leido")
    if leido:
        marca.append("FOLIO_LEIDO: %s" % (leido[1] if leido[0] == "arabe" else a_romano(leido[1])))
    calibrado = not cal["origen"].startswith("NO_CALIBRADA")
    if calibrado and leido and leido[0] == "arabe" and folio.isdigit() and int(folio) != leido[1]:
        marca.append("ALERTA: folio leído %d" % leido[1])
    elif calibrado and leido and leido[0] == "romano" and folio != a_romano(leido[1]) and not folio.isdigit():
        marca.append("ALERTA: folio leído %s" % a_romano(leido[1]))
    salida = ["", "<!-- " + " | ".join(marca) + " -->"]
    outline = []

    cab = [l for l in u["lineas"] if l.get("z") == "cab"]
    pie = [l for l in u["lineas"] if l.get("z") == "pie"]
    for l in cab:
        salida.append("<!-- CABECERA: %s -->" % comentario(l["p"].strip()))

    cuerpo_l = [l for l in u["lineas"] if not l.get("z")]
    if not u["lineas"]:
        salida.append("<!-- PÁGINA SIN TEXTO -->")

    ys = sorted((l["y0"] + l["y1"]) / 2.0 for l in cuerpo_l if l["k"] == "texto")
    pasos = [b - a for a, b in zip(ys, ys[1:]) if 0.7 * cuerpo <= b - a <= 2.2 * cuerpo]
    interlineado = statistics.median(pasos) if pasos else 1.2 * cuerpo
    anchos = sorted(l["x1"] for l in cuerpo_l if l["k"] == "texto" and len(l["p"]) >= 40)
    der = anchos[int(0.9 * (len(anchos) - 1))] if anchos else u["ancho"]

    prev = None          # (tipo, línea)
    pila = []            # sangrías de la lista en curso
    ult_titulo = None    # (índice en salida, nivel, línea, índice en outline)

    def blanco():
        if salida and salida[-1] != "":
            salida.append("")

    for idx, l in enumerate(cuerpo_l):
        sig = cuerpo_l[idx + 1] if idx + 1 < len(cuerpo_l) else None
        if l["k"] == "tabla":
            blanco()
            salida.append(l["md"])
            salida.append("")
            prev, ult_titulo = ("tabla", l), None
            continue
        it = info_titulo(l, cuerpo)
        nivel = None
        if it:
            if it["ratio"] >= RATIO_TITULO and niveles:
                nivel = nivel_de(it["ratio"], niveles)
            else:
                sola = sum(1 for o in cuerpo_l if o["bl"] == l["bl"]) == 1
                if sola and (it["negrita"] or it["mayus"]) and it["palabras"] <= 15:
                    nivel = min(len(niveles) + 1, 4)
        if nivel:
            texto = render_inline(l["sp"], 0, estilos=False)
            gap = l["y0"] - prev[1]["y1"] if prev else 999
            if (ult_titulo and prev and prev[0] == "titulo" and ult_titulo[1] == nivel
                    and (prev[1]["bl"] == l["bl"] or gap < 0.8 * l["s"])):
                i0 = ult_titulo[0]
                salida[i0] = salida[i0] + " " + texto
                if ult_titulo[3] is not None:
                    outline[ult_titulo[3]]["titulo"] += " " + texto
            else:
                blanco()
                salida.append("#" * nivel + " " + texto)
                salida.append("")
                outline.append({"nivel": nivel, "titulo": texto, "folio": folio, "hoja": u["hoja"]})
                ult_titulo = (len(salida) - 2, nivel, l, len(outline) - 1)
            prev = ("titulo", l)
            continue

        m = RE_LISTA.match(l["p"])
        gap = (l["y0"] - prev[1]["y1"]) if prev and prev[0] != "tabla" else 999
        paso = (((l["y0"] + l["y1"]) - (prev[1]["y0"] + prev[1]["y1"])) / 2.0) if prev and prev[0] != "tabla" else 999
        salto = paso > 1.3 * interlineado or gap > 0.65 * l["s"]
        if m:
            grupo = next(g for g in ("num", "comp", "numlet", "let", "rom", "bul") if m.group(g))
            tol = 0.8 * cuerpo
            if prev is None or prev[0] not in ("lista", "cont"):
                pila = [l["x0"]]
            else:
                while len(pila) > 1 and l["x0"] < pila[-1] - tol:
                    pila.pop()
                if l["x0"] < pila[0] - tol:
                    pila = [l["x0"]]
                elif l["x0"] > pila[-1] + tol:
                    pila.append(l["x0"])
            nivel_l = min(len(pila) - 1, 3)
            etiqueta = m.group(1).strip()
            resto = render_inline(l["sp"], m.end(), estilos=True)
            if prev is None or prev[0] not in ("lista", "cont"):
                blanco()
            sang = "    " * nivel_l
            if grupo == "num":
                salida.append("%s%s %s" % (sang, etiqueta, resto))
            elif grupo == "bul":
                salida.append("%s- %s" % (sang, resto))
            else:
                salida.append("%s- %s %s" % (sang, esc(etiqueta).replace(".", "\\."), resto))
            prev = ("lista", l)
            ult_titulo = None
            continue

        texto = render_inline(l["sp"], 0, estilos=True)
        if prev and prev[0] in ("lista", "cont") and not salto and (
                not l["bl"].startswith("o") or prev[1]["bl"] == l["bl"] or l["x0"] > prev[1]["x0"] + 0.3 * l["s"]):
            salida.append(texto)
            prev = ("cont", l)
            continue
        nuevo = (prev is None or prev[0] not in ("texto",)
                 or (l["bl"].startswith("o") and prev[1]["bl"] != l["bl"])
                 or salto
                 or (l["x0"] - prev[1]["x0"] > 0.9 * l["s"] and prev[1]["x1"] < der - 1.0 * l["s"]
                     and sig is not None and sig["k"] == "texto" and sig["bl"] == l["bl"]
                     and sig["x0"] < l["x0"] - 0.5 * l["s"]))
        if nuevo:
            blanco()
            salida.append(proteger_inicio(texto))
        else:
            salida.append(texto)
        prev = ("texto", l)
        ult_titulo = None

    for f in sorted(u["figuras"], key=lambda f: f["y0"]):
        blanco()
        salida.append("```yaml\nfigura:\n  hoja_pdf: %d\n  ancho_px: %d\n  alto_px: %d\n  archivo: imagenes/%s\n```"
                      % (u["hoja"], f["ancho"], f["alto"], f["archivo"]))
        salida.append("![figura hoja %d](imagenes/%s)" % (u["hoja"], f["archivo"]))
        salida.append("")
    if pie:
        blanco()
    for l in pie:
        salida.append("<!-- PIE: %s -->" % comentario(l["p"].strip()))
    return salida, outline, folio


# --------------------------------------------------------------------------------------
# Metadatos
# --------------------------------------------------------------------------------------

RE_NOMBRE = re.compile(r"^(\d{4}) - (.+?) - (.+?)(?: \[offset(-?\d+)\])?$")


def parsear_nombre(stem):
    m = RE_NOMBRE.match(stem)
    if m:
        return {"anio": m.group(1), "autor": m.group(2), "titulo": m.group(3),
                "offset": int(m.group(4)) if m.group(4) is not None else None, "patron": True,
                "base": "%s - %s - %s" % (m.group(1), m.group(2), m.group(3))}
    a = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", stem)
    return {"anio": a.group(1) if a else "por_completar", "autor": "por_completar", "titulo": stem,
            "offset": None, "patron": False, "base": stem}


def buscar_isbn(unidades):
    textos = []
    for u in unidades[:25] + unidades[-8:]:
        textos.append(" ".join(l["p"] for l in u["lineas"] if l["k"] == "texto"))
    t = " ".join(textos)
    res = []
    for m in re.finditer(r"ISBN(?:-1[03])?\s*:?\s*([0-9Xx][0-9Xx\s\-]{8,16}[0-9Xx])", t, re.I):
        c = re.sub(r"\s+", "", m.group(1))
        if isbn_valido(c) and c not in res:
            res.append(c)
    return res


def buscar_anio_copyright(unidades):
    t = " ".join(l["p"] for u in unidades[:25] for l in u["lineas"] if l["k"] == "texto")
    m = re.search(r"(?:©|\(c\)|copyright|derechos reservados)[^\d]{0,40}((?:19|20)\d{2})", t, re.I)
    return m.group(1) if m else None


def frontmatter(meta, unidades, cal, outline, isbn, anio_c, n_hojas, stats, aviso):
    n_u = len(unidades)
    off = cal["offset"]
    folio_fin = n_u - off
    L = ["---", "registro_tipo: libro_transcripcion",
         "titulo: " + yaml_str(meta["titulo"]),
         "autor: " + yaml_str(meta["autor"]),
         "anio: " + yaml_str(meta["anio"])]
    if anio_c and meta["anio"] == "por_completar":
        L.append("anio_probable_copyright: " + yaml_str(anio_c))
    L.append("isbn_detectado: [%s]" % ", ".join(yaml_str(i) for i in isbn))
    L.append("fuente_archivo: " + yaml_str(meta["archivo"]))
    L.append("hojas_pdf: %d" % n_hojas)
    if n_u != n_hojas:
        L.append("paginas_dobles_separadas: true")
        L.append("unidades_de_pagina: %d" % n_u)
    L += ["foliacion:",
          "  formula: \"FOLIO_IMPRESO = POSICION - offset\"",
          "  offset: %d" % off,
          "  origen: " + yaml_str(cal["origen"]),
          "  primer_folio_arabigo_en_posicion: %d" % max(1, off + 1),
          "  folio_final: %d" % folio_fin]
    if cal["off_rom"] is not None:
        L.append("  offset_romano: %d" % cal["off_rom"])
    if cal["alerta"]:
        L.append("  alerta: " + yaml_str(cal["alerta"]))
    L.append("  validez_legal: \"Citar FOLIO_IMPRESO y verificar contra la página impresa; el OCR puede contener errores.\"")
    L += ["transcripcion:",
          "  motor: \"capa de texto del PDF cuando existe; OCR Tesseract (%s, %d dpi) en el resto\"" % (OCR_LANG, DPI),
          "  paginas_texto_pdf: %d" % stats["texto_pdf"],
          "  paginas_ocr: %d" % stats["ocr"],
          "  paginas_sin_texto: [%s]" % ", ".join(str(h) for h in stats["sin_texto"][:200]),
          "  paginas_ocr_dudosas: [%s]" % ", ".join(str(h) for h in stats["dudosas"][:200]),
          "  figuras_extraidas: %d" % stats["figuras"],
          "  tablas_detectadas: %d" % stats["tablas"]]
    if aviso:
        L.append("aviso: " + yaml_str(aviso))
    esquema = [o for o in outline if o["nivel"] <= 3][:500]
    if esquema:
        L.append("estructura:")
        for o in esquema:
            L.append("  - {nivel: %d, titulo: %s, folio: %s, hoja_pdf: %d}"
                     % (o["nivel"], yaml_str(o["titulo"]), yaml_str(o["folio"]), o["hoja"]))
    else:
        L.append("estructura: []")
    L.append("---")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------------------
# Proceso de un libro
# --------------------------------------------------------------------------------------


def ya_existe(base):
    for d in glob.glob(glob.escape(str(CARPETA / base)) + " [[]*p]"):
        if glob.glob(os.path.join(glob.escape(d), "*.md")):
            return True
    return False


def procesar(pdf):
    meta = parsear_nombre(pdf.stem)
    meta["archivo"] = pdf.name
    if ya_existe(meta["base"]):
        print("YA EXISTE carpeta para este libro, no se reprocesa:", meta["base"])
        return
    trabajo = CARPETA / ".trabajo" / pdf.stem
    clave = "%d-%d" % (pdf.stat().st_size, int(pdf.stat().st_mtime))
    if trabajo.exists() and (trabajo / "origen.txt").exists() and (trabajo / "origen.txt").read_text() != clave:
        shutil.rmtree(str(trabajo))
    trabajo.mkdir(parents=True, exist_ok=True)
    (trabajo / "origen.txt").write_text(clave)
    dir_img = trabajo / "imagenes"

    doc = fitz.open(str(pdf))
    n_hojas = len(doc)
    print("Procesando: %s (%d hojas)" % (pdf.name, n_hojas))
    t0 = time.time()
    unidades = []
    pos = 0
    for hoja in range(1, n_hojas + 1):
        page = doc[hoja - 1]
        for lado, clip in lados(page):
            pos += 1
            cache = trabajo / ("u%05d.json" % pos)
            if cache.exists():
                u = json.loads(cache.read_text(encoding="utf-8"))
            else:
                u = extraer_unidad(doc, page, hoja, lado, clip, pos, dir_img)
                cache.write_text(json.dumps(u, ensure_ascii=False), encoding="utf-8")
            unidades.append(u)
        if hoja % 10 == 0 or hoja == n_hojas:
            print("  hoja %d/%d  (%.0f s)" % (hoja, n_hojas, time.time() - t0))
    doc.close()

    cuerpo = calcular_cuerpo(unidades)
    marcar_margenes(unidades, cuerpo)
    for u in unidades:
        u["leido"] = leer_folio(u)
    cal = calibrar(unidades, meta["offset"])
    if cal["alerta"]:
        print("  AVISO:", cal["alerta"])
    ctx = {"cuerpo": cuerpo, "niveles": construir_niveles(unidades, cuerpo)}

    cuerpo_md, outline = [], []
    for u in unidades:
        s, o, _ = render_unidad(u, ctx, cal)
        cuerpo_md += s
        outline += o

    stats = {
        "texto_pdf": sum(1 for u in unidades if u["fuente"] == "texto_pdf"),
        "ocr": sum(1 for u in unidades if u["fuente"].startswith("ocr")),
        "sin_texto": [u["hoja"] for u in unidades if u["fuente"] == "sin_texto"],
        "dudosas": [u["hoja"] for u in unidades if u["conf"] is not None and u["conf"] < CONF_DUDOSA],
        "figuras": sum(len(u["figuras"]) for u in unidades),
        "tablas": sum(1 for u in unidades for l in u["lineas"] if l["k"] == "tabla"),
    }
    aviso = None
    if not meta["patron"]:
        aviso = "nombre de archivo sin el patrón 'Año - Autor - Título [offsetNN]': autor y título por completar"
    fm = frontmatter(meta, unidades, cal, outline, buscar_isbn(unidades), buscar_anio_copyright(unidades),
                     n_hojas, stats, aviso)

    n_impresas = max(0, len(unidades) - max(cal["offset"], 0))
    nombre_final = "%s [%dp]" % (meta["base"], n_impresas)
    destino = CARPETA / nombre_final
    destino.mkdir(parents=True, exist_ok=True)
    salida = destino / (nombre_final + ".md")
    tmp = destino / (nombre_final + ".md.tmp")
    tmp.write_text(fm + "\n" + "\n".join(cuerpo_md).strip() + "\n", encoding="utf-8")
    tmp.rename(salida)
    if dir_img.exists():
        shutil.move(str(dir_img), str(destino / "imagenes"))
    if pdf.parent == CARPETA:
        shutil.move(str(pdf), str(destino / pdf.name))
    else:
        shutil.copy2(str(pdf), str(destino / pdf.name))
    shutil.rmtree(str(trabajo), ignore_errors=True)
    try:
        (CARPETA / ".trabajo").rmdir()   # solo si quedó vacío
    except OSError:
        pass
    print("LISTO: %s  (offset %d, %s; %d títulos; %.0f s)"
          % (destino.name, cal["offset"], cal["origen"].split(" ")[0], len(outline), time.time() - t0))
    return salida


# --------------------------------------------------------------------------------------
# Vigilancia de la carpeta (escaneo cada 5 s)
# --------------------------------------------------------------------------------------

cola = queue.Queue()
vistos = set()


def esperar_copia_completa(ruta):
    anterior = -1
    while True:
        try:
            tam = ruta.stat().st_size
        except FileNotFoundError:
            return False
        if tam == anterior and tam > 0:
            return True
        anterior = tam
        time.sleep(2)


def trabajador():
    while True:
        pdf = cola.get()
        try:
            if esperar_copia_completa(pdf):
                procesar(pdf)
                if not pdf.exists():
                    vistos.discard(pdf)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("ERROR con", pdf.name, "->", e)
        cola.task_done()


def encolar(ruta):
    ruta = Path(ruta)
    if ruta.name.startswith(".") or ruta.is_dir() or ruta.suffix.lower() != ".pdf":
        return
    if ruta in vistos:
        return
    vistos.add(ruta)
    cola.put(ruta)


if __name__ == "__main__":
    CARPETA.mkdir(parents=True, exist_ok=True)
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            procesar(Path(a).expanduser().resolve())
        sys.exit(0)
    threading.Thread(target=trabajador, daemon=True).start()
    print("Vigilando", CARPETA, "(Ctrl+C para salir)")
    try:
        while True:
            for p in sorted(CARPETA.glob("*.pdf")):
                encolar(p)
            time.sleep(5)
    except KeyboardInterrupt:
        pass
