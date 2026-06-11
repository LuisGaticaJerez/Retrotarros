#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mockup_poleras.py — Mockups visuales de las poleras: silueta de remera (frente
con el estampado de pecho + espalda con el estampado grande), por combo.

No es print-ready; es catalogo visual para decidir. Salida:
  studio/branding/poleras/mockups/mockup-<combo>-<tela>.png

Uso:  python scripts/mockup_poleras.py
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRINT = REPO / "studio" / "branding" / "poleras" / "print"
# escenas de espalda de Luis (en el Drive); fallback a print/ del repo si no estan
DRIVE_FONDOS = Path(r"G:\Mi unidad\Imagenes retrotarros\Branding\Poleras\fondos\print")
OUT = REPO / "studio" / "branding" / "poleras" / "mockups"

TELA = {"negra": "#15151a", "blanca": "#efece6"}
COSTURA = {"negra": "#2a2a30", "blanca": "#d6d2c8"}


def _uri(p: Path) -> str:
    return p.resolve().as_uri()


def _shirt_svg(fill: str, stroke: str) -> str:
    # remera vista plana: cuello en curva, hombros, mangas, cuerpo recto
    return f'''<svg viewBox="0 0 360 400" width="100%" height="100%" style="position:absolute;inset:0;
      filter:drop-shadow(0 18px 30px rgba(0,0,0,.35))" xmlns="http://www.w3.org/2000/svg">
  <path d="M100,34 C120,20 142,20 180,32 C218,20 240,20 260,34 L330,76 L294,130 L262,108 L262,384 L98,384 L98,108 L66,130 L30,76 Z"
        fill="{fill}" stroke="{stroke}" stroke-width="3"/>
  <path d="M132,32 C150,58 210,58 228,32" fill="none" stroke="{stroke}" stroke-width="6" opacity=".8"/>
</svg>'''


def _prenda(fill, stroke, art_uri, *, pecho):
    """Una remera con un estampado. pecho=True -> chico arriba-izq; False -> grande centrado."""
    if pecho:
        box = 'left:30%;top:20%;width:23%'
    else:
        box = 'left:50%;top:30%;width:64%;transform:translateX(-50%)'
    return (f'<div style="position:relative;width:380px;height:422px">'
            + _shirt_svg(fill, stroke)
            + f'<img src="{art_uri}" style="position:absolute;{box};'
            'object-fit:contain;image-rendering:pixelated"/>'
            '</div>')


def _mockup_html(tela, pecho_uri, espalda_uri):
    fill = TELA[tela]
    stroke = COSTURA[tela]
    return ('<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0}'
            'body{background:#3a3a42}</style></head><body>'
            '<div class="card" style="display:flex;gap:30px;padding:34px;background:#3a3a42;width:830px">'
            + _prenda(fill, stroke, pecho_uri, pecho=True)
            + _prenda(fill, stroke, espalda_uri, pecho=False)
            + '</div></body></html>')


# combos: (nombre, pecho_png_en_print, espalda_png)  espalda puede ser del Drive
def _espalda(name_drive, name_repo):
    d = DRIVE_FONDOS / name_drive
    return d if d.exists() else (PRINT / name_repo)


def combos(tela):
    t = "dark" if tela == "negra" else "light"
    return [
        ("gameboy", PRINT / f"pecho-dotmatrix-{t}.png",
         _espalda("Retrotarros_Banner_GameBoy_espalda_PRINT.png", f"espalda-gameboy-{t}.png")),
        ("arcade", PRINT / f"pecho-ciudad-{t}.png",
         _espalda("Retrotarros_Banner_Arcade_espalda_PRINT.png", f"espalda-arcade-{t}.png")),
        ("tarrovision", PRINT / f"pecho-wordmark-{t}.png",
         _espalda("Retrotarros_Banner_TarroVision_espalda_PRINT.png", f"espalda-tarrovision-{t}.png")),
        ("sol", PRINT / f"pecho-sol-{t}.png",
         _espalda("Retrotarros_Banner_Original_espalda_PRINT.png", f"espalda-wordmark-synthwave-{t}.png")),
        ("equipo-luis", PRINT / f"pecho-banner-luis-{t}.png", PRINT / f"espalda-badge-{t}.png"),
    ]


def generar(progress=print):
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    hechos = []
    tmp = OUT / "_mockup_tmp.html"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for tela in ("negra", "blanca"):
            for nombre, pecho, espalda in combos(tela):
                html = _mockup_html(tela, _uri(pecho), _uri(espalda))
                tmp.write_text(html, encoding="utf-8")
                pg = b.new_page(viewport={"width": 830, "height": 490}, device_scale_factor=2)
                pg.goto(tmp.resolve().as_uri(), wait_until="networkidle")
                pg.wait_for_timeout(500)
                dst = OUT / f"mockup-{nombre}-{tela}.png"
                pg.locator(".card").screenshot(path=str(dst))
                pg.close()
                hechos.append(dst)
                progress(f"[mockup] {dst.name}")
        b.close()
    tmp.unlink(missing_ok=True)
    return hechos


if __name__ == "__main__":
    generar()
    print("LISTO ->", OUT)
