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
#
# origin queda SIEMPRE en la URL canónica de GitHub. En el sandbox de Claude
# Code web, el proxy de la sesión reescribe github.com (insteadOf que inyecta
# el entorno, con puerto que CAMBIA por sesión) y autentica el push él solo.
# Fuera del sandbox, si existe GH_PAT, un credential helper acotado a
# github.com lo entrega en el formato correcto (x-access-token:TOKEN).
#
# NUNCA incrustar el token en la URL del remote: el formato usuario-sin-
# contraseña rompe el push no interactivo ("terminal prompts disabled") y el
# token queda impreso en `git remote -v` y en los mensajes de error de git.
git remote set-url origin "https://github.com/vsuareeez/diario-vicho.git" 2>/dev/null

if [ -n "$GH_PAT" ]; then
  git config credential."https://github.com".helper \
    '!f() { echo username=x-access-token; echo "password=${GH_PAT}"; }; f' 2>/dev/null
  echo "[diario] OK: origin=github.com (proxy de sesión o GH_PAT vía credential helper)."
else
  echo "[diario] OK: origin=github.com (push vía proxy de la sesión)."
  echo "[diario] Si el push da 403, define GH_PAT o activa el permiso de escritura de la GitHub App."
fi
echo "[diario] Publicar: git checkout main && git merge <rama-claude> && git push origin main"
exit 0
