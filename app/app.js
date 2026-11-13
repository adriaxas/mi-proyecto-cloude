(() => {
'use strict';
const EX = window.EXERCISES;
const KEY = 'modulo2-progreso-v1';
const IMG_LINKS = {
  'ej cap 3 17 PropCompuestos.jpg': 'https://drive.google.com/file/d/1WV2570vHZ2JKUD9LYktOuRs-Z2v7vX5q/view',
  'ozono.jpg': 'https://drive.google.com/file/d/1EyPSDeEI1e7Cq1-bWaphESJ_JBMF3KkV/view'
};
let progress = {};
try { progress = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(progress)); } catch (e) {} };

const $ = (s, r = document) => r.querySelector(s);
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') el.className = v; else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) el.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) el.append(k instanceof Node ? k : document.createTextNode(k));
  return el;
}
const norm = s => String(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().replace(/\s+/g, ' ').toLowerCase();
const setMark = (el, ok) => {
  el.classList.remove('ok', 'ko'); el.classList.add(ok ? 'ok' : 'ko');
  const old = el.querySelector(':scope > .mark'); if (old) old.remove();
  if (!el.matches('input,td')) el.append(h('span', { class: 'mark' }, ok ? '✔' : '✘'));
};

// ---------- Renderers: each returns { node, check() -> {correct,total} } ----------
const shuffled = a => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
function renderQuiz(ex) {
  const wrap = h('div'); const qs = [];
  ex.data.questions.forEach((q, qi) => {
    const box = h('div', { class: 'q' });
    const correctN = q.answers.filter(a => a.correct).length;
    const radio = q.type === 'multichoice' || (q.type === 'multiselect' && correctN === 1);
    box.append(h('div', {}, h('strong', {}, `${qi + 1}. `), q.text));
    let getOk, fb = h('div', { class: 'fb' });
    if (q.type === 'short') {
      const inp = h('input', { type: 'text', 'aria-label': `Respuesta ${qi + 1}` });
      box.append(inp);
      getOk = () => { const v = norm(inp.value); const hit = q.answers.find(a => a.correct && norm(a.text) === v); return !!hit; };
    } else {
      const labels = [];
      const inputs = q.answers.map((a, ai) => {
        const i = h('input', { type: radio ? 'radio' : 'checkbox', name: `q${ex.id}_${qi}` });
        labels.push(h('label', {}, i, ' ', a.text)); return i;
      });
      (q.shuffle ? shuffled(labels) : labels).forEach(l => box.append(l));
      getOk = () => q.answers.every((a, i) => inputs[i].checked === !!a.correct);
    }
    box.append(fb); qs.push({ box, getOk, q });
    wrap.append(box);
  });
  return { node: wrap, check() {
    let c = 0;
    qs.forEach(({ box, getOk, q }) => {
      const ok = getOk(); if (ok) c++; setMark(box, ok);
      const fb = box.querySelector('.fb');
      fb.textContent = ok ? '' : 'Respuesta correcta: ' + q.answers.filter(a => a.correct).map(a => a.text).join(' / ') + (q.explain ? ' — ' + q.explain : '');
    });
    return { correct: c, total: qs.length };
  } };
}

function renderMatch(ex) {
  const { items, options } = ex.data; const rows = [];
  const tb = h('tbody');
  items.forEach((it, i) => {
    const sel = h('select', { 'aria-label': it.left }, h('option', { value: '' }, '???'), options.map(o => h('option', { value: o }, o)));
    const mk = h('td');
    tb.append(h('tr', {}, h('td', {}, it.left), h('td', {}, sel), mk));
    rows.push({ it, sel, mk });
  });
  return { node: h('table', { class: 'match' }, tb), check() {
    let c = 0;
    rows.forEach(({ it, sel, mk }) => {
      const ok = it.correct.includes(sel.value); if (ok) c++;
      mk.textContent = ok ? '✔' : '✘ Correcta: ' + it.correct.join(' / '); mk.className = 'mark ' + (ok ? 'ok' : 'ko');
    });
    return { correct: c, total: rows.length };
  } };
}

function renderCloze(ex) {
  const { text, gaps, caseSensitive, wordList } = ex.data; const fields = [];
  const box = h('div', { class: 'cloze' });
  text.split(/(\{\{\d+\}\})/).forEach(part => {
    const m = part.match(/^\{\{(\d+)\}\}$/);
    if (!m) { box.append(part); return; }
    const gap = gaps.find(g => g.n === +m[1]);
    const inp = h('input', { type: 'text', 'aria-label': `Hueco ${gap.n}`, title: gap.hint || '', autocomplete: 'off' });
    const rv = h('span', { class: 'fb' }); fields.push({ inp, gap, rv }); box.append(inp, rv);
  });
  const node = h('div');
  if (wordList && wordList.length) node.append(h('p', { class: 'fb' }, 'Palabras: ' + wordList.join(' · ')));
  node.append(box);
  return { node, check() {
    let c = 0;
    fields.forEach(({ inp, gap, rv }) => {
      const ok = gap.answers.some(a => norm(a) === norm(inp.value));
      if (ok) c++; setMark(inp, ok);
      rv.textContent = ok ? '' : ' → ' + gap.answers.join(' / ');
    });
    return { correct: c, total: fields.length };
  } };
}

function renderCross(ex) {
  const { grid, across, down } = ex.data;
  const tb = h('tbody'); const inputs = {};
  const nums = {};
  [...across, ...down].forEach(w => { nums[w.row + ',' + w.col] = w.n; });
  grid.forEach((row, r) => {
    const tr = h('tr');
    row.forEach((ch, c) => {
      if (!ch) { tr.append(h('td')); return; }
      const inp = h('input', { type: 'text', maxlength: 1, 'aria-label': `Fila ${r + 1}, columna ${c + 1}` });
      inp.addEventListener('input', () => { inp.value = inp.value.toUpperCase(); });
      const td = h('td', { class: 'cell' }, inp);
      if (nums[r + ',' + c]) td.append(h('span', { class: 'n' }, String(nums[r + ',' + c])));
      inputs[r + ',' + c] = { td, inp, ch }; tr.append(td);
    });
    tb.append(tr);
  });
  const clues = (title, list) => h('div', {}, h('h4', {}, title), h('ol', { class: 'clues' }, list.map(w => h('li', { value: w.n }, w.clue))));
  const rvx = h('div', { class: 'fb' });
  const node = h('div', {}, rvx, h('div', { class: 'grid-wrap' }, h('table', { class: 'grid' }, tb)), clues('Horizontales', across), clues('Verticales', down));
  const words = [...across.map(w => ({ ...w, dr: 0, dc: 1 })), ...down.map(w => ({ ...w, dr: 1, dc: 0 }))];
  return { node, check() {
    let c = 0; const bad = new Set(); const miss = [];
    words.forEach(w => {
      const cells = [...w.answer].map((_, i) => inputs[(w.row + w.dr * i) + ',' + (w.col + w.dc * i)]);
      const ok = cells.every((x, i) => x && x.inp.value.toUpperCase() === w.answer[i]);
      if (ok) c++; else { miss.push(w.n + (w.dr ? '↓ ' : '→ ') + w.answer); cells.forEach(x => x && bad.add(x)); }
    });
    Object.values(inputs).forEach(x => { x.td.classList.remove('ok', 'ko'); x.td.classList.add(bad.has(x) ? 'ko' : (x.inp.value ? 'ok' : 'ko')); });
    rvx.textContent = miss.length ? 'Respuestas correctas de las palabras falladas: ' + miss.join(' · ') : '';
    return { correct: c, total: words.length };
  } };
}

const RENDER = { quiz: renderQuiz, match: renderMatch, cloze: renderCloze, cross: renderCross };

// ---------- Scoring ----------
// Puntaje = (aciertos − intentos fallidos previos) / total × 100, como en Hot Potatoes.
function scoreOf(correct, total, fails) { return Math.max(0, Math.round(100 * (correct - fails) / total)); }
const cls = s => s >= 80 ? 'good' : s < 50 ? 'bad' : '';

// ---------- UI ----------
let currentId = EX[0].id;
const partOf = ex => ex.part || 1;
const numOf = ex => partOf(ex) === 2 ? ex.id - 200 : ex.id;
function renderMenu() {
  const menu = $('#menu'); menu.replaceChildren();
  let key = null;
  EX.forEach(ex => {
    const k = partOf(ex) + ':' + ex.chapter;
    if (k !== key) {
      if (!key || key.split(':')[0] !== String(partOf(ex))) menu.append(h('h2', { class: 'part' }, partOf(ex) === 1 ? 'Parte 1 · Ejercicios de la guía' : 'Parte 2 · Ejercicios nuevos'));
      key = k; menu.append(h('h3', {}, `Capítulo ${ex.chapter}`));
    }
    const p = progress[ex.id];
    menu.append(h('button', { class: ex.id === currentId ? 'on' : '', 'data-id': ex.id, onclick: () => { currentId = ex.id; show(); } },
      h('span', {}, `${numOf(ex)}. ${ex.title}`),
      h('span', { class: 'sc ' + (p ? cls(p.best) : '') }, p ? p.best + '%' : '–')));
  });
}
function renderTotal() {
  const avgOf = l => Math.round(l.reduce((a, e) => a + (progress[e.id]?.best || 0), 0) / l.length);
  const parts = [1, 2].map(n => EX.filter(e => partOf(e) === n));
  const t = $('#total');
  t.textContent = `Parte 1: ${avgOf(parts[0])}% (${parts[0].filter(e => progress[e.id]).length}/${parts[0].length}) · Parte 2: ${avgOf(parts[1])}% (${parts[1].filter(e => progress[e.id]).length}/${parts[1].length})`;
  const chs = [...new Set(EX.map(e => partOf(e) + ':' + e.chapter))];
  t.title = chs.map(k => { const [pt, c] = k.split(':'); return `P${pt} cap. ${c}: ${avgOf(EX.filter(e => partOf(e) === +pt && e.chapter === +c))}%`; }).join('  |  ');
}
function show() {
  const ex = EX.find(e => e.id === currentId); const main = $('#main'); main.replaceChildren();
  let fails = 0, locked = false;
  const r = RENDER[ex.type](ex);
  const res = h('div', { 'aria-live': 'polite' });
  const prog = progress[ex.id];
  main.append(h('h2', {}, `${partOf(ex) === 2 ? 'Parte 2 · ' : ''}Ejercicio ${numOf(ex)} · ${ex.title}`));
  if (ex.subtitle) main.append(h('p', { class: 'sub' }, ex.subtitle));
  (ex.images || []).forEach(f => {
    const img = h('img', { src: 'images/' + encodeURIComponent(f), alt: f, style: 'max-width:100%;display:block;margin:8px 0' });
    img.addEventListener('error', () => img.replaceWith(h('a', { class: 'imgref', href: IMG_LINKS[f] || '#', target: '_blank', rel: 'noopener' }, '🖼 Ver imagen del ejercicio: ' + f)));
    main.append(img);
  });
  if (ex.table) main.append(h('div', { class: 'tbl' }, h('table', {}, h('thead', {}, h('tr', {}, ex.table.head.map(x => h('th', {}, x)))), h('tbody', {}, ex.table.rows.map(r => h('tr', {}, r.map(x => h('td', {}, x))))))));
  if (ex.instructions) main.append(h('div', { class: 'ins' }, ex.instructions));
  main.append(r.node);
  const check = h('button', { class: 'p', onclick: () => {
    if (locked) return;
    const { correct, total } = r.check();
    const score = scoreOf(correct, total, ex.noPenalty ? 0 : fails);
    const p = progress[ex.id] || { best: 0, attempts: 0 };
    p.attempts++; p.last = score; p.best = Math.max(p.best, score); progress[ex.id] = p; save();
    const all = correct === total;
    res.replaceChildren(h('div', { class: 'result ' + (all ? 'good' : 'bad') },
      `Correctas: ${correct}/${total} · Puntaje: ${score}%` + (fails && !ex.noPenalty ? ` (−${fails} por intentos fallidos)` : '') +
      (all ? ' — ¡Correcto! Bien hecho.' : ' — Hay respuestas incorrectas, marcadas con ✘. Inténtalo nuevamente.')));
    if (all) { locked = true; check.disabled = true; } else fails++;
    renderMenu(); renderTotal();
  } }, 'Comprobar respuestas');
  const retry = h('button', { class: 's', onclick: show }, 'Reiniciar ejercicio');
  main.append(h('div', { class: 'actions' }, check, retry,
    prog ? h('span', { class: 'fb' }, `Mejor puntaje: ${prog.best}% · Intentos: ${prog.attempts}`) : ''), res);
  renderMenu();
}
const reset = h('button', { class: 's', onclick: () => { if (confirm('¿Borrar todo el progreso?')) { progress = {}; save(); show(); renderTotal(); } } }, 'Borrar progreso');
document.querySelector('.top').append(reset);
renderTotal(); show();
})();
