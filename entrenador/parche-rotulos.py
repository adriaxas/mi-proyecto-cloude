#!/usr/bin/env python3
"""Sin pistas en los ejercicios (Adrián, 11/11/2026): se saca el rótulo «calculadora» y los rótulos «Razones y proporciones»
(unidad y tema) de la esquina de arriba a la derecha de cada pregunta, y el nombre de la estación en el recorrido.
Idempotente. Uso: python3 parche-rotulos.py <ruta del HTML>"""
import sys
ruta=sys.argv[1];h=open(ruta,encoding="utf-8").read();orig=h;err=[]
def rep(n,v,nv,marca):
    global h
    if marca in h: print("  =",n,": ya estaba");return
    c=h.count(v)
    if c!=1: err.append(f"{n}: aparece {c} veces");print("  !",err[-1]);return
    h=h.replace(v,nv);print("  +",n)
print("parche-rotulos →",ruta)
rep("rótulo de la pregunta",
 '<span>${uni} · ${it.tema}${prof}${vid}${ctrl}${it.k==="calc"?\' <span class="calcflag">calculadora</span>\':""}</span></div>`;',
 '<span>${it.u==="r3"?"":uni+" · "+it.tema}${prof}${vid}${ctrl}</span></div>`;   /* sin pistas: ni «Razones y proporciones» ni «calculadora» (Adrián, 11/11/2026) */',
 "sin pistas: ni «Razones y proporciones»")
rep("rótulo en el detalle del Historial",
 '<span>${r.unidad?nomUnidad(r.unidad)+" · ":""}${esc(r.tema||"")}</span></div>`;',
 '<span>${r.unidad===\'r3\'?"":(r.unidad?nomUnidad(r.unidad)+" · ":"")+esc(r.tema||"")}</span></div>`;',
 "r.unidad==='r3'?\"\"")
rep("recorrido: nombre de la estación",
 "sub:`${a.nombre} · ${paso} · se contesta y se pasa al siguiente`",
 "sub:`${a.u===\"r3\"||/^(Razones|Proporciones|Proporcionalidad)/i.test(a.nombre)?\"\":a.nombre+\" · \"}${paso} · se contesta y se pasa al siguiente`",
 'a.u==="r3"||/^(Razones|Proporciones')
if err: print("HAY ERRORES");sys.exit(1)
if h!=orig: open(ruta,"w",encoding="utf-8").write(h);print("escrito")
else: print("sin cambios")
