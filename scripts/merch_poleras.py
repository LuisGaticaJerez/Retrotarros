#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merch_poleras.py — Artes print-ready para poleras Retrotarros (DTF/DTG full color).

Genera en studio/branding/poleras/print/:
  PECHO izquierdo (~9 cm @300dpi):
    pecho-mascota-<dark|light>.png    TarroBot + RETROTARROS chico
    pecho-wordmark-<dark|light>.png   solo wordmark RETROTARROS
  ESPALDA (~30 cm @300dpi):
    espalda-stacked-<dark|light>.png    logo hero apilado
    espalda-synthwave-<dark|light>.png  sol retro + grid + mascota
    espalda-crt-<dark|light>.png        TarroVision CRT + tagline
    espalda-arcade-<dark|light>.png     sprite pixel + PRESS START

  -dark  = arte para POLERA OSCURA (blancos + neon + glow)
  -light = arte para POLERA CLARA (tinta oscura, sin glow, neon ajustado)

Todos los PNG van con fondo TRANSPARENTE a 300 DPI (device_scale_factor=3).
Ademas genera poleras-contact-sheet.png con mockups sobre tela negra y blanca.

Uso:  python scripts/merch_poleras.py
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from branding_tarrobot import CY, MG, YE, DK, SCREEN, FONTS, mascota_svg  # noqa: E402

OUT = REPO / "studio" / "branding" / "poleras"
PRINT = OUT / "print"

# tinta "blanca" segun polera
INK = {"dark": "#FFFFFF", "light": DK}


def _css(variant: str) -> str:
    glow = variant == "dark"
    ink = INK[variant]
    return f"""
{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
.stage{{position:relative;display:flex;flex-direction:column;align-items:center;
  justify-content:center;overflow:hidden;background:transparent}}
.mascot{{{'filter:drop-shadow(0 0 26px rgba(0,229,255,.55));' if glow else ''}z-index:2}}
.wm{{font-family:Orbitron;font-weight:900;color:{ink};z-index:2;line-height:1;
  {'text-shadow:0 0 16px rgba(255,46,136,.55);' if glow else ''}}}
.wm b{{color:{CY}}}
.tag{{font-family:'Press Start 2P';color:{CY};z-index:2;
  {'text-shadow:0 0 10px rgba(0,229,255,.5);' if glow else ''}}}
.px{{font-family:'Press Start 2P';z-index:2;line-height:1}}
"""


def _doc(body: str, variant: str) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<style>{_css(variant)}</style></head><body>{body}</body></html>')


# ───────────────────────── PECHO ─────────────────────────

def pecho_mascota(v: str) -> str:
    return ('<div class="stage" style="width:360px;height:430px">'
            + mascota_svg("neutral", 250)
            + '<div class="wm" style="font-size:40px;letter-spacing:2px;margin-top:16px">RETRO<b>TARROS</b></div>'
            + '</div>')


def pecho_wordmark(v: str) -> str:
    return ('<div class="stage" style="width:600px;height:140px">'
            '<div class="wm" style="font-size:52px;letter-spacing:2px;white-space:nowrap">RETRO<b>TARROS</b></div>'
            '</div>')


# ───────────────────────── ESPALDA ─────────────────────────

def espalda_stacked(v: str) -> str:
    return ('<div class="stage" style="width:1100px;height:1320px">'
            + mascota_svg("feliz", 640)
            + '<div class="wm" style="font-size:118px;letter-spacing:4px;margin-top:40px;white-space:nowrap">RETRO<b>TARROS</b></div>'
            + '<div class="tag" style="font-size:42px;letter-spacing:14px;margin-top:26px">TARROBOT</div>'
            + '</div>')


def espalda_synthwave(v: str) -> str:
    ink = INK[v]
    glow = 'filter="url(#g)"' if v == "dark" else ''
    # sol retro con franjas + grid en perspectiva + mascota al centro
    return (f'''<div class="stage" style="width:1100px;height:1400px">
<svg width="1100" height="980" viewBox="0 0 1100 980" style="position:absolute;top:0;z-index:1" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{YE}"/><stop offset="0.55" stop-color="{MG}"/><stop offset="1" stop-color="{MG}"/>
    </linearGradient>
    <mask id="slits">
      <rect width="1100" height="980" fill="white"/>
      <rect x="0" y="560" width="1100" height="16" fill="black"/>
      <rect x="0" y="620" width="1100" height="22" fill="black"/>
      <rect x="0" y="688" width="1100" height="28" fill="black"/>
    </mask>
    <filter id="g"><feDropShadow dx="0" dy="0" stdDeviation="14" flood-color="{MG}" flood-opacity="0.55"/></filter>
  </defs>
  <circle cx="550" cy="430" r="330" fill="url(#sun)" mask="url(#slits)" {glow}/>
  <g stroke="{CY}" stroke-width="3" {'opacity="0.9"' if v == 'dark' else 'opacity="0.95"'}>
    <line x1="550" y1="790" x2="550" y2="980"/>
    <line x1="550" y1="790" x2="250" y2="980"/><line x1="550" y1="790" x2="850" y2="980"/>
    <line x1="550" y1="790" x2="-40" y2="980"/><line x1="550" y1="790" x2="1140" y2="980"/>
    <line x1="115" y1="828" x2="985" y2="828"/>
    <line x1="10" y1="878" x2="1090" y2="878"/>
    <line x1="-90" y1="940" x2="1190" y2="940"/>
  </g>
</svg>
<div style="position:absolute;top:280px;z-index:2;display:flex;justify-content:center;width:100%">'''
            + mascota_svg("neutral", 380) + '''</div>
<div style="position:absolute;bottom:120px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm" style="font-size:118px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag" style="font-size:23px;letter-spacing:6px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
</div>
</div>''')


def espalda_crt(v: str) -> str:
    ink = INK[v]
    scan = ''.join(f'<rect x="120" y="{210 + i * 56}" width="860" height="6" fill="{CY}" opacity="0.28"/>'
                   for i in range(11))
    glitch = (f'<rect x="120" y="392" width="860" height="26" fill="{MG}" opacity="0.55"/>'
              f'<rect x="120" y="430" width="430" height="14" fill="{CY}" opacity="0.5"/>'
              f'<rect x="640" y="540" width="340" height="18" fill="{YE}" opacity="0.45"/>')
    return (f'''<div class="stage" style="width:1100px;height:1380px">
<svg width="1100" height="960" viewBox="0 0 1100 960" style="z-index:1" xmlns="http://www.w3.org/2000/svg">
  <rect x="70" y="120" width="960" height="700" rx="36" fill="{CY}"/>
  <rect x="110" y="160" width="880" height="620" rx="20" fill="{SCREEN}"/>
  <rect x="135" y="185" width="830" height="570" fill="none" stroke="{MG}" stroke-width="7"/>
  {scan}{glitch}
  <circle cx="100" cy="100" r="20" fill="{MG}"/>
  <rect x="240" y="820" width="120" height="56" fill="{CY}"/>
  <rect x="740" y="820" width="120" height="56" fill="{CY}"/>
  <g font-family="'Press Start 2P'" font-size="40" fill="{YE}">
    <text x="550" y="500" text-anchor="middle">EN VIVO</text>
  </g>
</svg>
<div style="position:absolute;bottom:170px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm" style="font-size:118px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag" style="font-size:23px;letter-spacing:6px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
</div>
</div>''')


def espalda_arcade(v: str) -> str:
    ink = INK[v]
    # en tela clara el amarillo se pierde -> textos amarillos pasan a magenta
    acc = YE if v == "dark" else MG
    # mascota "sprite": el SVG canonico ya es pixel-art friendly; lo enmarcamos en HUD arcade
    return (f'''<div class="stage" style="width:1100px;height:1400px">
<div style="display:flex;justify-content:space-between;width:920px;z-index:2">
  <div class="px" style="font-size:34px;color:{MG}">1UP</div>
  <div class="px" style="font-size:34px;color:{ink}">HI-SCORE</div>
  <div class="px" style="font-size:34px;color:{acc}">1986</div>
</div>
<div style="margin-top:60px;z-index:2">''' + mascota_svg("wow", 560) + f'''</div>
<div class="px" style="font-size:64px;color:{acc};margin-top:80px;letter-spacing:4px">PRESS START</div>
<div class="px" style="font-size:30px;color:{CY};margin-top:40px;letter-spacing:6px">INSERT COIN(S)</div>
<div style="margin-top:90px;z-index:2;display:flex;flex-direction:column;align-items:center">
  <div class="wm" style="font-size:108px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
</div>
</div>''')


# ───────────────────────── build ─────────────────────────

DISENOS = [
    ("pecho-mascota", pecho_mascota),
    ("pecho-wordmark", pecho_wordmark),
    ("espalda-stacked", espalda_stacked),
    ("espalda-synthwave", espalda_synthwave),
    ("espalda-crt", espalda_crt),
    ("espalda-arcade", espalda_arcade),
]


def generar(progress=print) -> list[Path]:
    from playwright.sync_api import sync_playwright
    PRINT.mkdir(parents=True, exist_ok=True)
    hechos = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for nombre, fn in DISENOS:
            for v in ("dark", "light"):
                html = fn(v)
                page = browser.new_page(viewport={"width": 1400, "height": 1600},
                                        device_scale_factor=3)  # 300 dpi aprox
                page.set_content(_doc(html, v))
                page.wait_for_timeout(700)
                dst = PRINT / f"{nombre}-{v}.png"
                page.locator(".stage").screenshot(path=str(dst), omit_background=True)
                page.close()
                hechos.append(dst)
                progress(f"[poleras] {dst.name}")
        browser.close()
    return hechos


def contact_sheet(progress=print) -> Path:
    """Mockup: cada arte sobre 'tela' negra y blanca, en una sola lamina."""
    from playwright.sync_api import sync_playwright
    cards = []
    for nombre, _ in DISENOS:
        for v, tela in (("dark", "#101014"), ("light", "#f1efe9")):
            f = (PRINT / f"{nombre}-{v}.png")
            if not f.exists():
                continue
            cards.append(
                f'<div style="background:{tela};border-radius:14px;padding:26px;display:flex;'
                f'flex-direction:column;align-items:center;justify-content:center;gap:12px">'
                f'<img src="{f.resolve().as_uri()}" style="max-width:300px;max-height:330px;object-fit:contain">'
                f'<div style="font-family:monospace;font-size:13px;color:{"#888" if v == "light" else "#aaa"}">'
                f'{nombre}-{v}</div></div>')
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>*{margin:0;padding:0}</style></head>'
            '<body><div class="sheet" style="background:#2a2a30;padding:30px;display:grid;'
            'grid-template-columns:repeat(4,1fr);gap:22px;width:1640px">'
            + "".join(cards) + '</div></body></html>')
    dst = OUT / "poleras-contact-sheet.png"
    # via archivo en disco (file://) para que los <img src="file://..."> carguen
    tmp = OUT / "_sheet_tmp.html"
    tmp.write_text(html, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1700, "height": 2400})
        page.goto(tmp.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(900)
        page.locator(".sheet").screenshot(path=str(dst))
        browser.close()
    tmp.unlink(missing_ok=True)
    progress(f"[poleras] {dst.name}")
    return dst


if __name__ == "__main__":
    generar()
    contact_sheet()
    print("LISTO ->", PRINT)
