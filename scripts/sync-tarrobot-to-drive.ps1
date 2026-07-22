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
# .Path explicito: Resolve-Path devuelve un PathInfo, no un string. PathInfo NO
# tiene una propiedad .Length de verdad (PowerShell la resuelve via
# enumeracion implicita y da "1"), asi que $RepoRoot.Length + 1 en el bloque de
# episodios de abajo calculaba mal el offset del Substring y armaba relPaths
# rotos (con la ruta absoluta pegada). Con .Path, $RepoRoot es un string plano
# y .Length funciona como se espera.
$RepoRoot = (Resolve-Path (Join-Path $ScriptRoot "..")).Path

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
$episodios = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Filter "*.html" -Recurse -File |
    Where-Object { $_.Name -notlike "_*" -and $_.DirectoryName -notmatch '\\resenas($|\\)' }
foreach ($ep in $episodios) {
    $relPath = $ep.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath
}
Write-Host ""

# 2b-bis. Resenas (carpeta APARTE studio\resenas\, no la raiz plana de studio\).
# FIX 2026-07-21: el Get-ChildItem de arriba no es recursivo, asi que las resenas
# quedaban fuera del sync sin este bloque.
if (Test-Path (Join-Path $RepoRoot "studio\resenas")) {
    Write-Host "Resenas:" -ForegroundColor Cyan
    Sync-Item "studio\resenas" -Recursive
    Write-Host ""
}

# 2c. Carpetas de imagenes de episodios (box arts, sprites, paneos)
# Necesarias para que los HTMLs con <img src="img/..."> renderizen bien.
# FIX 2026-07-21 (reorg): "studio\img" plano solo tiene resenas/ y thumbnails/
# desde la reorganizacion; las imagenes por-episodio ahora viven en
# "studio\<categoria>\img\<slug>\" (hermanas del HTML). Sync-Item plano de
# "studio\img" dejaba de copiar el 90% de las box arts sin ningun error visible.
# Recorremos TODAS las carpetas llamadas "img" bajo studio\ (incluye la raiz
# resenas/thumbnails y cada carpeta anidada por categoria).
Write-Host "Imagenes de episodios:" -ForegroundColor Cyan
$imgDirs = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Directory -Recurse -Filter "img" -ErrorAction SilentlyContinue
foreach ($imgDir in $imgDirs) {
    $relPath = $imgDir.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath -Recursive
}
Write-Host ""

# 2c-bis. Capturas PNG de slides (generadas por capture-slides.py). Las usa Luis
# para edicion/CapCut y como respaldo de cada slide. Fix 2026-06-25: faltaban en el sync.
# FIX 2026-07-21 (reorg): mismo problema que 2c -- las carpetas "captures\<slug>"
# ahora viven anidadas por categoria, no en la raiz plana "studio\captures".
Write-Host "Capturas de slides (PNG):" -ForegroundColor Cyan
$capDirs = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Directory -Recurse -Filter "captures" -ErrorAction SilentlyContinue
foreach ($capDir in $capDirs) {
    $relPath = $capDir.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath -Recursive
}
Write-Host ""

# 2d. CARPETAS DE PRODUCCION por episodio: "G:\Mi unidad\Studio\<slug>\"
# FIX 2026-06-19 (desfase): estas carpetas (la fuente de produccion de Luis) tenian
# COPIAS del HTML y gameboxes que NADIE actualizaba -> se desfasaban del repo y del
# sync. Ahora, para cada carpeta de produccion que exista, refrescamos el <slug>.html
# y los gameboxes (img\<slug>\) desde el repo. NO se tocan: guiones .docx, captures\,
# teasers\ ni nada que solo viva en el Drive. Asi los 3 lugares quedan SIEMPRE al dia.
Write-Host "Carpetas de produccion (Studio\<slug>):" -ForegroundColor Cyan
$ProdRoot  = Split-Path -Parent $Destino          # G:\Mi unidad\Studio
$StudioSrc = Join-Path $RepoRoot "studio"
$prodOk = 0; $prodSkip = 0
if (Test-Path $ProdRoot) {
    Get-ChildItem $ProdRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -notmatch "^(tarrobot|TarroBot-Instalador|pautas|_template)" } |
        ForEach-Object {
            $slug    = $_.Name
            $prodDir = $_.FullName
            $htmlSrc = Join-Path $StudioSrc "$slug.html"
            if (Test-Path $htmlSrc) {
                if (-not $DryRun) {
                    # HTML: el repo es canonico -> sobrescribir siempre
                    Copy-Item $htmlSrc -Destination (Join-Path $prodDir "$slug.html") -Force
                    # Gameboxes: repo\studio\img\<slug>\ -> Studio\<slug>\img\<slug>\
                    # /E agrega+actualiza, SIN /MIR para no borrar assets que solo viven en prod.
                    $imgSrc = Join-Path $StudioSrc "img\$slug"
                    if (Test-Path $imgSrc) {
                        & robocopy $imgSrc (Join-Path $prodDir "img\$slug") /E /NJH /NJS /NDL /NP /NC /NS | Out-Null
                    }
                    Write-Host "  [PROD]   $slug\ (html + gameboxes al dia)" -ForegroundColor Green
                }
                $prodOk++
            } else {
                # Carpeta en la raiz sin HTML fuente en el repo (ej. solo capturas/teasers)
                $prodSkip++
            }
        }
}
Write-Host "  Produccion actualizada: $prodOk  |  sin HTML fuente: $prodSkip" -ForegroundColor Gray
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
            # /XD fondos: NO tocar las carpetas que Luis sube directo al Drive
            # (recortes de espalda). El /MIR borraria todo lo que no este en el
            # repo, y esos recortes viven solo en el Drive. NUNCA quitar este /XD.
            & robocopy $src $dst /MIR /XD fondos mockups-fuente /NJH /NJS /NDL /NP /NC /NS | Out-Null
        }
        Write-Host "  [BRAND]  $rel -> Branding\$($brandingMap[$rel])\" -ForegroundColor Green
    }
}
Write-Host ""

# 6. Instalador vigente -> carpeta unica en Drive (borra versiones viejas con /MIR)
# La carpeta TarroBot-Instalador/ en Drive siempre tiene UN SOLO ZIP: el actual.
# Asi Luis va a Drive, entra ahi, y solo ve el correcto. No hay confusion de versiones.
Write-Host "Instalador vigente -> Drive:" -ForegroundColor Cyan

# 6a. LIMPIEZA: el instalador oficial vive en TarroBot-Instalador\ (carpeta hermana).
# Cualquier TarroBot-Studio-v*.zip o *Setup*.exe suelto DENTRO de $Destino (raiz o
# installer\) es legacy de versiones viejas (1.5.1/1.5.2) y confunde. Se borran.
# Solo toca esos patrones: NO toca install.bat, .venv, desktop.ini ni logs (instalacion real).
# Fix 2026-06-19: aparecieron zombies 1.5.1/1.5.2 que hicieron creer que la version era vieja.
if (-not $DryRun) {
    $zombiePatterns = @("TarroBot-Studio-v*.zip", "TarroBot-Studio-Setup-v*.exe")
    $zombieDirs = @($Destino, (Join-Path $Destino "installer"))
    foreach ($zd in $zombieDirs) {
        if (Test-Path $zd) {
            foreach ($pat in $zombiePatterns) {
                Get-ChildItem -Path $zd -Filter $pat -File -ErrorAction SilentlyContinue | ForEach-Object {
                    Remove-Item -LiteralPath $_.FullName -Force
                    Write-Host "  [LIMPIEZA] instalador viejo borrado: $($_.Name)" -ForegroundColor Yellow
                }
            }
        }
    }
}

$DistDir = Resolve-Path (Join-Path $ScriptRoot "..\installers\tarrobot-studio\dist")
$InstallerZip = Get-ChildItem -Path $DistDir -Filter "TarroBot-Studio-v*-slim.zip" |
    Sort-Object Name -Descending | Select-Object -First 1
if ($InstallerZip) {
    $InstallerDest = Join-Path (Split-Path -Parent $Destino) "TarroBot-Instalador"
    if (-not $DryRun) {
        if (-not (Test-Path $InstallerDest)) { New-Item -ItemType Directory -Path $InstallerDest -Force | Out-Null }
        # /MIR: borra todo lo que no sea el ZIP actual (elimina versiones viejas)
        $tempDir = Join-Path $env:TEMP "tarrobot-installer-sync"
        if (-not (Test-Path $tempDir)) { New-Item -ItemType Directory -Path $tempDir -Force | Out-Null }
        Copy-Item $InstallerZip.FullName -Destination $tempDir -Force
        & robocopy $tempDir $InstallerDest /MIR /NJH /NJS /NDL /NP /NC /NS | Out-Null
        Remove-Item -Recurse -Force $tempDir
        Write-Host "  [INSTALL] $($InstallerZip.Name) -> TarroBot-Instalador\" -ForegroundColor Green
    } else {
        Write-Host "  [DRY ]   $($InstallerZip.Name) -> TarroBot-Instalador\" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SKIP]   No se encontro ZIP de instalador en dist\" -ForegroundColor DarkGray
}
Write-Host ""

# 6b. Modus operandi + memoria -> carpeta hermana en el Drive (respaldo).
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

# 7. .env file con la ruta para que install.bat la sugiera (opcional)
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
