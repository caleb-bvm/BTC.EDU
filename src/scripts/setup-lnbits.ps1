$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    New-Item -ItemType Directory -Force .local/tools | Out-Null
    if (-not (Test-Path .local/tools/uv.exe)) {
        Invoke-WebRequest 'https://github.com/astral-sh/uv/releases/download/0.12.21/uv-x86_64-pc-windows-msvc.zip' -OutFile .local/tools/uv.zip
        Expand-Archive -LiteralPath .local/tools/uv.zip -DestinationPath .local/tools -Force
    }
    if (-not (Test-Path .local/lnbits)) {
        git clone --depth 1 --branch v1.6.2 https://github.com/lnbits/lnbits.git .local/lnbits
        if ($LASTEXITCODE -ne 0) { throw 'No se pudo descargar LNbits.' }
    }
    $revision = git -C .local/lnbits rev-parse HEAD
    if ($revision -ne '9349da153c223b008f7d80453b53a54e09c8ed3d') { throw 'La copia local no coincide con LNbits 1.6.2.' }
    $env:UV_CACHE_DIR = Join-Path $projectRoot '.local/uv-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot '.local/python'
    & ./.local/tools/uv.exe sync --project .local/lnbits --python 3.12 --no-dev --frozen --no-install-package uvloop
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
    if (-not (Test-Path .local/lnbits/.env)) { Copy-Item config/lnbits.env.example .local/lnbits/.env }
    New-Item -ItemType Directory -Force .local/lnbits/data/logs,.local/lnbits/lnbits/extensions,.local/lnbits/data/wasm_extensions | Out-Null
    Write-Output 'Entorno preparado. Ejecuta ./scripts/start-lnbits.ps1.'
} finally { Pop-Location }
