#!/usr/bin/env python3
"""
Generador de El Diario de Vicho.

Una sola fuente de verdad: los archivos de `ediciones/`.
Este script escanea esa carpeta, calcula el numero (#N / #N.k) y la fecha de
cada edicion a partir del nombre del archivo, y con eso:

  1. Regenera el bloque de "Ediciones anteriores" (los chips) dentro de la
     edicion mas reciente, entre los marcadores ARCHIVE:START / ARCHIVE:END.
  2. Regenera `index.html` como copia de esa edicion, con las rutas de los
     chips apuntando a `ediciones/...` en vez de `../ediciones/...`.

Asi la lista de ediciones deja de escribirse a mano en dos sitios: se genera.

Uso:
    python3 build.py            # regenera y escribe los archivos
    python3 build.py --check    # no escribe; falla si algo esta desincronizado

Solo usa la biblioteca estandar. No toca las ediciones antiguas (quedan
congeladas): solo reescribe la mas reciente y `index.html`.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDICIONES = ROOT / "ediciones"
INDEX = ROOT / "index.html"

MESES = ["ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "sep", "oct", "nov", "dic"]

# Etiquetas extra opcionales por archivo (p. ej. una 2a edicion "de tarde").
# La clave es el nombre del archivo dentro de ediciones/.
ETIQUETAS = {
    "2026-06-15-v2.html": "(tarde)",
}

NOMBRE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:-v(\d+))?\.html$")
MARCADORES_RE = re.compile(
    r"<!-- ARCHIVE:START -->.*?<!-- ARCHIVE:END -->", re.DOTALL)


def descubrir_ediciones():
    """Devuelve la lista de ediciones ordenada cronologicamente, cada una como
    un dict con: file, fecha (str legible), num (#N / #N.k), etiqueta."""
    items = []
    for path in EDICIONES.glob("*.html"):
        m = NOMBRE_RE.match(path.name)
        if not m:
            continue
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        version = int(m.group(4)) if m.group(4) else 1
        items.append({
            "file": path.name,
            "orden": (y, mo, d, version),
            "fecha": f"{d} {MESES[mo - 1]} {y}",
            "clave_dia": (y, mo, d),
        })

    if not items:
        sys.exit("No hay ediciones en ediciones/*.html")

    items.sort(key=lambda x: x["orden"])

    # Numeracion: #N incrementa por dia distinto; ediciones extra del mismo dia
    # son #N.1, #N.2, ...
    n = 0
    dia_prev = None
    sub = 0
    for it in items:
        if it["clave_dia"] != dia_prev:
            n += 1
            sub = 0
            dia_prev = it["clave_dia"]
        else:
            sub += 1
        it["num"] = f"#{n}" if sub == 0 else f"#{n}.{sub}"
        it["etiqueta"] = ETIQUETAS.get(it["file"], "")
    return items


def construir_archivo(ediciones, prefijo):
    """HTML del bloque .archive completo, con las rutas usando `prefijo`."""
    lineas = []
    for i, ed in enumerate(ediciones):
        es_actual = i == len(ediciones) - 1
        clase = "chip today" if es_actual else "chip"
        texto = f'{ed["num"]} · {ed["fecha"]}'
        if ed["etiqueta"]:
            texto += f' {ed["etiqueta"]}'
        if es_actual:
            texto += " · actual"
        lineas.append(
            f'      <a class="{clase}" href="{prefijo}{ed["file"]}">{texto}</a>')
    chips = "\n".join(lineas)
    return (
        "  <div class=\"archive\">\n"
        "    <h3>📚 Ediciones anteriores</h3>\n"
        "    <div class=\"chips\">\n"
        f"{chips}\n"
        "    </div>\n"
        "  </div>"
    )


def reemplazar_bloque(texto, bloque, origen):
    envuelto = f"<!-- ARCHIVE:START -->\n{bloque}\n  <!-- ARCHIVE:END -->"
    nuevo, n = MARCADORES_RE.subn(lambda _m: envuelto, texto)
    if n == 0:
        sys.exit(
            f"No se encontraron los marcadores ARCHIVE:START/END en {origen}.\n"
            "Toda edicion debe incluir, justo antes del <footer>:\n"
            "  <!-- ARCHIVE:START -->\n  <!-- ARCHIVE:END -->")
    return nuevo


def main():
    ap = argparse.ArgumentParser(description="Genera index.html y el archivo de ediciones.")
    ap.add_argument("--check", action="store_true",
                    help="No escribe; sale con codigo 1 si algo esta desincronizado.")
    args = ap.parse_args()

    ediciones = descubrir_ediciones()
    reciente = ediciones[-1]
    reciente_path = EDICIONES / reciente["file"]

    texto_reciente = reciente_path.read_text(encoding="utf-8")
    bloque_ed = construir_archivo(ediciones, "../ediciones/")
    nuevo_reciente = reemplazar_bloque(texto_reciente, bloque_ed, reciente_path.name)

    bloque_index = construir_archivo(ediciones, "ediciones/")
    nuevo_index = reemplazar_bloque(nuevo_reciente, bloque_index, "index.html")

    index_actual = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""

    if args.check:
        desync = []
        if nuevo_reciente != texto_reciente:
            desync.append(reciente["file"])
        if nuevo_index != index_actual:
            desync.append("index.html")
        if desync:
            print("Desincronizado (corre `python3 build.py`): " + ", ".join(desync))
            sys.exit(1)
        print(f"OK · {len(ediciones)} ediciones · reciente {reciente['num']} "
              f"({reciente['fecha']})")
        return

    reciente_path.write_text(nuevo_reciente, encoding="utf-8")
    INDEX.write_text(nuevo_index, encoding="utf-8")
    print(f"Generado · {len(ediciones)} ediciones · portada = {reciente['num']} "
          f"({reciente['fecha']}) · {reciente['file']}")


if __name__ == "__main__":
    main()
