# dl-gameplay.ps1
# Descarga un gameplay desde una URL de YouTube (yt-dlp) y, opcionalmente,
# lo corta en clips de B-roll encadenando extract-broll.ps1.
#
# Uso:
#   .\scripts\dl-gameplay.ps1 -Url "https://www.youtube.com/watch?v=XXXX" -Slug "starfox"
#   .\scripts\dl-gameplay.ps1 -Url "..." -Slug "starfox" -Broll
#   .\scripts\dl-gameplay.ps1 -Url "..." -Slug "starfox" -Broll -Threshold 4.0 -MinSceneLen 6
#
# Parámetros:
#   -Url          URL del video (obligatorio). Se ignoran playlists, baja solo ese video.
#   -Slug         Identificador corto en kebab-case (obligatorio).
#                 Salida = D:\Recursos Retrotarros\videos\<slug>.mp4
#   -MaxHeight    Resolución máxima a descargar (default 1080).
#   -Broll        Si se indica, al terminar corre extract-broll.ps1 sobre el video.
#   -Threshold    Se pasa tal cual a extract-broll.ps1 (default 5.5).
#   -MinSceneLen  Se pasa tal cual a extract-broll.ps1 (default 8).
#   -OutputBase   Carpeta donde queda el MP4 (default D:\Recursos Retrotarros\videos).
#
# Requisitos (una sola vez por máquina):
#   - winget install --id=yt-dlp.yt-dlp
#   - winget install --id=Gyan.FFmpeg
#   - Para -Broll: pip install scenedetect[opencv]
#
# Ojo con los derechos: el gameplay de otros creadores puede traer Content ID o
# strikes en un canal monetizado. Anota de dónde sale cada clip.

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,

    [Parameter(Mandatory=$true)]
    [string]$Slug,

    [int]$MaxHeight = 1080,

    [switch]$Broll,

    [double]$Threshold = 5.5,

    [int]$MinSceneLen = 8,

    [string]$OutputBase = "D:\Recursos Retrotarros\videos"
)

# --- Validaciones ---
if ($Slug -notmatch '^[a-z0-9][a-z0-9-]*$') {
    Write-Host "ERROR: slug inválido '$Slug'. Usa kebab-case (ej. psvita-uncharted)." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command yt-dlp -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: yt-dlp no está instalado. Ejecuta:" -ForegroundColor Red
    Write-Host "  winget install --id=yt-dlp.yt-dlp" -ForegroundColor Yellow
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

# --- Preparar salida ---
New-Item -ItemType Directory -Force -Path $OutputBase | Out-Null
$outFile = Join-Path $OutputBase "$Slug.mp4"

if (Test-Path $outFile) {
    Write-Host "ERROR: ya existe $outFile. Borra o renombra el archivo, o usa otro slug." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Retrotarros · dl-gameplay ===" -ForegroundColor Cyan
Write-Host "URL         : $Url"
Write-Host "Slug        : $Slug"
Write-Host "Salida      : $outFile"
Write-Host "Resolución  : hasta ${MaxHeight}p"
Write-Host "B-roll      : $(if ($Broll) { 'sí (extract-broll al terminar)' } else { 'no' })"
Write-Host ""

# --- Descargar ---
$startTime = Get-Date

& yt-dlp `
    --no-playlist `
    -f "bv*[height<=$MaxHeight]+ba/b[height<=$MaxHeight]" `
    --merge-output-format mp4 `
    -o $outFile `
    $Url

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: yt-dlp falló (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

$elapsed = (Get-Date) - $startTime
$sizeMB = [math]::Round((Get-Item $outFile).Length / 1MB, 1)

Write-Host ""
Write-Host "=== DESCARGA LISTA ===" -ForegroundColor Green
Write-Host "Archivo : $outFile"
Write-Host "Tamaño  : $sizeMB MB"
Write-Host "Tiempo  : $([math]::Round($elapsed.TotalSeconds, 1))s"

# --- Encadenar B-roll ---
if ($Broll) {
    Write-Host ""
    & "$PSScriptRoot\extract-broll.ps1" -Video $outFile -Slug $Slug -Threshold $Threshold -MinSceneLen $MinSceneLen
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Próximo paso: cortar en clips con"
Write-Host "  .\scripts\extract-broll.ps1 -Video `"$outFile`" -Slug `"$Slug`""
