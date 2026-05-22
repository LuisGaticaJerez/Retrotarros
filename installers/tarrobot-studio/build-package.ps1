# build-package.ps1
# Arma el paquete TarroBot Studio listo para distribuir al PC del estudio.
#
# Uso:
#   .\installers\tarrobot-studio\build-package.ps1                # full (todo)
#   .\installers\tarrobot-studio\build-package.ps1 -Slim          # solo lo basico
#                                                                  (usa cuando el
#                                                                   estudio leera todo
#                                                                   por Drive sync)
#
# Resultado:
#   installers\tarrobot-studio\dist\TarroBot-Studio-v1.0\
#   installers\tarrobot-studio\dist\TarroBot-Studio-v1.0.zip

param(
    [switch]$Slim
)

$ErrorActionPreference = "Stop"

$Version = "1.3.0"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "..\..")
$DistDir = Join-Path $ScriptRoot "dist"
$Suffix = if ($Slim) { "-slim" } else { "" }
$PackageName = "TarroBot-Studio-v$Version$Suffix"
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
Copy-Item (Join-Path $ScriptRoot "TarroBot-debug.bat") -Destination $PackageDir
Copy-Item (Join-Path $ScriptRoot "requirements.txt") -Destination $PackageDir
Copy-Item (Join-Path $ScriptRoot "README-ESTUDIO.txt") -Destination $PackageDir

# Copiar scripts del repo (solo los que necesita TarroBot Live)
Write-Host "Copiando scripts del repo..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "scripts") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "scripts\tarrobot.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\tarrobot-live.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\tarrobot-tray.py") -Destination (Join-Path $PackageDir "scripts\")
# Sprint 9: modulo de control OBS por WebSocket
Copy-Item (Join-Path $RepoRoot "scripts\obs_controller.py") -Destination (Join-Path $PackageDir "scripts\")
# Script de sync al Drive (opcional, util si el operador edita pautas localmente)
Copy-Item (Join-Path $RepoRoot "scripts\sync-tarrobot-to-drive.ps1") -Destination (Join-Path $PackageDir "scripts\")
# Sprint 13-16: modulo social (chat multi-plataforma + LLM resolver + auto-respond)
Copy-Item (Join-Path $RepoRoot "scripts\message_store.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\social_manager.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\llm_resolver.py") -Destination (Join-Path $PackageDir "scripts\")
Copy-Item (Join-Path $RepoRoot "scripts\auto_respond.py") -Destination (Join-Path $PackageDir "scripts\")
# Subcarpeta connectors (Twitch + Discord + YouTube)
New-Item -ItemType Directory -Path (Join-Path $PackageDir "scripts\connectors") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "scripts\connectors\*.py") -Destination (Join-Path $PackageDir "scripts\connectors\")

# Copiar templates HTML
Write-Host "Copiando templates HTML..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "studio") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-live.html") -Destination (Join-Path $PackageDir "studio\")
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-control.html") -Destination (Join-Path $PackageDir "studio\")
# Sprint 9-12: configs editables del personaje y recetas
Copy-Item (Join-Path $RepoRoot "studio\obs-aliases.json") -Destination (Join-Path $PackageDir "studio\")
Copy-Item (Join-Path $RepoRoot "studio\tarrobot-recetas.json") -Destination (Join-Path $PackageDir "studio\")

# Sprint 12: carpetas vacias para exports/shorts (TarroBot escribe ahi)
New-Item -ItemType Directory -Path (Join-Path $PackageDir "studio\exports") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "studio\shorts") -Force | Out-Null
"# Salida de /api/episodio/exportar-descripcion (titulos, descripciones, hashtags, prompts thumbnail)." |
    Set-Content -Path (Join-Path $PackageDir "studio\exports\README.txt") -Encoding UTF8
"# Salida de /api/queue/short-export (MP3 + SRT por dato puntual, listo para CapCut/DaVinci)." |
    Set-Content -Path (Join-Path $PackageDir "studio\shorts\README.txt") -Encoding UTF8

# Sprint 9: incluir FluidSynth + DLLs si Luis los tiene en installers/tarrobot-studio/bin/
$binSrc = Join-Path $ScriptRoot "bin"
if (Test-Path $binSrc) {
    Write-Host "Copiando FluidSynth bin\..." -ForegroundColor Green
    $binDst = Join-Path $PackageDir "bin"
    New-Item -ItemType Directory -Path $binDst -Force | Out-Null
    Get-ChildItem -Path $binSrc -File | ForEach-Object {
        Copy-Item $_.FullName -Destination $binDst
    }
    Write-Host "  FluidSynth bundle incluido (saltea descarga del install.bat)" -ForegroundColor Gray
}

# Copiar base de datos
Write-Host "Copiando base de datos TarroBot..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "data") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "data\tarrobot-database.json") -Destination (Join-Path $PackageDir "data\")

if (-not $Slim) {
    # Sprint 8.4: incluir pautas + audio + melodias para paquete autocontenido
    Write-Host ""
    Write-Host "Modo FULL: incluyendo pautas + audio + melodias..." -ForegroundColor Yellow

    # Pautas JSON (guiones de episodios)
    $pautasSrc = Join-Path $RepoRoot "studio\pautas"
    $pautasDst = Join-Path $PackageDir "studio\pautas"
    if (Test-Path $pautasSrc) {
        New-Item -ItemType Directory -Path $pautasDst -Force | Out-Null
        Get-ChildItem -Path $pautasSrc -Filter "*.tarrobot.json" | ForEach-Object {
            Copy-Item $_.FullName -Destination $pautasDst
            Write-Host "  pauta: $($_.Name)" -ForegroundColor Gray
        }

        # MP3s precargados de las pautas
        $audioSrc = Join-Path $pautasSrc "audio"
        if (Test-Path $audioSrc) {
            $audioDst = Join-Path $pautasDst "audio"
            New-Item -ItemType Directory -Path $audioDst -Force | Out-Null
            $mp3Count = 0
            Get-ChildItem -Path $audioSrc -Recurse -Filter "*.mp3" | ForEach-Object {
                $rel = $_.FullName.Substring($audioSrc.Length + 1)
                $dstFile = Join-Path $audioDst $rel
                $dstParent = Split-Path -Parent $dstFile
                if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Path $dstParent -Force | Out-Null }
                Copy-Item $_.FullName -Destination $dstFile
                $mp3Count++
            }
            Write-Host "  MP3s precargados: $mp3Count" -ForegroundColor Gray
        }
    } else {
        Write-Host "  (no hay pautas en el repo, saltando)" -ForegroundColor DarkGray
    }

    # Melodias: MIDIs + soundfont si existen (gitignored, no estan en repo pero
    # si Luis los tiene localmente los incluimos)
    $melSrc = Join-Path $RepoRoot "studio\melodias"
    if (Test-Path $melSrc) {
        $melDst = Join-Path $PackageDir "studio\melodias"
        New-Item -ItemType Directory -Path $melDst -Force | Out-Null
        $midiCount = 0
        Get-ChildItem -Path $melSrc -Filter "*.mid*" | ForEach-Object {
            Copy-Item $_.FullName -Destination $melDst
            $midiCount++
        }
        if ($midiCount -gt 0) {
            Write-Host "  MIDIs: $midiCount" -ForegroundColor Gray
        }
        $sf2 = Join-Path $melSrc "soundfont.sf2"
        if (Test-Path $sf2) {
            $sf2Size = "{0:N1} MB" -f ((Get-Item $sf2).Length / 1MB)
            Copy-Item $sf2 -Destination $melDst
            Write-Host "  soundfont.sf2: $sf2Size" -ForegroundColor Gray
        }
        # gitkeep documentacion
        $keep = Join-Path $melSrc ".gitkeep"
        if (Test-Path $keep) { Copy-Item $keep -Destination $melDst }
    }
} else {
    Write-Host ""
    Write-Host "Modo SLIM: SOLO scripts + templates + DB base." -ForegroundColor Yellow
    Write-Host "El estudio leera pautas/audio/melodias desde el Drive sincronizado." -ForegroundColor Yellow
}

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
Write-Host "  PACKAGE ZIP LISTO" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Carpeta: $PackageDir" -ForegroundColor White
Write-Host "ZIP:     $ZipPath  ($zipSizeKB KB)" -ForegroundColor White
Write-Host ""

# ─────────────────────────────────────────────────────────────────
# Inno Setup: si esta instalado, compilar TarroBot-Studio-Setup-vX.X.exe
# ─────────────────────────────────────────────────────────────────
$IsccPaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 5\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 5\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe",
    "${env:LOCALAPPDATA}\Programs\Inno Setup 5\ISCC.exe"
)
$Iscc = $null
foreach ($p in $IsccPaths) {
    if (Test-Path $p) { $Iscc = $p; break }
}

if ($Iscc) {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  Compilando instalador .exe con Inno Setup" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "ISCC.exe encontrado: $Iscc" -ForegroundColor Gray
    Write-Host ""

    $IssFile = Join-Path $ScriptRoot "installer.iss"
    if (-not (Test-Path $IssFile)) {
        Write-Host "[WARN] installer.iss no existe en $ScriptRoot. Saltando compilacion .exe." -ForegroundColor Yellow
    } else {
        # Compilar (cwd debe ser el dir del .iss para que los paths relativos resuelvan)
        Push-Location $ScriptRoot
        try {
            & $Iscc /Q $IssFile
            if ($LASTEXITCODE -eq 0) {
                $ExePath = Join-Path $DistDir "TarroBot-Studio-Setup-v$Version.exe"
                if (Test-Path $ExePath) {
                    $exeSize = (Get-Item $ExePath).Length
                    $exeSizeKB = [math]::Round($exeSize / 1KB, 1)
                    Write-Host ""
                    Write-Host "============================================================" -ForegroundColor Green
                    Write-Host "  INSTALADOR .EXE LISTO" -ForegroundColor Green
                    Write-Host "============================================================" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "Setup:   $ExePath" -ForegroundColor White
                    Write-Host "Tamano:  $exeSizeKB KB" -ForegroundColor White
                    Write-Host ""
                    Write-Host "Distribuye este .exe al estudio. Doble click y next-next-finish." -ForegroundColor Cyan
                    Write-Host "Permite elegir carpeta de instalacion, modo Full o Slim, y crea" -ForegroundColor Cyan
                    Write-Host "shortcuts en escritorio y menu inicio. Es un instalador estandar Windows." -ForegroundColor Cyan
                } else {
                    Write-Host "[WARN] ISCC corrio OK pero no encuentro el .exe en $DistDir" -ForegroundColor Yellow
                }
            } else {
                Write-Host "[ERROR] ISCC fallo con codigo $LASTEXITCODE" -ForegroundColor Red
            }
        } finally {
            Pop-Location
        }
    }
} else {
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host "  Inno Setup NO instalado" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para generar TAMBIEN un instalador .exe profesional:" -ForegroundColor White
    Write-Host ""
    Write-Host "  1. Descarga Inno Setup 6 (gratis, ~5 MB):" -ForegroundColor White
    Write-Host "     https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "  2. Instalalo (next-next-finish)." -ForegroundColor White
    Write-Host "  3. Vuelve a correr este script:" -ForegroundColor White
    Write-Host "     .\installers\tarrobot-studio\build-package.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Sin Inno Setup, igual tienes el ZIP listo arriba." -ForegroundColor Gray
    Write-Host ""
}

Write-Host "Siguiente paso:" -ForegroundColor Cyan
Write-Host "  Opcion A (ZIP, simple):" -ForegroundColor White
Write-Host "    1. Copia $PackageName.zip a la PC del estudio (USB / Drive / etc)" -ForegroundColor Gray
Write-Host "    2. Descomprime en alguna carpeta (ej. C:\TarroBot-Studio\)" -ForegroundColor Gray
Write-Host "    3. Doble click en install.bat" -ForegroundColor Gray
Write-Host ""
if ($Iscc) {
    Write-Host "  Opcion B (.exe, recomendado para distribucion):" -ForegroundColor White
    Write-Host "    1. Copia TarroBot-Studio-Setup-v$Version.exe a la PC del estudio" -ForegroundColor Gray
    Write-Host "    2. Doble click. Sigue el wizard." -ForegroundColor Gray
    Write-Host "    3. Al final corre install.bat automaticamente (descarga deps, etc)" -ForegroundColor Gray
    Write-Host ""
}
