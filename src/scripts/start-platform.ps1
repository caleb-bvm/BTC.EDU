$ErrorActionPreference = 'Stop'
$srcRoot = Split-Path $PSScriptRoot -Parent
$env:UV_CACHE_DIR = Join-Path $srcRoot '.local/uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $srcRoot '.local/python'
$env:PYTHONUTF8 = '1'
Push-Location $srcRoot
try {
    & ./.local/tools/uv.exe run --no-sync python manage.py runserver 127.0.0.1:8000 --noreload
    if ($LASTEXITCODE -ne 0) { throw 'La plataforma terminó con error.' }
} finally { Pop-Location }
