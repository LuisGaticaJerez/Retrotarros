#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fondos_to_print.py — Procesa los recortes de espalda que Luis sube al Drive
(carpeta fondos/) a versiones print-ready: escala con NEAREST (pixel-art crisp)
y embebe 300 DPI. Salida en fondos/print/<nombre>_PRINT.png.

Regla de tamano (igual a las 4 espaldas originales):
  - VERTICAL (alto >= ancho):  alto = 4000 px  (~34 cm @ 300 dpi)
  - HORIZONTAL (ancho > alto):  ancho = 3600 px (~30 cm @ 300 dpi)
El otro lado se calcula por escala uniforme. Asi una espalda alta llena la
espalda completa y una horizontal queda como franja ancha.

Uso:
  python scripts/fondos_to_print.py            # todas las de fondos/
  python scripts/fondos_to_print.py Barrio     # solo las que matcheen "Barrio"
"""
import sys
from pathlib import Path

from PIL import Image

# fondos vive en el Drive; fallback a una copia local si existiera
DRIVE_FONDOS = Path(r"G:\Mi unidad\Imagenes retrotarros\Branding\Poleras\fondos")
REPO_FONDOS = Path(__file__).resolve().parent.parent / "studio" / "branding" / "poleras" / "fondos"

DPI = 300
MAX_W = 3600   # 30 cm @ 300 dpi  -> tope para espaldas horizontales
MAX_H = 4000   # 34 cm @ 300 dpi  -> tope para espaldas verticales


def _fondos_dir() -> Path:
    if DRIVE_FONDOS.exists():
        return DRIVE_FONDOS
    if REPO_FONDOS.exists():
        return REPO_FONDOS
    raise SystemExit(f"No encuentro fondos/ ni en Drive ni en repo:\n  {DRIVE_FONDOS}\n  {REPO_FONDOS}")


def _target_size(w: int, h: int) -> tuple[int, int]:
    if w > h:                       # horizontal -> tope de ancho
        scale = MAX_W / w
    else:                           # vertical/cuadrada -> tope de alto
        scale = MAX_H / h
    return round(w * scale), round(h * scale)


def procesar(filtro: str | None = None, progress=print) -> list[Path]:
    base = _fondos_dir()
    out = base / "print"
    out.mkdir(parents=True, exist_ok=True)
    hechos: list[Path] = []
    for src in sorted(base.glob("*.png")):
        if filtro and filtro.lower() not in src.name.lower():
            continue
        im = Image.open(src).convert("RGBA")
        tw, th = _target_size(im.width, im.height)
        big = im.resize((tw, th), Image.NEAREST)
        dst = out / f"{src.stem}_PRINT.png"
        big.save(dst, dpi=(DPI, DPI))
        cm_w, cm_h = tw / DPI * 2.54, th / DPI * 2.54
        progress(f"[print] {dst.name:50} {tw}x{th}  ({cm_w:.1f} x {cm_h:.1f} cm)")
        hechos.append(dst)
    return hechos


if __name__ == "__main__":
    filtro = sys.argv[1] if len(sys.argv) > 1 else None
    hechos = procesar(filtro)
    print(f"\nLISTO -> {len(hechos)} PRINT en {_fondos_dir() / 'print'}")
