"""
update-tagline-images.py

Reemplaza el tagline 'RETROGAMES + BATERIA' por 'NOSTALGIA + JUEGOS + MUSICA'
en los 4 banners del canal usando PIL.

Estrategia por imagen:
- Conocemos a ojo el bbox donde está el texto viejo (rectángulo interior de la barra).
- Rellenamos ese bbox con el color del fondo interior (sampleado de la propia imagen).
- Escribimos encima el texto nuevo, centrado, con Press Start 2P amarillo.

Uso:
    python scripts/update-tagline-images.py logo      # solo Logo
    python scripts/update-tagline-images.py all       # los 4
    python scripts/update-tagline-images.py preview   # genera previews .preview.png sin sobreescribir originales

Output:
    Por defecto guarda un backup con sufijo .bak.png antes de sobreescribir.
"""

import sys
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path("D:/Recursos Retrotarros/repo/assets")
# Press Start 2P: mismo font del título "RETROTARROS" en los banners.
# Es ASCII-only (sin tildes) pero matchea el estilo arcade original.
# Decisión 2026-05-15: "MUSICA" sin tilde es consistente con "BATERIA" del banner viejo.
FONT_PATH = ASSETS / "fonts" / "PressStart2P-Regular.ttf"

NEW_TAGLINE = "NOSTALGIA + JUEGOS + MUSICA"
YELLOW = (255, 210, 63)  # #FFD23F · texto/borde amarillo arcade

# Configuración por imagen.
# bbox = (x1, y1, x2, y2) del rectángulo INTERIOR de la barra que tapamos.
# sample_xy = pixel donde sampleamos el color de fondo interior.
# font_size = tamaño tipografía para el tagline nuevo.
# text_y_offset = ajuste vertical fino del texto dentro del bbox.
IMAGES = {
    "logo": {
        "file": "Retrotarros_Logo_v2_1920x1080.png",
        # La barra ocupa aprox X: 365-1555, Y: 432-512 en el 1920x1080
        "bbox": (390, 440, 1535, 508),
        "sample_xy": (400, 450),  # esquina superior izquierda del interior
        "font_size": 32,
        "text_y_offset": 0,
    },
    "banner": {
        "file": "Retrotarros_Banner_Barrio_2560x1440.png",
        # Cartel grande del medio: tagline está en línea pequeña debajo del título
        "bbox": (530, 305, 1290, 365),
        "sample_xy": (540, 320),
        "font_size": 28,
        "text_y_offset": 0,
    },
    "avatar": {
        "file": "Retrotarros_Avatar_v2_800x800.png",
        # Barra amarilla centrada bajo "RETROTARROS"
        "bbox": (165, 515, 635, 580),
        "sample_xy": (175, 525),
        "font_size": 18,
        "text_y_offset": 0,
    },
    "shorts": {
        "file": "Retrotarros_Shorts_v2_1080x1920.png",
        # Imagen REAL es 840x1456 (nombre 1080x1920 era nominal).
        # Texto al pie - NO en caja, sobre background synthwave gradient.
        "bbox": (110, 1050, 730, 1115),
        "sample_xy": (50, 1075),  # zona limpia al borde izquierdo
        "font_size": 22,
        "text_y_offset": 0,
    },
}


def process_image(key: str, preview_only: bool = False) -> Path:
    cfg = IMAGES[key]
    src = ASSETS / cfg["file"]
    if not src.exists():
        print(f"ERROR: no existe {src}")
        sys.exit(1)

    img = Image.open(src).convert("RGB")
    bbox = cfg["bbox"]
    x1, y1, x2, y2 = bbox

    # Samplear color del fondo interior
    bg = img.getpixel(cfg["sample_xy"])
    print(f"[{key}] bg sample {cfg['sample_xy']} = {bg}")

    # Tapar el rectángulo interior con el color sampleado
    draw = ImageDraw.Draw(img)
    draw.rectangle(bbox, fill=bg)

    # Cargar fuente
    font = ImageFont.truetype(str(FONT_PATH), cfg["font_size"])

    # Medir texto para centrarlo
    text_bbox = draw.textbbox((0, 0), NEW_TAGLINE, font=font)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]

    bw = x2 - x1
    bh = y2 - y1

    tx = x1 + (bw - tw) // 2
    ty = y1 + (bh - th) // 2 - cfg["text_y_offset"]

    # Si el texto no cabe en ancho, achicar font (60px de margen lateral)
    if tw > bw - 60:
        new_size = int(cfg["font_size"] * (bw - 60) / tw)
        print(f"[{key}] texto no cabe, reduciendo font {cfg['font_size']} -> {new_size}")
        font = ImageFont.truetype(str(FONT_PATH), new_size)
        text_bbox = draw.textbbox((0, 0), NEW_TAGLINE, font=font)
        tw = text_bbox[2] - text_bbox[0]
        th = text_bbox[3] - text_bbox[1]
        tx = x1 + (bw - tw) // 2
        ty = y1 + (bh - th) // 2 - cfg["text_y_offset"]

    draw.text((tx, ty), NEW_TAGLINE, font=font, fill=YELLOW)
    print(f"[{key}] texto dibujado en ({tx},{ty}) size {tw}x{th}")

    # Guardar
    if preview_only:
        out = src.with_suffix(".preview.png")
    else:
        # Backup primero
        backup = src.with_suffix(".bak.png")
        if not backup.exists():
            shutil.copy2(src, backup)
            print(f"[{key}] backup -> {backup.name}")
        out = src
    img.save(out)
    print(f"[{key}] guardado -> {out.name}")
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1].lower()
    if arg == "all":
        for key in IMAGES:
            process_image(key, preview_only=False)
    elif arg == "preview":
        for key in IMAGES:
            process_image(key, preview_only=True)
    elif arg in IMAGES:
        process_image(arg, preview_only="--preview" in sys.argv)
    else:
        print(f"ERROR: opción inválida '{arg}'. Usá: all | preview | {' | '.join(IMAGES)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
