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
# Que sincroniza (SOLO datos del canal; desde la fase 5 de la separacion, 2026-11-06):
#   - carpetas de produccion por episodio: <slug>.html y gameboxes (Studio\<slug>\)
#   - studio/pautas/*.tarrobot.json + audio/*
#   - studio/melodias/* (.mid, .midi, soundfont.sf2 si existe)
#   - studio/shorts/tarroshort-*.mp4 (shorts finales; NO la carpeta audio/)
#   - studio/branding/poleras -> Imagenes retrotarros\Branding\Poleras
#   - docs/modus-operandi -> Studio\_modus-operandi (respaldo)
#
# Que NO sincroniza (lo publica cada herramienta desde su propio repo):
#   - scripts, plantillas, recetas y base de datos de TarroBot: TarroStudio (publicar-en-drive.ps1)
#   - el instalador del estudio: vive en el repo de TarroStudio
#   - .venv, .git, videos master, capturas

param(
    [string]$Destino = "G:\Mi unidad\Studio\tarrobot",
    [switch]$DryRun,
    # Modo rapido (2026-10-21): salta shorts MP4, branding, instalador, melodias, tarrobot-out y el barrido
    # recursivo de carpetas de produccion. Alcanza para actualizar scripts, DB, pautas JSON y modus operandi.
    [switch]$Rapido
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
# .Path explicito: Resolve-Path devuelve un PathInfo, no un string. PathInfo NO
# tiene una propiedad .Length de verdad (PowerShell la resuelve via
# enumeracion implicita y da "1"), asi que $RepoRoot.Length + 1 en el bloque de
# episodios de abajo calculaba mal el offset del Substring y armaba relPaths
# rotos (con la ruta absoluta pegada). Con .Path, $RepoRoot es un string plano
# y .Length funciona como se espera.
$RepoRoot = (Resolve-Path (Join-Path $ScriptRoot "..")).Path

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Canal -> Drive (datos del canal)" -ForegroundColor Cyan
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

# Los scripts, plantillas y la base de datos de TarroBot los publica TarroStudio (D:\Recursos Retrotarros\TarroTools\TarroStudio,
# publicar-en-drive.ps1), que deja la marca .publicado-por-tarrostudio. Este script ya no los copia.
if (-not (Test-Path (Join-Path $Destino ".publicado-por-tarrostudio"))) {
    Write-Host "[AVISO] No hay marca .publicado-por-tarrostudio en el destino: TarroStudio todavia no se publico aqui." -ForegroundColor Yellow
    Write-Host "        Este script solo lleva datos del canal; el panel se publica desde el repo de TarroStudio." -ForegroundColor Yellow
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

# 1. CARPETAS DE PRODUCCION por episodio: "G:\Mi unidad\Studio\<slug>\"
# (renombrado de "2d" a "2b" el 2026-07-23 al eliminar los bloques 2b/2b-bis/2c/2c-bis
# que mirroreaban studio/ completo -- ver spec 2026-07-23-tarrobot-studio-root-split)
# FIX 2026-06-19 (desfase): estas carpetas (la fuente de produccion de Luis) tenian
# COPIAS del HTML y gameboxes que NADIE actualizaba -> se desfasaban del repo y del
# sync. Ahora, para cada carpeta de produccion que exista, refrescamos el <slug>.html
# y los gameboxes (img\<slug>\) desde el repo. NO se tocan: guiones .docx, captures\,
# teasers\ ni nada que solo viva en el Drive. Asi los 3 lugares quedan SIEMPRE al dia.
# FIX 2026-07-21 (reorg, diferido de la Tarea 6 a esta Tarea 9 a proposito): el
# $htmlSrc plano (studio\$slug.html) ya no existe para el 90% de los episodios --
# ahora viven anidados por categoria. Buscamos el HTML por nombre de forma
# recursiva bajo studio\ en vez de asumir la ruta plana, y calculamos $imgSrc
# como hermano de donde se encontro (no de $StudioSrc).
Write-Host "Carpetas de produccion (Studio\<slug>):" -ForegroundColor Cyan
$ProdRoot  = Split-Path -Parent $Destino          # G:\Mi unidad\Studio
$StudioSrc = Join-Path $RepoRoot "studio"
$prodOk = 0; $prodSkip = 0
if ((Test-Path $ProdRoot) -and -not $Rapido) {
    Get-ChildItem $ProdRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch "^(tarrobot|TarroBot-Instalador|Tools|pautas|_template)" } |
        ForEach-Object {
            $slug    = $_.Name
            $prodDir = $_.FullName
            $htmlMatches = @(Get-ChildItem -Path $StudioSrc -Filter "$slug.html" -File -Recurse -ErrorAction SilentlyContinue)
            if ($htmlMatches.Count -eq 1) {
                $htmlSrc = $htmlMatches[0].FullName
                if (-not $DryRun) {
                    # HTML: el repo es canonico -> sobrescribir siempre
                    Copy-Item $htmlSrc -Destination (Join-Path $prodDir "$slug.html") -Force
                    # Gameboxes: hermano del HTML encontrado -> Studio\<slug>\img\<slug>\
                    # /E agrega+actualiza, SIN /MIR para no borrar assets que solo viven en prod.
                    $imgSrc = Join-Path $htmlMatches[0].DirectoryName "img\$slug"
                    if (Test-Path $imgSrc) {
                        & robocopy $imgSrc (Join-Path $prodDir "img\$slug") /E /NJH /NJS /NDL /NP /NC /NS | Out-Null
                    }
                    Write-Host "  [PROD]   $slug\ (html + gameboxes al dia)" -ForegroundColor Green
                }
                $prodOk++
            } else {
                # Carpeta en la raiz sin HTML fuente en el repo (ej. solo capturas/teasers),
                # o mas de un match (no deberia pasar, find_html tambien lo trataria como error)
                $prodSkip++
            }
        }
}
Write-Host "  Produccion actualizada: $prodOk  |  sin HTML fuente: $prodSkip" -ForegroundColor Gray
Write-Host ""

# 2. Pautas completas (JSON + audio precargado)
Write-Host "Pautas (JSON + audio):" -ForegroundColor Cyan
Sync-Item "studio\pautas" -Recursive
Write-Host ""

# 3. Melodias (MIDIs + soundfont)
Write-Host "Melodias (MIDIs + soundfont):" -ForegroundColor Cyan
if (-not $Rapido) { Sync-Item "studio\melodias" -Recursive }
Write-Host ""

# 4. Shorts verticales (MP4 finales de TarroShort). Solo los tarroshort-*.mp4,
#     NO la carpeta audio/ (intermedios de render). Fix 2026-06-03.
Write-Host "Shorts TarroShort (MP4 finales):" -ForegroundColor Cyan
$shortsDir = Join-Path $RepoRoot "studio\shorts"
if ((Test-Path $shortsDir) -and -not $Rapido) {
    Get-ChildItem -Path $shortsDir -Filter "tarroshort-*.mp4" -File |
        ForEach-Object { Sync-Item "studio\shorts\$($_.Name)" }
}
Write-Host ""

# 5. Branding -> carpeta CANONICA de imagenes (no duplicar en Studio). Fix 2026-06-10.
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
    if ((Test-Path $src) -and -not $Rapido) {
        $dst = Join-Path $BrandingDest $brandingMap[$rel]
        if (-not $DryRun) {
            # /XD fondos: NO tocar las carpetas que Luis sube directo al Drive
            # (recortes de espalda). El /MIR borraria todo lo que no este en el
            # repo, y esos recortes viven solo en el Drive. NUNCA quitar este /XD.
            & robocopy $src $dst /MIR /XD fondos mockups-fuente /NJH /NJS /NDL /NP /NC /NS | Out-Null
        }
        Write-Host "  [BRAND]  $rel -> Branding\$($brandingMap[$rel])\" -ForegroundColor Green
    }
}
Write-Host ""

# 6. Modus operandi + memoria -> carpeta hermana en el Drive (respaldo).
# La fuente canonica es el repo (docs\modus-operandi\). Esto es el respaldo que Luis
# pidio para tenerlo aparte, junto al resto del estudio. /MIR: el repo manda, se espeja.
# NO editar la copia del Drive a mano; se pisa en cada sync.
Write-Host "Modus operandi + memoria -> Studio\_modus-operandi:" -ForegroundColor Cyan
$MoSrc = Join-Path $RepoRoot "docs\modus-operandi"
if (Test-Path $MoSrc) {
    $MoDest = Join-Path $ProdRoot "_modus-operandi"
    if (-not $DryRun) {
        & robocopy $MoSrc $MoDest /MIR /NJH /NJS /NDL /NP /NC /NS | Out-Null
        Write-Host "  [DOCS]   docs\modus-operandi -> Studio\_modus-operandi\" -ForegroundColor Green
    } else {
        Write-Host "  [DRY ]   docs\modus-operandi -> Studio\_modus-operandi\" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SKIP]   docs\modus-operandi no existe en el repo" -ForegroundColor DarkGray
}
Write-Host ""

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
Write-Host "  setx RETROTARROS_STUDIO_ROOT `"$(Split-Path -Parent $Destino)`"" -ForegroundColor Yellow
Write-Host ""
