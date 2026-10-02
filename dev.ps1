# Ejecutar desde la raíz: ./dev.ps1
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$srcRoot = Join-Path $PSScriptRoot 'src'
$lnbitsProcess = $null

# Fallar antes de preparar o arrancar si otro servidor ocupa los puertos.
$ports = @(8000, 5000)
foreach ($port in $ports) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try { $listener.Start() }
    catch { throw "El puerto $port está ocupado. Detén el servidor existente y vuelve a ejecutar ./dev.ps1." }
    finally { $listener.Stop() }
}

Write-Host 'Preparando plataforma, dependencias y migraciones...'
& (Join-Path $srcRoot 'scripts/setup-platform.ps1')
Write-Host 'Preparando LNbits con pagos ficticios...'
& (Join-Path $srcRoot 'scripts/setup-lnbits.ps1')

$env:PYTHONUTF8 = '1'
Push-Location $srcRoot
try {
        $lnbitsRoot = Join-Path $srcRoot '.local/lnbits'
        $lnbitsProcess = Start-Process -FilePath (Join-Path $lnbitsRoot '.venv/Scripts/python.exe') `
            -ArgumentList @('-m', 'uvicorn', 'lnbits.__main__:app', '--loop', 'asyncio', '--host', '127.0.0.1', '--port', '5000') `
            -WorkingDirectory $lnbitsRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $srcRoot '.local/lnbits-dev.stdout.log') `
            -RedirectStandardError (Join-Path $srcRoot '.local/lnbits-dev.stderr.log')

        $ready = $false
        for ($attempt = 0; $attempt -lt 60; $attempt++) {
            if ($lnbitsProcess.HasExited) { throw 'LNbits terminó con error. Revisa src/.local/lnbits-dev.stderr.log.' }
            try {
                $null = Invoke-WebRequest 'http://127.0.0.1:5000/' -UseBasicParsing -TimeoutSec 2
                $ready = $true
                break
            } catch { Start-Sleep -Milliseconds 500 }
        }
        if (-not $ready) { throw 'LNbits no respondió a tiempo. Revisa src/.local/lnbits-dev.stderr.log.' }
        Write-Host 'LNbits: http://127.0.0.1:5000/ (FakeWallet, sin fondos reales)'
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
