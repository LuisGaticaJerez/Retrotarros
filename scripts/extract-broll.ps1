# extract-broll.ps1
# Extrae clips de B-roll desde un gameplay largo usando PySceneDetect.
# Detecta cortes de escena/cámara y genera 1 MP4 por escena (sin re-encoding).
#
# Uso:
#   .\scripts\extract-broll.ps1 -Video "D:\Recursos Retrotarros\videos\Star Fox 64.mp4" -Slug "starfox"
#   .\scripts\extract-broll.ps1 -Video "...mp4" -Slug "starfox" -Threshold 4.0 -MinSceneLen 6
#
# Parámetros:
#   -Video        Ruta absoluta al MP4 fuente (obligatorio).
#   -Slug         Identificador corto para la carpeta de salida (obligatorio).
#                 Salida = D:\Recursos Retrotarros\videos\clips\clips-<slug>\
#   -Threshold    Sensibilidad del detector adaptive (default 5.5).
#                 Bajalo (3.0-4.0) si querés MÁS clips.
#                 Subilo (7.0-9.0) si querés MENOS clips.
#   -MinSceneLen  Duración mínima de cada clip en segundos (default 8).
#   -OutputBase   Carpeta base donde crear clips-<slug>
#                 (default D:\Recursos Retrotarros\videos\clips).
#
# Requisitos (una sola vez por máquina):
#   - Python 3.10+
#   - pip install scenedetect[opencv]
#   - winget install --id=Gyan.FFmpeg
#
# Convención Retrotarros:
#   Slug en kebab-case (ej. psvita-uncharted, snes-zelda, n64-mario).
#   El script siempre crea carpeta `clips-<slug>` para que sea fácil de encontrar.

param(
    [Parameter(Mandatory=$true)]
    [string]$Video,

    [Parameter(Mandatory=$true)]
    [string]$Slug,

    [double]$Threshold = 5.5,

    [int]$MinSceneLen = 8,

    [string]$OutputBase = "D:\Recursos Retrotarros\videos\clips"
)

# --- Validaciones ---
if (-not (Test-Path $Video)) {
    Write-Host "ERROR: no se encontró el video: $Video" -ForegroundColor Red
    exit 1
}

if ($Slug -notmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Host "ERROR: slug inválido '$Slug'. Usá kebab-case (ej. psvita-uncharted)." -ForegroundColor Red
    exit 1
}

# --- ffmpeg en PATH (winget no lo agrega global) ---
$ffmpegPath = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe" -Filter "ffmpeg.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($ffmpegPath) {
    $env:PATH = "$($ffmpegPath.DirectoryName);$env:PATH"
    Write-Host "ffmpeg detectado: $($ffmpegPath.FullName)" -ForegroundColor DarkGray
} else {
    Write-Host "WARN: ffmpeg no encontrado en winget. Asumiendo que está en PATH del sistema." -ForegroundColor Yellow
}

# --- scenedetect disponible ---
$scenedetectCheck = & python -m scenedetect --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PySceneDetect no instalado. Ejecutá:" -ForegroundColor Red
    Write-Host "  pip install scenedetect[opencv]" -ForegroundColor Yellow
    exit 1
}

# --- Preparar carpeta de salida ---
$outputDir = Join-Path $OutputBase "clips-$Slug"
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

Write-Host ""
Write-Host "=== Retrotarros · extract-broll ===" -ForegroundColor Cyan
Write-Host "Video       : $Video"
Write-Host "Slug        : $Slug"
Write-Host "Salida      : $outputDir"
Write-Host "Threshold   : $Threshold (bajo=más clips, alto=menos)"
Write-Host "Min len     : ${MinSceneLen}s"
Write-Host ""

# --- Ejecutar PySceneDetect ---
$startTime = Get-Date

& scenedetect `
    -i $Video `
    -o $outputDir `
    detect-adaptive `
    --threshold $Threshold `
    --min-scene-len "${MinSceneLen}s" `
    split-video `
    --copy

$elapsed = (Get-Date) - $startTime

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: scenedetect falló (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

# --- Resumen ---
$clips = Get-ChildItem -Path $outputDir -Filter "*.mp4"
$totalSize = ($clips | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host ""
Write-Host "=== LISTO ===" -ForegroundColor Green
Write-Host "Clips generados : $($clips.Count)"
Write-Host "Tamaño total    : $([math]::Round($totalSize, 1)) MB"
Write-Host "Tiempo          : $([math]::Round($elapsed.TotalSeconds, 1))s"
Write-Host "Carpeta         : $outputDir"
Write-Host ""
Write-Host "Próximo paso: abrir 5-10 clips al azar para revisar. Si hay muy pocos/muchos:"
Write-Host "  - Más clips → bajá threshold (ej. -Threshold 3.5)"
Write-Host "  - Menos clips → subí threshold (ej. -Threshold 8.0)"
