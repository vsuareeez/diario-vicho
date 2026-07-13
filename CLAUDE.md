# El Diario de Vicho — instrucciones para Claude

## Descripción
Newsletter diario en HTML publicado en GitHub Pages en `vsuareeez/diario-vicho`.
Una edición por día (o `.1`, `.2`... si hay varias en el mismo día).

## Flujo de trabajo — SIEMPRE push a main

Las sesiones de Claude Code en la web crean automáticamente una rama `claude/...`.
**Nunca dejar el trabajo en esa rama.** Al terminar, hacer siempre:

```bash
git checkout main
git merge claude/<nombre-rama>
git push origin main
```

Eso es todo: el hook de sesión (`.claude/diario-setup.sh`) deja `origin` en
`https://github.com/vsuareeez/diario-vicho.git` y la autenticación ya está
resuelta (el proxy de la sesión reescribe github.com y autentica el push;
fuera del sandbox, un credential helper entrega `GH_PAT`).

- **Nunca** poner `GH_PAT` dentro de una URL de remote: rompe el push no
  interactivo y el token queda impreso en errores y logs.
- **Nunca** hardcodear URLs de proxy (`127.0.0.1:<puerto>`): el puerto cambia
  en cada sesión.
- Si el push falla, restaurar la URL canónica y reintentar:
  `git remote set-url origin https://github.com/vsuareeez/diario-vicho.git`

## Numeración de ediciones
- Primera edición del día: `#N` → archivo `ediciones/YYYY-MM-DD.html`
- Segunda edición del mismo día: `#N.1` → archivo `ediciones/YYYY-MM-DD-v2.html`
- Tercera: `#N.2` → `ediciones/YYYY-MM-DD-v3.html`

## Estructura de cada edición
Cinco secciones con colores CSS fijos:
- **IA / Tech** → `.ai` (púrpura `#8b7bff`)
- **Finanzas** → `.fin` (verde `#46d08a`)
- **Deportes** → `.sport` (rojo/naranja `#ff7a5c`)
- **Geografía e Historia** → `.geo` (azul claro `#3fb6d6`)
- **Idiomas** → `.lang` (amarillo `#ffcf6b`)

## Reglas HTML obligatorias (`build.py --check` las hace cumplir)
- `<h1>` para el título principal (no `<div>`)
- `onerror="this.nextElementSibling.remove();this.remove()"` en cada `<img>` para ocultar imagen Y crédito si falla
- El `<span class="credit">` va **inmediatamente después** de su `<img>` (el onerror borra al hermano siguiente)
- Sin `loading="lazy"` en la primera imagen; **con** `loading="lazy"` en todas las demás
- `alt` descriptivo en cada `<img>`
- `<title>` debe incluir la fecha del día ("12 de julio de 2026")
- URLs de imagen: `Special:FilePath/<archivo>?width=1200`

## Imágenes — encuadre obligatorio con `object-position`
El recuadro `.photo` es una franja muy ancha (~3.3:1) y `object-fit:cover`
recorta por el **centro vertical**: en cualquier foto vertical eso muestra el
pecho y corta la cara. Por eso **cada `<img>` lleva
`style="object-position:50% Y%"`** elegido según el tipo de foto
(`build.py --check` lo exige):

| Tipo de foto | Y |
|---|---|
| Retrato / busto / cara | **20–25%** |
| Persona de cuerpo entero | **15%** |
| Edificio, monumento | **30–35%** |
| Paisaje, estadio, sala amplia, horizontal genérica | **40–50%** |

Preferir fotos **horizontales** cuando haya opción: sufren mucho menos recorte.

Verificación del filename: `commons.wikimedia.org` está **bloqueado por la red
del sandbox** (no intentar curl ni WebFetch: da 403). Verificar el nombre
exacto con WebSearch (`site:commons.wikimedia.org File:...`) y deducir la
orientación/composición de la descripción del resultado. Nunca inventar
nombres de archivo.

## Presupuesto de contenido — OBLIGATORIO (`build.py --check` lo hace cumplir)
El diario se infló edición a edición sin que nadie lo decidiera: de ~2.000 palabras
(ediciones #7–#8, el patrón bueno) a ~5.900 (9 jul). El patrón a imitar es la
edición **#7 (4 jun 2026)**: mismo diseño, mismas 5 secciones, pero conciso.
Límites duros (validados por `build.py` en la edición nueva; `--check` falla si se pasan):

| Elemento | Límite |
|---|---|
| Edición completa | **2.400 palabras** (sin contar el archivo de chips) |
| Cada `<section>` | **450 palabras** |
| Cada `<li>` | **110 palabras** (una viñeta = 2-3 frases, no 3 párrafos) |
| Cada `.lead` | **60 palabras** |
| Intro bajo el masthead | **30 palabras** (1-2 frases) |
| Citas `.pull` | **máx 2 por edición, 50 palabras cada una** |
| `.tagline` | **45 caracteres, máx 2 segmentos** con ` · ` |

Principios: **una noticia por sección**, no tres. Cortar datos secundarios, no
comprimirlos con abreviaturas. Si algo no cabe, va en la edición de mañana.

## Regla del `tagline` (la línea bajo cada título de sección)
El `.tagline` es una **etiqueta, no un resumen**. Se descontroló con el tiempo
(pasó de "Tecnología · Lo importante" a frases enteras con 3-4 datos). Mantenerlo corto:
- Máximo **~40 caracteres** y **máximo 2 segmentos** separados por ` · `.
- 2 a 4 palabras. Categoría/tema, no la noticia. La noticia va en el cuerpo, no aquí.
- ✅ Bien: `Tecnología · IA`, `Wall Street`, `Fútbol · Mundial`, `Efeméride`
- ❌ Mal: `Seúl, 3ª oficina Asia-Pacífico · LG CNS · Samsung SDS · Fable 5 sigue suspendido`

## Archivos a actualizar en cada edición
1. Crear `ediciones/YYYY-MM-DD.html` (o `-v2`, `-v3`...) con el contenido del día.
2. Justo antes del `<footer>`, incluir los marcadores del archivo (vacíos):
   ```html
   <!-- ARCHIVE:START -->
   <!-- ARCHIVE:END -->
   ```
   **No escribir los chips a mano.**
3. Ejecutar `python3 build.py`. El script:
   - genera la lista de chips agrupada por mes (número y fecha desde el nombre del archivo),
   - la inserta en la edición nueva,
   - regenera `index.html` como copia de la edición más reciente,
   - avisa si la edición se pasa del presupuesto de contenido.
4. **Obligatorio antes del push:** `python3 build.py --check`. Falla si algo quedó
   desincronizado, **si la edición nueva viola el presupuesto de contenido** o
   **si incumple las reglas HTML** (h1, onerror, crédito hermano, lazy, alt,
   fecha en el título, object-position). Si falla por presupuesto: recortar la
   edición (no abreviar: quitar datos secundarios) y volver a correr `build.py`.

> `index.html` **se genera**, no se edita a mano. Si hay que corregir el contenido
> de la edición actual, editar el archivo en `ediciones/` y volver a correr `build.py`.
> Para etiquetas especiales de un chip (p. ej. `(tarde)`), añadir la entrada al dict
> `ETIQUETAS` en `build.py`.
