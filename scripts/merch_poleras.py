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

# Morado: color de ambiente/decoracion del canal (halos, grids, marcos de
# dispositivos). El CYAN queda RESERVADO para acompañar a TarroBot (su cuerpo)
# y el wordmark TARROS — no para decorar. (Luis 2026-06-xx)
PU = "#7C2FF0"      # morado neon (lineas, bordes, grids)
PU_DK = "#3A1A6E"   # morado profundo (cuerpos de dispositivo)


def _css(variant: str) -> str:
    glow = variant == "dark"
    ink = INK[variant]
    light = variant == "light"
    # Letras de los disenos SIN TarroBot, segun tela (que no se camuflen):
    #   polera BLANCA -> negro + morado    |    polera NEGRA -> naranja
    nc_retro = DK if light else "#FFA64D"      # RETRO
    nc_tarros = PU if light else "#FF6A00"     # TARROS
    nc_tag = PU if light else "#FF7A1A"        # tagline
    nc_glow = "" if light else "text-shadow:0 0 12px rgba(255,106,0,.5);"
    return f"""
{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
.stage{{position:relative;display:flex;flex-direction:column;align-items:center;
  justify-content:center;overflow:hidden;background:transparent}}
.mascot{{{'filter:drop-shadow(0 0 22px rgba(0,229,255,.5)) drop-shadow(0 0 40px rgba(124,47,240,.45));' if glow else ''}z-index:2}}
.halo{{position:absolute;left:50%;transform:translateX(-50%);border-radius:50%;z-index:0;
  background:radial-gradient(circle, rgba(124,47,240,{'.5' if glow else '.16'}) 0%, rgba(124,47,240,{'.18' if glow else '.06'}) 40%, transparent 70%)}}
.wm{{font-family:Orbitron;font-weight:900;color:{ink};z-index:2;line-height:1;
  {'text-shadow:0 0 16px rgba(255,46,136,.55);' if glow else ''}}}
.wm b{{color:{CY}}}
.tag{{font-family:'Press Start 2P';color:{CY};z-index:2;
  {'text-shadow:0 0 10px rgba(0,229,255,.5);' if glow else ''}}}
/* REGLA: sin TarroBot (mascota/cara/palabra) NO hay cyan.
   Letras segun tela para no camuflarse: blanca->negro+morado | negra->naranja. */
.wm.nc{{color:{nc_retro}}}
.wm.nc b{{color:{nc_tarros}}}
.tag.nc{{color:{nc_tag};{nc_glow}}}
.px{{font-family:'Press Start 2P';z-index:2;line-height:1}}
"""


def _doc(body: str, variant: str) -> str:
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<style>{_css(variant)}</style></head><body>{body}</body></html>')


# ───────────────────────── PECHO ─────────────────────────

def pecho_mascota(v: str) -> str:
    return ('<div class="stage" style="width:360px;height:430px">'
            + '<div class="halo" style="width:340px;height:340px;top:10px"></div>'
            + mascota_svg("neutral", 250)
            + '<div class="wm" style="font-size:40px;letter-spacing:2px;margin-top:16px">RETRO<b>TARROS</b></div>'
            + '</div>')


def pecho_wordmark(v: str) -> str:
    return ('<div class="stage" style="width:600px;height:140px">'
            '<div class="wm nc" style="font-size:52px;letter-spacing:2px;white-space:nowrap">RETRO<b>TARROS</b></div>'
            '</div>')


# ───────────────────────── ESPALDA ─────────────────────────

def espalda_stacked(v: str) -> str:
    return ('<div class="stage" style="width:1100px;height:1320px">'
            + '<div class="halo" style="width:880px;height:880px;top:60px"></div>'
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
  <g stroke="{PU}" stroke-width="3" {'opacity="0.95"' if v == 'dark' else 'opacity="0.9"'}>
    <line x1="550" y1="790" x2="550" y2="980"/>
    <line x1="550" y1="790" x2="250" y2="980"/><line x1="550" y1="790" x2="850" y2="980"/>
    <line x1="550" y1="790" x2="-40" y2="980"/><line x1="550" y1="790" x2="1140" y2="980"/>
    <line x1="115" y1="828" x2="985" y2="828"/>
    <line x1="10" y1="878" x2="1090" y2="878"/>
    <line x1="-90" y1="940" x2="1190" y2="940"/>
  </g>
</svg>
<div class="halo" style="width:640px;height:640px;top:200px"></div>
<div style="position:absolute;top:280px;z-index:2;display:flex;justify-content:center;width:100%">'''
            + mascota_svg("neutral", 380) + '''</div>
<div style="position:absolute;bottom:120px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm" style="font-size:118px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag" style="font-size:23px;letter-spacing:6px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
</div>
</div>''')


def espalda_crt(v: str) -> str:
    ink = INK[v]
    scan = ''.join(f'<rect x="120" y="{210 + i * 56}" width="860" height="6" fill="{PU}" opacity="0.30"/>'
                   for i in range(11))
    glitch = (f'<rect x="120" y="392" width="860" height="26" fill="{MG}" opacity="0.55"/>'
              f'<rect x="120" y="430" width="430" height="14" fill="{PU}" opacity="0.6"/>'
              f'<rect x="640" y="540" width="340" height="18" fill="{YE}" opacity="0.45"/>')
    return (f'''<div class="stage" style="width:1100px;height:1380px">
<svg width="1100" height="960" viewBox="0 0 1100 960" style="z-index:1" xmlns="http://www.w3.org/2000/svg">
  <rect x="70" y="120" width="960" height="700" rx="36" fill="{PU_DK}" stroke="{PU}" stroke-width="6"/>
  <rect x="110" y="160" width="880" height="620" rx="20" fill="{SCREEN}"/>
  <rect x="135" y="185" width="830" height="570" fill="none" stroke="{MG}" stroke-width="7"/>
  {scan}{glitch}
  <circle cx="100" cy="100" r="20" fill="{MG}"/>
  <rect x="240" y="820" width="120" height="56" fill="{PU}"/>
  <rect x="740" y="820" width="120" height="56" fill="{PU}"/>
  <g font-family="'Press Start 2P'" font-size="40" fill="{YE}">
    <text x="550" y="500" text-anchor="middle">EN VIVO</text>
  </g>
</svg>
<div style="position:absolute;bottom:170px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm nc" style="font-size:118px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag nc" style="font-size:23px;letter-spacing:6px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
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
<div class="halo" style="width:560px;height:560px;top:130px"></div>
<div style="margin-top:60px;z-index:2">''' + mascota_svg("guino", 560) + f'''</div>
<div class="px" style="font-size:64px;color:{acc};margin-top:80px;letter-spacing:4px">PRESS START</div>
<div class="px" style="font-size:30px;color:{PU};margin-top:40px;letter-spacing:6px">INSERT COIN(S)</div>
<div style="margin-top:90px;z-index:2;display:flex;flex-direction:column;align-items:center">
  <div class="wm" style="font-size:108px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
</div>
</div>''')


# ───────────────────────── motivos del universo del canal ─────────────────────────

def _gameboy_svg(w: int) -> str:
    """Game Boy synthwave: cuerpo oscuro borde cyan, pantalla con cara TarroBot,
    cruceta, botones A/B magenta, START/SELECT, parlante. viewBox 0 0 300 480."""
    h = int(w * 480 / 300)
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 300 480" xmlns="http://www.w3.org/2000/svg" style="z-index:2">
  <rect x="10" y="10" width="280" height="460" rx="26" fill="{PU_DK}" stroke="{PU}" stroke-width="7"/>
  <rect x="34" y="44" width="232" height="180" rx="12" fill="#1a1330"/>
  <rect x="60" y="64" width="180" height="140" rx="4" fill="{SCREEN}"/>
  <rect x="68" y="72" width="164" height="124" fill="none" stroke="{MG}" stroke-width="3"/>
  <rect x="100" y="104" width="26" height="26" fill="{YE}"/>
  <rect x="174" y="104" width="26" height="26" fill="{YE}"/>
  <rect x="109" y="111" width="9" height="12" fill="{SCREEN}"/>
  <rect x="183" y="111" width="9" height="12" fill="{SCREEN}"/>
  <rect x="118" y="158" width="64" height="12" fill="{YE}"/>
  <circle cx="48" cy="54" r="5" fill="{MG}"/>
  <text x="150" y="242" text-anchor="middle" font-family="'Press Start 2P'" font-size="13" fill="{YE}" letter-spacing="3">RETROTARROS</text>
  <g fill="{PU}">
    <rect x="46" y="288" width="22" height="62" rx="4"/>
    <rect x="26" y="308" width="62" height="22" rx="4"/>
  </g>
  <circle cx="216" cy="330" r="20" fill="{MG}"/>
  <circle cx="262" cy="304" r="20" fill="{MG}"/>
  <text x="216" y="366" text-anchor="middle" font-family="'Press Start 2P'" font-size="11" fill="{YE}">B</text>
  <text x="262" y="340" text-anchor="middle" font-family="'Press Start 2P'" font-size="11" fill="{YE}">A</text>
  <rect x="96" y="394" width="44" height="11" rx="5" fill="{PU}" transform="rotate(-22 118 399)"/>
  <rect x="160" y="394" width="44" height="11" rx="5" fill="{PU}" transform="rotate(-22 182 399)"/>
  <g stroke="{MG}" stroke-width="7" stroke-linecap="round">
    <line x1="216" y1="416" x2="252" y2="452"/>
    <line x1="234" y1="408" x2="270" y2="444"/>
    <line x1="252" y1="400" x2="288" y2="436"/>
  </g>
</svg>'''


def pecho_gameboy(v: str) -> str:
    return ('<div class="stage" style="width:340px;height:560px">'
            + _gameboy_svg(280) + '</div>')


def espalda_gameboy(v: str) -> str:
    return ('<div class="stage" style="width:1100px;height:1500px;gap:0">'
            + _gameboy_svg(620)
            + '<div class="wm" style="font-size:104px;letter-spacing:4px;margin-top:64px;white-space:nowrap">RETRO<b>TARROS</b></div>'
            + f'<div class="tag" style="font-size:24px;letter-spacing:7px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>'
            + '</div>')


def espalda_wordmark_synthwave(v: str) -> str:
    glow = 'filter="url(#g2)"' if v == "dark" else ''
    # sol de franjas gigante + wordmark cruzandolo + grid abajo. Sin mascota.
    return (f'''<div class="stage" style="width:1200px;height:1400px">
<svg width="1200" height="1400" viewBox="0 0 1200 1400" style="position:absolute;inset:0;z-index:1" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sun2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{YE}"/><stop offset="0.5" stop-color="{MG}"/><stop offset="1" stop-color="{MG}"/>
    </linearGradient>
    <mask id="slits2">
      <rect width="1200" height="1400" fill="white"/>
      <rect x="0" y="600" width="1200" height="20" fill="black"/>
      <rect x="0" y="664" width="1200" height="28" fill="black"/>
      <rect x="0" y="744" width="1200" height="36" fill="black"/>
      <rect x="0" y="840" width="1200" height="44" fill="black"/>
    </mask>
    <filter id="g2"><feDropShadow dx="0" dy="0" stdDeviation="16" flood-color="{MG}" flood-opacity="0.5"/></filter>
  </defs>
  <circle cx="600" cy="560" r="430" fill="url(#sun2)" mask="url(#slits2)" {glow}/>
  <g stroke="{PU}" stroke-width="3" opacity="0.95">
    <line x1="600" y1="1020" x2="600" y2="1400"/>
    <line x1="600" y1="1020" x2="260" y2="1400"/><line x1="600" y1="1020" x2="940" y2="1400"/>
    <line x1="600" y1="1020" x2="-120" y2="1400"/><line x1="600" y1="1020" x2="1320" y2="1400"/>
    <line x1="140" y1="1090" x2="1060" y2="1090"/>
    <line x1="20" y1="1190" x2="1180" y2="1190"/>
    <line x1="-140" y1="1330" x2="1340" y2="1330"/>
  </g>
</svg>
<div style="position:absolute;top:760px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm nc" style="font-size:138px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag nc" style="font-size:25px;letter-spacing:7px;margin-top:30px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
</div>
</div>''')


def espalda_tarrovision(v: str) -> str:
    # TarroVision fiel a los decks: cuerpo oscuro, LED magenta, marca amarilla,
    # perillas y parlante; en pantalla, atardecer synthwave.
    return (f'''<div class="stage" style="width:1100px;height:1400px">
<svg width="1020" height="900" viewBox="0 0 1020 900" style="z-index:2" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="body" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2a1a52"/><stop offset="1" stop-color="#160d2e"/>
    </linearGradient>
    <linearGradient id="sun3" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{YE}"/><stop offset="1" stop-color="{MG}"/>
    </linearGradient>
    <mask id="slits3">
      <rect width="1020" height="900" fill="white"/>
      <rect x="120" y="430" width="780" height="12" fill="black"/>
      <rect x="120" y="474" width="780" height="16" fill="black"/>
      <rect x="120" y="528" width="780" height="20" fill="black"/>
    </mask>
  </defs>
  <rect x="20" y="20" width="980" height="760" rx="34" fill="url(#body)" stroke="{PU}" stroke-width="5"/>
  <circle cx="84" cy="78" r="11" fill="{MG}"/>
  <text x="510" y="92" text-anchor="middle" font-family="'Press Start 2P'" font-size="26" fill="{YE}" letter-spacing="8">TARROVISION</text>
  <text x="924" y="90" text-anchor="end" font-family="'Press Start 2P'" font-size="15" fill="{PU}">CH-86</text>
  <rect x="80" y="130" width="860" height="540" rx="18" fill="#241a3d"/>
  <rect x="104" y="152" width="812" height="496" rx="14" fill="{SCREEN}"/>
  <g mask="url(#slits3)">
    <circle cx="510" cy="430" r="200" fill="url(#sun3)"/>
  </g>
  <g stroke="{PU}" stroke-width="2.4" opacity="0.95">
    <line x1="510" y1="560" x2="510" y2="648"/>
    <line x1="510" y1="560" x2="330" y2="648"/><line x1="510" y1="560" x2="690" y2="648"/>
    <line x1="510" y1="560" x2="140" y2="648"/><line x1="510" y1="560" x2="880" y2="648"/>
    <line x1="240" y1="588" x2="780" y2="588"/>
    <line x1="160" y1="620" x2="860" y2="620"/>
  </g>
  <rect x="104" y="152" width="812" height="496" rx="14" fill="none" stroke="{MG}" stroke-width="4"/>
  <circle cx="160" cy="724" r="20" fill="#160d2e" stroke="{PU}" stroke-width="4"/>
  <circle cx="230" cy="724" r="20" fill="#101016" stroke="{MG}" stroke-width="4"/>
  <g stroke="#3a3a42" stroke-width="6" stroke-linecap="round">
    <line x1="800" y1="710" x2="930" y2="710"/>
    <line x1="800" y1="728" x2="930" y2="728"/>
    <line x1="800" y1="746" x2="930" y2="746"/>
  </g>
  <rect x="240" y="800" width="130" height="62" fill="#160d2e" stroke="{PU}" stroke-width="5"/>
  <rect x="650" y="800" width="130" height="62" fill="#160d2e" stroke="{PU}" stroke-width="5"/>
</svg>
<div style="position:absolute;bottom:130px;z-index:2;display:flex;flex-direction:column;align-items:center;width:100%">
  <div class="wm nc" style="font-size:114px;letter-spacing:4px;white-space:nowrap">RETRO<b>TARROS</b></div>
  <div class="tag nc" style="font-size:23px;letter-spacing:6px;margin-top:24px;white-space:nowrap">NOSTALGIA + JUEGOS + MUSICA</div>
</div>
</div>''')


# ───────────────────────── build ─────────────────────────

DISENOS = [
    ("pecho-mascota", pecho_mascota),
    ("pecho-wordmark", pecho_wordmark),
    ("pecho-gameboy", pecho_gameboy),
    ("espalda-stacked", espalda_stacked),
    ("espalda-synthwave", espalda_synthwave),
    ("espalda-crt", espalda_crt),
    ("espalda-arcade", espalda_arcade),
    ("espalda-gameboy", espalda_gameboy),
    ("espalda-wordmark-synthwave", espalda_wordmark_synthwave),
    ("espalda-tarrovision", espalda_tarrovision),
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
