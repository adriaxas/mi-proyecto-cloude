#!/usr/bin/env python3
"""Cálculos con decimales: se pide hasta CENTÉSIMOS (dos lugares después de la coma) y se acepta con dos o con tres.
Adrián, 09/11/2026: «si es 1,252 y él pone 1,25 es lo mismo, tomalo como que está bien»; «1,125 cuando el resultado era 1,12:
estaba bien y se lo tomaba mal». calcVale() acepta el valor redondeado o truncado a centésimos, o a menos de medio centésimo.
También recorrige el Historial (cálculos con decimales que salieron mal por eso). Idempotente.
Uso: python3 parche-decimales.py <ruta del HTML>"""
import sys
ruta=sys.argv[1];h=open(ruta,encoding="utf-8").read();orig=h;err=[]
def rep(n,v,nv,marca):
    global h
    if marca in h: print("  =",n,": ya estaba");return
    c=h.count(v)
    if c!=1: err.append(f"{n}: aparece {c} veces");print("  !",err[-1]);return
    h=h.replace(v,nv);print("  +",n)
print("parche-decimales →",ruta)
rep("calcVale",
 'const respTxt=c=>c.frac?c.frac:String(c.resp).replace(".",",");',
 '''const respTxt=c=>c.frac?c.frac:String(c.resp).replace(".",",");
/* Decimales (Adrián, 09/11/2026): se pide hasta centésimos y vale con dos o con tres lugares. Si el resultado es 1,252 y escribe
   1,25 (o 1,125 cuando se esperaba 1,12), está bien: se acepta el redondeado o el truncado a centésimos, o a menos de medio centésimo. */
function calcVale(v,c){
  if(v==null||isNaN(v))return false;
  if(Math.abs(v-c.resp)<=(c.tol||0)+1e-9)return true;
  if(c.frac||Number.isInteger(c.resp))return false;
  const r2=Math.round(c.resp*100)/100,t2=Math.trunc(c.resp*100)/100;
  return Math.abs(v-r2)<1e-9||Math.abs(v-t2)<1e-9||Math.abs(v-c.resp)<=0.005+1e-9;
}''',"function calcVale(v,c)")
rep("corregir usa calcVale","ok=!vacio&&Math.abs(v-c.resp)<=(c.tol||0)+1e-9;","ok=!vacio&&calcVale(v,c);","ok=!vacio&&calcVale(v,c);")
rep("consigna: pedir dos decimales",
 "      h+=`<p>${it.c.txt}</p><label style=\"padding-left:0\"><input type=\"text\" inputmode=",
 "      h+=`<p>${it.c.txt}</p>${!it.c.frac&&!Number.isInteger(it.c.resp)&&!/decimal|redonde|fracci/i.test(it.c.txt)?'<p class=\"note\" style=\"margin:-4px 0 8px\">Si el resultado tiene decimales, escribilo con <b>dos lugares después de la coma</b> (centésimos). Con tres también vale.</p>':\"\"}<label style=\"padding-left:0\"><input type=\"text\" inputmode=",
 "dos lugares después de la coma</b> (centésimos)")
rep("Historial: recorregir cálculos",
 '      if(r.ok||r.tipo!=="fill")return;\n',
 '''      if(r.ok)return;
      if(r.tipo==="calc"){const dv=aNumero(String(r.respuestaDada||"").split(" ")[0]),cv=numeroDe(r.respuestaCorrecta);
        if(dv!=null&&cv!=null&&!/\\//.test(String(r.respuestaCorrecta))&&calcVale(dv,{resp:cv})){r.ok=true;r.recorregida="decimales";cambio=true}
        return}
      if(r.tipo!=="fill")return;
''','r.recorregida="decimales"')
rep("versión de la recorrección",'const RECORREGIDO_V="2026-11-08a";','const RECORREGIDO_V="2026-11-09a";','const RECORREGIDO_V="2026-11-09a";')
if err: print("HAY ERRORES");sys.exit(1)
if h!=orig: open(ruta,"w",encoding="utf-8").write(h);print("escrito")
else: print("sin cambios")
