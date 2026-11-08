#!/bin/sh
# Aplica los seis parches, en orden, sobre una copia de la versión viva.  Uso: sh aplicar-todo.sh <vivo.html> <salida.html>
set -e
cp "$1" "$2"
python3 -I parche-sincalc.py "$2"
python3 -I parche-sin-cap7.py "$2"
python3 -I parche-ortografia.py "$2" leer-la-consigna/plantilla.html
python3 -I parche-recorregir.py "$2" leer-la-consigna/plantilla.html leer-la-consigna/integrar-en-entrenador.py
python3 -I inyectar-figuras.py "$2"
python3 -I parche-plan.py "$2"
