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

$Version = "1.1"
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

# Copiar templates HTML
Write-Host "Copiando templates HTML..." -ForegroundColor Green
New-Item -ItemType Directory -Path (Join-Path $PackageDir "studio") -Force | Out-Null
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-live.html") -Destination (Join-Path $PackageDir "studio\")
Copy-Item (Join-Path $RepoRoot "studio\_template-tarrobot-control.html") -Destination (Join-Path $PackageDir "studio\")

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
