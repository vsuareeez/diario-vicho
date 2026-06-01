# 🗞️ El Diario de Vicho

> Newsletter diario generado con IA, publicado como HTML estático en GitHub Pages.

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen?logo=github)](https://vsuareeez.github.io/diario-vicho/)
[![Automatización](https://img.shields.io/badge/Automatizado-Claude%20Code%20Routines-blueviolet?logo=anthropic)](https://claude.ai/code)
[![Stack](https://img.shields.io/badge/Stack-HTML5%20%2B%20CSS3-orange?logo=html5)](https://vsuareeez.github.io/diario-vicho/)

🌐 **Sitio en vivo:** [vsuareeez.github.io/diario-vicho](https://vsuareeez.github.io/diario-vicho/)

---

## ¿Qué es?

**El Diario de Vicho** es un newsletter HTML minimalista publicado diariamente (o casi) mediante una rutina automática de Claude Code. Cada edición cubre 5 temas con una noticia relevante del día, imágenes de Wikimedia Commons y redacción en español.

No usa frameworks, no tiene JavaScript, no tiene base de datos. Solo HTML y CSS.

---

## 📰 Secciones

| Sección | Color | Contenido |
|---------|-------|-----------|
| 🤖 **IA & Tecnología** | `#7c3aed` (violeta) | Noticias de inteligencia artificial, modelos y empresas tech |
| 💹 **Finanzas** | `#059669` (verde) | Mercados, commodities, índices bursátiles |
| ⚽ **Deportes** | `#dc2626` (rojo) | Fútbol, tenis, eventos internacionales |
| 🌍 **Geografía & Historia** | `#0284c7` (celeste) | Efemérides, países, historia del día |
| 📖 **Idiomas** | `#d97706` (amarillo) | Etimologías, curiosidades del español e inglés |

---

## 🗂️ Estructura del proyecto

```
diario-vicho/
├── index.html                  # Edición activa (siempre la más reciente)
├── ediciones/
│   ├── 2026-05-28.html         # Edición #1
│   ├── 2026-05-29.html         # Edición #2
│   ├── 2026-05-30.html         # Edición #3
│   ├── 2026-05-31.html         # Edición #4
│   ├── 2026-06-01-v2.html      # Edición #4.1 (segunda del día)
│   └── ...
├── CLAUDE.md                   # Instrucciones para el agente en cada sesión
└── README.md                   # Este archivo
```

> **Convención de nombres:**
> - Primera edición del día → `YYYY-MM-DD.html` → numerada `#N`
> - Segunda edición del mismo día → `YYYY-MM-DD-v2.html` → numerada `#N.1`

---

## ⚙️ Cómo funciona la automatización

```
Claude Code Routines (trigger diario)
         │
         ▼
  Lee CLAUDE.md con instrucciones
         │
         ▼
  Genera contenido para las 5 secciones
  (noticias reales del día, sin repetir ediciones anteriores)
         │
         ▼
  Actualiza index.html + crea ediciones/YYYY-MM-DD.html
         │
         ▼
  Commit + push a main
         │
         ▼
  GitHub Pages publica automáticamente
```

### Configuración de la rutina

| Parámetro | Valor |
|-----------|-------|
| **Trigger** | Diario (horario configurado en Routines) |
| **Repositorio** | `vsuareeez/diario-vicho` |
| **Permisos requeridos** | *Allow unrestricted branch pushes* |
| **Branch de trabajo** | `main` (las ramas `claude/...` se crean automáticamente, pero siempre se fusionan a `main` al finalizar) |

---

## 📋 Reglas de generación

- **CSS reutilizado** — Las variables CSS (`--ai`, `--fin`, `--sport`, `--geo`, `--lang`) están definidas una sola vez; no se duplica el bloque `<style>` entre ediciones.
- **Sin repetición** — Cada edición verifica las anteriores para no cubrir el mismo tema dos días seguidos.
- **Contenido de respaldo** — Si no hay noticias del día, se usa una efeméride, un dato curioso o un hecho verificable.
- **Imágenes verificadas** — Solo se usan URLs de Wikimedia Commons (`Special:FilePath/nombre?width=1000`). Si la imagen falla, el atributo `onerror` la oculta junto al crédito automáticamente.
- **HTML semántico** — Cada edición tiene un `<h1>` con el nombre de la sección, `<title>` con la fecha, y sin JS ni dependencias externas.

---

## 💡 Lecciones aprendidas

- **Las tareas de archivo no son para la nube.** Scripts `.bat` y `.ps1` solo funcionan en Windows local; en Claude Code Remoto (CCR) el push usa el PAT directamente en la URL del remote.
- **Las imágenes de Wikimedia son fiables.** El formato `Special:FilePath/Nombre_Archivo.jpg?width=1000` resuelve correctamente, incluso con nombres con espacios o caracteres especiales (URL-encoded).
- **Los arreglos van en el prompt, no en el HTML.** Si una edición tiene un error (fecha incorrecta, número de edición mal), se corrige en el `index.html` directamente, sin crear archivos extra.
- **`CLAUDE.md` es la memoria del agente.** Cada vez que Claude genera una nueva edición, lo primero que lee es `CLAUDE.md` para saber las reglas, el historial y la convención del proyecto.

---

## 🛠️ Stack

| Capa | Tecnología |
|------|-----------|
| Contenido | HTML5 + CSS3 (sin frameworks) |
| Publicación | GitHub Pages |
| Automatización | [Claude Code Routines](https://claude.ai/code) |
| Imágenes | [Wikimedia Commons](https://commons.wikimedia.org/) |
| Agente | Claude (Sonnet / Opus) |

---

<p align="center">
  Hecho con ☕ y Claude · <a href="https://vsuareeez.github.io/diario-vicho/">Ver última edición</a>
</p>
