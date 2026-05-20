# build-package.ps1
# Arma el paquete TarroBot Studio listo para distribuir al PC del estudio.
#
# Uso:
#   .\installers\tarrobot-studio\build-package.ps1
#
# Resultado:
#   installers\tarrobot-studio\dist\TarroBot-Studio-v1.0\
#   installers\tarrobot-studio\dist\TarroBot-Studio-v1.0.zip

$ErrorActionPreference = "Stop"

$Version = "1.0"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "..\..")
$DistDir = Join-Path $ScriptRoot "dist"
$PackageName = "TarroBot-Studio-v$Version"
$PackageDir = Join-Path $DistDir $PackageName
$ZipPath = Join-Path $DistDir "$PackageName.zip"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TarroBot Studio - Build Package v$Version" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Limpieza previa
if (Test-Path $PackageDir) {
    Write-Host "Limpiando build anterior..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $PackageDir
}
if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}

# Crear carpeta de destino
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null

# Copiar archivos del instalador
Write-Host "Copiando archivos del instalador..." -ForegroundColor Green
Copy-Item (Join-Path $ScriptRoot "install.bat") -Destination $PackageDir
Copy-Item (Join-Path $ScriptRoot "TarroBot.bat") -Destination $PackageDir
Copy-Item (Join-Path $ScriptRoot "requirements.txt") -Destination $PackageDir
Copy-Item (Join-Path $ScriptRoot "README-ESTUDIO.txt") -Destination $PackageDir

# Copiar scripts del repo (solo los que necesita TarroBot Live)
Write-Host "Copiando scripts del repo..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "scripts") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "scripts\tarrobot.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\tarrobot-live.py") -Destination (Join-Path $PackageDir "scripts\")

# Copiar templates HTML
Write-Host "Copiando templates HTML..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "studio") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-live.html") -Destination (Join-Path $PackageDir "studio\")
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-control.html") -Destination (Join-Path $PackageDir "studio\")

# Copiar base de datos
Write-Host "Copiando base de datos TarroBot..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "data") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "data\tarrobot-database.json") -Destination (Join-Path $PackageDir "data\")

# Listar contenido
Write-Host ""
Write-Host "Contenido del paquete:" -ForegroundColor Cyan
Get-ChildItem $PackageDir -Recurse | ForEach-Object {
    $rel = $_.FullName.Substring($PackageDir.Length + 1)
    if ($_.PSIsContainer) {
        Write-Host "  [dir]  $rel\" -ForegroundColor Gray
    } else {
        $size = "{0:N0}" -f $_.Length
        Write-Host "  [file] $rel  ($size bytes)" -ForegroundColor Gray
    }
}

# Crear ZIP
Write-Host ""
Write-Host "Comprimiendo a ZIP..." -ForegroundColor Yellow
Compress-Archive -Path "$PackageDir\*" -DestinationPath $ZipPath -Force

$zipSize = (Get-Item $ZipPath).Length
$zipSizeKB = [math]::Round($zipSize / 1KB, 1)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  PACKAGE LISTO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Carpeta: $PackageDir" -ForegroundColor White
Write-Host "ZIP:     $ZipPath  ($zipSizeKB KB)" -ForegroundColor White
Write-Host ""
Write-Host "Siguiente paso:" -ForegroundColor Cyan
Write-Host "  1. Copia $PackageName.zip a la PC del estudio (USB / Drive / etc)" -ForegroundColor White
Write-Host "  2. Descomprime en alguna carpeta (ej. C:\TarroBot-Studio\)" -ForegroundColor White
Write-Host "  3. Doble click en install.bat" -ForegroundColor White
Write-Host "  4. Listo" -ForegroundColor White
Write-Host ""
