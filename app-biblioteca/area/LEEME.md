# Pestaña «Área» de la app Biblioteca de Adrián

El 15/11/2026 se publicó en el artefacto una pestaña «Área» que lista y abre los archivos de `areas/guiones-redes-sociales/`.

- `ver-area.js`: la función que reemplaza al cartel «Todavía no está construida» en `index.html`.
- `generar-areas.py`: arma `areas-0.json` con el contenido de los archivos.

**Importante:** si el generador local de la app vuelve a publicar `index.html`, este cambio se pisa. Para conservarlo, hay que copiar `ver-area.js` dentro de la plantilla del generador y publicar `areas-0.json` junto con el resto de los archivos.

Para sumar otras áreas, agregar más entradas a la lista `areas` del JSON: la pestaña muestra un botón por área cuando hay más de una.
