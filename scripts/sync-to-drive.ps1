# scripts/sync-to-drive.ps1
# Copia el contenido de studio/ a la carpeta de Google Drive sincronizada.
# Drive Desktop se encarga de subir a la nube automáticamente.
#
# Uso:
#   .\scripts\sync-to-drive.ps1
#
# Estructura resultante en Drive:
#   G:\Mi unidad\Studio\<slug>\<slug>.html
#   G:\Mi unidad\Studio\<slug>\img\<slug>\*.{jpg,png}

$ErrorActionPreference = "Stop"

# === CONFIG ===
$RepoStudio = Join-Path $PSScriptRoot "..\studio"
$DriveRoot  = "G:\Mi unidad\Studio"

# === VERIFICACIONES ===
if (-not (Test-Path "G:\Mi unidad")) {
    Write-Host "ERROR: No se encuentra 'G:\Mi unidad'. Google Drive for Desktop no está montado." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $RepoStudio)) {
    Write-Host "ERROR: No se encuentra la carpeta del repo: $RepoStudio" -ForegroundColor Red
    exit 1
}

# Crear raíz Studio si no existe
if (-not (Test-Path $DriveRoot)) {
    New-Item -ItemType Directory -Path $DriveRoot -Force | Out-Null
    Write-Host "Creada carpeta raíz: $DriveRoot" -ForegroundColor Green
}

# === COPIAR CADA HTML CON SU CARPETA DE IMÁGENES ===
$htmlFiles = Get-ChildItem -Path $RepoStudio -Filter "*.html" -File

if ($htmlFiles.Count -eq 0) {
    Write-Host "No se encontraron archivos .html en $RepoStudio" -ForegroundColor Yellow
    exit 0
}

foreach ($html in $htmlFiles) {
    $slug = [System.IO.Path]::GetFileNameWithoutExtension($html.Name)
    $destDir = Join-Path $DriveRoot $slug
    $destImgDir = Join-Path $destDir "img\$slug"
    $srcImgDir = Join-Path $RepoStudio "img\$slug"

    # Crear carpeta del slug
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # Copiar HTML
    Copy-Item -Path $html.FullName -Destination $destDir -Force
    Write-Host "  HTML → $destDir\$($html.Name)" -ForegroundColor Cyan

    # Copiar imágenes si existen
    if (Test-Path $srcImgDir) {
        if (-not (Test-Path $destImgDir)) {
            New-Item -ItemType Directory -Path $destImgDir -Force | Out-Null
        }
        $imgs = Get-ChildItem -Path $srcImgDir -File -Recurse
        if ($imgs.Count -gt 0) {
            Copy-Item -Path "$srcImgDir\*" -Destination $destImgDir -Recurse -Force
            Write-Host "  IMG  → $destImgDir ($($imgs.Count) archivos)" -ForegroundColor Cyan
        }
    }
}

Write-Host ""
Write-Host "Sincronización completa. Drive Desktop subirá los cambios a la nube." -ForegroundColor Green
Write-Host "Ver en: https://drive.google.com → Mi unidad → Studio" -ForegroundColor Green
