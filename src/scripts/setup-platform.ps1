$ErrorActionPreference = 'Stop'
$srcRoot = Split-Path $PSScriptRoot -Parent
Push-Location $srcRoot
try {
    $env:UV_CACHE_DIR = Join-Path $srcRoot '.local/uv-cache'
    $env:UV_PYTHON_INSTALL_DIR = Join-Path $srcRoot '.local/python'
    $env:PYTHONUTF8 = '1'
    $uvPath = Join-Path $srcRoot '.local/tools/uv.exe'
    if (-not (Test-Path $uvPath)) {
        $toolsRoot = Join-Path $srcRoot '.local/tools'
        New-Item -ItemType Directory -Force $toolsRoot | Out-Null
        $uvArchive = Join-Path $toolsRoot 'uv.zip'
        Invoke-WebRequest 'https://github.com/astral-sh/uv/releases/download/0.12.21/uv-x86_64-pc-windows-msvc.zip' -OutFile $uvArchive
        Expand-Archive -LiteralPath $uvArchive -DestinationPath $toolsRoot -Force
        if (-not (Test-Path $uvPath)) { throw 'No se pudo preparar uv.' }
    }
    & $uvPath sync --locked --python 3.12
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
    if (-not (Test-Path .env)) {
        $randomBytes = [byte[]]::new(48)
        [System.Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
        $secret = [Convert]::ToBase64String($randomBytes)
        (Get-Content config/platform.env.example -Raw).Replace('GENERAR_EN_SETUP', $secret) | Set-Content .env -Encoding utf8
    }
    New-Item -ItemType Directory -Force (Join-Path $srcRoot '.local') | Out-Null
    & $uvPath run --no-sync python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo preparar la base de datos.' }
} finally { Pop-Location }
