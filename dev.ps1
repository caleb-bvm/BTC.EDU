# Ejecutar desde la raíz: ./dev.ps1
# Inicia todo lo necesario según COMMERCE_PAYMENT_MODE en src/.local/commerce.env:
#   regtest: red Polar, LNbits regtest (5001) y la plataforma (8000).
#   fake o sin configurar: LNbits con FakeWallet (5000) y la plataforma (8000).
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$srcRoot = Join-Path $PSScriptRoot 'src'
$lnbitsProcess = $null

$mode = 'fake'
$commerceEnv = Join-Path $srcRoot '.local/commerce.env'
if (Test-Path -LiteralPath $commerceEnv) {
    $line = Get-Content -LiteralPath $commerceEnv | Where-Object { $_ -match '^\s*COMMERCE_PAYMENT_MODE\s*=' } | Select-Object -Last 1
    if ($line) { $mode = ($line -split '=', 2)[1].Trim().Trim('"', "'") }
}
if ($mode -notin @('fake', 'regtest')) { throw "Modo de pago desconocido en src/.local/commerce.env: $mode" }
$lnbitsPort = if ($mode -eq 'regtest') { 5001 } else { 5000 }

# Fallar antes de preparar o arrancar si otro servidor ocupa los puertos.
foreach ($port in @(8000, $lnbitsPort)) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try { $listener.Start() }
    catch { throw "El puerto $port está ocupado. Detén el servidor existente y vuelve a ejecutar ./dev.ps1." }
    finally { $listener.Stop() }
}

Write-Host "Modo de pago: $mode"
Write-Host 'Preparando plataforma, dependencias y migraciones...'
& (Join-Path $srcRoot 'scripts/setup-platform.ps1')

$lnbitsRoot = Join-Path $srcRoot '.local/lnbits'
$lnbitsPython = Join-Path $lnbitsRoot '.venv/Scripts/python.exe'
if ($mode -eq 'regtest') {
    if (-not (Test-Path -LiteralPath $lnbitsPython)) { throw 'Falta LNbits. Ejecuta ./src/scripts/setup-lnbits.ps1 una vez.' }
    Write-Host 'Preparando la red Polar...'
    & (Join-Path $srcRoot 'scripts/prepare-polar.ps1')
    $logRoot = Join-Path $srcRoot '.local/lnbits-regtest'
    $arguments = @('"' + (Join-Path $srcRoot 'scripts/start-lnbits-regtest.py') + '"')
    $workingDirectory = $srcRoot
} else {
    Write-Host 'Preparando LNbits con pagos ficticios...'
    & (Join-Path $srcRoot 'scripts/setup-lnbits.ps1')
    $logRoot = Join-Path $srcRoot '.local'
    $arguments = @('-m', 'uvicorn', 'lnbits.__main__:app', '--loop', 'asyncio', '--host', '127.0.0.1', '--port', '5000')
    $workingDirectory = $lnbitsRoot
}
New-Item -ItemType Directory -Force $logRoot | Out-Null
$stdoutLog = Join-Path $logRoot ($(if ($mode -eq 'regtest') { 'stdout.log' } else { 'lnbits-dev.stdout.log' }))
$stderrLog = Join-Path $logRoot ($(if ($mode -eq 'regtest') { 'stderr.log' } else { 'lnbits-dev.stderr.log' }))

$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
Push-Location $srcRoot
try {
    $lnbitsProcess = Start-Process -FilePath $lnbitsPython -ArgumentList $arguments `
        -WorkingDirectory $workingDirectory -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog

    $lnbitsUrl = "http://127.0.0.1:$lnbitsPort/"
    $ready = $false
    for ($attempt = 0; $attempt -lt 90; $attempt++) {
        if ($lnbitsProcess.HasExited) { throw "LNbits terminó con error. Revisa $stderrLog." }
        try {
            $null = Invoke-WebRequest $lnbitsUrl -UseBasicParsing -TimeoutSec 2
            $ready = $true
            break
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $ready) { throw "LNbits no respondió a tiempo. Revisa $stderrLog." }
    $backendLabel = if ($mode -eq 'regtest') { 'regtest con bob en Polar' } else { 'FakeWallet, sin fondos reales' }
    Write-Host "LNbits: $lnbitsUrl ($backendLabel)"
    Write-Host 'Plataforma: http://127.0.0.1:8000/'
    Write-Host 'Recarga automática activada. Ctrl+C detiene los servicios iniciados aquí.'
    & (Join-Path $srcRoot '.venv/Scripts/python.exe') manage.py runserver 127.0.0.1:8000
    if ($LASTEXITCODE -ne 0) { throw 'La plataforma terminó con error.' }
} finally {
    if ($null -ne $lnbitsProcess -and -not $lnbitsProcess.HasExited) {
        Stop-Process -Id $lnbitsProcess.Id -ErrorAction SilentlyContinue
    }
    Pop-Location
}
