# scripts/sync-to-drive.ps1
# Copia el contenido de studio/ a la carpeta de Google Drive sincronizada,
# y convierte las pautas/discusiones MD a DOCX para que el PC del estudio
# las pueda abrir en Word.
#
# Uso:
#   .\scripts\sync-to-drive.ps1
#
# Estructura resultante en Drive (G:\Mi unidad\Studio\):
#   <slug>/<slug>.html
#   <slug>/img/<slug>/*.{jpg,png}
#   pautas/pauta-<slug>.docx
#   pautas/discusion-<slug>.docx
#
# Requiere: pandoc instalado (winget install JohnMacFarlane.Pandoc)

$ErrorActionPreference = "Stop"

# === CONFIG ===
$RepoRoot   = Join-Path $PSScriptRoot ".."
$RepoStudio = Join-Path $RepoRoot "studio"
$RepoDocs   = Join-Path $RepoRoot "docs"
$DriveRoot  = "G:\Mi unidad\Studio"
$DrivePautas = Join-Path $DriveRoot "pautas"

# Buscar pandoc en ubicaciones comunes
$PandocExe = $null
$pandocCandidates = @(
  "$env:LOCALAPPDATA\Pandoc\pandoc.exe",
  "$env:ProgramFiles\Pandoc\pandoc.exe",
  "pandoc.exe"
)
foreach ($p in $pandocCandidates) {
  $found = Get-Command $p -ErrorAction SilentlyContinue
  if ($found) { $PandocExe = $found.Source; break }
}

# === VERIFICACIONES ===
if (-not (Test-Path "G:\Mi unidad")) {
    Write-Host "ERROR: No se encuentra 'G:\Mi unidad'. Google Drive for Desktop no está montado." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $RepoStudio)) {
    Write-Host "ERROR: No se encuentra la carpeta del repo: $RepoStudio" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $DriveRoot)) {
    New-Item -ItemType Directory -Path $DriveRoot -Force | Out-Null
    Write-Host "Creada carpeta raíz en Drive: $DriveRoot" -ForegroundColor Green
}

if (-not (Test-Path $DrivePautas)) {
    New-Item -ItemType Directory -Path $DrivePautas -Force | Out-Null
}

# === 1. COPIAR HTML + IMAGENES POR SLUG ===
Write-Host "`n[1/2] Copiando HTML + imágenes..." -ForegroundColor Yellow
$htmlFiles = Get-ChildItem -Path $RepoStudio -Filter "*.html" -File

foreach ($html in $htmlFiles) {
    $slug = [System.IO.Path]::GetFileNameWithoutExtension($html.Name)
    $destDir = Join-Path $DriveRoot $slug
    $destImgDir = Join-Path $destDir "img\$slug"
    $srcImgDir = Join-Path $RepoStudio "img\$slug"

    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    Copy-Item -Path $html.FullName -Destination $destDir -Force
    Write-Host "  HTML → $destDir\$($html.Name)" -ForegroundColor Cyan

    if (Test-Path $srcImgDir) {
        if (-not (Test-Path $destImgDir)) {
            New-Item -ItemType Directory -Path $destImgDir -Force | Out-Null
        }
        $imgs = Get-ChildItem -Path $srcImgDir -File -Recurse -ErrorAction SilentlyContinue
        if ($imgs.Count -gt 0) {
            Copy-Item -Path "$srcImgDir\*" -Destination $destImgDir -Recurse -Force
            Write-Host "  IMG  → $destImgDir ($($imgs.Count) archivos)" -ForegroundColor Cyan
        }
    }
}

# === 2. CONVERTIR PAUTAS Y DISCUSIONES MD → DOCX ===
Write-Host "`n[2/2] Convirtiendo pautas/discusiones a DOCX..." -ForegroundColor Yellow

if (-not $PandocExe) {
    Write-Host "  WARN: pandoc no encontrado. Saltando conversión a DOCX." -ForegroundColor Yellow
    Write-Host "  Instalá pandoc: winget install JohnMacFarlane.Pandoc" -ForegroundColor Yellow
} else {
    Write-Host "  Usando pandoc: $PandocExe" -ForegroundColor Gray
    $mdPattern = @("pauta-*.md", "discusion-*.md")
    foreach ($pattern in $mdPattern) {
        $mds = Get-ChildItem -Path $RepoDocs -Filter $pattern -File
        foreach ($md in $mds) {
            $base = [System.IO.Path]::GetFileNameWithoutExtension($md.Name)
            $outDocx = Join-Path $DrivePautas "$base.docx"
            & $PandocExe -f gfm -t docx $md.FullName -o $outDocx 2>$null
            if ($LASTEXITCODE -eq 0) {
                $size = (Get-Item $outDocx).Length
                Write-Host ("  DOCX → {0}  ({1:N0} bytes)" -f "$base.docx", $size) -ForegroundColor Cyan
            } else {
                Write-Host "  ERR  → $base.docx" -ForegroundColor Red
            }
        }
    }
}

Write-Host "`nSincronización completa. Drive Desktop subirá los cambios a la nube." -ForegroundColor Green
Write-Host "Ver en: https://drive.google.com → Mi unidad → Studio" -ForegroundColor Green
