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
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EDICIONES = ROOT / "ediciones"
INDEX = ROOT / "index.html"

MESES = ["ene", "feb", "mar", "abr", "may", "jun",
         "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGO = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# El archivo se agrupa por mes con <details>/<summary>: plegable sin JS.
# Estilos inline para no depender del <style> de cada edicion (las antiguas
# estan congeladas). Solo el mes de la edicion actual queda abierto.
ESTILO_DETAILS = "margin:0 0 10px"
ESTILO_MES = ("cursor:pointer;font-size:11px;letter-spacing:.18em;"
              "text-transform:uppercase;color:var(--muted);"
              "padding:6px 0;user-select:none")
ESTILO_CHIPS_MES = "margin:8px 0 4px"

# Etiquetas extra opcionales por archivo (p. ej. una 2a edicion "de tarde").
# La clave es el nombre del archivo dentro de ediciones/.
ETIQUETAS = {
    "2026-06-15-v2.html": "(tarde)",
}

NOMBRE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:-v(\d+))?\.html$")
MARCADORES_RE = re.compile(
    r"<!-- ARCHIVE:START -->.*?<!-- ARCHIVE:END -->", re.DOTALL)

# ---------------------------------------------------------------------------
# Presupuesto de contenido (anti-inflacion).
#
# El contenido fue creciendo edicion a edicion sin que nadie lo decidiera:
# de ~2.000 palabras (ediciones #7-#8, el patron bueno) a ~5.900 (9 jul).
# Estos limites estan calibrados en las ediciones #7-#8 con algo de margen.
# Se validan solo en la edicion mas reciente (las antiguas quedan congeladas)
# y solo a partir de LINT_DESDE.
# ---------------------------------------------------------------------------
LINT_DESDE = (2026, 7, 11)
LIMITES = {
    "total": 2400,        # palabras visibles de la edicion (sin el archivo de chips)
    "seccion": 450,       # palabras por <section>
    "li": 110,            # palabras por <li> (una viñeta = 2-3 frases, no 3 parrafos)
    "lead": 60,           # palabras del parrafo .lead de cada seccion
    "intro": 30,          # palabras de la intro bajo el masthead
    "pull": 50,           # palabras por cita .pull
    "pulls_max": 2,       # citas .pull por edicion
    "tagline_chars": 45,  # caracteres por .tagline
    "tagline_segs": 2,    # segmentos separados por · en el .tagline
}


def _palabras(fragmento):
    texto = re.sub(r"<[^>]+>", " ", fragmento)
    return len(html.unescape(texto).split())


def lint_contenido(texto):
    """Valida el presupuesto de contenido de una edicion.
    Devuelve la lista de violaciones (vacia si todo bien)."""
    t = re.sub(r"<style>.*?</style>", "", texto, flags=re.DOTALL)
    t = MARCADORES_RE.sub("", t)  # el archivo de chips no cuenta
    v = []

    total = _palabras(t)
    if total > LIMITES["total"]:
        v.append(f"edicion completa: {total} palabras (max {LIMITES['total']})")

    for m in re.finditer(r"<section[^>]*>(.*?)</section>", t, re.DOTALL):
        sec = m.group(1)
        h2 = re.search(r"<h2>([^<]*)</h2>", sec)
        nombre = h2.group(1).strip() if h2 else "?"
        n = _palabras(sec)
        if n > LIMITES["seccion"]:
            v.append(f"seccion «{nombre}»: {n} palabras (max {LIMITES['seccion']})")

    lis = [_palabras(x) for x in re.findall(r"<li[^>]*>(.*?)</li>", t, re.DOTALL)]
    pasados = [n for n in lis if n > LIMITES["li"]]
    if pasados:
        v.append(f"{len(pasados)} <li> superan {LIMITES['li']} palabras "
                 f"(el mayor: {max(pasados)})")

    leads = [_palabras(x) for x in
             re.findall(r'<p class="lead">(.*?)</p>', t, re.DOTALL)]
    pasados = [n for n in leads if n > LIMITES["lead"]]
    if pasados:
        v.append(f"{len(pasados)} .lead superan {LIMITES['lead']} palabras "
                 f"(el mayor: {max(pasados)})")

    intro = re.search(r'class="intro"[^>]*>(.*?)</', t, re.DOTALL)
    if intro and _palabras(intro.group(1)) > LIMITES["intro"]:
        v.append(f"intro: {_palabras(intro.group(1))} palabras (max {LIMITES['intro']})")

    pulls = [_palabras(x) for x in
             re.findall(r'<div class="pull">(.*?)</div>', t, re.DOTALL)]
    if len(pulls) > LIMITES["pulls_max"]:
        v.append(f"{len(pulls)} citas .pull (max {LIMITES['pulls_max']})")
    for n in pulls:
        if n > LIMITES["pull"]:
            v.append(f"cita .pull de {n} palabras (max {LIMITES['pull']})")

    for tg in re.findall(r'class="tagline">([^<]*)<', t):
        tg = html.unescape(tg).strip()
        if len(tg) > LIMITES["tagline_chars"] or \
                tg.count("·") + 1 > LIMITES["tagline_segs"]:
            v.append(f"tagline demasiado largo: «{tg}» "
                     f"(max {LIMITES['tagline_chars']} chars, "
                     f"{LIMITES['tagline_segs']} segmentos)")
    return v


# El recuadro .photo es una franja ~3.3:1; object-fit:cover recorta por el
# centro vertical y decapita cualquier foto vertical. Cada <img> debe traer
# un object-position elegido a proposito (caras ~20%, edificios ~35%...).
ONERROR_OK = 'onerror="this.nextElementSibling.remove();this.remove()"'


def lint_html(texto, clave_dia):
    """Reglas de calidad HTML de la edicion (antes solo vivian en el prompt
    de la rutina y dependian de la memoria). Devuelve lista de violaciones."""
    t = re.sub(r"<style>.*?</style>", "", texto, flags=re.DOTALL)
    t = MARCADORES_RE.sub("", t)
    v = []

    if not re.search(r"<h1[\s>]", t):
        v.append("falta <h1> para el titulo principal")

    y, mo, d = clave_dia
    fecha = f"{d} de {MESES_LARGO[mo - 1].lower()} de {y}"
    titulo = re.search(r"<title>(.*?)</title>", t, re.DOTALL)
    if not titulo or fecha not in titulo.group(1):
        v.append(f"el <title> no incluye la fecha «{fecha}»")

    imgs = re.findall(r"<img\b[^>]*>", t)
    if not imgs:
        v.append("la edicion no tiene imagenes")
    for i, img in enumerate(imgs, 1):
        if ONERROR_OK not in img:
            v.append(f"img #{i}: el onerror debe borrar imagen y credito: {ONERROR_OK}")
        if "alt=" not in img:
            v.append(f"img #{i}: falta alt")
        if "object-position" not in img:
            v.append(f'img #{i}: falta style="object-position:50% Y%" (encuadre del sujeto)')
        if i == 1 and 'loading="lazy"' in img:
            v.append('img #1: no debe llevar loading="lazy" (va above the fold)')
        if i > 1 and 'loading="lazy"' not in img:
            v.append(f'img #{i}: falta loading="lazy"')

    con_credito = len(re.findall(r'<img\b[^>]*>\s*<span class="credit">', t))
    if imgs and con_credito != len(imgs):
        v.append(f'{len(imgs) - con_credito} <img> sin <span class="credit"> como '
                 "hermano inmediato (el onerror borra el hermano siguiente)")
    return v


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
    """HTML del bloque .archive completo: un <details> plegable por mes
    (solo el mes actual abierto), con las rutas usando `prefijo`."""
    mes_actual = ediciones[-1]["orden"][:2]
    lineas = []
    mes_abierto = None
    for i, ed in enumerate(ediciones):
        y, mo = ed["orden"][0], ed["orden"][1]
        if (y, mo) != mes_abierto:
            if mes_abierto is not None:
                lineas.append("    </div>\n    </details>")
            abierto = " open" if (y, mo) == mes_actual else ""
            cuantas = sum(1 for e in ediciones if e["orden"][:2] == (y, mo))
            lineas.append(f'    <details{abierto} style="{ESTILO_DETAILS}">')
            lineas.append(
                f'    <summary style="{ESTILO_MES}">{MESES_LARGO[mo - 1]} {y}'
                f' · {cuantas} ediciones</summary>')
            lineas.append(f'    <div class="chips" style="{ESTILO_CHIPS_MES}">')
            mes_abierto = (y, mo)
        es_actual = i == len(ediciones) - 1
        clase = "chip today" if es_actual else "chip"
        texto = f'{ed["num"]} · {ed["fecha"]}'
        if ed["etiqueta"]:
            texto += f' {ed["etiqueta"]}'
        if es_actual:
            texto += " · actual"
        lineas.append(
            f'      <a class="{clase}" href="{prefijo}{ed["file"]}">{texto}</a>')
    lineas.append("    </div>\n    </details>")
    cuerpo = "\n".join(lineas)
    return (
        "  <div class=\"archive\">\n"
        "    <h3>📚 Ediciones anteriores</h3>\n"
        f"{cuerpo}\n"
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

    # Presupuesto de contenido + calidad HTML: solo la edicion mas reciente
    # y solo desde LINT_DESDE (las anteriores quedan como estan).
    violaciones = []
    if reciente["clave_dia"] >= LINT_DESDE:
        violaciones = (lint_contenido(texto_reciente)
                       + lint_html(texto_reciente, reciente["clave_dia"]))
    for msg in violaciones:
        print(f"⚠️  {msg}")

    if args.check:
        desync = []
        if nuevo_reciente != texto_reciente:
            desync.append(reciente["file"])
        if nuevo_index != index_actual:
            desync.append("index.html")
        if desync:
            print("Desincronizado (corre `python3 build.py`): " + ", ".join(desync))
            sys.exit(1)
        if violaciones:
            print(f"FALLA presupuesto/calidad HTML en {reciente['file']}: "
                  "corregir la edicion y volver a correr build.py.")
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
