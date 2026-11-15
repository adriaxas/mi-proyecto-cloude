// Pestaña «Área» de la app Biblioteca de Adrián (publicada el 15/11/2026).
// Reemplaza a la función verArea() que solo mostraba «Todavía no está construida».
// Lee areas-0.json, publicado junto a la página.
let AREAS=null;
function _areaCarga(cb){fetch('areas-0.json',{cache:'no-cache'}).then(r=>r.ok?r.json():Promise.reject(r.status)).then(j=>{AREAS=j;cb()}).catch(e=>{document.getElementById('m').innerHTML='<h2>Área</h2><div class="sub">No se pudieron cargar los archivos del área ('+E(String(e))+').</div>'})}
function verArea(a,g,f){document.body.dataset.modo='inicio';_marcarTab('appA');try{history.replaceState(null,'','#area')}catch(e){}window.scrollTo(0,0);
 const m=document.getElementById('m');
 if(!AREAS){m.innerHTML='<h2>Área</h2><div class="sub">Cargando…</div>';return _areaCarga(()=>verArea(a,g,f))}
 const A=AREAS.areas||[];if(a==null&&A.length===1)a=0;
 const CSS='<style>.arealec blockquote{margin:0 0 .5em;padding-left:14px;border-left:3px solid var(--ac)}.arealec h4{font:700 1.02em/1.35 -apple-system,system-ui,sans-serif;margin:1.7em 0 .5em}.arealec .tb{font-family:-apple-system,system-ui,sans-serif}.arealec ul.md{list-style:disc;padding-left:22px}.arealec ul.md li{border:0;padding:2px 0}</style>';
 if(a!=null&&g!=null&&f!=null&&A[a]&&A[a].g[g]&&A[a].g[g].f[f]){const G=A[a].g[g],X=G.f[f];
  const nav=(k,t)=>G.f[k]?`<a class="in" onclick="verArea(${a},${g},${k})">${t}</a>`:'<span></span>';
  m.innerHTML=CSS+`<div class="volver"><a onclick="verArea(${a})">← Volver</a></div><div class="miga"><a onclick="verArea()">Área</a> › <a onclick="verArea(${a})">${E(A[a].n)}</a> › ${E(G.n)}</div><div class="lec arealec"><div class="lect">${E(X.t)}</div><div class="lecn">${E(X.p)}</div>${md(X.x)}<div class="lecnav">${nav(f-1,'← Anterior')}${nav(f+1,'Siguiente →')}</div></div>`;return}
 if(a!=null&&A[a]){const R=A[a];
  m.innerHTML=(A.length>1?`<div class="miga"><a onclick="verArea()">Área</a> › ${E(R.n)}</div>`:'')+`<h2>${E(R.n)}</h2><div class="sub">${E(R.d||'')}${AREAS.fecha?' · Actualizado el '+E(AREAS.fecha):''}</div>`+R.g.map((G,gi)=>`<h3>${E(G.n)} <span class="cnt">${G.f.length}</span></h3><ul>`+G.f.map((X,fi)=>`<li><a class="in" onclick="verArea(${a},${gi},${fi})">${E(X.t)}</a>`+(X.s?`<div class="fu">${E(X.s)}</div>`:'')+'</li>').join('')+'</ul>').join('');return}
 m.innerHTML='<h2>Área</h2><div class="sub">Archivos de «2 Areas» publicados en la app.</div><div class="grid">'+A.map((R,k)=>`<button class="cat" onclick="verArea(${k})"><b>${E(R.n)}</b><span>${R.g.reduce((n,G)=>n+G.f.length,0)} archivos</span></button>`).join('')+'</div>'}
