"""
tarjetas_qr.py - Retrotarros Studio Suite

Genera la TARJETA IMPRIMIBLE horizontal (70x55mm) con QR al canal y la PLANCHA
tamano CARTA lista para imprenta (tarjetas repetidas calzando con la hoja +
marcas de corte). Tema FONDO BLANCO para ahorrar tinta.

QR real con segno (correccion H). Salida: PNG 300 DPI + PDF imprenta.

Salida: studio/branding/tarjetas/
  tarjeta-retrotarros-70x55.png          tarjeta sola (300 DPI)
  plancha-carta-tarjeta-70x55.pdf        hoja carta con la grilla (imprenta)
  plancha-carta-tarjeta-70x55.png        preview de la plancha
  qr-retrotarros.png                     QR suelto reutilizable

Uso:
  python scripts/tarjetas_qr.py --url "https://www.youtube.com/@retrotarros"
  python scripts/tarjetas_qr.py --url "<URL>" --ancho 70 --alto 55
"""

from __future__ import annotations

import io
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

# Paleta (tema blanco)
CY = "#00E5FF"; MG = "#FF2E88"; YE = "#FFD23F"
INK = "#14102b"      # texto oscuro (casi negro navy)
QRDARK = "#0a0820"   # modulos del QR
GRIDLINE = "#9aa0b4" # marcas de corte
FONTS = ("@import url('https://fonts.googleapis.com/css2?"
         "family=Press+Start+2P&family=Share+Tech+Mono&display=swap');")

# Carta (US Letter) en mm + parametros de plancha
PAPER_W, PAPER_H = 215.9, 279.4
MIN_MARGIN = 8.0
TICK = 4.0


def _mascota_svg(size_px: int) -> str:
    """Reusa la mascota del kit de branding (cara feliz). La usan tambien
    otros scripts de tarjetas, no cambiar la firma."""
    sys.path.insert(0, str(REPO / "scripts"))
    from branding_tarrobot import mascota_svg
    return mascota_svg("feliz", size_px)


def _qr_datauri(url: str, scale: int = 16) -> str:
    """QR como data-uri PNG (escala perfecto, sin lios de viewBox)."""
    import base64
    import segno
    qr = segno.make(url, error="h")
    buff = io.BytesIO()
    qr.save(buff, kind="png", scale=scale, border=2, dark=QRDARK, light="#ffffff")
    return "data:image/png;base64," + base64.b64encode(buff.getvalue()).decode("ascii")


def _card_css(card_w: float, card_h: float) -> str:
    """Tarjeta horizontal, FONDO BLANCO (ahorro de tinta)."""
    return f"""
.card{{width:{card_w}mm;height:{card_h}mm;background:#fff;position:relative;
  overflow:hidden;font-family:'Press Start 2P';display:flex;flex-direction:row;
  align-items:center;gap:3mm;padding:4mm}}
.card .left{{flex:1;display:flex;flex-direction:column;align-items:flex-start;
  justify-content:center;gap:1.5mm;min-width:0}}
.card .brand{{color:{INK};font-size:5mm;line-height:1.14;letter-spacing:.2mm}}
.card .brand b{{color:{MG}}}
.card .sub{{color:{MG};font-size:1.9mm;letter-spacing:1mm}}
.card .tag{{font-family:'Share Tech Mono';color:#5b6072;font-size:1.8mm;letter-spacing:.2mm}}
.card .masc{{display:flex;align-items:center;gap:1.4mm;margin-top:.8mm}}
.card .masc svg{{width:10mm;height:10mm}}
.card .handle{{color:{INK};font-size:1.7mm;letter-spacing:.1mm}}
.card .handle b{{color:{MG}}}
.card .right{{display:flex;flex-direction:column;align-items:center;gap:1.4mm;flex:none}}
.card .qrbox{{width:24mm;height:24mm;border:0.3mm solid #d7dae6;border-radius:1mm;
  padding:0.8mm;display:flex;align-items:center;justify-content:center}}
.card .qrbox img{{width:100%;height:100%;display:block;image-rendering:pixelated}}
.card .scanme{{color:{INK};font-size:1.9mm;letter-spacing:.3mm}}
"""


def _card_inner(qr_uri: str, mascot: str) -> str:
    return (
        '<div class="card">'
        '<div class="left">'
        '<div class="brand">RETRO<br><b>TARROS</b></div>'
        '<div class="sub">TARROBOT</div>'
        '<div class="tag">NOSTALGIA · JUEGOS · MUSICA</div>'
        f'<div class="masc">{mascot}<div class="handle">@<b>retrotarros</b></div></div>'
        '</div>'
        '<div class="right">'
        f'<div class="qrbox"><img src="{qr_uri}" alt="QR"></div>'
        '<div class="scanme">ESCANEAME</div>'
        '</div>'
        '</div>')


def _single_doc(qr_uri: str, mascot: str, w: float, h: float) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}'
            f'*{{margin:0;box-sizing:border-box}}{_card_css(w, h)}'
            f'</style></head><body>{_card_inner(qr_uri, mascot)}</body></html>')


def _crop_ticks(cols, rows, cw, ch, mx, my) -> str:
    parts = []
    line = f'<div style="position:absolute;background:{GRIDLINE};{{0}}"></div>'
    block_bottom = my + rows * ch
    block_right = mx + cols * cw
    for i in range(cols + 1):
        x = mx + i * cw
        parts.append(line.format(f"left:{x-0.1}mm;top:{my-TICK}mm;width:0.2mm;height:{TICK}mm"))
        parts.append(line.format(f"left:{x-0.1}mm;top:{block_bottom}mm;width:0.2mm;height:{TICK}mm"))
    for j in range(rows + 1):
        y = my + j * ch
        parts.append(line.format(f"top:{y-0.1}mm;left:{mx-TICK}mm;height:0.2mm;width:{TICK}mm"))
        parts.append(line.format(f"top:{y-0.1}mm;left:{block_right}mm;height:0.2mm;width:{TICK}mm"))
    return "".join(parts)


def _sheet_doc(qr_uri: str, mascot: str, cw: float, ch: float):
    cols = max(1, int((PAPER_W - 2 * MIN_MARGIN) // cw))
    rows = max(1, int((PAPER_H - 2 * MIN_MARGIN) // ch))
    mx = (PAPER_W - cols * cw) / 2
    my = (PAPER_H - rows * ch) / 2
    cards = ""
    for r in range(rows):
        for c in range(cols):
            x = mx + c * cw; y = my + r * ch
            cards += (f'<div style="position:absolute;left:{x}mm;top:{y}mm">'
                      + _card_inner(qr_uri, mascot) + '</div>')
    ticks = _crop_ticks(cols, rows, cw, ch, mx, my)
    doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}'
           f'*{{margin:0;box-sizing:border-box}}'
           f'.sheet{{width:{PAPER_W}mm;height:{PAPER_H}mm;background:#fff;position:relative;overflow:hidden}}'
           f'{_card_css(cw, ch)}</style></head><body>'
           f'<div class="sheet">{cards}{ticks}</div></body></html>')
    return doc, cols, rows


def generar(url: str, ancho_mm: float = 70, alto_mm: float = 55, progress=print) -> dict:
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    qr_uri = _qr_datauri(url)
    mascot = _mascota_svg(64)

    single = OUT / f"tarjeta-retrotarros-{int(ancho_mm)}x{int(alto_mm)}.png"
    qr_png = OUT / "qr-retrotarros.png"
    sheet_pdf = OUT / f"plancha-carta-tarjeta-{int(ancho_mm)}x{int(alto_mm)}.pdf"
    sheet_png = OUT / f"plancha-carta-tarjeta-{int(ancho_mm)}x{int(alto_mm)}.png"

    import segno
    segno.make(url, error="h").save(str(qr_png), scale=20, border=2, dark=QRDARK, light="#ffffff")

    single_html = _single_doc(qr_uri, mascot, ancho_mm, alto_mm)
    sheet_html, cols, rows = _sheet_doc(qr_uri, mascot, ancho_mm, alto_mm)
    t1 = OUT / ".card-single.html"; t1.write_text(single_html, encoding="utf-8")
    t2 = OUT / ".card-sheet.html"; t2.write_text(sheet_html, encoding="utf-8")

    vw = round(ancho_mm / 25.4 * 96); vh = round(alto_mm / 25.4 * 96)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": vw + 4, "height": vh + 4}, device_scale_factor=300 / 96)
        pg.goto(t1.resolve().as_uri()); pg.wait_for_timeout(700)
        pg.locator(".card").screenshot(path=str(single))
        progress(f"[tarjeta] {single.name} (300 DPI, fondo blanco)")
        pg.close()
        pg2 = b.new_page(viewport={"width": 880, "height": 1140}, device_scale_factor=2)
        pg2.goto(t2.resolve().as_uri()); pg2.wait_for_timeout(900)
        pg2.locator(".sheet").screenshot(path=str(sheet_png))
        pg2.pdf(path=str(sheet_pdf), width=f"{PAPER_W}mm", height=f"{PAPER_H}mm",
                print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        progress(f"[tarjeta] {sheet_pdf.name} ({cols}x{rows} = {cols*rows} tarjetas/hoja)")
        progress(f"[tarjeta] {sheet_png.name}")
        b.close()

    for t in (t1, t2):
        try:
            t.unlink()
        except Exception:
            pass
    return {"single": single, "pdf": sheet_pdf, "png": sheet_png, "qr": qr_png,
            "cols": cols, "rows": rows, "n": cols * rows, "url": url}


def main():
    ap = argparse.ArgumentParser(description="Tarjeta horizontal con QR (fondo blanco) + plancha carta")
    ap.add_argument("--url", required=True, help="URL destino del QR")
    ap.add_argument("--ancho", type=float, default=70, help="ancho en mm (default 70)")
    ap.add_argument("--alto", type=float, default=55, help="alto en mm (default 55)")
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
