"""
tarjetas_qr.py - Retrotarros Studio Suite

Genera TARJETAS IMPRIMIBLES (para repartir a invitados/entrevistados en ferias)
con un codigo QR que redirige al hub del canal. Una cara, formato 70x55mm,
lista para imprenta: PNG a 300 DPI + PDF con sangrado (bleed) de 3mm.

Estilo: plantilla del canal (pixel Press Start 2P, navy, mascota TarroBot).
QR real generado con segno (alta correccion de errores).

Uso:
  python scripts/tarjetas_qr.py --url "https://linktr.ee/retrotarros"
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

CY = "#00E5FF"; MG = "#FF2E88"; YE = "#FFD23F"; NAVY = "#0e0a20"; QRDARK = "#0a0820"
FONTS = ("@import url('https://fonts.googleapis.com/css2?"
         "family=Press+Start+2P&family=Share+Tech+Mono&display=swap');")


def _mascota_svg(size_px: int) -> str:
    """Reusa la mascota del kit de branding (cara feliz)."""
    sys.path.insert(0, str(REPO / "scripts"))
    from branding_tarrobot import mascota_svg
    return mascota_svg("feliz", size_px)


def _qr_datauri(url: str, scale: int = 16) -> str:
    """Devuelve el QR como data-uri PNG (escala perfecto en el <img>, sin
    problemas de viewBox)."""
    import base64
    import segno
    qr = segno.make(url, error="h")  # 30% correccion (robusto en impresion)
    buff = io.BytesIO()
    qr.save(buff, kind="png", scale=scale, border=2, dark=QRDARK, light="#ffffff")
    b64 = base64.b64encode(buff.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _card_html(url: str, ancho_mm: float, alto_mm: float, bleed_mm: float = 3.0) -> str:
    total_w = ancho_mm + 2 * bleed_mm
    total_h = alto_mm + 2 * bleed_mm
    mascot = _mascota_svg(64)  # tamano real lo controla el CSS (mm)
    qr_uri = _qr_datauri(url)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS}
*{{margin:0;box-sizing:border-box}}
html,body{{margin:0}}
.card{{width:{total_w}mm;height:{total_h}mm;background:{NAVY};position:relative;
  overflow:hidden;font-family:'Press Start 2P'}}
.scan{{position:absolute;inset:0;background:repeating-linear-gradient(0deg,
  rgba(0,0,0,.16) 0 2px,transparent 2px 4px);opacity:.30;pointer-events:none}}
.grid{{position:absolute;inset:0;background-image:
  linear-gradient(rgba(0,229,255,.05) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,229,255,.05) 1px,transparent 1px);
  background-size:6mm 6mm}}
/* zona segura: sangrado + margen interno */
.safe{{position:absolute;inset:{bleed_mm + 3}mm;display:flex;align-items:center;gap:3mm}}
.left{{flex:1;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:1.4mm;min-width:0}}
.brand{{color:{MG};font-size:3mm;letter-spacing:.3mm;line-height:1.15;
  text-shadow:0 0 1.5mm rgba(255,46,136,.5)}}
.tag{{font-family:'Share Tech Mono';color:{YE};font-size:1.9mm;letter-spacing:.2mm}}
.masc{{display:flex;align-items:flex-end;gap:1.6mm;margin-top:.6mm}}
.masc svg{{width:13mm;height:13mm;filter:drop-shadow(0 0 1.5mm rgba(0,229,255,.55))}}
.handle{{color:#fff;font-size:2mm;letter-spacing:.1mm}}
.handle b{{color:{CY}}}
.right{{display:flex;flex-direction:column;align-items:center;gap:1.4mm;flex:none}}
.qrbox{{background:#fff;border-radius:1.4mm;padding:1.2mm;box-shadow:0 0 2mm rgba(0,229,255,.35);
  width:23mm;height:23mm;display:flex;align-items:center;justify-content:center}}
.qrbox img{{width:100%;height:100%;display:block;image-rendering:pixelated}}
.scanme{{color:{CY};font-size:2mm;letter-spacing:.3mm;text-shadow:0 0 1mm rgba(0,229,255,.6)}}
</style></head><body>
<div class="card">
  <div class="scan"></div><div class="grid"></div>
  <div class="safe">
    <div class="left">
      <div class="brand">RETRO<br>TARROS</div>
      <div class="tag">NOSTALGIA · JUEGOS · MUSICA</div>
      <div class="masc">{mascot}<div class="handle">@<b>retrotarros</b></div></div>
    </div>
    <div class="right">
      <div class="qrbox"><img src="{qr_uri}" alt="QR Retrotarros"></div>
      <div class="scanme">ESCANEAME</div>
    </div>
  </div>
</div></body></html>"""


def generar(url: str, ancho_mm: float = 70, alto_mm: float = 55, progress=print) -> dict:
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    bleed = 3.0
    html = _card_html(url, ancho_mm, alto_mm, bleed)
    tmp = OUT / ".tarjeta-tmp.html"
    tmp.write_text(html, encoding="utf-8")

    stem = f"tarjeta-retrotarros-{int(ancho_mm)}x{int(alto_mm)}"
    png = OUT / f"{stem}.png"
    pdf = OUT / f"{stem}.pdf"
    qr_png = OUT / "qr-retrotarros.png"

    # QR suelto (reutilizable) via segno
    import segno
    segno.make(url, error="h").save(str(qr_png), scale=20, border=2, dark=QRDARK, light="#ffffff")

    total_w_mm = ancho_mm + 2 * bleed
    total_h_mm = alto_mm + 2 * bleed
    # px para 300 DPI: mm/25.4*300
    vw = round(total_w_mm / 25.4 * 96)  # px a 96dpi (viewport)
    vh = round(total_h_mm / 25.4 * 96)
    dsf = 300 / 96  # device scale factor para 300 DPI efectivos

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        # PNG 300 DPI
        pg = b.new_page(viewport={"width": vw + 4, "height": vh + 4}, device_scale_factor=dsf)
        pg.goto(tmp.resolve().as_uri()); pg.wait_for_timeout(700)
        pg.locator(".card").screenshot(path=str(png))
        progress(f"[tarjeta] {png.name} (300 DPI con sangrado {bleed}mm)")
        # PDF print-ready (tamano fisico con sangrado)
        pg.pdf(path=str(pdf), width=f"{total_w_mm}mm", height=f"{total_h_mm}mm",
               print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        progress(f"[tarjeta] {pdf.name} (PDF imprenta)")
        b.close()

    try:
        tmp.unlink()
    except Exception:
        pass
    return {"png": png, "pdf": pdf, "qr": qr_png, "url": url}


def main():
    ap = argparse.ArgumentParser(description="Genera tarjetas imprimibles con QR al canal")
    ap.add_argument("--url", required=True, help="URL destino del QR (linktree/web/canal)")
    ap.add_argument("--ancho", type=float, default=70, help="ancho en mm (default 70)")
    ap.add_argument("--alto", type=float, default=55, help="alto en mm (default 55)")
    args = ap.parse_args()
    try:
        r = generar(args.url, args.ancho, args.alto)
        print(f"OK: tarjeta -> {r['png']}")
        print(f"OK: PDF     -> {r['pdf']}")
        print(f"QR apunta a: {r['url']}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
