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

## Archivos a actualizar en cada edición
1. `index.html` → edición actual
2. `ediciones/YYYY-MM-DD.html` (o `-v2`, `-v3`...) → copia de archivo
3. Sección `.archive` en ambos archivos → agregar chip de la edición nueva
