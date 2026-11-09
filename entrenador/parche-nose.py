#!/usr/bin/env python3
"""Opción «No sé» en cada pregunta de las prácticas (tests, recorrido, viaje, repaso, examen de 10).
Pedido de Adrián, 09/11/2026. «No sé» cuenta como respuesta ERRÓNEA (no como en blanco): se muestra la corrección,
queda registrada como «No sé» y suma un error al tema, al recorrido y al Historial.
Idempotente. Uso: python3 parche-nose.py <ruta del HTML>"""
import sys
ruta = sys.argv[1]
h = open(ruta, encoding="utf-8").read()
orig = h
err = []

def rep(nombre, viejo, nuevo, marca):
    global h
    if marca in h:
        print("  =", nombre, ": ya estaba"); return
    n = h.count(viejo)
    if n != 1:
        err.append(f"{nombre}: aparece {n} veces"); print("  !", err[-1]); return
    h = h.replace(viejo, nuevo); print("  +", nombre)

print("parche-nose →", ruta)
rep("estilo",
    ".velo-cap .btn{padding:9px 16px;font-size:.92rem}",
    ".velo-cap .btn{padding:9px 16px;font-size:.92rem}\n.nose-bar{margin-top:10px}\n.nose-bar .chipsel{padding:7px 16px;font-size:.9rem}\n.nose-bar .chipsel.on{background:var(--warn-soft);border-color:var(--warn);color:var(--warn)}\n.q.done .nose-bar{display:none}",
    ".nose-bar{margin-top:10px}")
rep("botón en cada pregunta",
    '    h+=`<div class="exp"></div></div>`;\n  });\n  h+=`</form><div class="bar"><button class="btn" id="entregar">',
    '    h+=`<div class="nose-bar"><button type="button" class="chipsel" data-nose="${i}" aria-pressed="false">No sé</button></div>`;\n    h+=`<div class="exp"></div></div>`;\n  });\n  h+=`</form><div class="bar"><button class="btn" id="entregar">',
    'data-nose="${i}"')
rep("comportamiento del botón",
    '  document.querySelectorAll("#f [data-ini]").forEach(b=>b.addEventListener("click",()=>iniciarPregunta(+b.dataset.ini,true)));',
    '''  document.querySelectorAll("#f [data-ini]").forEach(b=>b.addEventListener("click",()=>iniciarPregunta(+b.dataset.ini,true)));
  /* «No sé»: cuenta como error (no como en blanco), se ve la corrección. Se destilda tocando otra vez. */
  document.querySelectorAll("#f [data-nose]").forEach(b=>b.addEventListener("click",()=>{
    const i=+b.dataset.nose,d=$("#q"+i),on=d.dataset.nose!=="1";
    d.dataset.nose=on?"1":"";b.classList.toggle("on",on);b.setAttribute("aria-pressed",String(on));b.textContent=on?"No sé ✓ (tocá de nuevo para contestar)":"No sé";
    d.querySelectorAll("input[type=radio]").forEach(r=>{if(on)r.checked=false;r.disabled=on});
    d.querySelectorAll("input[type=text],input[type=number],input.num,select,textarea").forEach(x=>{if(on)x.value="";x.disabled=on});
    d.dispatchEvent(new Event("change",{bubbles:true}));
  }));''',
    "«No sé»: cuenta como error")
rep("hayRespuesta",
    "  const d=document.querySelector(\"#q\"+i); if(!d)return false;\n",
    "  const d=document.querySelector(\"#q\"+i); if(!d)return false;\n  if(d.dataset.nose===\"1\")return true;   /* «No sé» es una respuesta */\n",
    "«No sé» es una respuesta")
rep("corregir: el «No sé» es error",
    "    let ok=false,vacio=false,expHTML=\"\",fuente=\"\",enun=\"\",dada=\"\",correcta=\"\";\n    if(it.k===\"mc\"){",
    "    let ok=false,vacio=false,expHTML=\"\",fuente=\"\",enun=\"\",dada=\"\",correcta=\"\";\n    const nose=d.dataset.nose===\"1\";\n    if(it.k===\"mc\"){",
    "const nose=d.dataset.nose===\"1\";")
rep("corregir: registro del «No sé»",
    "    if(vacio)sin++;\n    if(ok)ac++;\n    const enBlanco=parcial&&vacio;",
    "    if(nose){vacio=false;ok=false;dada=\"No sé\";expHTML=expHTML.replace(/Sin responder\\./,\"Marcaste «No sé».\");d.querySelectorAll(\"[data-nose]\").forEach(x=>x.disabled=true)}\n    if(vacio)sin++;\n    if(ok)ac++;\n    const enBlanco=parcial&&vacio;",
    "Marcaste «No sé».")
if err:
    print("HAY ERRORES: no se escribió"); sys.exit(1)
if h != orig:
    open(ruta, "w", encoding="utf-8").write(h); print("escrito")
else:
    print("sin cambios")
