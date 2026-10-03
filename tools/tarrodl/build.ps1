# build.ps1
# Compila TarroDL.exe (un solo archivo, sin consola) con PyInstaller.
#
# Uso:
#   .\tools\tarrodl\build.ps1
#
# Salida: tools\tarrodl\dist\TarroDL.exe
# OJO: el exe sale sin firma digital. Si Smart App Control de Windows esta activo
# puede bloquearlo ("Una directiva de Control de aplicaciones bloqueo este archivo").
# En ese caso usar iniciar-tarrodl.cmd, que corre el mismo programa con Python.
#
# El exe no lleva yt-dlp ni ffmpeg adentro: los busca en el PC (PATH o winget).
# Por eso no hay que recompilar cuando YouTube rompe yt-dlp: basta el boton
# "Actualizar yt-dlp" de la propia app.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor DarkGray
    python -m venv .venv
}

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
& $py -m pip install --quiet --upgrade pip pyinstaller
if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar PyInstaller" }

& $py -m PyInstaller --noconfirm --onefile --noconsole --name TarroDL `
    --icon "$PSScriptRoot\ui\favicon.ico" `
    --add-data "$PSScriptRoot\ui;ui" `
    --distpath "$PSScriptRoot\dist" --workpath "$PSScriptRoot\build" --specpath "$PSScriptRoot\build" `
    "$PSScriptRoot\tarrodl.py"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller fallo" }

Write-Host ""
Write-Host "Listo: $PSScriptRoot\dist\TarroDL.exe" -ForegroundColor Green
