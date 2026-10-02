$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$lnbitsRoot = Join-Path $projectRoot '.local/lnbits'
$uvPath = Join-Path $projectRoot '.local/tools/uv.exe'
$env:UV_CACHE_DIR = Join-Path $projectRoot '.local/uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot '.local/python'
$env:PYTHONUTF8 = '1'
if (-not (Test-Path $uvPath)) { throw 'Falta uv local. Consulta docs/lnbits-local.md.' }
Push-Location $lnbitsRoot
try {
    # El lanzador oficial exige uvloop, que no funciona en Windows.
    & $uvPath run --no-sync python -m uvicorn lnbits.__main__:app --loop asyncio --host 127.0.0.1 --port 5000
    if ($LASTEXITCODE -ne 0) { throw 'LNbits terminó con error.' }
} finally { Pop-Location }
