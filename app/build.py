"""Regenera exercises.js, ejercicios-modulo2.html (autónomo) y artifact.html desde las fuentes."""
import json
r = lambda f: open(f, encoding='utf-8').read()
w = lambda f, t: open(f, 'w', encoding='utf-8').write(t)
base = json.loads(r('../data/exercises.json')); ref = json.loads(r('../data/examen_refuerzo.json'))
ex = 'window.EXERCISES = ' + json.dumps(base + ref, ensure_ascii=False) + ';\n'
w('exercises.js', ex)
css, js = r('style.css'), r('app.js')
w('ejercicios-modulo2.html', r('index.html')
  .replace('<link rel="stylesheet" href="style.css">', '<style>\n' + css + '</style>')
  .replace('<script src="exercises.js"></script>', '<script>\n' + ex + '</script>')
  .replace('<script src="app.js"></script>', '<script>\n' + js + '</script>'))

# --- versión Artifact: tema claro/oscuro, sin confirm(), sin header pegajoso ---
light = ":root{--bg:#f5f7fb;--card:#fff;--ink:#1d2433;--mute:#667085;--line:#dde2ec;--acc:#2f5bea;--ok:#1a8f4c;--okbg:#e6f6ec;--ko:#c62828;--kobg:#fdeaea;--cell:#fff;--cellink:#111}"
dark = "--bg:#10141c;--card:#1a202c;--ink:#e8ecf4;--mute:#9aa4b8;--line:#2b3446;--acc:#7b9bff;--ok:#5fd18c;--okbg:#14301f;--ko:#ff8a8a;--kobg:#3a1c1c;--cell:#232b3b;--cellink:#e8ecf4;color-scheme:dark"
a, b = css.index(':root{'), css.index('*{box-sizing')
c = css[:a] + light + '\n@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){' + dark + '}}\n:root[data-theme="dark"]{' + dark + '}\n' + css[b:]
for old, new in [("background:#fff}", "background:var(--cell)}"), ("color:#000;background:transparent", "color:var(--cellink);background:transparent"),
                 (".grid td.cell.ok{background:#bdebd0}.grid td.cell.ko{background:#f6c4c4}", ".grid td.cell.ok{background:var(--okbg)}.grid td.cell.ko{background:var(--kobg)}"),
                 ("color:#444;pointer-events", "color:var(--mute);pointer-events"), ("border:1px solid var(--ink);background:var(--cell)", "border:1px solid var(--mute);background:var(--cell)"),
                 (";position:sticky;top:0;z-index:5", ""),
                 ("body{margin:0;", "body{margin:0;padding-block:0;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));"),
                 (".layout{display:flex;gap:16px;max-width:1100px;margin:0 auto;padding:16px}", ".layout{display:flex;gap:16px;max-width:1100px;margin:0 auto;padding-block:16px}"),
                 (".top{display:flex;", ".top{margin-inline:-16px;padding-inline:16px;display:flex;")]:
    assert old in c, old; c = c.replace(old, new)
ajs = js.replace("const reset = h('button', { class: 's', onclick: () => { if (confirm('¿Borrar todo el progreso?')) { progress = {}; save(); show(); renderTotal(); } } }, 'Borrar progreso');",
"""let armed = false;
const reset = h('button', { class: 's', onclick: () => {
  if (!armed) { armed = true; reset.textContent = 'Confirmar: borrar todo'; setTimeout(() => { armed = false; reset.textContent = 'Borrar progreso'; }, 4000); return; }
  armed = false; reset.textContent = 'Borrar progreso'; progress = {}; save(); show(); renderTotal();
} }, 'Borrar progreso');""")
assert 'confirm(' not in ajs
w('artifact.html', '<title>Ejercicios Módulo 2</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>\n' + c + '</style>\n'
  '<header class="top">\n  <h1>Ejercicios interactivos <span>Módulo 2</span></h1>\n  <div id="total" class="total" aria-live="polite"></div>\n</header>\n'
  '<div class="layout">\n  <nav id="menu" aria-label="Ejercicios"></nav>\n  <main id="main"></main>\n</div>\n<script>\n' + ex + '</script>\n<script>\n' + ajs + '</script>\n')
