@echo off
REM ============================================================
REM  Publicar "El Diario de Vicho" en GitHub
REM  Hace commit y push de los cambios de la carpeta a GitHub.
REM  Requiere: Git para Windows instalado y autenticado una vez.
REM ============================================================

cd /d "%~dp0"

REM Fecha para el mensaje del commit
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set HOY=%%i

git add -A
git commit -m "Edicion %HOY%" 2>nul
if %errorlevel%==0 (
  echo Cambios confirmados. Subiendo a GitHub...
) else (
  echo No habia cambios nuevos que confirmar.
)
git push

echo.
echo Listo. Si no hubo errores, tu sitio se actualizara en 1-2 minutos.
