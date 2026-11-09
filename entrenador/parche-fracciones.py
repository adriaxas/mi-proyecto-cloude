#!/usr/bin/env python3
"""Fracción y decimal son lo mismo (Adrián, 09/11/2026): «si él contesta en decimal y vos exigís fracción, o viceversa… tomalo como sinónimo
o exigilo en la pregunta». Se hacen las dos cosas:
 - 3/4 y 0,75 valen igual; si el resultado es una fracción (13/18) vale el decimal a centésimos (0,72); si es decimal vale la fracción equivalente.
 - La consigna lo dice: «podés responder como fracción o como decimal».
 - Única exigencia: si el enunciado dice «irreducible», la fracción tiene que venir simplificada (y la corrección lo avisa).
Recorrige también el Historial. Idempotente. Uso: python3 parche-fracciones.py <ruta del HTML>"""
import sys
ruta=sys.argv[1];h=open(ruta,encoding="utf-8").read();orig=h;err=[]
def rep(n,v,nv,marca):
    global h
    if marca in h: print("  =",n,": ya estaba");return
    c=h.count(v)
    if c!=1: err.append(f"{n}: aparece {c} veces");print("  !",err[-1]);return
    h=h.replace(v,nv);print("  +",n)
print("parche-fracciones →",ruta)
# 1 · calcVale con el texto escrito
i=h.find("function calcVale(v,c){")
if "function calcVale(v,c,crudo){" in h: print("  = calcVale: ya estaba")
elif i<0: err.append("no encuentro calcVale (¿falta parche-decimales?)");print("  !",err[-1])
else:
    j=h.find("\n}\n",i)+2
    h=h[:i]+r'''function calcVale(v,c,crudo){
  /* fracción y decimal son lo mismo (Adrián, 09/11/2026); la única exigencia es «irreducible» cuando el enunciado lo pide */
  if(v==null||isNaN(v))return false;
  const esFr=/\//.test(String(crudo||""));
  if(esFr&&/irreducible/i.test(c.txt||"")&&fraccionReducible(crudo)&&Math.abs(v-c.resp)<=(c.tol||0)+1e-9)return false;
  if(Math.abs(v-c.resp)<=(c.tol||0)+1e-9)return true;
  if(Number.isInteger(c.resp))return false;
  if(c.frac&&esFr)return false;   /* una fracción distinta de la correcta no vale por parecerse en decimales */
  const r2=Math.round(c.resp*100)/100,t2=Math.trunc(c.resp*100)/100;
  return Math.abs(v-r2)<1e-9||Math.abs(v-t2)<1e-9||Math.abs(v-c.resp)<=0.005+1e-9;
}
function fraccionReducible(t){
  const m=String(t||"").trim().match(/^(?:\d+\s+)?(\d+)\s*\/\s*(\d+)$/);if(!m)return false;
  let a=+m[1],b=+m[2];while(b){[a,b]=[b,a%b]}return a>1;
}'''+h[j:]
    print("  + calcVale con fracciones")
rep("corregir pasa lo escrito","ok=!vacio&&calcVale(v,c);","ok=!vacio&&calcVale(v,c,crudo);","calcVale(v,c,crudo);")
rep("corrección: aviso de «irreducible»",
 "        Resultado: <b>${respTxt(c)} ${c.unidad}</b>.\n",
 "        ${!ok&&!vacio&&/irreducible/i.test(c.txt)&&/\\//.test(crudo)&&fraccionReducible(crudo)&&Math.abs(v-c.resp)<1e-9?`El valor está bien, pero el enunciado pedía la fracción <b>irreducible</b>: había que simplificarla. `:\"\"}Resultado: <b>${respTxt(c)} ${c.unidad}</b>${c.frac&&!Number.isInteger(c.resp)?` (en decimal, ${String(Math.round(c.resp*100)/100).replace(\".\",\",\")})`:\"\"}.\n",
 "el enunciado pedía la fracción <b>irreducible</b>")
# 2 · consigna
rep("consigna: se puede en fracción o en decimal",
 "${!it.c.frac&&!Number.isInteger(it.c.resp)&&!/decimal|redonde|fracci/i.test(it.c.txt)?'<p class=\"note\" style=\"margin:-4px 0 8px\">Si el resultado tiene decimales, escribilo con <b>dos lugares después de la coma</b> (centésimos). Con tres también vale.</p>':\"\"}",
 "${!Number.isInteger(it.c.resp)&&!/decimal|redonde|fracci/i.test(it.c.txt)?'<p class=\"note\" style=\"margin:-4px 0 8px\">Podés responder como <b>fracción</b> o como <b>decimal</b>: las dos valen. Si es decimal, con <b>dos lugares después de la coma</b> (centésimos); con tres también vale.</p>':(!Number.isInteger(it.c.resp)&&/irreducible/i.test(it.c.txt)?'<p class=\"note\" style=\"margin:-4px 0 8px\">Si la escribís como fracción, tiene que ir simplificada. También vale en decimal (dos lugares después de la coma).</p>':\"\")}",
 "Podés responder como <b>fracción</b> o como <b>decimal</b>")
# 3 · Historial
rep("Historial: fracción y decimal",
 'if(dv!=null&&cv!=null&&!/\\//.test(String(r.respuestaCorrecta))&&calcVale(dv,{resp:cv})){r.ok=true;r.recorregida="decimales";cambio=true}',
 'if(dv!=null&&cv!=null&&calcVale(dv,{resp:cv,frac:/\\//.test(String(r.respuestaCorrecta))?String(r.respuestaCorrecta):undefined,txt:r.enunciado},String(r.respuestaDada||"").split(" ")[0])){r.ok=true;r.recorregida="decimales";cambio=true}',
 "txt:r.enunciado},String(r.respuestaDada")
rep("versión de la recorrección",'const RECORREGIDO_V="2026-11-09a";','const RECORREGIDO_V="2026-11-09b";','const RECORREGIDO_V="2026-11-09b";')
if err: print("HAY ERRORES");sys.exit(1)
if h!=orig: open(ruta,"w",encoding="utf-8").write(h);print("escrito")
else: print("sin cambios")
