# sync-tarrobot-to-drive.ps1
# Sincroniza SOLO los archivos que TarroBot necesita al Drive sincronizado.
# Asi el PC del estudio (con modo Drive activado en install.bat) los ve
# automaticamente, sin tener que regenerar ZIPs ni mover pendrives.
#
# Uso:
#   .\scripts\sync-tarrobot-to-drive.ps1
#   .\scripts\sync-tarrobot-to-drive.ps1 -Destino "G:\Mi unidad\Studio\tarrobot"
#   .\scripts\sync-tarrobot-to-drive.ps1 -DryRun        (solo muestra que copiaria)
#
# Que sincroniza:
#   - scripts/tarrobot.py
#   - scripts/tarrobot-live.py
#   - scripts/tarrobot-tray.py
#   - scripts Sprint 17-18 (TarroTeaser + OBS Assistant + CapCut Ready)
#   - studio/_template-tarrobot-live.html
#   - studio/_template-tarrobot-control.html
#   - studio/_template-tarrobot-slide.html  (si existe)
#   - studio/*.html (TODOS los HTMLs de episodios del canal · fix 2026-05-27)
#   - studio/img/* recursive (imagenes de episodios, box arts, sprites)
#   - studio/pautas/*.tarrobot.json + audio/*
#   - studio/melodias/* (.mid, .midi, soundfont.sf2 si existe)
#   - studio/shorts/tarroshort-*.mp4 (shorts finales · fix 2026-06-03; NO la carpeta audio/)
#   - studio/branding/* (kit visual de TarroBot para redes · fix 2026-06-03)
#   - data/tarrobot-database.json
#
# Que NO sincroniza:
#   - .venv, .git, videos master, capturas
#   - El instalador del estudio (ese se distribuye solo la primera vez)

param(
    [string]$Destino = "G:\Mi unidad\Studio\tarrobot",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "..")

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TarroBot -> Drive sync" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repo origen: $RepoRoot" -ForegroundColor Gray
Write-Host "Destino:     $Destino" -ForegroundColor Gray
Write-Host "DryRun:      $DryRun" -ForegroundColor Gray
Write-Host ""

# Verificar que el destino exista (o crearlo)
$destinoPadre = Split-Path -Parent $Destino
if (-not (Test-Path $destinoPadre)) {
    Write-Host "[ERROR] El padre del destino no existe: $destinoPadre" -ForegroundColor Red
    Write-Host "        Verifica que Drive este sincronizado." -ForegroundColor Red
    exit 1
}

if (-not $DryRun) {
    if (-not (Test-Path $Destino)) {
        New-Item -ItemType Directory -Path $Destino -Force | Out-Null
        Write-Host "Creada carpeta destino: $Destino" -ForegroundColor Yellow
    }
}

# Funcion helper: copia un archivo o directorio si existe, manteniendo estructura
$totalCopied = 0
$totalSkipped = 0
function Sync-Item {
    param([string]$Rel, [switch]$Recursive)

    $src = Join-Path $RepoRoot $Rel
    $dst = Join-Path $Destino $Rel

    if (-not (Test-Path $src)) {
        Write-Host "  [SKIP]   $Rel  (no existe en origen)" -ForegroundColor DarkGray
        $script:totalSkipped++
        return
    }

    if ($DryRun) {
        Write-Host "  [DRY ]   $Rel" -ForegroundColor Yellow
        return
    }

    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path $dstParent)) {
        New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
    }

    if ($Recursive -and (Get-Item $src).PSIsContainer) {
        # Carpeta -> robocopy con mirror para limpiar archivos que ya no estan
        $robocopyArgs = @($src, $dst, "/MIR", "/NJH", "/NJS", "/NDL", "/NP", "/NC", "/NS")
        & robocopy @robocopyArgs | Out-Null
        Write-Host "  [DIR ]   $Rel\" -ForegroundColor Green
    } else {
        Copy-Item -Path $src -Destination $dst -Force
        Write-Host "  [COPY]   $Rel" -ForegroundColor Green
    }
    $script:totalCopied++
}

# 1. Scripts Python de TarroBot
Write-Host "Scripts:" -ForegroundColor Cyan
Sync-Item "scripts\tarrobot.py"
Sync-Item "scripts\tarrobot-live.py"
Sync-Item "scripts\tarrobot-tray.py"
Sync-Item "scripts\obs_controller.py"
# Sprint 13: modulo social (chat multi-plataforma Twitch/Discord/YouTube)
Sync-Item "scripts\message_store.py"
Sync-Item "scripts\social_manager.py"
Sync-Item "scripts\connectors" -Recursive
# Sprint 15: resolver LLM (pauta enriquecida + cache local + telemetria + modo barato)
Sync-Item "scripts\llm_resolver.py"
# Sprint 16: auto-respond toggle (modulo dedicado con config persistida)
Sync-Item "scripts\auto_respond.py"
# Sprint 17: TarroTeaser + job manager + utilidades de captura (Retrotarros Studio Suite)
Sync-Item "scripts\tarroteaser.py"
Sync-Item "scripts\teaser_jobs.py"
Sync-Item "scripts\generate-teaser.py"
Sync-Item "scripts\capture-slides.py"
# Sprint 18: OBS healthcheck + auto-setup + auto-record + lower-thirds + CapCut Ready
Sync-Item "scripts\obs_healthcheck.py"
Sync-Item "scripts\obs_setup.py"
Sync-Item "scripts\obs_recorder.py"
Sync-Item "scripts\capcut_ready.py"
# Sprint 19: TarroShort (MP4 vertical para redes con TarroBot leyendo)
Sync-Item "scripts\tarroshort_render.py"
Sync-Item "scripts\tarroshort_jobs.py"
Write-Host ""

# 2. Templates HTML
Write-Host "Templates:" -ForegroundColor Cyan
Sync-Item "studio\_template-tarrobot-live.html"
Sync-Item "studio\_template-tarrobot-control.html"
Sync-Item "studio\_template-tarrobot-slide.html"
Sync-Item "studio\obs-aliases.json"
Sync-Item "studio\tarrobot-recetas.json"
Write-Host ""

# 2b. HTMLs de EPISODIOS del canal (lo que se proyecta en grabacion)
# FIX 2026-05-27: estos faltaban en el sync. Sin esto, Luis va al estudio,
# abre n64-coleccion.html y no la encuentra. Sync masivo de todos los HTMLs
# que NO empiezan con underscore (esos son templates internos).
Write-Host "HTMLs de episodios:" -ForegroundColor Cyan
$episodios = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Filter "*.html" -File |
    Where-Object { $_.Name -notlike "_*" }
foreach ($ep in $episodios) {
    $relPath = "studio\$($ep.Name)"
    Sync-Item $relPath
}
Write-Host ""

# 2c. Carpeta de imagenes de episodios (box arts, sprites, paneos)
# Necesarias para que los HTMLs con <img src="img/..."> renderizen bien.
Write-Host "Imagenes de episodios:" -ForegroundColor Cyan
if (Test-Path (Join-Path $RepoRoot "studio\img")) {
    Sync-Item "studio\img" -Recursive
}
Write-Host ""

# 3. DB
Write-Host "Database:" -ForegroundColor Cyan
Sync-Item "data\tarrobot-database.json"
Write-Host ""

# 4. Pautas completas (JSON + audio precargado)
Write-Host "Pautas (JSON + audio):" -ForegroundColor Cyan
Sync-Item "studio\pautas" -Recursive
Write-Host ""

# 5. Melodias (MIDIs + soundfont)
Write-Host "Melodias (MIDIs + soundfont):" -ForegroundColor Cyan
Sync-Item "studio\melodias" -Recursive
Write-Host ""

# 5b. Shorts verticales (MP4 finales de TarroShort). Solo los tarroshort-*.mp4,
#     NO la carpeta audio/ (intermedios de render). Fix 2026-06-03.
Write-Host "Shorts TarroShort (MP4 finales):" -ForegroundColor Cyan
$shortsDir = Join-Path $RepoRoot "studio\shorts"
if (Test-Path $shortsDir) {
    Get-ChildItem -Path $shortsDir -Filter "tarroshort-*.mp4" -File |
        ForEach-Object { Sync-Item "studio\shorts\$($_.Name)" }
}
Write-Host ""

# 5c. Branding -> carpeta CANONICA de imagenes (no duplicar en Studio). Fix 2026-06-10.
#     Va a "G:\Mi unidad\Imagenes retrotarros\Branding\<subcarpeta>" en vez de
#     Studio\tarrobot\studio\branding (que era el duplicado). Subcarpetas nuevas,
#     no pisa las manuales de Luis (Avatars, Banners, Logo, Stickers, etc.).
Write-Host "Branding -> Imagenes retrotarros\Branding:" -ForegroundColor Cyan
$DriveRoot = Split-Path -Parent (Split-Path -Parent $Destino)   # ej. G:\Mi unidad
$BrandingDest = Join-Path $DriveRoot "Imagenes retrotarros\Branding"
# Solo POLERAS (lo nuevo). El kit TarroBot y las tarjetas ya viven en las
# carpetas oficiales de Luis (Avatars/Banners/Logo/Stickers/Tarjetas_imprimibles);
# no se duplican. La fuente de todo sigue versionada en el repo git.
$brandingMap = [ordered]@{
    "studio\branding\poleras"  = "Poleras"
}
foreach ($rel in $brandingMap.Keys) {
    $src = Join-Path $RepoRoot $rel
    if (Test-Path $src) {
        $dst = Join-Path $BrandingDest $brandingMap[$rel]
        if (-not $DryRun) {
            & robocopy $src $dst /MIR /NJH /NJS /NDL /NP /NC /NS | Out-Null
        }
        Write-Host "  [BRAND]  $rel -> Branding\$($brandingMap[$rel])\" -ForegroundColor Green
    }
}
Write-Host ""

# 6. .env file con la ruta para que install.bat la sugiera (opcional)
if (-not $DryRun) {
    $infoPath = Join-Path $Destino "INSTALL-INFO.txt"
    @"
TarroBot - Carpeta sincronizada desde Drive
============================================

Esta carpeta es un mirror parcial del repo Retrotarros (solo lo que
TarroBot necesita). La sincroniza Luis con:

  .\scripts\sync-tarrobot-to-drive.ps1

Para usar desde el PC del estudio:

1. Al correr install.bat, en el paso [6/8] "Configurando ubicacion
   del repo Retrotarros", pega esta ruta:

   $Destino

2. install.bat valida que existan scripts/tarrobot-live.py y
   data/tarrobot-database.json. Si la estructura quedo bien, queda
   guardado como RETROTARROS_REPO.

3. De ahi en adelante, cualquier cambio que Luis haga en su PC y
   sincronice con este script va a aparecer automatico en el estudio.

Ultima sincronizacion: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@ | Set-Content -Path $infoPath -Encoding UTF8
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SYNC COMPLETO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Archivos/carpetas sincronizados: $totalCopied" -ForegroundColor White
Write-Host "  Skipped (no existen):            $totalSkipped" -ForegroundColor Gray
Write-Host ""
Write-Host "Drive Desktop sincronizara los cambios al cloud en 1-3 min." -ForegroundColor White
Write-Host "Despues, el PC del estudio los vera automatico (si tiene" -ForegroundColor White
Write-Host "configurada esta ruta en RETROTARROS_REPO)." -ForegroundColor White
Write-Host ""
Write-Host "En el estudio: para apuntar a esta carpeta, corre una vez:" -ForegroundColor Cyan
Write-Host "  setx RETROTARROS_REPO `"$Destino`"" -ForegroundColor Yellow
Write-Host ""
