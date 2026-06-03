#!/usr/bin/env bash
# ============================================================
#  SessionStart hook — El Diario de Vicho
#  Deja git listo para PUBLICAR en main sin intervención manual.
#  Se ejecuta solo al arrancar cada sesión de Claude Code.
# ============================================================
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

# Identidad de los commits (para que GitHub los marque como verificados)
git config user.name  "Claude"                 2>/dev/null
git config user.email "noreply@anthropic.com"  2>/dev/null

# Autenticación para el push.
if [ -n "$GH_PAT" ]; then
  # Vía token: directa a github.com, no depende del proxy de la sesión.
  git remote set-url origin "https://${GH_PAT}@github.com/vsuareeez/diario-vicho.git" 2>/dev/null
  echo "[diario] OK: publicación lista vía GH_PAT. Para publicar: git push origin HEAD:main"
else
  echo "[diario] AVISO: GH_PAT no está definido. Se intentará el proxy de la sesión (origin actual)."
  echo "[diario] Si el push da 403/permiso denegado, define GH_PAT en las variables de entorno del entorno, o activa el permiso de escritura de la GitHub App."
fi
exit 0
