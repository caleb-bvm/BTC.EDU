$ErrorActionPreference = 'Stop'
$srcRoot = Split-Path $PSScriptRoot -Parent
$env:PYTHONUTF8 = '1'
Push-Location $srcRoot
try {
    $pythonPath = Join-Path $srcRoot '.venv/Scripts/python.exe'
    if (-not (Test-Path $pythonPath)) { throw 'Ejecuta setup-platform.ps1 primero.' }
    & $pythonPath manage.py check
    if ($LASTEXITCODE -ne 0) { throw 'La configuración tiene errores.' }
    & $pythonPath manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'Faltan migraciones.' }
    & $pythonPath manage.py test accounts core content media creators commerce learning --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw 'Fallaron las pruebas.' }
    & ./.venv/Scripts/ruff.exe check .
    if ($LASTEXITCODE -ne 0) { throw 'Hay errores de revisión estática.' }
    & $pythonPath scripts/verify-commerce-concurrency.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la comprobación de concurrencia comercial.' }
    & $pythonPath scripts/verify-assessment-concurrency.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la comprobación de concurrencia de evaluaciones.' }
    & $pythonPath scripts/verify-essential-concurrency.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la comprobación de concurrencia de certificados y preguntas.' }
    & $pythonPath scripts/verify-community-concurrency.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la comprobación de concurrencia de comunidad.' }
} finally { Pop-Location }
