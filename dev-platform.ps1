# Ejecutar desde la raíz: ./dev-platform.ps1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$srcRoot = Join-Path $PSScriptRoot 'src'

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 8000)
try { $listener.Start() }
catch { throw 'El puerto 8000 está ocupado. Detén el servidor existente y vuelve a ejecutar ./dev-platform.ps1.' }
finally { $listener.Stop() }

Write-Host 'Preparando plataforma, dependencias y migraciones...'
& (Join-Path $srcRoot 'scripts/setup-platform.ps1')

$env:PYTHONUTF8 = '1'
Push-Location $srcRoot
try {
    Write-Host 'Plataforma: http://127.0.0.1:8000/'
    Write-Host 'Recarga automática activada. Ctrl+C detiene la plataforma.'
    & (Join-Path $srcRoot '.venv/Scripts/python.exe') manage.py runserver 127.0.0.1:8000
    if ($LASTEXITCODE -ne 0) { throw 'La plataforma terminó con error.' }
} finally { Pop-Location }
