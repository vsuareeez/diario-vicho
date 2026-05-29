# ============================================================
#  Agrega Claude Cowork al arranque automático de Windows
#  Ejecutar una sola vez (no necesita ser administrador)
# ============================================================

$startup = [System.Environment]::GetFolderPath("Startup")
$shortcut = Join-Path $startup "Claude Cowork.lnk"

# Busca el ejecutable de Claude en las ubicaciones típicas
$candidates = @(
    "$env:LOCALAPPDATA\Programs\claude\Claude.exe",
    "$env:LOCALAPPDATA\Programs\Claude\Claude.exe",
    "$env:ProgramFiles\Claude\Claude.exe",
    "$env:ProgramFiles (x86)\Claude\Claude.exe"
)

$exe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $exe) {
    Write-Host "❌ No se encontró Claude.exe. Búscalo manualmente en:" -ForegroundColor Red
    Write-Host "   %LOCALAPPDATA%\Programs\" -ForegroundColor Yellow
    Write-Host "   y crea un acceso directo en la carpeta:" -ForegroundColor Yellow
    Write-Host "   $startup" -ForegroundColor Cyan
    exit 1
}

$shell = New-Object -ComObject WScript.Shell
$lnk   = $shell.CreateShortcut($shortcut)
$lnk.TargetPath     = $exe
$lnk.WorkingDirectory = Split-Path $exe
$lnk.WindowStyle    = 7   # 7 = minimizado al arrancar
$lnk.Description    = "Claude Cowork — inicio automático"
$lnk.Save()

Write-Host ""
Write-Host "✅ Listo. Claude Cowork arrancará minimizado cada vez que inicies Windows." -ForegroundColor Green
Write-Host "   Acceso directo creado en:" -ForegroundColor Gray
Write-Host "   $shortcut" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Flujo diario automático:" -ForegroundColor Gray
Write-Host "   → Windows inicia  → Cowork abre minimizado" -ForegroundColor White
Write-Host "   → 07:05 AM        → Claude genera el newsletter" -ForegroundColor White
Write-Host "   → 07:30 AM        → publicar.bat sube a GitHub Pages" -ForegroundColor White
