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
#   - studio/_template-tarrobot-live.html
#   - studio/_template-tarrobot-control.html
#   - studio/_template-tarrobot-slide.html  (si existe)
#   - studio/pautas/*.tarrobot.json + audio/*
#   - studio/melodias/* (.mid, .midi, soundfont.sf2 si existe)
#   - data/tarrobot-database.json
#
# Que NO sincroniza:
#   - .venv, .git, videos, capturas, otros HTMLs del canal
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
Write-Host ""

# 2. Templates HTML
Write-Host "Templates:" -ForegroundColor Cyan
Sync-Item "studio\_template-tarrobot-live.html"
Sync-Item "studio\_template-tarrobot-control.html"
Sync-Item "studio\_template-tarrobot-slide.html"
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
