"""
tarjetas_vertical_qr.py - Retrotarros Studio Suite

Tarjeta VERTICAL estilo endcard de TarroBot (pixel, mascota, QR al canal) +
PLANCHA tamano CARTA lista para imprenta: las tarjetas repetidas calzando con
la hoja, con marcas de corte (crop ticks) en los margenes.

Salida: studio/branding/tarjetas/
  tarjeta-vertical-55x85.png            tarjeta sola (300 DPI, con sangrado)
  plancha-carta-tarjeta-vertical.pdf    hoja carta con la grilla (imprenta)
  plancha-carta-tarjeta-vertical.png    preview de la plancha

Uso:
  python scripts/tarjetas_vertical_qr.py --url "https://www.youtube.com/@retrotarros"
  python scripts/tarjetas_vertical_qr.py --url "<URL>" --ancho 55 --alto 85
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path


def _resolve_repo() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent.parent] + list(here.parents):
        if (p / "studio").is_dir() and (p / "scripts").is_dir():
            return p
    return here.parent.parent


REPO = _resolve_repo()
OUT = REPO / "studio" / "branding" / "tarjetas"

CY = "#00E5FF"; MG = "#FF2E88"; YE = "#FFD23F"; NAVY = "#0e0a20"
FONTS = ("@import url('https://fonts.googleapis.com/css2?"
         "family=Press+Start+2P&family=Share+Tech+Mono&display=swap');")

# Carta (US Letter) en mm
PAPER_W, PAPER_H = 215.9, 279.4
MIN_MARGIN = 7.0  # margen minimo de la hoja (mm)
TICK = 4.0        # largo de las marcas de corte (mm)


def _helpers():
    sys.path.insert(0, str(REPO / "scripts"))
    from tarjetas_qr import _qr_datauri, _mascota_svg
    return _qr_datauri, _mascota_svg


def _card_css(card_w: float, card_h: float) -> str:
    return f"""
.card{{width:{card_w}mm;height:{card_h}mm;background:{NAVY};position:relative;
  overflow:hidden;font-family:'Press Start 2P';display:flex;flex-direction:column;
  align-items:center;justify-content:flex-start;padding:3.5mm 3mm;gap:1.6mm}}
.card .scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,
  rgba(0,0,0,.16) 0 2px,transparent 2px 4px);opacity:.3;pointer-events:none}}
.card .grid{{position:absolute;inset:0;background-image:
  linear-gradient(rgba(0,229,255,.05) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,229,255,.05) 1px,transparent 1px);
  background-size:5mm 5mm}}
.card .hdr{{border:0.5mm solid {MG};color:{MG};font-size:1.9mm;letter-spacing:.3mm;
  padding:1mm 2mm;z-index:2;text-shadow:0 0 1mm rgba(255,46,136,.6)}}
.card .masc{{z-index:2;margin-top:.6mm}}
.card .masc svg{{width:19mm;height:19mm;filter:drop-shadow(0 0 1.5mm rgba(0,229,255,.55))}}
.card .brand{{z-index:2;color:#fff;font-size:4.6mm;line-height:1.12;text-align:center;
  letter-spacing:.3mm;text-shadow:0 0 1.5mm rgba(0,229,255,.55)}}
.card .brand b{{color:{CY}}}
.card .sub{{z-index:2;color:{YE};font-size:2mm;letter-spacing:1mm}}
.card .qrbox{{z-index:2;background:#fff;border-radius:1.4mm;padding:1.2mm;
  width:25mm;height:25mm;display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 2mm rgba(0,229,255,.35);margin-top:.6mm}}
.card .qrbox img{{width:100%;height:100%;display:block;image-rendering:pixelated}}
.card .scanme{{z-index:2;color:{CY};font-size:1.9mm;letter-spacing:.4mm;
  text-shadow:0 0 1mm rgba(0,229,255,.6)}}
.card .foot{{z-index:2;color:{MG};font-size:2.2mm;letter-spacing:.3mm;
  text-shadow:0 0 1mm rgba(255,46,136,.6)}}
"""


def _card_inner(qr_uri: str, mascot: str) -> str:
    return (
        '<div class="card">'
        '<div class="scan"></div><div class="grid"></div>'
        '<div class="hdr">@RETROTARROS</div>'
        f'<div class="masc">{mascot}</div>'
        '<div class="brand">RETRO<b>TARROS</b></div>'
        '<div class="sub">TARROBOT</div>'
        f'<div class="qrbox"><img src="{qr_uri}" alt="QR"></div>'
        '<div class="scanme">ESCANEA Y SIGUENOS</div>'
        '<div class="foot">@retrotarros</div>'
        '</div>')


def _single_card_doc(qr_uri: str, mascot: str, card_w: float, card_h: float) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}'
            f'*{{margin:0;box-sizing:border-box}}{_card_css(card_w, card_h)}'
            f'</style></head><body>{_card_inner(qr_uri, mascot)}</body></html>')


def _crop_ticks(cols: int, rows: int, card_w: float, card_h: float,
                mx: float, my: float) -> str:
    """Marcas de corte (lineas finas) en los margenes, alineadas a la grilla."""
    parts = []
    line = '<div style="position:absolute;background:#555;{0}"></div>'
    # verticales: en x = mx + i*card_w, ticks arriba y abajo del bloque
    block_bottom = my + rows * card_h
    for i in range(cols + 1):
        x = mx + i * card_w
        parts.append(line.format(
            f"left:{x - 0.1}mm;top:{my - TICK}mm;width:0.2mm;height:{TICK}mm"))
        parts.append(line.format(
            f"left:{x - 0.1}mm;top:{block_bottom}mm;width:0.2mm;height:{TICK}mm"))
    # horizontales: en y = my + j*card_h, ticks a izquierda y derecha
    block_right = mx + cols * card_w
    for j in range(rows + 1):
        y = my + j * card_h
        parts.append(line.format(
            f"top:{y - 0.1}mm;left:{mx - TICK}mm;height:0.2mm;width:{TICK}mm"))
        parts.append(line.format(
            f"top:{y - 0.1}mm;left:{block_right}mm;height:0.2mm;width:{TICK}mm"))
    return "".join(parts)


def _sheet_doc(qr_uri: str, mascot: str, card_w: float, card_h: float):
    cols = int((PAPER_W - 2 * MIN_MARGIN) // card_w)
    rows = int((PAPER_H - 2 * MIN_MARGIN) // card_h)
    cols = max(1, cols); rows = max(1, rows)
    block_w = cols * card_w
    block_h = rows * card_h
    mx = (PAPER_W - block_w) / 2
    my = (PAPER_H - block_h) / 2

    cards = ""
    for r in range(rows):
        for c in range(cols):
            x = mx + c * card_w
            y = my + r * card_h
            cards += (f'<div style="position:absolute;left:{x}mm;top:{y}mm">'
                      + _card_inner(qr_uri, mascot) + '</div>')
    ticks = _crop_ticks(cols, rows, card_w, card_h, mx, my)

    doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}'
           f'*{{margin:0;box-sizing:border-box}}'
           f'.sheet{{width:{PAPER_W}mm;height:{PAPER_H}mm;background:#fff;position:relative;overflow:hidden}}'
           f'{_card_css(card_w, card_h)}'
           f'</style></head><body><div class="sheet">{cards}{ticks}</div></body></html>')
    return doc, cols, rows


def generar(url: str, card_w: float = 55, card_h: float = 85, progress=print) -> dict:
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    qr_datauri, mascota_svg = _helpers()
    qr_uri = qr_datauri(url)
    mascot = mascota_svg(64)  # tarjetas_qr ya usa cara feliz

    single = OUT / f"tarjeta-vertical-{int(card_w)}x{int(card_h)}.png"
    sheet_pdf = OUT / "plancha-carta-tarjeta-vertical.pdf"
    sheet_png = OUT / "plancha-carta-tarjeta-vertical.png"

    single_html = _single_card_doc(qr_uri, mascot, card_w, card_h)
    sheet_html, cols, rows = _sheet_doc(qr_uri, mascot, card_w, card_h)
    tmp1 = OUT / ".vc-single.html"; tmp1.write_text(single_html, encoding="utf-8")
    tmp2 = OUT / ".vc-sheet.html"; tmp2.write_text(sheet_html, encoding="utf-8")

    # px para tarjeta sola a 300 DPI (con sangrado interno del diseno)
    vw = round(card_w / 25.4 * 96); vh = round(card_h / 25.4 * 96)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        # tarjeta sola 300 DPI
        pg = b.new_page(viewport={"width": vw + 4, "height": vh + 4}, device_scale_factor=300 / 96)
        pg.goto(tmp1.resolve().as_uri()); pg.wait_for_timeout(700)
        pg.locator(".card").screenshot(path=str(single))
        progress(f"[tarjeta] {single.name}")
        pg.close()
        # plancha carta: PDF imprenta + PNG preview
        pg2 = b.new_page(viewport={"width": 880, "height": 1140}, device_scale_factor=2)
        pg2.goto(tmp2.resolve().as_uri()); pg2.wait_for_timeout(900)
        pg2.locator(".sheet").screenshot(path=str(sheet_png))
        pg2.pdf(path=str(sheet_pdf), width=f"{PAPER_W}mm", height=f"{PAPER_H}mm",
                print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        progress(f"[tarjeta] {sheet_pdf.name} ({cols}x{rows} = {cols*rows} tarjetas/hoja)")
        progress(f"[tarjeta] {sheet_png.name}")
        b.close()

    for t in (tmp1, tmp2):
        try:
            t.unlink()
        except Exception:
            pass
    return {"single": single, "pdf": sheet_pdf, "png": sheet_png,
            "cols": cols, "rows": rows, "n": cols * rows, "url": url}


def main():
    ap = argparse.ArgumentParser(description="Tarjeta vertical con QR + plancha carta imprimible")
    ap.add_argument("--url", required=True, help="URL destino del QR")
    ap.add_argument("--ancho", type=float, default=55, help="ancho tarjeta mm (default 55)")
    ap.add_argument("--alto", type=float, default=85, help="alto tarjeta mm (default 85)")
    args = ap.parse_args()
    try:
        r = generar(args.url, args.ancho, args.alto)
        print(f"OK: tarjeta sola -> {r['single']}")
        print(f"OK: plancha PDF  -> {r['pdf']}  ({r['n']} tarjetas/hoja)")
        print(f"QR apunta a: {r['url']}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
