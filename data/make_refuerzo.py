# Genera data/examen_refuerzo.json (examen de refuerzo de Química, caps. 3-6 + repaso del Módulo 1)
import json, random
Q = []
def mc(text, ok, wrong, why=""):
    Q.append({"type": "multichoice", "shuffle": True, "text": text, "explain": why,
              "answers": [{"text": ok, "correct": True}] + [{"text": w, "correct": False} for w in wrong]})
def vf(text, val, why=""):
    Q.append({"type": "multichoice", "text": text, "explain": why,
              "answers": [{"text": "VERDADERO", "correct": val}, {"text": "FALSO", "correct": not val}]})
def fill(text, accepted, why=""):
    Q.append({"type": "short", "text": text, "explain": why,
              "answers": [{"text": a, "correct": True} for a in accepted]})

# ---------- Opción múltiple (distractores parecidos, una sola correcta) ----------
mc("¿Qué grupo funcional tienen los alcoholes, como el etanol?", "–OH", ["–COOH", "–CHO", "–O–"],
   "–OH es el oxhidrilo. –COOH es de los ácidos carboxílicos y –CHO de los aldehídos.")
mc("La acetona (quitaesmalte) pertenece a la función…", "cetona", ["éter", "éster", "aldehído"],
   "La propanona (acetona) es una cetona: el grupo carbonilo está dentro de la cadena.")
mc("¿Qué función orgánica oxigenada da el aroma de frutas como la pera o el ananá y se usa en perfumes y golosinas?",
   "Los ésteres", ["Los éteres", "Los aldehídos", "Los ácidos carboxílicos"], "Éster ≠ éter: los ésteres son los aromáticos.")
mc("Si en el metano (CH₄) se reemplaza un hidrógeno por el grupo –OH, se obtiene…", "metanol", ["etanol", "metanal", "metano"],
   "Un carbono → 'met-'; con –OH es un alcohol: metanol. El etanol tiene dos carbonos.")
mc("El eteno (etileno) es un gas que…", "ayuda a madurar las frutas", ["se usa como naftalina para la ropa", "se usa como quitaesmalte", "retrasa la maduración de las frutas"], "")
mc("¿Qué logró Wöhler en 1828 y derrumbó la idea de la 'fuerza vital'?", "Sintetizó urea en el laboratorio a partir de sustancias inorgánicas",
   ["Extrajo urea de la orina de un animal", "Fabricó alcohol a partir del azúcar", "Descubrió que el carbono es un elemento"],
   "Una sustancia orgánica, la urea, se podía fabricar sin un ser vivo.")
mc("¿Qué producto de una combustión es un sólido negro (hollín)?", "El carbono", ["El monóxido de carbono", "El dióxido de carbono", "El vapor de agua"],
   "El humo negro son finas partículas de carbono.")
mc("¿Por qué el monóxido de carbono es tan peligroso en ambientes cerrados?", "Se une a la hemoglobina e impide el transporte de oxígeno",
   ["Se une a la insulina y desregula el azúcar en sangre", "Reacciona con el oxígeno del aire y forma ozono", "Tiene un olor muy intenso que irrita los ojos"],
   "Es incoloro e inodoro, por eso no se nota.")
mc("Al quemar completamente propano (C₃H₈) con suficiente oxígeno, los productos son…", "CO₂ y H₂O", ["CO y H₂O", "C y H₂O", "CO₂ y H₂"],
   "Combustión completa: dióxido de carbono + agua.")
mc("¿Qué biomolécula contiene fósforo (P) además de C, H, O y N?", "Los ácidos nucleicos", ["Las proteínas", "Los lípidos", "Los glúcidos"],
   "Las proteínas llevan C, H, O, N (a veces S); lípidos y glúcidos, C, H y O.")
mc("La seda y el colágeno son ejemplos de proteínas con función…", "estructural", ["enzimática", "de transporte", "reguladora"],
   "Las enzimas (proteasas, lipasas) catalizan; las estructurales dan forma y soporte.")
mc("¿Por qué conviene no cocinar demasiado los alimentos con vitamina C?", "Es hidrosoluble y se destruye con la cocción",
   ["Es liposoluble y se funde con la grasa", "Se transforma en glucosa", "Es un mineral que se evapora"], "")
mc("El magnesio (Mg) tiene 2 electrones en su último nivel. Para parecerse al neón tiende a…", "perder 2 electrones y formar un catión",
   ["ganar 6 electrones", "perder 2 electrones y formar un anión", "compartir 2 electrones con el neón"],
   "Al perder electrones queda con carga positiva: catión.")
mc("¿Cuántos electrones tiene el flúor en su último nivel después de formar el ion F⁻?", "8", ["7", "6", "10"],
   "Tenía 7, gana 1 y llega al octeto, como el neón.")
mc("¿Qué tipo de unión hay entre el hidrógeno y el cloro en el HCl?", "Covalente: los dos son no metales y comparten electrones",
   ["Iónica: el hidrógeno cede su electrón al cloro", "Metálica: los dos átomos forman una nube de electrones", "Iónica: el cloro cede su electrón al hidrógeno"], "")
mc("¿Por qué un alambre de cobre se puede estirar sin romperse?", "Los cationes se deslizan porque la nube de electrones mantiene unido el cristal",
   ["Los electrones quedan fijos entre los cationes y lo mantienen rígido", "Los cationes se transforman en aniones al estirarse", "Porque el cobre tiene uniones covalentes"], "")
mc("¿Qué característica es propia de una base?", "Tacto jabonoso y acción sobre las grasas",
   ["Sabor agrio", "Reacción con metales liberando hidrógeno", "Enrojece el papel tornasol azul"], "")
mc("¿De qué color se pone la fenolftaleína en una solución de hidróxido de sodio (NaOH)?", "Rojo grosella (se enrojece)", ["Azul", "Incolora", "Amarilla"],
   "En ácidos queda incolora; en bases se enrojece.")
mc("¿Cuál es la fórmula del hidróxido de calcio?", "Ca(OH)₂", ["CaOH", "CaO", "Ca₂OH"], "El calcio es Ca²⁺: necesita dos oxhidrilos.")
mc("¿Qué se forma cuando reaccionan un ácido y una base?", "Una sal y agua", ["Un óxido y agua", "Otro ácido e hidrógeno", "Una sal y dióxido de carbono"],
   "HCl + NaOH → NaCl + H₂O es una neutralización.")
mc("Una reacción irreversible continúa hasta que…", "se consume por completo el reactivo que está en defecto",
   ["se iguala la cantidad de reactivos y de productos", "los productos reaccionan entre sí y regeneran los reactivos", "se acaba la energía del ambiente"], "")
mc("En 2 Al + 3 Cl₂ → 2 AlCl₃, el 2 pequeño de Cl₂ indica…", "la cantidad de átomos de cloro que tiene cada molécula",
   ["la cantidad de moléculas de cloro que reaccionan", "la carga eléctrica del cloro", "los electrones que gana el cloro"],
   "Subíndice = átomos en la molécula. Coeficiente (el 3 de adelante) = moléculas que reaccionan.")
mc("El oro de 18 quilates es…", "una solución (aleación): una mezcla homogénea", ["una sustancia simple", "una sustancia compuesta", "una mezcla heterogénea"],
   "El oro de 24 quilates sería la sustancia simple; el de 18 lleva otros metales mezclados.")
mc("El ozono (O₃) es…", "una sustancia simple", ["una sustancia compuesta", "una solución", "una mezcla heterogénea"],
   "Aunque tenga 3 átomos, todos son del mismo elemento: oxígeno.")
mc("¿Cuál de estas es una propiedad intensiva?", "La densidad", ["La masa", "El volumen", "La longitud"], "Las intensivas no dependen de la cantidad de materia.")

# ---------- Verdadero o falso ----------
vf("En la molécula de nitrógeno (N₂), los átomos comparten tres pares de electrones.", True, "Triple enlace covalente.")
vf("En la molécula de agua, el oxígeno completa ocho electrones y cada hidrógeno completa dos.", True, "El hidrógeno se completa con 2, no con 8.")
vf("En la molécula de oxígeno (O₂), un átomo le cede dos electrones al otro.", False, "En la unión covalente se comparten, no se ceden.")
vf("En el CO₂, el carbono forma dos enlaces dobles.", True, "O=C=O: cuatro pares compartidos en total.")
vf("Los compuestos iónicos conducen la electricidad en estado sólido.", False, "Solo conducen fundidos o disueltos en agua.")
vf("El helio tiene ocho electrones en su último nivel.", False, "El helio tiene 2: es la excepción a la regla del octeto.")
vf("Los hidrocarburos contienen carbono, hidrógeno y oxígeno.", False, "Solo carbono e hidrógeno.")
vf("Los lípidos son insolubles en agua.", True, "")
vf("La glucosa y la sacarosa se disuelven en agua.", True, "Monosacáridos y disacáridos son solubles.")
vf("El colesterol es un lípido necesario para formar la vitamina D y algunas hormonas.", True, "")
vf("En la doble hélice del ADN, la adenina se aparea con la citosina.", False, "A–T y C–G.")
vf("Los ácidos, disueltos en agua, conducen la corriente eléctrica.", True, "")
vf("Los ácidos reaccionan con ciertos metales y liberan hidrógeno.", True, "Las bases no lo hacen.")
vf("Los ácidos azulean el papel tornasol.", False, "Los ácidos lo enrojecen; las bases lo azulean.")
vf("Una solución de pH 9 es ácida.", False, "pH menor que 7 es ácido; mayor que 7, básico.")
vf("La reacción HCl + NaOH → NaCl + H₂O es una reacción de síntesis.", False, "Es de neutralización: dos sustancias que se reordenan, no se unen en una sola.")
vf("En la combustión incompleta de un hidrocarburo puede formarse monóxido de carbono.", True, "")
vf("El carbono es el único elemento biogenésico.", False, "Los biogenésicos son C, H, O, N, P y S.")
vf("Todos los compuestos orgánicos contienen carbono.", True, "")
vf("El acero es una aleación de hierro y aluminio.", False, "Es hierro con un poco de carbono.")
vf("La masa y el volumen de una muestra son propiedades extensivas.", True, "")
vf("Una macrobiomolécula puede tener miles de átomos.", True, "")

# ---------- Completar (palabra técnica, se escribe) ----------
fill("Un átomo metálico que pierde electrones se transforma en un ______.", ["catión"])
fill("Un átomo no metálico que gana electrones se transforma en un ______.", ["anión"])
fill("La fuerza que une al catión con el anión es la atracción ______.", ["electrostática"])
fill("A la propiedad del carbono de unirse formando cadenas largas se la llama ______.", ["concatenación", "encadenamiento"])
fill("La creencia de que solo los seres vivos fabricaban compuestos orgánicos se llamó teoría ______.", ["vitalista"])
fill("El azúcar de los nucleótidos del ADN es la ______.", ["desoxirribosa"])
fill("El azúcar de los nucleótidos del ARN es la ______.", ["ribosa"], "ADN: desoxirribosa. ARN: ribosa.")
fill("La proteína que transporta el oxígeno en los glóbulos rojos es la ______.", ["hemoglobina"])
fill("Las hormonas como la insulina son proteínas con función ______.", ["reguladora", "hormonal"])
fill("Los elementos ______ (C, H, O, N, P y S) forman parte de los seres vivos.", ["biogenésicos", "bioelementos"])
fill("Un brasero en un ambiente cerrado produce, por combustión incompleta, el gas tóxico ______.", ["monóxido de carbono", "CO"],
     "Monóxido (un oxígeno) ≠ dióxido (dos oxígenos).")
fill("El vinagre contiene ácido ______ diluido.", ["acético"])
fill("Los gases SO₂ y NO₂ que forman la lluvia ácida son ______ de azufre y de nitrógeno.", ["óxidos"])
fill("El NaCl, la sal de cocina, se llama ______ de sodio.", ["cloruro"])
fill("El recipiente de fondo plano y cuello largo para preparar soluciones de concentración exacta es el matraz ______.", ["aforado"],
     "El Erlenmeyer es cónico y no sirve para medir volumen exacto.")
fill("Los metales se pueden transformar en láminas porque son ______.", ["maleables"])
fill("Una dispersión de partículas sólidas en un líquido, como el agua de río con barro, es una ______.", ["suspensión"])
fill("El vapor de agua que pasa directamente a cristales de hielo sufre una ______ (cambio de gas a sólido).", ["deposición", "sublimación inversa", "sublimación regresiva"])
fill("Un sistema de una sola fase es ______; con dos o más fases es heterogéneo.", ["homogéneo"])
fill("El número ______ (A) es la suma de protones y neutrones.", ["másico"])

random.Random(14112026).shuffle(Q)
for i, q in enumerate(Q): q["id"] = i + 1

match_funciones = {
    "id": 102, "chapter": 99, "type": "match", "title": "Funciones orgánicas",
    "subtitle": "Relacioná cada descripción con la función orgánica.", "instructions": "Desplegá el menú y elegí la respuesta correcta.", "images": [],
    "data": {"items": [
        {"left": "Grupo –OH; el etanol es un ejemplo", "correct": ["Alcohol"]},
        {"left": "Grupo –COOH; el ácido acético del vinagre es un ejemplo", "correct": ["Ácido carboxílico"]},
        {"left": "Grupo carbonilo dentro de la cadena; la acetona es un ejemplo", "correct": ["Cetona"]},
        {"left": "Dan aroma a frutas y se usan en perfumes", "correct": ["Éster"]},
        {"left": "Formados solo por carbono e hidrógeno; el metano es un ejemplo", "correct": ["Hidrocarburo"]},
        {"left": "Grupo carbonilo en el extremo de la cadena (–CHO)", "correct": ["Aldehído"]}],
        "options": ["Alcohol", "Ácido carboxílico", "Cetona", "Éster", "Hidrocarburo", "Aldehído"]}}
match_clasif = {
    "id": 103, "chapter": 99, "type": "match", "title": "Sustancia simple, compuesta o solución",
    "subtitle": "Clasificá cada material.", "instructions": "Desplegá el menú y elegí la respuesta correcta.", "images": [],
    "data": {"items": [
        {"left": "Agua (H₂O)", "correct": ["Sustancia compuesta"]},
        {"left": "Oxígeno (O₂)", "correct": ["Sustancia simple"]},
        {"left": "Azúcar (sacarosa)", "correct": ["Sustancia compuesta"]},
        {"left": "Bronce (cobre y estaño)", "correct": ["Solución"]},
        {"left": "Hierro (Fe)", "correct": ["Sustancia simple"]},
        {"left": "Dióxido de carbono (CO₂)", "correct": ["Sustancia compuesta"]},
        {"left": "Aire filtrado", "correct": ["Solución"]}],
        "options": ["Sustancia simple", "Sustancia compuesta", "Solución"]}}
exam = {"id": 101, "chapter": 99, "type": "quiz", "title": "Examen de refuerzo: preguntas mezcladas", "noPenalty": True,
        "subtitle": "Mezcla de opción múltiple, verdadero o falso y completar. Los temas son los que más se fallaron en las prácticas.",
        "instructions": "En completar escribí el término técnico (la tilde y las mayúsculas no cuentan). Al comprobar vas a ver la respuesta correcta y una explicación.",
        "images": [], "data": {"questions": Q}}
json.dump([exam, match_funciones, match_clasif], open("/home/user/mi-proyecto-cloude/data/examen_refuerzo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(Q), Counter("short" if q["type"] == "short" else ("vf" if q["answers"][0]["text"] == "VERDADERO" else "mc") for q in Q))
