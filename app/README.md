# Ejercicios interactivos – Módulo 2

App web sin dependencias. Abrir `app/ejercicios-modulo2.html` en el navegador.

- **Parte 1:** los 15 ejercicios originales de la carpeta de Drive (cap. 3 a 7).
- **Parte 2:** 21 ejercicios nuevos (cap. 3 a 6) con los mismos formatos (opción múltiple, V/F, emparejar, completar, crucigrama) y preguntas basadas en la guía oficial.
- Puntaje por ejercicio = (aciertos − intentos fallidos previos) / total × 100. Se guarda el mejor puntaje en el navegador. No se distinguen tildes ni mayúsculas, y al comprobar se muestra la respuesta correcta.
- Fuentes: `data/exercises.json` (Parte 1), `data/make_parte2.py` → `data/parte2.json` (Parte 2). `python3 app/build.py` regenera `exercises.js`, `ejercicios-modulo2.html` y `artifact.html`.
