# ============================================================
#  Registrar tarea de Windows: publicar El Diario de Vicho
#  Ejecuta publicar.bat cada día a las 07:30 AM
#  Correr una sola vez como Administrador
# ============================================================

$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Definition
$bat     = Join-Path $carpeta "publicar.bat"
$nombre  = "DiarioVicho-Publicar"

$accion  = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$bat`"" -WorkingDirectory $carpeta
$trigger = New-ScheduledTaskTrigger -Daily -At "07:30AM"
$config  = New-ScheduledTaskSettingsSet `
               -StartWhenAvailable `
               -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
               -MultipleInstances IgnoreNew

# Corre con el usuario actual, sin necesitar contraseña visible
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken -RunLevel Highest

# Eliminar si ya existe
Unregister-ScheduledTask -TaskName $nombre -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName   $nombre `
    -Action     $accion `
    -Trigger    $trigger `
    -Settings   $config `
    -Principal  $principal `
    -Description "Publica El Diario de Vicho en GitHub Pages cada mañana a las 07:30"

Write-Host ""
Write-Host "✅ Tarea '$nombre' registrada." -ForegroundColor Green
Write-Host "   Se ejecutará todos los días a las 07:30 AM." -ForegroundColor Cyan
Write-Host "   Para verla: Programador de tareas > Biblioteca > $nombre" -ForegroundColor Gray
