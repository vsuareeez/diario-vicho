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

Para el push, usar el token configurado en la variable de entorno `GH_PAT`:

```bash
git remote set-url origin "https://${GH_PAT}@github.com/vsuareeez/diario-vicho.git"
git push origin main
git remote set-url origin "http://local_proxy@127.0.0.1:44585/git/vsuareeez/diario-vicho"
```

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

## Reglas HTML obligatorias
- `<h1>` para el título principal (no `<div>`)
- `onerror="this.nextElementSibling.remove();this.remove()"` en cada `<img>` para ocultar imagen Y crédito si falla
- Sin `loading="lazy"` en la primera imagen de la primera sección
- `<title>` debe incluir la fecha del día
- Imágenes: siempre verificar filename exacto en Wikimedia Commons antes de usar

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
   - genera la lista de chips (número y fecha desde el nombre del archivo),
   - la inserta en la edición nueva,
   - regenera `index.html` como copia de la edición más reciente.
4. `python3 build.py --check` no escribe: falla si algo quedó desincronizado (útil antes del push).

> `index.html` **se genera**, no se edita a mano. Si hay que corregir el contenido
> de la edición actual, editar el archivo en `ediciones/` y volver a correr `build.py`.
> Para etiquetas especiales de un chip (p. ej. `(tarde)`), añadir la entrada al dict
> `ETIQUETAS` en `build.py`.
