# Genera data/parte2.json: Parte 2 del Módulo 2 (caps. 3 a 6), mismos formatos que los ejercicios 17-29, preguntas nuevas.
# Fuente de contenido: guía oficial de Química Módulo 2. Se evitan los errores conocidos de la guía.
import json, random
EX = []
def add(ex_id, chapter, type_, title, subtitle, instructions, data, **kw):
    EX.append(dict(id=200 + ex_id, part=2, chapter=chapter, title=title, subtitle=subtitle, instructions=instructions, type=type_, images=[], data=data, **kw))
def A(text, ok, why=""): return {"text": text, "correct": ok}
def mc(text, ok, wrong, why="", shuffle=False):
    return {"type": "multichoice", "text": text, "explain": why, **({"shuffle": True} if shuffle else {}),
            "answers": [A(ok, True)] + [A(w, False) for w in wrong]}
def vf(text, val, why=""):
    return {"type": "multichoice", "text": text, "explain": why, "answers": [A("VERDADERO", val), A("FALSO", not val)]}
def short(text, accepted, why=""):
    return {"type": "short", "text": text, "explain": why, "answers": [A(a, True) for a in accepted]}
def cloze(text, gaps, wordlist=None):
    d = {"text": text, "gaps": [{"n": i + 1, "answers": g, "hint": ""} for i, g in enumerate(gaps)], "caseSensitive": False}
    if wordlist: d["wordList"] = wordlist
    return d
def match(items, options): return {"items": [{"left": l, "correct": [c]} for l, c in items], "options": options}

# ---------------- CAPÍTULO 3 · Uniones químicas ----------------
add(1, 3, "quiz", "PROPIEDADES DE LAS SUSTANCIAS IÓNICAS, COVALENTES Y METÁLICAS",
    "A partir de la información de la tabla sobre las sustancias P, Q, R, S y T, decidí cuál es iónica, cuál metálica y cuál covalente.",
    "Para cada sustancia seleccioná la única respuesta correcta.",
    {"questions": [mc(f"{s} es una sustancia", ok, [o for o in ("Iónica", "Covalente", "Metálica") if o != ok], why) for s, ok, why in [
        ("P", "Iónica", "No conduce en estado sólido pero sí fundida, y se disuelve en agua: es iónica."),
        ("Q", "Covalente", "Es un gas formado por moléculas, con punto de ebullición muy bajo: covalente."),
        ("R", "Metálica", "Conduce siempre la electricidad, es brillante y se puede laminar y estirar: metálica."),
        ("S", "Iónica", "Forma cristales, es una sal y conduce disuelta en agua: iónica."),
        ("T", "Covalente", "Líquido que no conduce la electricidad y está formado por moléculas: covalente.")]]},
    table={"head": ["Sustancia", "Estado a temperatura ambiente", "¿Conduce la electricidad?", "Otras observaciones"],
           "rows": [["P", "Sólido", "No conduce sólida; sí cuando se funde", "Se disuelve en agua; puntos de fusión elevados"],
                    ["Q", "Gas", "No", "Está formada por moléculas; punto de ebullición muy bajo"],
                    ["R", "Sólido", "Sí, siempre", "Brillante; se puede laminar y estirar en hilos"],
                    ["S", "Sólido", "No conduce sólida; sí disuelta en agua", "Forma cristales; es una sal"],
                    ["T", "Líquido", "No", "Está formada por moléculas; punto de ebullición bajo"]]})

add(2, 3, "match", "COMPUESTOS IÓNICOS, COVALENTES Y METÁLICOS",
    "Ejercicio de emparejamiento", "Desplegá las opciones de la derecha y elegí la respuesta correcta.",
    match([("a) Los átomos comparten electrones de a pares.", "COMPUESTOS COVALENTES"),
           ("b) Los cationes están sumergidos en una nube de electrones.", "COMPUESTOS METÁLICOS"),
           ("c) Se forman por la unión de un metal con un no metal.", "COMPUESTOS IÓNICOS"),
           ("d) Forman redes cristalinas de cationes y aniones.", "COMPUESTOS IÓNICOS"),
           ("e) Se unen únicamente átomos de no metales.", "COMPUESTOS COVALENTES"),
           ("f) Son maleables y dúctiles.", "COMPUESTOS METÁLICOS"),
           ("g) Conducen la electricidad cuando se funden o se disuelven en agua.", "COMPUESTOS IÓNICOS"),
           ("h) Salvo el mercurio, son sólidos a temperatura ambiente.", "COMPUESTOS METÁLICOS"),
           ("i) Forman moléculas; con átomos de carbono pueden formar macromoléculas.", "COMPUESTOS COVALENTES")],
          ["COMPUESTOS IÓNICOS", "COMPUESTOS COVALENTES", "COMPUESTOS METÁLICOS"]))

add(3, 3, "quiz", "LA MOLÉCULA DE DIÓXIDO DE CARBONO",
    "El dióxido de carbono se representa O=C=O: el carbono comparte dos pares de electrones con cada átomo de oxígeno. Considerá esa información y contestá las preguntas.",
    "Escribí la respuesta. Las tildes y las mayúsculas no cuentan.",
    {"questions": [
        short("¿Cuántos átomos de oxígeno hay en la molécula?", ["2", "dos"]),
        short("¿Cuántos átomos de carbono hay en la molécula?", ["1", "uno", "un"]),
        short("¿Cuál es la fórmula de este compuesto?", ["CO2", "CO₂"], "Un carbono y dos oxígenos."),
        short("¿Cuántos pares de electrones comparte el carbono con cada oxígeno?", ["2", "dos"]),
        short("¿Cómo se llama el enlace en el que se comparten dos pares de electrones?", ["doble", "enlace doble", "doble enlace", "union doble"]),
        short("¿Cuántos electrones queda rodeando cada átomo en su último nivel?", ["8", "ocho"], "Cumplen la regla del octeto."),
        short("¿Cómo se clasifica la unión entre estos átomos: iónica, metálica o covalente?", ["covalente"], "Los dos son no metales y comparten electrones.")]})

add(4, 3, "cloze", "UNIÓN IÓNICA Y UNIÓN COVALENTE", "Rellenar los espacios en blanco",
    "Completá la palabra que falta en cada espacio. Las tildes y las mayúsculas no cuentan.",
    cloze("1- En la unión iónica un átomo {{1}} electrones y el otro los {{2}}.\n\n"
          "2- El átomo metálico que cede electrones queda con carga positiva y se llama {{3}}; el átomo no metálico que los recibe se llama {{4}}.\n\n"
          "3- Los iones de carga opuesta se mantienen unidos por la atracción {{5}}.\n\n"
          "4- Las sustancias iónicas forman redes {{6}}, se disuelven en agua y conducen la electricidad cuando están fundidas o {{7}} en agua.\n\n"
          "5- En la unión covalente los átomos de los no metales {{8}} electrones de a pares y forman {{9}}.",
          [["cede", "pierde"], ["gana", "recibe", "capta", "incorpora"], ["catión", "cation"], ["anión", "anion"], ["electrostática"], ["cristalinas"],
           ["disueltas", "disueltos", "disuelta", "en solución"], ["comparten"], ["moléculas"]]))

# ---------------- CAPÍTULO 4 · Familias de compuestos ----------------
add(5, 4, "quiz", "TIPOS DE COMPUESTOS QUÍMICOS", "", "Para cada compuesto seleccioná la única opción correcta.",
    {"questions": [mc(f, ok, [o for o in ("Óxido", "Ácido", "Base", "Sal") if o != ok], why) for f, ok, why in [
        ("HCl", "Ácido", "Tiene hidrógeno unido a un no metal."),
        ("Mg(OH)₂", "Base", "Un metal unido a grupos oxhidrilo: hidróxido."),
        ("SO₃", "Óxido", "Binario de oxígeno con un no metal."),
        ("CaCO₃", "Sal", "Metal unido a un grupo no metálico (carbonato)."),
        ("H₂SO₄", "Ácido", "Hidrógeno unido a un no metal acompañado de oxígeno."),
        ("Na₂O", "Óxido", "Oxígeno unido a un metal."),
        ("Al(OH)₃", "Base", "Hidróxido: metal + oxhidrilos."),
        ("CuSO₄", "Sal", "Metal (cobre) unido al grupo sulfato."),
        ("H₃PO₄", "Ácido", "Hidrógeno + grupo no metálico con oxígeno."),
        ("MgCl₂", "Sal", "Metal unido a un no metal."),
        ("Fe₂O₃", "Óxido", "Oxígeno + metal (hierro)."),
        ("KOH", "Base", "Metal unido a un oxhidrilo.")]]})

add(6, 4, "match", "ESCALA DE pH", "Determiná qué tipo de solución corresponde a los siguientes valores de pH",
    "Desplegá el menú y seleccioná la respuesta correcta.",
    match([("- pH 3", "Solución ácida"), ("- pH 8,5", "Solución básica"), ("- pH 13", "Solución básica"),
           ("- pH 6,2", "Solución ácida"), ("- pH 7", "Solución neutra"), ("- pH 10", "Solución básica"), ("- pH 0,5", "Solución ácida")],
          ["Solución ácida", "Solución básica", "Solución neutra"]))

add(7, 4, "quiz", "CONCEPTO DE pH", "", "Seleccioná la única respuesta correcta.",
    {"questions": [
        mc("El pH es una medida de…", "la acidez, con valores de 0 a 14", ["la temperatura de una solución", "la cantidad de agua de una solución", "la densidad de una solución, de 0 a 100"], shuffle=True),
        mc("Una sustancia neutra tiene un pH…", "igual a 7", ["menor que 7", "mayor que 7", "igual a 0"], "Ácidas: menor que 7. Básicas: mayor que 7.", True),
        mc("¿Cuál de estas soluciones es la más ácida?", "pH 2", ["pH 5", "pH 7", "pH 12"], "Cuanto menor el pH, más ácida.", True),
        mc("¿Cuál de estas soluciones es la menos básica?", "pH 8", ["pH 9", "pH 10,5", "pH 13,5"], "Todas son básicas; la más cercana a 7 es la menos básica.", True),
        mc("¿Cuál es el instrumento de laboratorio que mide el pH?", "El pH-metro", ["El termómetro", "La probeta", "El tubo de ensayo"], "", True),
        mc("¿Qué indica la notación pH ∈ (7, 14]?", "Una sustancia básica", ["Una sustancia ácida", "Una sustancia neutra", "Una sustancia que no tiene pH"], "El paréntesis excluye el 7.", True),
        mc("¿Entre qué valores se recomienda que esté el pH de un líquido para no dañar la piel?", "Entre 4 y 9", ["Entre 0 y 2", "Entre 10 y 14", "Solo exactamente 7"], "", True)]})

add(8, 4, "cloze", "INDICADORES ÁCIDO-BASE", "Rellenar los espacios en blanco",
    "Completá las palabras que faltan. Las tildes y las mayúsculas no cuentan.",
    cloze("1- El papel tornasol azul se pone de color {{1}} frente a un ácido.\n\n"
          "2- El papel tornasol rojo se pone de color {{2}} frente a una base.\n\n"
          "3- La fenolftaleína es incolora en medio {{3}} y se pone de color rojo grosella en medio {{4}}.\n\n"
          "4- Las sustancias que cambian de color según el pH se llaman {{5}}.",
          [["rojo"], ["azul"], ["ácido", "acido", "ácida"], ["básico", "alcalino", "básica", "basico"], ["indicadores"]]))

add(9, 4, "cloze", "ÓXIDOS, ÁCIDOS, BASES Y SALES", "Rellenar los espacios en blanco",
    "Completá la palabra que falta. Las tildes y las mayúsculas no cuentan.",
    cloze("1- Los óxidos son sustancias {{1}} formadas por oxígeno y otro elemento.\n\n"
          "2- El carácter ácido lo da la presencia de {{2}}.\n\n"
          "3- Las bases o hidróxidos tienen un metal unido a uno o más grupos {{3}}.\n\n"
          "4- El NaCl se llama cloruro de {{4}}.\n\n"
          "5- Cuando un ácido y una base reaccionan se forman una sal y {{5}}.\n\n"
          "6- La lluvia ácida se forma cuando los óxidos de {{6}} y de nitrógeno reaccionan con el agua y el oxígeno de la atmósfera.\n\n"
          "7- El ácido del vinagre es el ácido {{7}} y el de las gaseosas es el ácido {{8}}.",
          [["binarias", "binarios"], ["hidrógeno", "hidrogeno"], ["oxhidrilo", "hidroxilo", "OH", "oxidrilo"], ["sodio"], ["agua"], ["azufre"], ["acético"], ["carbónico"]]))

# ---------------- CAPÍTULO 5 · Reacciones químicas ----------------
add(10, 5, "match", "CLASIFICACIÓN DE REACCIONES QUÍMICAS", "Ejercicio de emparejamiento",
    "Desplegá las opciones de la derecha y elegí la respuesta correcta.",
    match([("a) Un ácido y una base reaccionan y se forman una sal y agua.", "REACCIONES DE NEUTRALIZACIÓN"),
           ("b) Varias sustancias sencillas se unen para formar una más compleja.", "REACCIONES DE SÍNTESIS"),
           ("c) Una sustancia compleja se transforma en dos o más sustancias más sencillas.", "REACCIONES DE DESCOMPOSICIÓN"),
           ("d) Absorben calor del ambiente.", "REACCIONES ENDOTÉRMICAS"),
           ("e) Liberan calor.", "REACCIONES EXOTÉRMICAS"),
           ("f) Transcurren en un solo sentido hasta que se consume el reactivo que está en defecto.", "REACCIONES IRREVERSIBLES"),
           ("g) Se representan con dos flechas de sentidos opuestos.", "REACCIONES REVERSIBLES"),
           ("h) Combustible + oxígeno → sustancia carbonada + agua + energía.", "REACCIONES DE COMBUSTIÓN")],
          ["REACCIONES DE SÍNTESIS", "REACCIONES DE DESCOMPOSICIÓN", "REACCIONES DE NEUTRALIZACIÓN", "REACCIONES DE COMBUSTIÓN",
           "REACCIONES ENDOTÉRMICAS", "REACCIONES EXOTÉRMICAS", "REACCIONES REVERSIBLES", "REACCIONES IRREVERSIBLES"]))

add(11, 5, "cloze", "REACTIVOS Y PRODUCTOS",
    "En las siguientes frases, que describen diferentes reacciones químicas, identificá cuáles son los reactivos y cuáles son los productos.",
    "En los espacios en blanco completá con una R si se trata de un reactivo o una P si se trata de un producto.",
    cloze("a) En la combustión del metano, el metano y el oxígeno reaccionan y se forman dióxido de carbono, agua y energía.\n - Metano {{1}}\n - Oxígeno {{2}}\n - Dióxido de carbono {{3}}\n - Agua {{4}}\n\n"
          "b) Un antiácido con hidróxido de aluminio neutraliza el ácido clorhídrico del estómago y se forman cloruro de aluminio y agua.\n - Hidróxido de aluminio {{5}}\n - Ácido clorhídrico {{6}}\n - Cloruro de aluminio {{7}}\n - Agua {{8}}\n\n"
          "c) Al calentar el óxido de mercurio se descompone en mercurio y oxígeno.\n - Óxido de mercurio {{9}}\n - Mercurio {{10}}\n - Oxígeno {{11}}\n\n"
          "d) El hidrógeno y el yodo se combinan y forman yoduro de hidrógeno.\n - Hidrógeno {{12}}\n - Yodo {{13}}\n - Yoduro de hidrógeno {{14}}\n\n"
          "e) La picadura de una hormiga (ácido fórmico) se neutraliza con amoníaco y se obtienen una sal y agua.\n - Ácido fórmico {{15}}\n - Amoníaco {{16}}\n - Sal {{17}}\n - Agua {{18}}",
          [["R", "r"], ["R", "r"], ["P", "p"], ["P", "p"], ["R", "r"], ["R", "r"], ["P", "p"], ["P", "p"], ["R", "r"], ["P", "p"], ["P", "p"],
           ["R", "r"], ["R", "r"], ["P", "p"], ["R", "r"], ["R", "r"], ["P", "p"], ["P", "p"]]))

add(12, 5, "cloze", "ÁTOMOS EN UNA FÓRMULA", "Rellenar los espacios en blanco",
    "Completá en cada espacio el número de átomos que corresponda.",
    cloze("1- En una molécula de HNO₃ hay {{1}} átomo de hidrógeno, {{2}} átomo de nitrógeno y {{3}} átomos de oxígeno.\n\n"
          "2- En una unidad fórmula de Al(OH)₃ hay {{4}} átomo de aluminio, {{5}} átomos de oxígeno y {{6}} átomos de hidrógeno.\n\n"
          "3- En una unidad fórmula de Ca(NO₃)₂ hay {{7}} átomo de calcio, {{8}} átomos de nitrógeno y {{9}} átomos de oxígeno.\n\n"
          "4- En una unidad fórmula de Fe₂(SO₄)₃ hay {{10}} átomos de hierro, {{11}} átomos de azufre y {{12}} átomos de oxígeno.\n\n"
          "5- En 3 moléculas de H₂O hay {{13}} átomos de hidrógeno y {{14}} átomos de oxígeno.\n\n"
          "6- En una unidad fórmula de NaHCO₃ hay {{15}} átomo de sodio, {{16}} átomo de hidrógeno, {{17}} átomo de carbono y {{18}} átomos de oxígeno.",
          [["1"], ["1"], ["3"], ["1"], ["3"], ["3"], ["1"], ["2"], ["6"], ["2"], ["3"], ["12"], ["6"], ["3"], ["1"], ["1"], ["1"], ["3"]]))

# ---------------- CAPÍTULO 6 · Química orgánica ----------------
def build_cross():
    words = [("AMINOACIDOS", "Monómeros que forman las proteínas."),
             ("ALMIDON", "Polisacárido de reserva de energía en los vegetales."),
             ("GLUCOGENO", "Polisacárido de reserva de energía en las células animales."),
             ("CELULOSA", "Polisacárido que forma la pared celular de los vegetales."),
             ("POLIMEROS", "Moléculas muy grandes formadas por la unión de muchas moléculas pequeñas, llamadas monómeros."),
             ("NUCLEOTIDOS", "Monómeros de los ácidos nucleicos."),
             ("INSULINA", "Proteína reguladora que controla el nivel de azúcar en la sangre."),
             ("FRUCTOSA", "Monosacárido presente en la miel y en las frutas."),
             ("CONCATENACION", "Capacidad del carbono de unirse a otros carbonos formando cadenas largas."),
             ("HIDROCARBUROS", "Compuestos que contienen sólo carbono e hidrógeno."),
             ("ALCOHOL", "Función orgánica oxigenada cuyo grupo funcional es –OH.")]
    best = None
    for seed in range(4000):
        rnd = random.Random(seed); order = words[:]; rnd.shuffle(order)
        order.sort(key=lambda w: -len(w[0]) if seed % 2 else 0)
        grid = {}; placed = []
        def fits(w, r, c, dr, dc):
            n = 0
            if (r - dr, c - dc) in grid or (r + dr * len(w), c + dc * len(w)) in grid: return -1
            for i, ch in enumerate(w):
                p = (r + dr * i, c + dc * i); g = grid.get(p)
                if g is not None:
                    if g != ch: return -1
                    n += 1
                else:
                    for q in ((p[0] + dc, p[1] + dr), (p[0] - dc, p[1] - dr)):
                        if q in grid: return -1
            return n
        def put(w, r, c, dr, dc, clue):
            for i, ch in enumerate(w): grid[(r + dr * i, c + dc * i)] = ch
            placed.append((w, r, c, dr, dc, clue))
        w0, cl0 = order[0]; put(w0, 0, 0, 0, 1, cl0)
        for w, cl in order[1:]:
            cands = []
            for (pr, pc), g in list(grid.items()):
                for i, ch in enumerate(w):
                    if ch != g: continue
                    for dr, dc in ((1, 0), (0, 1)):
                        r, c = pr - dr * i, pc - dc * i
                        n = fits(w, r, c, dr, dc)
                        if n >= 1: cands.append((n, rnd.random(), r, c, dr, dc))
            if cands:
                cands.sort(reverse=True); _, _, r, c, dr, dc = cands[0]; put(w, r, c, dr, dc, cl)
        rs = [p[0] for p in grid]; cs = [p[1] for p in grid]
        area = (max(rs) - min(rs) + 1) * (max(cs) - min(cs) + 1)
        score = (len(placed), -area)
        if best is None or score > best[0]: best = (score, dict(grid), list(placed))
    _, grid, placed = best
    r0 = min(p[0] for p in grid); c0 = min(p[1] for p in grid)
    H = max(p[0] for p in grid) - r0 + 1; W = max(p[1] for p in grid) - c0 + 1
    G = [["" for _ in range(W)] for _ in range(H)]
    for (r, c), ch in grid.items(): G[r - r0][c - c0] = ch
    starts = sorted({(p[1] - r0, p[2] - c0) for p in placed}); num = {s: i + 1 for i, s in enumerate(starts)}
    across, down = [], []
    for w, r, c, dr, dc, clue in placed:
        e = {"n": num[(r - r0, c - c0)], "clue": clue, "answer": w, "row": r - r0, "col": c - c0}
        (down if dr else across).append(e)
    across.sort(key=lambda e: e["n"]); down.sort(key=lambda e: e["n"])
    return {"grid": G, "across": across, "down": down}, len(placed)
cross, nplaced = build_cross()
add(13, 6, "cross", "BIOMOLÉCULAS Y QUÍMICA DEL CARBONO", "Resolvé el crucigrama.", "Escribí una letra por casillero, sin tildes.", cross)

add(14, 6, "quiz", "COMPUESTOS ORGÁNICOS", "Indicar si las siguientes afirmaciones son verdaderas o falsas", "Para cada frase seleccioná VERDADERO o FALSO.",
    {"questions": [
        vf("Los compuestos orgánicos contienen siempre carbono y, en casi todos los casos, hidrógeno.", True),
        vf("Los carbonatos y los óxidos simples de carbono, como el CO₂, se consideran compuestos inorgánicos.", True, "La guía los clasifica como inorgánicos."),
        vf("La mayoría de las sustancias orgánicas se disuelve muy bien en agua.", False, "La mayoría no tiene afinidad por el agua, sobre todo con más de cinco átomos de carbono."),
        vf("Las sustancias orgánicas conducen la electricidad igual que las iónicas.", False, "No conducen la electricidad."),
        vf("Al calentar azúcar queda un residuo de carbono porque las sustancias orgánicas se descomponen por el calor.", True),
        vf("El vinagre y la madera son materiales orgánicos; la sal de mesa y el vidrio son inorgánicos.", True),
        vf("Los hidrocarburos contienen carbono, hidrógeno y oxígeno.", False, "Contienen solo carbono e hidrógeno."),
        vf("Los compuestos con el mismo grupo funcional forman una función química y muestran propiedades parecidas.", True),
        vf("Hasta principios del siglo XIX se creía que las sustancias orgánicas solo podían producirlas los seres vivos, por una 'fuerza vital'.", True)]})

add(15, 6, "quiz", "MOLÉCULAS ORGÁNICAS Y GRUPOS FUNCIONALES", "Ejercicio de opción múltiple", "Para cada frase seleccioná la única respuesta correcta.",
    {"questions": [
        mc("El grupo funcional de los alcoholes es…", "–OH", ["–COOH", "–CHO", "–CO–"], "–COOH: ácidos. –CHO: aldehídos. –CO–: cetonas.", True),
        mc("El ácido acético del vinagre tiene el grupo funcional…", "–COOH", ["–CHO", "–COO–", "–O–"], "–COO– es de los ésteres.", True),
        mc("La propanona (acetona), el quitaesmalte, es un ejemplo de…", "una cetona", ["un éter", "un éster", "un aldehído"], "", True),
        mc("¿Qué función oxigenada da el aroma de frutas como la banana y la frutilla y se usa en perfumes y golosinas?", "Los ésteres", ["Los éteres", "Los aldehídos", "Los alcoholes"], "Éster ≠ éter.", True),
        mc("Si en el etano se reemplaza un hidrógeno por el grupo –OH se obtiene…", "etanol", ["etanal", "metanol", "ácido etanoico"], "El alcohol en gel es etanol.", True),
        mc("El metanal (formol) se usa para…", "conservar muestras biológicas", ["quitar el esmalte de uñas", "dar aroma a las frutas", "preparar vinagre"], "", True),
        mc("El éter etílico se usó como…", "anestesia y solvente", ["conservante de alimentos", "perfume de frutas", "combustible de motores"], "", True),
        mc("Los hidrocarburos que tienen solo enlaces simples entre carbonos se llaman…", "alcanos", ["alquenos", "alquinos", "aromáticos"], "Alcanos: -ano. Alquenos: -eno (doble). Alquinos: -ino (triple).", True),
        mc("Los compuestos formados solo por C y H se llaman…", "hidrocarburos", ["aminas", "alcoholes", "amidas"], "", True)]})

add(16, 6, "match", "FUNCIONES ORGÁNICAS", "Ejercicio de emparejamiento", "Desplegá las opciones de la derecha y elegí la respuesta correcta.",
    match([("a) El etanol del alcohol en gel", "ALCOHOL"), ("b) El ácido acético del vinagre", "ÁCIDO"), ("c) La acetona, quitaesmalte", "CETONA"),
           ("d) El aroma de la banana y la frutilla", "ÉSTER"), ("e) El metanal, formol", "ALDEHÍDO"), ("f) El éter etílico, anestesia", "ÉTER"),
           ("g) El metano del gas natural", "HIDROCARBURO")],
          ["ALCOHOL", "ÁCIDO", "CETONA", "ÉSTER", "ALDEHÍDO", "ÉTER", "HIDROCARBURO"]))

add(17, 6, "quiz", "COMBUSTIÓN", "Indicá si las siguientes afirmaciones son VERDADERAS o FALSAS", "Para cada frase seleccioná VERDADERO o FALSO.",
    {"questions": [
        vf("Con poca disponibilidad de oxígeno, la combustión produce carbón (C).", True),
        vf("Con una cantidad intermedia de oxígeno, la combustión produce monóxido de carbono (CO).", True),
        vf("En la combustión completa se forman dióxido de carbono y agua.", True),
        vf("Cuanto más completa es la combustión, menor es la cantidad de energía que se obtiene.", False, "Cuanto más completa, más energía."),
        vf("2 CH₄ + 4 O₂ → 2 CO₂ + 4 H₂O + energía representa una combustión incompleta.", False, "Con mucho oxígeno es completa."),
        vf("En las tres ecuaciones de combustión del metano de la guía, a partir de 2 CH₄ siempre se forman 4 H₂O.", True),
        vf("El monóxido de carbono es un gas tóxico que inhibe la oxigenación de la sangre.", True),
        vf("El humo negro de los escapes de los vehículos está formado por finas partículas de carbono.", True),
        vf("El dióxido de carbono es uno de los principales gases de efecto invernadero.", True)]})

add(18, 6, "match", "SUSTANCIA CARBONADA DE LA COMBUSTIÓN", "Ejercicio de emparejamiento", "Desplegá las opciones de la derecha y elegí la respuesta correcta.",
    match([("a) Se forma cuando hay gran disponibilidad de oxígeno.", "Dióxido de carbono (CO₂)"),
           ("b) Se forma cuando hay poco oxígeno y queda un residuo negro sólido.", "Carbón (C)"),
           ("c) Es el gas tóxico que puede producir un brasero en un ambiente mal ventilado.", "Monóxido de carbono (CO)"),
           ("d) Son las partículas finas del humo negro de los escapes.", "Carbón (C)"),
           ("e) Es uno de los principales gases de efecto invernadero.", "Dióxido de carbono (CO₂)"),
           ("f) Se forma con una cantidad intermedia de oxígeno.", "Monóxido de carbono (CO)")],
          ["Dióxido de carbono (CO₂)", "Monóxido de carbono (CO)", "Carbón (C)"]))

add(19, 6, "quiz", "BIOMOLÉCULAS", "Ejercicio de opción múltiple", "Para cada frase seleccioná la única respuesta correcta.",
    {"questions": [
        mc("¿Qué biomolécula contiene C, H, O, N y P?", "Los ácidos nucleicos", ["Las proteínas", "Los lípidos", "Los glúcidos"], "Proteínas: C, H, O, N. Lípidos y glúcidos: C, H, O.", True),
        mc("¿Qué polisacárido forma la pared celular de los vegetales?", "La celulosa", ["El almidón", "El glucógeno", "La glucosa"], "Almidón: reserva vegetal. Glucógeno: reserva animal.", True),
        mc("¿Qué polisacárido usan las células animales como reserva de glucosa?", "El glucógeno", ["El almidón", "La celulosa", "La sacarosa"], "", True),
        mc("Los monómeros de las proteínas son los…", "aminoácidos", ["nucleótidos", "monosacáridos", "triglicéridos"], "", True),
        mc("Los monómeros de los ácidos nucleicos son los…", "nucleótidos", ["aminoácidos", "monosacáridos", "ácidos grasos"], "", True),
        mc("¿Cuáles son vitaminas liposolubles?", "A, D, E y K", ["El complejo B y la C", "Solo la C", "Solo las del complejo B"], "Las hidrosolubles (B y C) se destruyen con la cocción.", True),
        mc("La hemoglobina es una proteína que…", "transporta oxígeno en los glóbulos rojos", ["controla el nivel de azúcar en sangre", "forma las uñas y el pelo", "acelera las reacciones químicas"], "", True),
        mc("La insulina es una proteína con función…", "reguladora", ["estructural", "de transporte", "enzimática"], "Controla el nivel de azúcar en sangre.", True),
        mc("El colágeno, la queratina y la elastina son proteínas…", "estructurales", ["enzimáticas", "reguladoras", "de transporte"], "", True),
        mc("El azúcar que forma los nucleótidos del ARN es la…", "ribosa", ["desoxirribosa", "glucosa", "sacarosa"], "ADN: desoxirribosa. ARN: ribosa.", True),
        mc("En la doble hélice del ADN, la timina se aparea con la…", "adenina", ["citosina", "guanina", "uracilo"], "A–T y C–G.", True)]})

add(20, 6, "quiz", "LÍPIDOS, GLÚCIDOS Y ÁCIDOS NUCLEICOS", "Indicar si las siguientes afirmaciones son verdaderas o falsas", "Para cada frase seleccioná VERDADERO o FALSO.",
    {"questions": [
        vf("Los lípidos no forman polímeros.", True),
        vf("El colesterol interviene en la formación de la vitamina D.", True),
        vf("Los triglicéridos son el material de reserva energética más común.", True),
        vf("Los monosacáridos y los disacáridos se disuelven en agua.", True),
        vf("La celulosa es una reserva de energía de las plantas.", False, "Cumple función estructural; la reserva vegetal es el almidón."),
        vf("Los ácidos nucleicos son polímeros formados por nucleótidos.", True),
        vf("El ARN tiene dos cadenas enfrentadas que forman una doble hélice.", False, "Eso es el ADN; el ARN tiene una sola cadena."),
        vf("El ARN contiene uracilo en lugar de timina.", True),
        vf("Las vitaminas hidrosolubles se acumulan en el tejido adiposo.", False, "Las que se acumulan son las liposolubles."),
        vf("Los aceites son triglicéridos líquidos a temperatura ambiente y las grasas son sólidas.", True),
        vf("Las macrobiomoléculas pueden tener más de 100.000 átomos.", True)]})

add(21, 6, "cloze", "BIOMOLÉCULAS", "Rellenar los espacios en blanco", "Completá la palabra que falta. Las tildes y las mayúsculas no cuentan.",
    cloze("1- Los hidratos de carbono contienen carbono, hidrógeno y {{1}}.\n\n"
          "2- El azúcar común o {{2}} es un disacárido formado por dos {{3}}.\n\n"
          "3- La reserva de glucosa de los vegetales es el {{4}} y la de los animales es el {{5}}.\n\n"
          "4- Las proteínas están formadas por unidades llamadas {{6}}; la proteína de los glóbulos rojos que transporta oxígeno es la {{7}}.\n\n"
          "5- Los monómeros de los ácidos nucleicos son los {{8}}: cada uno tiene un azúcar de cinco carbonos, una base nitrogenada y un grupo {{9}}.\n\n"
          "6- En el ADN el azúcar es la {{10}} y la base que se aparea con la guanina es la {{11}}.",
          [["oxígeno"], ["sacarosa"], ["monosacáridos", "azúcares simples"], ["almidón"], ["glucógeno"], ["aminoácidos"], ["hemoglobina"],
           ["nucleótidos"], ["fosfato"], ["desoxirribosa"], ["citosina"]]))

json.dump(EX, open("/home/user/mi-proyecto-cloude/data/parte2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(EX), "ejercicios; crucigrama:", nplaced, "de 11 palabras;", len(cross["grid"]), "x", len(cross["grid"][0]))
