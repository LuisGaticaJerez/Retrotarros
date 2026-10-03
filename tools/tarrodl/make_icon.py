"""Genera el icono de TarroDL (ui/favicon.svg y ui/favicon.ico) desde la mascota TarroBot.

Es la TV synthwave de studio/branding/tarrobot/mascota.svg con una flecha de descarga
en lugar de la boca, para distinguirla de TarroBot a simple vista.

Uso:  python tools/tarrodl/make_icon.py
Requiere: pip install playwright pillow  (y python -m playwright install chromium)
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

UI = Path(__file__).resolve().parent / "ui"
SIZES = (16, 24, 32, 48, 64, 128, 256)

# Misma paleta y geometria que mascota.svg (viewBox 64): TV cyan, pantalla oscura con marco magenta,
# ojos amarillos, antena magenta y patas cyan. La boca pasa a ser una flecha de descarga amarilla.
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" shape-rendering="crispEdges">
<rect x="2" y="6" width="60" height="50" rx="3" fill="#00E5FF"/>
<rect x="6" y="10" width="51" height="40" rx="2" fill="#0a0820"/>
<rect x="8" y="12" width="47" height="36" fill="none" stroke="#FF2E88" stroke-width="1.5"/>
<rect x="16" y="18" width="8" height="8" fill="#FFD23F"/>
<rect x="39" y="18" width="8" height="8" fill="#FFD23F"/>
<rect x="19" y="20" width="3" height="4" fill="#0a0820"/>
<rect x="42" y="20" width="3" height="4" fill="#0a0820"/>
<rect x="28" y="29" width="8" height="9" fill="#FFD23F"/>
<polygon points="19,37 45,37 32,47" fill="#FFD23F"/>
<circle cx="6" cy="5" r="2.6" fill="#FF2E88"/>
<rect x="14" y="56" width="8" height="5" fill="#00E5FF"/>
<rect x="42" y="56" width="8" height="5" fill="#00E5FF"/>
</svg>
"""


def render(page, size: int) -> Image.Image:
    page.set_viewport_size({"width": size, "height": size})
    page.set_content(
        f"<html><body style='margin:0;background:transparent'>"
        f"<img src='data:image/svg+xml;utf8,{SVG.replace('#', '%23').replace(chr(10), '')}' "
        f"width='{size}' height='{size}' style='display:block'></body></html>")
    page.wait_for_timeout(100)
    png = page.screenshot(omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})
    return Image.open(io.BytesIO(png)).convert("RGBA")


def main() -> None:
    (UI / "favicon.svg").write_text(SVG, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        frames = {s: render(page, s) for s in SIZES}
        browser.close()
    frames[256].save(UI / "favicon.ico", format="ICO", sizes=[(s, s) for s in SIZES],
                     append_images=[frames[s] for s in SIZES if s != 256])
    frames[256].save(UI / "favicon-256.png")
    print("listo:", UI / "favicon.svg", UI / "favicon.ico", UI / "favicon-256.png")


if __name__ == "__main__":
    main()
