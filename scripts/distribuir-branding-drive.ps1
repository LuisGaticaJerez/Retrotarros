# distribuir-branding-drive.ps1 - Retrotarros Studio Suite
#
# Reparte el kit de branding de TarroBot (studio/branding/tarrobot del repo)
# en la estructura ORDENADA del Drive "Imagenes retrotarros", siguiendo la
# convencion de nombres del canal: Retrotarros_<Tipo>_TarroBot_<size>.png
#
# Categorias existentes que reusa:
#   Branding\Avatars  Branding\Banners  Branding\Logo  Branding\Shorts_cover
#   Templates Tiktok_Shorts\EndCards   (endcard vertical estilo canal)
# Categorias NUEVAS que crea:
#   Branding\Stickers  Branding\Sources  Branding\Posts  Branding\EndCards_YouTube
#
# Tambien elimina el volcado plano viejo Branding\TarroBot (si existe).
#
# Uso:
#   .\scripts\distribuir-branding-drive.ps1
#   .\scripts\distribuir-branding-drive.ps1 -ImgBase "G:\Mi unidad\Imagenes retrotarros"

param(
    [string]$ImgBase = "G:\Mi unidad\Imagenes retrotarros"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Kit = Join-Path $RepoRoot "studio\branding\tarrobot"

if (-not (Test-Path $ImgBase)) {
    Write-Host "ERROR: no existe $ImgBase (Drive montado?)" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $Kit)) {
    Write-Host "ERROR: no existe el kit $Kit (corre branding_tarrobot.py primero)" -ForegroundColor Red
    exit 1
}

# Mapa origen(relativo al kit) -> destino(relativo a ImgBase)
$map = [ordered]@{
    "avatar-800.png"                  = "Branding\Avatars\Retrotarros_Avatar_TarroBot_800x800.png"
    "banner-youtube-2560x1440.png"    = "Branding\Banners\Retrotarros_Banner_TarroBot_2560x1440.png"
    "banner-x-1500x500.png"           = "Branding\Banners\Retrotarros_Banner_TarroBot_X_1500x500.png"
    "logo-horizontal-dark.png"        = "Branding\Logo\Retrotarros_Logo_TarroBot_Horizontal_dark.png"
    "logo-horizontal-transparent.png" = "Branding\Logo\Retrotarros_Logo_TarroBot_Horizontal_transparent.png"
    "logo-stacked-dark.png"           = "Branding\Logo\Retrotarros_Logo_TarroBot_Stacked_dark.png"
    "logo-stacked-transparent.png"    = "Branding\Logo\Retrotarros_Logo_TarroBot_Stacked_transparent.png"
    "story-1080x1920.png"             = "Branding\Shorts_cover\Retrotarros_Shorts_TarroBot_1080x1920.png"
    "post-1080.png"                   = "Branding\Posts\Retrotarros_Post_TarroBot_1080x1080.png"
    "endcards\endcard-vertical.png"   = "Templates Tiktok_Shorts\EndCards\Retrotarros_EndCard_TarroBot.png"
    "endcards\endcard-2videos.png"    = "Branding\EndCards_YouTube\Retrotarros_EndCard_TarroBot_YouTube_2videos.png"
    "endcards\endcard-1video.png"     = "Branding\EndCards_YouTube\Retrotarros_EndCard_TarroBot_YouTube_1video.png"
    "expresiones\neutral.png"         = "Branding\Stickers\Retrotarros_Sticker_TarroBot_neutral.png"
    "expresiones\feliz.png"           = "Branding\Stickers\Retrotarros_Sticker_TarroBot_feliz.png"
    "expresiones\wow.png"             = "Branding\Stickers\Retrotarros_Sticker_TarroBot_wow.png"
    "expresiones\pensando.png"        = "Branding\Stickers\Retrotarros_Sticker_TarroBot_pensando.png"
    "expresiones\guino.png"           = "Branding\Stickers\Retrotarros_Sticker_TarroBot_guino.png"
    "expresiones\sospecha.png"        = "Branding\Stickers\Retrotarros_Sticker_TarroBot_sospecha.png"
    "mascota.svg"                     = "Branding\Sources\Retrotarros_TarroBot_mascota.svg"
    "contact-sheet.png"               = "Branding\Sources\Retrotarros_TarroBot_contact-sheet.png"
    "README.md"                       = "Branding\Sources\Retrotarros_TarroBot_README.md"
}

Write-Host "Distribuyendo kit TarroBot en: $ImgBase" -ForegroundColor Cyan
Write-Host ""
$n = 0
foreach ($src in $map.Keys) {
    $from = Join-Path $Kit $src
    $to   = Join-Path $ImgBase $map[$src]
    if (-not (Test-Path $from)) {
        Write-Host "  [SKIP] no existe en kit: $src" -ForegroundColor Yellow
        continue
    }
    $toDir = Split-Path -Parent $to
    if (-not (Test-Path $toDir)) { New-Item -ItemType Directory -Path $toDir -Force | Out-Null }
    Copy-Item -Path $from -Destination $to -Force
    Write-Host ("  [OK] {0}" -f $map[$src]) -ForegroundColor Green
    $n++
}

# Tarjetas imprimibles (categoria nueva). Copia desde studio/branding/tarjetas.
$Tarjetas = Join-Path $RepoRoot "studio\branding\tarjetas"
if (Test-Path $Tarjetas) {
    $tdst = Join-Path $ImgBase "Branding\Tarjetas_imprimibles"
    if (-not (Test-Path $tdst)) { New-Item -ItemType Directory -Path $tdst -Force | Out-Null }
    $tmap = [ordered]@{
        "tarjeta-retrotarros-70x55.png"      = "Retrotarros_Tarjeta_TarroBot_70x55.png"
        "plancha-carta-tarjeta-70x55.pdf"    = "Retrotarros_Tarjeta_TarroBot_Plancha_Carta.pdf"
        "plancha-carta-tarjeta-70x55.png"    = "Retrotarros_Tarjeta_TarroBot_Plancha_Carta_preview.png"
        "qr-retrotarros.png"                 = "Retrotarros_QR_canal.png"
    }
    # Limpiar versiones obsoletas (navy / vertical / pdf single viejo)
    $obsoletos = @(
        "Retrotarros_Tarjeta_TarroBot_70x55.pdf",
        "Retrotarros_Tarjeta_TarroBot_Vertical_55x85.png"
    )
    foreach ($o in $obsoletos) {
        $op = Join-Path $tdst $o
        if (Test-Path $op) { Remove-Item $op -Force; Write-Host "  [CLEAN] Tarjetas_imprimibles\$o" -ForegroundColor Magenta }
    }
    foreach ($f in $tmap.Keys) {
        $from = Join-Path $Tarjetas $f
        if (Test-Path $from) {
            Copy-Item -Path $from -Destination (Join-Path $tdst $tmap[$f]) -Force
            Write-Host ("  [OK] Branding\Tarjetas_imprimibles\{0}" -f $tmap[$f]) -ForegroundColor Green
            $n++
        }
    }
}

# Eliminar el volcado plano viejo
$viejo = Join-Path $ImgBase "Branding\TarroBot"
if (Test-Path $viejo) {
    Remove-Item -Path $viejo -Recurse -Force
    Write-Host ""
    Write-Host "  [CLEAN] eliminado volcado plano: Branding\TarroBot" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "DISTRIBUCION COMPLETA: $n archivos repartidos." -ForegroundColor Green
Write-Host "Drive Desktop subira los cambios al cloud en 1-3 min." -ForegroundColor White
