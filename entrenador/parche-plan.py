#!/usr/bin/env python3
"""Plan de estudio (Adrián, 08/11/2026), sobre la versión viva del Entrenador:

  1. El examen es el SÁBADO 14/11/2026, de Química 2 y de Matemática 2 (EXAMEN_FECHA[10] decía 11/11).
     El día por día de los dos planes va del sábado 7/11 al viernes 13/11, con las dos materias cada día.
  2. Sin el capítulo 7 de Química: las estaciones salen de bancoExamen() (que ya no tiene k7) y lo que el
     Plan guarda aparte (el «Recorrido del día» del Historial) deja de llevar las respuestas del cap. 7.
  3. Tiempos del recorrido en el Historial: el intento del día guarda `tiempos` (inicio, fin, total, promedio)
     y los intentos viejos sin `tiempos` lo calculan de los `segundos` de cada respuesta.
  4. Sesiones 2, 3… del recorrido: terminado un recorrido se puede empezar otro, el mismo día o el que sea.
     Sale bien → 1 ejercicio; sale mal → los que llevaba + 1. Ejercicios siempre distintos a los ya vistos.
     Cada sesión es un intento del Historial (con fecha, hora, tiempo y resultado por estación).

Idempotente. Uso: python3 parche-plan.py <ruta del HTML>   (después de parche-sin-cap7.py y parche-recorregir.py)
Cualquier «!» frena todo."""
import sys

ruta = sys.argv[1]
h = open(ruta, encoding="utf-8").read()
orig = h
errores = []


def ya(marca):
    return marca in h


def reemplazar(nombre, viejo, nuevo, marca):
    global h
    if marca in h:
        print("  =", nombre, ": ya estaba")
        return
    n = h.count(viejo)
    if n != 1:
        errores.append(f"{nombre}: el texto a reemplazar aparece {n} veces (tiene que ser 1)")
        print("  !", errores[-1])
        return
    h = h.replace(viejo, nuevo)
    print("  +", nombre)


def reemplazar_funcion(nombre, nuevo, marca):
    """Reemplaza `function nombre(...)` entera (hasta el primer «\\n}\\n» a ras de la izquierda, o su línea si es de una sola)."""
    global h
    if marca in h:
        print("  =", nombre, ": ya estaba")
        return
    i = h.find("\nfunction " + nombre + "(")
    if i < 0 or h.count("\nfunction " + nombre + "(") != 1:
        errores.append(f"{nombre}: no encuentro la función (o está repetida)")
        print("  !", errores[-1])
        return
    i += 1
    fin_linea = h.find("\n", i)
    linea = h[i:fin_linea]
    if linea.count("{") == linea.count("}") and linea.rstrip().endswith("}"):
        j = fin_linea
    else:
        j = h.find("\n}\n", i)
        if j < 0:
            errores.append(f"{nombre}: no encuentro el final de la función")
            print("  !", errores[-1])
            return
        j += 2
    h = h[:i] + nuevo.rstrip("\n") + h[j:]
    print("  +", nombre)


print("parche-plan →", ruta)

# ───────────────────────── 1 · FECHA DEL EXAMEN Y DÍA POR DÍA ─────────────────────────
reemplazar(
    "fecha del examen",
    'const EXAMEN_FECHA={9:"2026-11-14",10:"2026-11-11"};',
    '''/* Adrián, 08/11/2026: «el examen es el día sábado» (14/11/2026), de Química 2 y de Matemática 2. */
const EXAMEN_FECHA={9:"2026-11-14",10:"2026-11-14"};''',
    "«el examen es el día sábado»",
)

i0 = h.find("const PLAN_DIAS={")
i1 = h.find("const PLAN_EXCLUIR=")
if "PLAN_7D_V2" not in h:
    if i0 < 0 or i1 < i0:
        errores.append("PLAN_DIAS: no encuentro el bloque")
        print("  !", errores[-1])
    else:
        nuevo = r'''/*PLAN_7D_V2*/ const PLAN_DIAS={
 9:{dias:[
  {f:"2026-11-07",horas:"Matemática 3 h · Química 3 h"},
  {f:"2026-11-08",horas:"Matemática 3 h · Química 3 h"},
  {f:"2026-11-09",horas:"Matemática 3 h · Química 3 h"},
  {f:"2026-11-10",horas:"Matemática 3 h · Química 3 h"},
  {f:"2026-11-11",horas:"Matemática 3 h · Química 3 h"},
  {f:"2026-11-12",horas:"Matemática 3 h · Química 3 h",nota:"Último día de estudio fuerte: mañana ya no se aprende nada nuevo, solo se repasa."},
  {f:"2026-11-13",horas:"Matemática 2 h · Química 2 h, terminando temprano",liviana:true,nota:"Mañana es el examen (sábado 14/11): hoy no se aprende nada nuevo. Recorrido corto, el examen de 10, las fórmulas, y a dormir temprano."}]},
 10:{dias:[
  {f:"2026-11-07",horas:"Química 3 h · Matemática 3 h"},
  {f:"2026-11-08",horas:"Química 3 h · Matemática 3 h"},
  {f:"2026-11-09",horas:"Química 3 h · Matemática 3 h"},
  {f:"2026-11-10",horas:"Química 3 h · Matemática 3 h"},
  {f:"2026-11-11",horas:"Química 3 h · Matemática 3 h"},
  {f:"2026-11-12",horas:"Química 3 h · Matemática 3 h",nota:"Último día de estudio fuerte: mañana ya no se aprende nada nuevo, solo se repasa."},
  {f:"2026-11-13",horas:"Química 2 h · Matemática 2 h, terminando temprano",liviana:true,nota:"Mañana es el examen (sábado 14/11): hoy no se aprende nada nuevo. Recorrido corto, el examen de 10 y repaso de lo que no salió. Nada nuevo a la noche."}]}};
'''
        h = h[:i0] + nuevo + h[i1:]
        print("  + plan día por día (7 al 13/11, examen sábado 14/11)")
else:
    print("  = plan día por día: ya estaba")

# ───────────────────────── 2/3/4 · SESIONES DEL RECORRIDO ─────────────────────────
BLOQUE = r'''/* ════════ SESIONES DEL RECORRIDO (Adrián, 08/11/2026) ════════
   «Necesito que haya una posibilidad de que se genere un nuevo recorrido … sesión 2, sesión 3 … cada ejercicio
   que se equivoca va a haber que sumarle uno más en la próxima sesión … con ejercicios distintos para que no
   pueda reconocer el patrón de respuesta, pero siempre en base a lo que la guía propone.»
   Un recorrido no es un día: terminado uno, se puede empezar otro (sesión 2, 3…), el mismo día o el que sea.
   J.sesion es la sesión en curso (1 si no hay otra) y J.est sus estaciones. Las que ya terminaron quedan en
   J.sesiones en versión compacta (resultado, ejercicios, ids vistos, cuáles salieron mal, segundos); lo completo
   de cada una está en el Historial: UN intento por sesión («recorrido_ex10_2026-11-08», «…_s2», «…_s3»).
   El estado de una estación es el de la última sesión en que salió. Cuántos ejercicios trae en la sesión
   siguiente: salió bien → 1; salió mal (o se salteó) → los que llevaba + 1; no se repite ningún ejercicio visto. */
const sesionN=J=>(J&&J.sesion)||1;
const sesionesDe=J=>((J&&J.sesiones)||[]).concat([{n:sesionN(J),est:(J&&J.est)||{},inicio:J&&J.inicio,fin:J&&J.fin,actual:true}]);
const resE=e=>e?(e.res||(e.e==="aprobada"?resDe(e):null)):null;
function compactEst(e){
  const rs=e.resp||[];
  return {e:e.e,res:resE(e),meta:e.meta||META_BASE,vistas:e.vistas||0,ok:e.ok||0,mal:e.mal||0,fecha:e.fecha||null,
    segs:e.segs!=null?e.segs:Math.round(10*rs.reduce((a,r)=>a+(+r.segundos||0),0))/10,
    qids:[...new Set(rs.map(r=>r.qid).filter(Boolean).concat(e.qids||[]))],
    fallos:[...new Set(rs.filter(r=>!r.ok&&r.qid).map(r=>r.qid).concat(e.fallos||[]))]};
}
function compactSesion(J){
  const est={};Object.entries(J.est||{}).forEach(([k,e])=>{est[k]=compactEst(e)});
  return {n:sesionN(J),inicio:J.inicio||null,fin:J.fin||ahora(),segs:Math.round(10*Object.values(est).reduce((a,e)=>a+(e.segs||0),0))/10,est};
}
/* la última sesión en que la estación salió (la actual cuenta si ya salió en ella) */
function estDe(J,id){
  const S=sesionesDe(J);
  for(let k=S.length-1;k>=0;k--){const e=S[k].est&&S[k].est[id];if(e&&resE(e))return e}
  return null;
}
/* el resultado más reciente de una estación ANTES de la sesión en curso: en las sesiones del mismo día que ya
   terminaron (Jcur) y en los días anteriores. De ahí sale cuántos ejercicios trae en la sesión que arranca. */
function entradaPrevia(id,f,Jcur){
  const S=[];
  jornadas.filter(j=>j.examen===examenSel&&j.fecha<f).sort(porFechaAsc).forEach(j=>sesionesDe(j).forEach(s=>S.push(s)));
  if(Jcur&&Jcur.fecha===f&&Jcur.examen===examenSel)(Jcur.sesiones||[]).forEach(s=>S.push(s));
  for(let k=S.length-1;k>=0;k--){const e=S[k].est&&S[k].est[id];if(e&&resE(e))return e}
  return null;
}
function sesionAnteriorDoc(J){
  const S=(J&&J.sesiones)||[],s=S[S.length-1];
  return s?{examen:J.examen,fecha:J.fecha,est:s.est,formulas:null}:null;
}
/* el día visto de punta a punta: en cada estación, lo de la última sesión en que salió */
function jorConsolidada(J){
  const est={};
  sesionesDe(J).forEach(s=>Object.keys(s.est||{}).forEach(k=>{if(!est[k])est[k]=estDe(J,k)||(J.est&&J.est[k])||s.est[k]}));
  return {...J,est};
}
/* ids de ejercicios que Fabricio ya vio en esta estación, en cualquier sesión de cualquier día */
function qidsVistosEst(id){
  const s=new Set();
  const sumar=e=>{if(!e)return;(e.resp||[]).forEach(r=>{if(r.qid)s.add(r.qid)});(e.qids||[]).forEach(q=>s.add(q))};
  jornadas.filter(j=>j.examen===examenSel).forEach(j=>{
    if(JOR&&JOR.examen===j.examen&&JOR.fecha===j.fecha)return;
    sesionesDe(j).forEach(x=>sumar(x.est&&x.est[id]));
  });
  if(JOR&&JOR.examen===examenSel)sesionesDe(JOR).forEach(x=>sumar(x.est&&x.est[id]));
  return s;
}
function sesionResumen(s){
  const E=planEstaciones();let sabe=0,dud=0,no=0,hechas=0,segs=0;
  E.forEach(st=>{const e=s.est&&s.est[st.id];if(!e)return;
    segs+=e.segs!=null?e.segs:(e.resp||[]).reduce((a,r)=>a+(+r.segundos||0),0);
    const r=resE(e);if(r){hechas++;if(r==="sabe")sabe++;else if(r==="dudoso")dud++;else no++}});
  return {n:s.n,sabe,dud,no,hechas,total:E.length,segs:Math.round(10*segs)/10,inicio:s.inicio,fin:s.fin,actual:!!s.actual};
}
const horaDe=iso=>{try{return new Date(iso).toLocaleTimeString("es-AR",{hour:"2-digit",minute:"2-digit",hour12:false})}catch(e){return ""}};
function sesionesHTML(J,soloAnteriores){
  const S=sesionesDe(J).map(sesionResumen).filter(r=>r.hechas>0&&!(soloAnteriores&&r.actual));
  if(!S.length)return "";
  return `<div class="sesiones" style="margin:6px 0 4px">${S.map(r=>`<div class="note" style="margin:2px 0"><b>Sesión ${r.n}</b>${r.inicio?` · ${horaDe(r.inicio)}${r.fin?"–"+horaDe(r.fin):""}`:""} · ${r.hechas} de ${r.total} · <span class="chipt ok">${r.sabe} sabe</span> <span class="chipt warn">${r.dud} a medias</span> <span class="chipt bad">${r.no} no salió</span>${r.segs>0?` · ${minTxt(Math.max(1,r.segs/60))} respondiendo`:""}${r.actual&&r.hechas<r.total?" · en curso":""}</div>`).join("")}</div>`;
}
/* cuántos ejercicios trae la próxima sesión (la suma de lo que lleva cada estación) */
function proximaSesionEjercicios(J){
  const d=planDia(J.fecha);
  return planEstaciones().reduce((s,st)=>s+metaPara(st,null,d,J.est&&J.est[st.id]),0);
}
function planNuevaSesion(){
  jorHoy();
  if(planActual())return;
  const n=sesionN(JOR),E=planEstaciones(),d=planDia(JOR.fecha),est={};
  const arch=compactSesion(JOR);
  E.forEach(st=>{est[st.id]={e:"pendiente",meta:metaPara(st,null,d,JOR.est&&JOR.est[st.id]),seg:0,vistas:0,ok:0,mal:0,rep:null,ult:null,resp:[],primero:null}});
  JOR.sesiones=(JOR.sesiones||[]).concat([arch]);
  JOR.sesion=n+1;JOR.est=est;JOR.inicio=null;JOR.fin=null;JOR.pos=0;JOR.item=null;JOR.itemId=null;JOR.itemEst=null;
  jorGuardar();render();try{scrollTo({top:0})}catch(e){}
}
const intentoSesionId=(ex,f,n)=>"recorrido_ex"+ex+"_"+f+(n>1?"_s"+n:"");
/* los intentos del recorrido que no guardaron `tiempos` (los de antes del 08/11) lo sacan de los `segundos` de cada respuesta */
function tiemposDeRespuestas(i){
  const rs=(i.respuestas||[]).filter(r=>!r.papel),con=rs.filter(r=>+r.segundos>0);
  const tt=Math.round(con.reduce((a,r)=>a+(+r.segundos),0));
  if(!(tt>0))return null;
  const ts=rs.map(r=>r.t).filter(Boolean).sort();
  return {inicio:i.fecha||ts[0]||null,fin:i.actualizado||ts[ts.length-1]||i.fecha||null,segundosTotal:tt,segundosPromedioPorPregunta:Math.round(10*tt/con.length)/10};
}
'''
reemplazar(
    "bloque de sesiones",
    "function planEstaciones(){\n  if(_planEstCache.ex===examenSel",
    BLOQUE + "function planEstaciones(){\n  if(_planEstCache.ex===examenSel",
    "SESIONES DEL RECORRIDO (Adrián, 08/11/2026)",
)

reemplazar_funcion("metaPara", r'''function metaPara(st,ayer,d,prev){
  /* cuántos ejercicios trae hoy cada estación: 1 normal (2 en la final). Si en la sesión anterior en que salió
     no salió bien, los que llevaba + 1 (1 → 2 → 3…); si salió bien, vuelve a 1 (Adrián, 08/11/2026). */
  const base=st.tipo==="final"?2:META_BASE;
  const a=prev!==undefined?prev:(ayer&&ayer.est&&ayer.est[st.id]);
  const r=resE(a);
  if(r==="nosabe"||r==="dudoso")return Math.max(base,a.meta||base)+1;
  return base;
}''', "/* cuántos ejercicios trae hoy cada estación: 1 normal (2 en la final). Si en la sesión anterior")

reemplazar_funcion("jorAnterior", r'''function jorAnterior(f){
  /* «ayer» = el día anterior más reciente; en cada estación, lo de la última sesión de ese día en que salió */
  const prev=jornadas.filter(j=>j.examen===examenSel&&j.fecha<f&&j.est).sort((a,b)=>a.fecha<b.fecha?1:-1);
  const j=prev[0];if(!j)return null;
  const est={};
  sesionesDe(j).forEach(s=>Object.keys(s.est||{}).forEach(k=>{if(!est[k]){const e=estDe(j,k);if(e)est[k]=e}}));
  return {...j,est};
}''', "/* «ayer» = el día anterior más reciente; en cada estación")

reemplazar_funcion("jorNueva", r'''function jorNueva(f){
  const d=planDia(f),ayer=jorAnterior(f),est={};
  planEstaciones().forEach(st=>{est[st.id]={e:"pendiente",meta:metaPara(st,ayer,d,entradaPrevia(st.id,f,null)),seg:0,vistas:0,ok:0,mal:0,rep:null,ult:null,resp:[],primero:null}});
  return {examen:examenSel,fecha:f,sesion:1,pos:0,est,papel:elegirPapel(ayer,d),formulas:null,formulasUlt:null,creada:ahora(),actualizado:ahora(),ayer:ayer?ayer.fecha:null,v2:true};
}''', "meta:metaPara(st,ayer,d,entradaPrevia(st.id,f,null))")

reemplazar(
    "jorFusionar: gana la sesión más nueva",
    "function jorFusionar(a,b){\n  if(!a)return b;if(!b)return a;\n",
    '''function jorFusionar(a,b){
  if(!a)return b;if(!b)return a;
  /* dos copias en sesiones distintas no se mezclan estación por estación: gana la sesión más nueva entera */
  if(sesionN(a)!==sesionN(b)){const {item,_id,...r}=sesionN(a)>sesionN(b)?a:b;const m=JSON.parse(JSON.stringify(r));m.v2=true;return m}
''',
    "gana la sesión más nueva entera",
)

reemplazar(
    "jorHoy: estaciones nuevas",
    'if(!est[st.id])est[st.id]={e:"pendiente",meta:metaPara(st,ayer,dd),',
    'if(!est[st.id])est[st.id]={e:"pendiente",meta:metaPara(st,ayer,dd,entradaPrevia(st.id,f,d)),',
    "metaPara(st,ayer,dd,entradaPrevia(st.id,f,d))",
)
reemplazar(
    "reconstruirDia: reajuste de hoy",
    "const m=metaPara(st,J,dd);",
    "const m=metaPara(st,J,dd,entradaPrevia(st.id,hoy,JOR));",
    "metaPara(st,J,dd,entradaPrevia(st.id,hoy,JOR))",
)
reemplazar(
    "jorCompletarDesdeIntento: id por sesión",
    'i._id==="recorrido_ex"+J.examen+"_"+J.fecha',
    "i._id===intentoSesionId(J.examen,J.fecha,sesionN(J))",
    "i._id===intentoSesionId(J.examen,J.fecha,sesionN(J))",
)

reemplazar_funcion("planItemPara", r'''function planItemPara(est,evitarQid){
  /* nunca un ejercicio que ya se vio en esta estación, en ninguna sesión (Adrián, 08/11/2026) */
  const todos=est.pool();
  let pool=todos;
  const calc=pool.filter(t=>t.k==="calc");if(calc.length)pool=calc;
  const vistos=qidsVistosEst(est.id);if(evitarQid)vistos.add(evitarQid);
  let nuevos=pool.filter(t=>!vistos.has(t.id));
  if(!nuevos.length)nuevos=todos.filter(t=>!vistos.has(t.id));
  if(nuevos.length){const set=armarSet(nuevos,"Recorrido","",1);if(set.items[0])return set.items[0]}
  /* no queda ninguno sin ver: se vuelve a uno visto, pero con otras cifras u otra redacción y con las opciones o filas barajadas */
  if(!todos.length)return null;
  const cand=todos.filter(t=>t.id!==evitarQid),t=(cand.length?cand:todos)[Math.floor(Math.random()*(cand.length||todos.length))];
  const x=variantePara(t,vistos);
  return limpiarBarajado([x])[0]||x;
}''', "nunca un ejercicio que ya se vio en esta estación, en ninguna sesión")

# planSeguir / planRegistrar: textos y fin de la sesión
reemplazar(
    "planSeguir: texto «costó»",
    '" (ayer este tema costó)"',
    '" (en la sesión anterior este tema costó)"',
    "en la sesión anterior este tema costó",
)
reemplazar(
    "planSeguir: título con la sesión",
    "titulo:`Recorrido de hoy · estación ${a.i+1} de ${E.length}`",
    'titulo:`Recorrido de hoy${sesionN(JOR)>1?" · sesión "+sesionN(JOR):""} · estación ${a.i+1} de ${E.length}`',
    'Recorrido de hoy${sesionN(JOR)>1',
)
reemplazar(
    "planRegistrar: fin de la sesión",
    'if(aprobada){e.e="aprobada";e.fecha=ahora();e.res=resDe(e);JOR.pos=(p.jornada.i+1)%planEstaciones().length}',
    'if(aprobada){e.e="aprobada";e.fecha=ahora();e.res=resDe(e);JOR.pos=(p.jornada.i+1)%planEstaciones().length;if(!planActual())JOR.fin=ahora()}',
    "if(!planActual())JOR.fin=ahora()",
)
reemplazar(
    "planRegistrar: mensaje al fallar",
    "mañana este tema vuelve primero y con un ejercicio más.",
    "en la próxima sesión este tema vuelve con un ejercicio más (y distinto).",
    "en la próxima sesión este tema vuelve con un ejercicio más",
)
reemplazar(
    "planRegistrar: sesión completa",
    ':"¡Recorrido del día completo!"}',
    ':"¡Sesión "+sesionN(JOR)+" completa! Desde el plan podés empezar la siguiente."}',
    "Desde el plan podés empezar la siguiente",
)

# Historial: un intento por sesión, con tiempos
reemplazar_funcion("intentoDiaId", r'''function intentoDiaId(){return intentoSesionId(JOR.examen,JOR.fecha,sesionN(JOR))}''', "return intentoSesionId(JOR.examen,JOR.fecha,sesionN(JOR))")

reemplazar_funcion("intentoDiaDoc", r'''function intentoDiaDoc(){
  /* un intento del Historial por SESIÓN del recorrido; guarda `tiempos` como los tests (Adrián, 08/11/2026) */
  const n=sesionN(JOR);
  const rs=[];Object.values(JOR.est).forEach(e=>(e.resp||[]).forEach(r=>{if(!r.rep)rs.push(r)}));
  const desde=n>1?String(JOR.inicio||ahora()):"";   /* los problemas en papel son del día: van en la sesión en que se hicieron */
  (JOR.papelResp||[]).forEach(r=>{if(n===1||String(r.t||"")>=desde)rs.push(r)});
  /* lo que ya estaba guardado en el Historial se conserva aunque la jornada en memoria no lo tenga (otro dispositivo, copia vieja) */
  const previo=(typeof intentosReales!=="undefined"?intentosReales:[]).find(i=>i._id===intentoDiaId());
  if(previo)(previo.respuestas||[]).forEach(r=>{if(!rs.some(x=>x.qid===r.qid&&x.t===r.t))rs.push({...r})});
  /* lo recorregido (ortografía) no se vuelve a desarreglar, y lo del capítulo 7 no vuelve a entrar */
  let lista=rs.map(r=>{const p=previo&&(previo.respuestas||[]).find(x=>x.qid===r.qid&&x.t===r.t);return p&&p.recorregida?{...p}:r});
  const fuera=r=>typeof respuestaFueraDelExamen==="function"&&respuestaFueraDelExamen(r);
  const extra=lista.filter(fuera);lista=lista.filter(r=>!fuera(r));
  lista.sort((a,b)=>String(a.t||"")<String(b.t||"")?-1:1);lista.forEach((r,i)=>r.n=i+1);
  const bien=lista.filter(x=>x.ok).length,porTema={},porTipo={};
  lista.forEach(x=>{(porTema[x.tema]=porTema[x.tema]||{ok:0,total:0}).total++;if(x.ok)porTema[x.tema].ok++;(porTipo[x.tipo]=porTipo[x.tipo]||{ok:0,total:0}).total++;if(x.ok)porTipo[x.tipo].ok++});
  const ex=exActual();
  const doc={examen:JOR.examen,materia:ex.materia,practica:"recorrido",dia:JOR.fecha,sesion:n,
    titulo:"Recorrido del día · "+fechaLarga(JOR.fecha)+(n>1?" · sesión "+n:""),
    fecha:JOR.inicio||(n>1?ahora():JOR.creada),actualizado:ahora(),alumno:(typeof alumnoInp!=="undefined"&&alumnoInp&&alumnoInp.value)||"Sin nombre",
    preguntas:lista.length,aciertos:bien,total:lista.length?Math.round(100*bien/lista.length):0,sinResponder:0,omitidas:0,parcial:false,
    porTema,porTipo,respuestas:lista,justificaciones:{escritas:0,total:0}};
  const t=tiemposDeRespuestas({respuestas:lista,fecha:doc.fecha,actualizado:doc.actualizado});
  if(t)doc.tiempos=t;
  if(previo){["recorregido","notaAnterior"].forEach(k=>{if(previo[k]!=null)doc[k]=previo[k]})}
  const exc=((previo&&previo.excluidas)||[]).concat(extra.map(r=>Object.assign({},r,{motivo:"capítulo 7: no entra"})));
  if(exc.length)doc.excluidas=exc;
  return doc;
}''', "Un intento del Historial por SESIÓN del recorrido".lower() if False else "un intento del Historial por SESIÓN del recorrido; guarda `tiempos`")

reemplazar_funcion("respuestasDelDia", r'''function respuestasDelDia(f){
  const out=[];
  /* el «Recorrido del día» (una práctica por sesión) ya está repartido en las estaciones: no se vuelve a repartir */
  intentos.filter(i=>i.examen===examenSel&&!i.lectura&&i.practica!=="recorrido"&&claveDia(i.fecha)===f).forEach(i=>{
    (i.respuestas||[]).forEach(r=>{if(r.papel||/^\(sin responder\)/.test(String(r.respuestaDada||"")))return;out.push({...r,t:r.t||i.fecha,de:i.titulo||""})});
  });
  return out;
}''', 'el «Recorrido del día» (una práctica por sesión) ya está repartido')

reemplazar(
    "fallosDe: ejercicios que salieron mal en sesiones compactas",
    "  if(j.formulas&&j.formulas.mal)out.formulas=j.formulas.mal.slice();",
    '''  Object.values(j.est).forEach(e=>(e.fallos||[]).forEach(qid=>{if(!vistos.has(qid)){vistos.add(qid);const t=BANCO_TODO.find(x=>x.id===qid);if(t)out.items.push(t)}}));
  if(j.formulas&&j.formulas.mal)out.formulas=j.formulas.mal.slice();''',
    "(e.fallos||[]).forEach(qid=>",
)

reemplazar_funcion("resumenJornada", r'''function resumenJornada(J){
  /* el día entero: en cada estación, el resultado de la última sesión en que salió */
  const E=planEstaciones();let sabe=0,dud=0,no=0,hechas=0;
  E.forEach(st=>{const e=estDe(J,st.id);if(!e)return;const r=resE(e);if(r){hechas++;if(r==="sabe")sabe++;else if(r==="dudoso")dud++;else no++}});
  return {sabe,dud,no,hechas,total:E.length};
}
function resumenSesion(J){
  /* la sesión en curso */
  const E=planEstaciones();let sabe=0,dud=0,no=0,hechas=0;
  E.forEach(st=>{const e=J&&J.est&&J.est[st.id];if(!e)return;const r=e.res||resDe(e);if(r){hechas++;if(r==="sabe")sabe++;else if(r==="dudoso")dud++;else no++}});
  return {sabe,dud,no,hechas,total:E.length};
}''', "function resumenSesion(J){")

reemplazar(
    "depurarIntento: tiempos del recorrido",
    "function depurarIntento(i){\n",
    "function depurarIntento(i){\n  if(i&&i.practica===\"recorrido\"&&!(i.tiempos&&+i.tiempos.segundosTotal>0)){const tt=tiemposDeRespuestas(i);if(tt)i={...i,tiempos:tt}}   /* el recorrido del día también muestra sus tiempos */\n",
    "el recorrido del día también muestra sus tiempos",
)

# ───────────────────────── PANTALLA: solapa «Plan de estudio» ─────────────────────────
reemplazar(
    "subPlan: sesión en curso",
    "const ix=P.dias.indexOf(dHoy),ayer=jorAnterior(hoy),fa=fallosDe(ayer),R=resumenJornada(J),a=planActual();",
    "const ix=P.dias.indexOf(dHoy),sesN=sesionN(J),ayer=sesN>1?sesionAnteriorDoc(J):jorAnterior(hoy),fa=fallosDe(ayer),R=resumenSesion(J),a=planActual();",
    "const ix=P.dias.indexOf(dHoy),sesN=sesionN(J)",
)
reemplazar(
    "subPlan: primer bloque en las sesiones 2, 3…",
    "    /* 1. repaso de ayer */\n    if(ayer){",
    r'''    /* 1. repaso de ayer (o de la sesión anterior, desde la sesión 2) */
    if(sesN>1){
      const hayS=fa.estaciones.length;
      h+=`<li><span class="num${hayS?"":" ok"}">${hayS?"1":"✓"}</span><div class="cuerpo"><b>Primero: lo que la sesión ${sesN-1} no salió</b> <small class="note">(${hayS?"≈ "+minTxt(5*fa.estaciones.length):"nada pendiente"})</small>`;
      if(!hayS)h+=`<p class="note" style="margin:3px 0 0">En la sesión ${sesN-1} salió todo lo que se recorrió. Esta sesión confirma, con ejercicios nuevos.</p>`;
      else h+=`<ol class="an-pasos"><li>Estos temas costaron en la sesión ${sesN-1}. Para cada uno, abrí la guía en la página que dice el botón y leé el apartado otra vez (5 minutos por tema, no más).</li><li>En el recorrido de esta sesión cada uno trae <b>un ejercicio más</b> que en la anterior, siempre ejercicios que todavía no viste.</li></ol><div class="plan-flojas">${fa.estaciones.map(({st,e})=>`<div class="floja"><span class="chipt ${e.res==="nosabe"?"bad":"warn"}">${e.res==="nosabe"?"no salió":"dudoso"}</span><b>${esc(st.nombre)}</b><span class="note"> · en la sesión ${sesN-1}: ${e.ok} bien, ${e.mal} mal · ahora trae ${(J.est[st.id]||{}).meta||META_BASE} ${((J.est[st.id]||{}).meta||META_BASE)===1?"ejercicio":"ejercicios"}</span><div class="acc">${guiaDeEstacion(st,fa.items)}</div></div>`).join("")}</div>`;
      h+=`</div></li>`;
    }else if(ayer){''',
    "Primero: lo que la sesión ${sesN-1} no salió",
)
reemplazar(
    "subPlan: título del recorrido con la sesión",
    "<b>El recorrido completo del módulo</b> <small class=\"note\">(${E.length} estaciones",
    "<b>El recorrido completo del módulo${sesN>1?\" · sesión \"+sesN:\"\"}</b> <small class=\"note\">(${E.length} estaciones",
    'El recorrido completo del módulo${sesN>1',
)
reemplazar(
    "subPlan: regla de los ejercicios",
    "<li>Los temas que ayer salieron mal traen dos ejercicios en vez de uno. Si uno te traba mucho, podés saltearlo: queda como «no salió» y mañana se repasa primero.</li>",
    "<li>Los temas que salieron mal en la sesión anterior traen un ejercicio más cada vez (1 → 2 → 3…), siempre distintos a los que ya viste. Si uno te traba mucho, podés saltearlo: queda como «no salió» y en la sesión siguiente trae un ejercicio más.</li>",
    "traen un ejercicio más cada vez (1 → 2 → 3…)",
)
reemplazar(
    "subPlan: botón de la sesión siguiente",
    '<button class="btn ghost chico" id="plansaltear">Saltear esta estación por ahora</button>`:""}<button class="btn ghost chico" id="planmapa">${R.hechas?"Ver las estaciones de hoy":"Ver las estaciones"}</button></div>\n      <div id="planmapabox" hidden>${mapaDiaHTML(J,true)}</div></div></li>`;',
    '<button class="btn ghost chico" id="plansaltear">Saltear esta estación por ahora</button>`:""}${!a&&R.hechas?`<button class="btn straw" id="plannuevasesion">Empezar la sesión ${sesN+1} (${proximaSesionEjercicios(J)} ejercicios)</button>`:""}<button class="btn ghost chico" id="planmapa" data-txt="${R.hechas?(sesN>1?"Ver las estaciones de la sesión "+sesN:"Ver las estaciones de hoy"):"Ver las estaciones"}">${R.hechas?(sesN>1?"Ver las estaciones de la sesión "+sesN:"Ver las estaciones de hoy"):"Ver las estaciones"}</button></div>\n      <div id="planmapabox" hidden>${mapaDiaHTML(J,true)}</div>${sesionesHTML(J,true)}</div></li>`;',
    'id="plannuevasesion"',
)
reemplazar(
    "subPlan: acciones de la sesión nueva",
    'const b1=$("#planseguir");if(b1)b1.addEventListener("click",planSeguir);',
    'const b1=$("#planseguir");if(b1)b1.addEventListener("click",planSeguir);\n  const bns=$("#plannuevasesion");if(bns)bns.addEventListener("click",()=>{bns.disabled=true;planNuevaSesion()});',
    'bns.addEventListener("click"',
)
reemplazar(
    "subPlan: texto del botón de las estaciones",
    'bm.textContent=box.hidden?"Ver las estaciones de hoy":"Ocultar las estaciones"',
    'bm.textContent=box.hidden?(bm.dataset.txt||"Ver las estaciones de hoy"):"Ocultar las estaciones"',
    'bm.dataset.txt||"Ver las estaciones de hoy"',
)
reemplazar(
    "subPlan: presentación",
    "Hoy se mide; lo que no sale, al otro día vuelve primero (repaso) y con un ejercicio más en su estación. Lo que ya sabés sigue con uno solo.<br>",
    "Hoy se mide; lo que no sale vuelve primero (repaso) y con un ejercicio más en su estación. Lo que ya sabés sigue con uno solo. <b>Terminado un recorrido podés empezar otro</b> (sesión 2, 3…, el mismo día o el que sea): cada estación que salió mal trae un ejercicio más, siempre distinto a los que ya viste.<br>",
    "Terminado un recorrido podés empezar otro",
)
reemplazar(
    "subPlan: día por día con sesiones",
    "${Jd&&d.f!==hoy&&R.hechas?mapaDiaHTML(Jd,false):\"\"}",
    "${Jd&&d.f!==hoy?sesionesHTML(Jd,false):\"\"}${Jd&&d.f!==hoy&&R.hechas?mapaDiaHTML(jorConsolidada(Jd),false):\"\"}",
    "mapaDiaHTML(jorConsolidada(Jd),false)",
)
reemplazar(
    "mapaDiaHTML: texto «costó»",
    '" (ayer costó)"',
    '" (la sesión anterior costó)"',
    "(la sesión anterior costó)",
)
reemplazar(
    "mapa de la semana: última sesión en que salió",
    "const e=Jd&&Jd.est&&Jd.est[x.id];return cel(e?(e.res||resDe(e)):null)",
    "const e=Jd&&estDe(Jd,x.id);return cel(e?resE(e):null)",
    "const e=Jd&&estDe(Jd,x.id);return cel(e?resE(e):null)",
)

if errores:
    print("\nHAY ERRORES: no se escribió nada.")
    sys.exit(1)
if h != orig:
    open(ruta, "w", encoding="utf-8").write(h)
    print("escrito")
else:
    print("sin cambios")
