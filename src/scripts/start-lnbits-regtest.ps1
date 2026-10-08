$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$pythonPath = Join-Path $projectRoot '.local/lnbits/.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Falta la instalación local de LNbits.' }
& $pythonPath (Join-Path $PSScriptRoot 'start-lnbits-regtest.py') @args
if ($LASTEXITCODE -ne 0) { throw 'LNbits regtest terminó con error.' }
