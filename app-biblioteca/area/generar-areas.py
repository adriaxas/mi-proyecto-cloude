#!/usr/bin/env python3
"""Genera areas-0.json para la pestaña «Área» de la app Biblioteca de Adrián.

Uso: python3 generar-areas.py > areas-0.json   (desde la raíz del repositorio)
Luego se publica areas-0.json como archivo del artefacto.
"""
import glob, json, os, re, sys, datetime

BASE = "areas/guiones-redes-sociales/"


def item(rel):
    x = open(BASE + rel, encoding="utf-8").read().replace("`", "")
    lineas = x.split("\n")
    titulo = rel
    if lineas[0].startswith("# "):
        titulo = lineas[0][2:].strip()
        x = "\n".join(lineas[1:]).lstrip("\n")
    m = re.search(r"\*\*Formato:\*\*\s*([^·\n]+)", x)
    return {"t": titulo, "p": BASE + rel, "s": m.group(1).strip() if m else "", "x": x}


guiones = ["00-presentacion-del-canal.md"] + sorted(
    os.path.basename(p) for p in glob.glob(BASE + "[0-9][0-9]-*.md")
    if not os.path.basename(p).startswith("00-"))
canal = ["00-linea-editorial.md", "00-plan-de-canal.md", "README.md"]
produccion = ["produccion/" + os.path.basename(p) for p in sorted(glob.glob(BASE + "produccion/*.md"))]

datos = {
    "fecha": datetime.date.today().strftime("%d/%m/%Y"),
    "areas": [{
        "n": "Guiones para redes sociales",
        "d": "Canal de psicología forense y práctica pericial",
        "g": [
            {"n": "Guiones", "f": [item(r) for r in guiones]},
            {"n": "Canal", "f": [item(r) for r in canal]},
            {"n": "Producción", "f": [item(r) for r in produccion]},
        ],
    }],
}
json.dump(datos, sys.stdout, ensure_ascii=False)
