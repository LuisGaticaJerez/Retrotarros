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
# Excepcion RESENAS (studio\resenas\*.html): el HTML aterriza igual en su propia
# carpeta <slug>/, pero la box art es compartida POR JUEGO (no por episodio) y
# vive en img/resenas/ al lado de las carpetas <slug>/, no adentro de cada una
# (el HTML referencia "../img/resenas/<key>.jpg").
#
# Requiere: pandoc instalado (winget install JohnMacFarlane.Pandoc)

$ErrorActionPreference = "Stop"

# === CONFIG ===
$RepoRoot       = Join-Path $PSScriptRoot ".."
$RepoStudio     = Join-Path $RepoRoot "studio"
$RepoDocs       = Join-Path $RepoRoot "docs"
$RepoTemplate   = Join-Path $RepoStudio "templates\reference.docx"
$DriveRoot      = "G:\Mi unidad\Studio"
$DrivePautas    = Join-Path $DriveRoot "pautas"

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
    # Saltar templates (slug que empieza con _)
    if ($slug.StartsWith("_")) {
        Write-Host "  SKIP $slug (template)" -ForegroundColor DarkGray
        continue
    }
    $destDir = Join-Path $DriveRoot $slug
    $destImgDir = Join-Path $destDir "img\$slug"
    $destCapturesDir = Join-Path $destDir "captures"
    $srcImgDir = Join-Path $RepoStudio "img\$slug"
    $srcCapturesDir = Join-Path $RepoStudio "captures\$slug"

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

    # Capturas PNG (regenerable con scripts/capture-slides.py, va al Drive
    # porque el editor las usa como overlay en DaVinci/CapCut)
    if (Test-Path $srcCapturesDir) {
        if (-not (Test-Path $destCapturesDir)) {
            New-Item -ItemType Directory -Path $destCapturesDir -Force | Out-Null
        }
        $caps = Get-ChildItem -Path $srcCapturesDir -File -Filter "*.png" -ErrorAction SilentlyContinue
        if ($caps.Count -gt 0) {
            Copy-Item -Path "$srcCapturesDir\*.png" -Destination $destCapturesDir -Force
            Write-Host "  CAP  → $destCapturesDir ($($caps.Count) PNGs)" -ForegroundColor Cyan
        }
    }
}

# === 1b. RESENAS (carpeta APARTE studio\resenas\, no la raiz plana de studio\) ===
# FIX 2026-07-21: el Get-ChildItem de arriba no es recursivo, asi que las resenas
# nunca llegaban al Drive -> Luis no las encontraba para grabar. Ademas, las
# imagenes de resenas se comparten por JUEGO (studio\img\resenas\<key>.jpg), no
# por episodio como el resto de formatos, y el HTML las referencia con
# "../img/resenas/<key>.jpg" -> hay que copiarlas a Studio\img\resenas\ (al lado
# de las carpetas <slug>\, no adentro) para que esa ruta relativa siga resolviendo.
$resenasDir = Join-Path $RepoStudio "resenas"
$resenaHtmlFiles = @()
if (Test-Path $resenasDir) {
    $resenaHtmlFiles = Get-ChildItem -Path $resenasDir -Filter "*.html" -File
    foreach ($html in $resenaHtmlFiles) {
        $slug = [System.IO.Path]::GetFileNameWithoutExtension($html.Name)
        $destDir = Join-Path $DriveRoot $slug
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $html.FullName -Destination $destDir -Force
        Write-Host "  HTML → $destDir\$($html.Name)" -ForegroundColor Cyan
    }
    $srcResenaImg = Join-Path $RepoStudio "img\resenas"
    if (Test-Path $srcResenaImg) {
        $destResenaImg = Join-Path $DriveRoot "img\resenas"
        if (-not (Test-Path $destResenaImg)) {
            New-Item -ItemType Directory -Path $destResenaImg -Force | Out-Null
        }
        $imgs = Get-ChildItem -Path $srcResenaImg -File -ErrorAction SilentlyContinue
        if ($imgs.Count -gt 0) {
            Copy-Item -Path "$srcResenaImg\*" -Destination $destResenaImg -Force
            Write-Host "  IMG  → $destResenaImg ($($imgs.Count) archivos, compartida entre resenas)" -ForegroundColor Cyan
        }
    }
}

# === 2. VERIFICACION: todo HTML del repo aterrizo en su carpeta por-episodio ===
# Salvaguarda anti-bug 2026-05-28: Luis fue a grabar n64-coleccion y el HTML no
# estaba en G:\Mi unidad\Studio\n64-coleccion\ (solo las capturas). Causa: el sync
# se corrio antes de que existiera el HTML. Este bloque corre ANTES de la conversion
# DOCX (que puede fallar por warnings de pandoc) para garantizar que la verificacion
# critica de grabacion siempre se ejecute. Falla ruidoso si falta algun episodio.
Write-Host "`n[2/3] Verificando que cada HTML aterrizo en su carpeta..." -ForegroundColor Yellow
$allHtmlFiles = @($htmlFiles) + @($resenaHtmlFiles)
$faltantes = @()
foreach ($html in $allHtmlFiles) {
    $slug = [System.IO.Path]::GetFileNameWithoutExtension($html.Name)
    if ($slug.StartsWith("_")) { continue }
    $destHtml = Join-Path (Join-Path $DriveRoot $slug) "$slug.html"
    if (-not (Test-Path $destHtml)) { $faltantes += $slug }
}
if ($faltantes.Count -gt 0) {
    Write-Host "  [ERROR] Estos episodios NO quedaron en el Drive:" -ForegroundColor Red
    $faltantes | ForEach-Object { Write-Host "          - $_" -ForegroundColor Red }
    Write-Host "  Revisa antes de ir a grabar." -ForegroundColor Red
    exit 1
} else {
    $totalEp = ($allHtmlFiles | Where-Object { -not $_.Name.StartsWith("_") }).Count
    Write-Host "  OK - los $totalEp HTMLs estan en su carpeta por-episodio." -ForegroundColor Green
}

# === 3. CONVERTIR PAUTAS Y DISCUSIONES MD → DOCX ===
# DOCX es conveniencia (Word en el estudio), NO critico para grabar. pandoc tira
# warnings de TeX que bajo ErrorActionPreference=Stop matarian el script, asi que
# lo bajamos a Continue solo para este bloque.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
Write-Host "`n[3/3] Convirtiendo pautas/discusiones a DOCX..." -ForegroundColor Yellow

if (-not $PandocExe) {
    Write-Host "  WARN: pandoc no encontrado. Saltando conversión a DOCX." -ForegroundColor Yellow
    Write-Host "  Instalá pandoc: winget install JohnMacFarlane.Pandoc" -ForegroundColor Yellow
} else {
    Write-Host "  Usando pandoc: $PandocExe" -ForegroundColor Gray
    if (Test-Path $RepoTemplate) {
        Write-Host "  Template:      $RepoTemplate" -ForegroundColor Gray
        $pandocArgs = @("-f", "gfm", "-t", "docx", "--reference-doc=$RepoTemplate")
    } else {
        Write-Host "  WARN: reference.docx no encontrado. Usando estilos default de pandoc." -ForegroundColor Yellow
        $pandocArgs = @("-f", "gfm", "-t", "docx")
    }
    $mdPattern = @("pauta-*.md", "discusion-*.md")
    foreach ($pattern in $mdPattern) {
        $mds = Get-ChildItem -Path $RepoDocs -Filter $pattern -File
        foreach ($md in $mds) {
            $base = [System.IO.Path]::GetFileNameWithoutExtension($md.Name)
            $outDocx = Join-Path $DrivePautas "$base.docx"
            & $PandocExe @pandocArgs $md.FullName -o $outDocx 2>$null
            if ($LASTEXITCODE -eq 0) {
                $size = (Get-Item $outDocx).Length
                Write-Host ("  DOCX → {0}  ({1:N0} bytes)" -f "$base.docx", $size) -ForegroundColor Cyan
            } else {
                Write-Host "  ERR  → $base.docx" -ForegroundColor Red
            }
        }
    }
}

$ErrorActionPreference = $prevEAP

Write-Host "`nSincronización completa. Drive Desktop subirá los cambios a la nube." -ForegroundColor Green
Write-Host "Ver en: https://drive.google.com → Mi unidad → Studio" -ForegroundColor Green
