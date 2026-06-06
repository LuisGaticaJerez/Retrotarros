"""
branding_tarrobot.py - Retrotarros Studio Suite

Genera el KIT DE BRANDING de TarroBot (la mascota TV synthwave) a partir del
SVG vectorial canonico. Todo en marca: paleta cyan/magenta/amarillo, fuentes
Orbitron + Press Start 2P. Reproducible (HTML + Playwright -> PNG).

Salida: studio/branding/tarrobot/
  avatar-800.png                      avatar / PFP redes (linea V2: anillo + pill)
  logo-horizontal-dark.png/-transparent.png
  logo-stacked-dark.png/-transparent.png
  expresiones/<estado>.png            sticker pack (transparente, 512)
  banner-youtube-2560x1440.png
  banner-x-1500x500.png
  post-1080.png                       plantilla post cuadrado
  story-1080x1920.png                 cover story / short
  mascota.svg                         fuente vectorial standalone
  contact-sheet.png                   hoja de contacto (preview de todo)

Uso:
  python scripts/branding_tarrobot.py            # genera todo
  python scripts/branding_tarrobot.py --sheet    # solo regenera la hoja de contacto
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
OUT = REPO / "studio" / "branding" / "tarrobot"

# ── Paleta y tipografias (sistema visual del canal) ──────────────────────
CY = "#00E5FF"   # cyan
MG = "#FF2E88"   # magenta
YE = "#FFD23F"   # amarillo
DK = "#06030f"   # fondo oscuro
SCREEN = "#0a0820"

FONTS = ("@import url('https://fonts.googleapis.com/css2?"
         "family=Orbitron:wght@700;900&family=Press+Start+2P&display=swap');")

# ── Mascota: cuerpo constante + cara parametrizable por expresion ────────
# viewBox 0 0 64 64. El cuerpo (TV cyan, pantalla, antena, patitas) no cambia;
# solo se intercambian ojos + boca segun la expresion.

def _body_back() -> str:
    return (
        f'<rect x="2" y="6" width="60" height="50" rx="3" fill="{CY}"/>'
        f'<rect x="6" y="10" width="51" height="40" rx="2" fill="{SCREEN}"/>'
        f'<rect x="8" y="12" width="47" height="36" fill="none" stroke="{MG}" stroke-width="1"/>'
    )

def _body_front() -> str:
    return (
        f'<circle cx="6" cy="5" r="2.2" fill="{MG}"/>'
        f'<rect x="14" y="56" width="8" height="5" fill="{CY}"/>'
        f'<rect x="42" y="56" width="8" height="5" fill="{CY}"/>'
    )

# Caras: cada una devuelve los elementos de ojos + boca (dentro de la pantalla).
FACES = {
    "neutral": (
        f'<rect x="16" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="38" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="19" y="24" width="3" height="4" fill="{SCREEN}"/>'
        f'<rect x="41" y="24" width="3" height="4" fill="{SCREEN}"/>'
        f'<rect x="22" y="38" width="20" height="4" fill="{YE}"/>'
    ),
    "feliz": (
        f'<rect x="16" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="38" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="19" y="24" width="3" height="4" fill="{SCREEN}"/>'
        f'<rect x="41" y="24" width="3" height="4" fill="{SCREEN}"/>'
        f'<path d="M21 37 Q32 46 43 37" fill="none" stroke="{YE}" stroke-width="3.4" stroke-linecap="round"/>'
    ),
    "wow": (
        f'<circle cx="20" cy="26" r="4.6" fill="{YE}"/>'
        f'<circle cx="42" cy="26" r="4.6" fill="{YE}"/>'
        f'<circle cx="20" cy="26" r="1.9" fill="{SCREEN}"/>'
        f'<circle cx="42" cy="26" r="1.9" fill="{SCREEN}"/>'
        f'<circle cx="32" cy="40" r="3.8" fill="none" stroke="{YE}" stroke-width="3"/>'
    ),
    "pensando": (
        f'<rect x="16" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="38" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="20" y="22.5" width="3" height="3" fill="{SCREEN}"/>'   # pupilas arriba (mirando)
        f'<rect x="42" y="22.5" width="3" height="3" fill="{SCREEN}"/>'
        f'<rect x="30" y="39" width="11" height="3.4" fill="{YE}"/>'      # boca corta, ladeada
    ),
    "guino": (
        f'<rect x="16" y="22" width="8" height="8" fill="{YE}"/>'         # ojo izq abierto
        f'<rect x="19" y="24" width="3" height="4" fill="{SCREEN}"/>'
        f'<rect x="38" y="26.5" width="8" height="2.6" fill="{YE}"/>'     # ojo der cerrado (linea)
        f'<path d="M24 38 Q32 43 40 38" fill="none" stroke="{YE}" stroke-width="3" stroke-linecap="round"/>'
    ),
    "sospecha": (
        f'<rect x="16" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="38" y="22" width="8" height="8" fill="{YE}"/>'
        f'<rect x="16" y="22" width="8" height="4" fill="{SCREEN}"/>'     # parpado superior
        f'<rect x="38" y="22" width="8" height="4" fill="{SCREEN}"/>'
        f'<rect x="19" y="27" width="3" height="2" fill="{SCREEN}"/>'     # pupilas bajas finas
        f'<rect x="41" y="27" width="3" height="2" fill="{SCREEN}"/>'
        f'<rect x="27" y="39" width="13" height="3.4" fill="{YE}"/>'      # boca recta, ladeada
    ),
}


def mascota_svg(face: str = "neutral", size: int = 440) -> str:
    inner = _body_back() + FACES.get(face, FACES["neutral"]) + _body_front()
    return (f'<svg class="mascot" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 64 64" width="{size}" height="{size}">{inner}</svg>')


# ── CSS base compartido por todos los assets ─────────────────────────────
CSS = f"""
{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
.stage{{position:relative;display:flex;flex-direction:column;align-items:center;
  justify-content:center;overflow:hidden}}
.bg-dark{{background:radial-gradient(circle at 50% 40%, #241046 0%, {DK} 72%)}}
.bg-wide{{background:radial-gradient(circle at 30% 45%, #241046 0%, {DK} 70%)}}
.transparent{{background:transparent}}
.grid{{position:absolute;inset:0;background-image:
  linear-gradient(rgba(0,229,255,.06) 1px,transparent 1px),
  linear-gradient(90deg,rgba(0,229,255,.06) 1px,transparent 1px);
  background-size:44px 44px}}
.mascot{{filter:drop-shadow(0 0 34px rgba(0,229,255,.55));z-index:2}}
.wm{{font-family:Orbitron;font-weight:900;color:#fff;z-index:2;
  text-shadow:0 0 18px rgba(255,46,136,.55);line-height:1}}
.wm b{{color:{CY}}}
.pill{{background:rgba(6,3,15,.55);border:3px solid {MG};border-radius:44px;
  padding:10px 34px;box-shadow:0 0 24px rgba(255,46,136,.4)}}
.ring{{position:absolute;border-radius:50%;border:6px solid rgba(0,229,255,.35);
  box-shadow:0 0 50px rgba(0,229,255,.3) inset, 0 0 40px rgba(255,46,136,.22)}}
.tag{{font-family:'Press Start 2P';color:{CY};z-index:2;
  text-shadow:0 0 12px rgba(0,229,255,.5)}}
"""


def _doc(body: str) -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


def _social_icons() -> str:
    """Fila de iconos sociales (estilo del canal): YouTube, TikTok, Instagram."""
    yt = ('<div style="width:150px;height:106px;background:#FF0000;border-radius:22px;'
          'display:flex;align-items:center;justify-content:center">'
          '<div style="width:0;height:0;border-left:38px solid #fff;'
          'border-top:24px solid transparent;border-bottom:24px solid transparent;margin-left:8px"></div></div>')
    tk = ('<div style="width:150px;height:106px;background:#000;border-radius:22px;'
          'display:flex;align-items:center;justify-content:center;position:relative">'
          '<div style="font-size:64px;color:#fff">&#9835;</div>'
          f'<div style="position:absolute;left:42px;top:24px;font-size:64px;color:{CY};opacity:.8">&#9835;</div></div>')
    ig = ('<div style="width:150px;height:106px;border-radius:22px;'
          'background:linear-gradient(45deg,#F58529,#DD2A7B,#8134AF,#515BD4);'
          'display:flex;align-items:center;justify-content:center">'
          '<div style="width:54px;height:54px;border:6px solid #fff;border-radius:16px;position:relative">'
          '<div style="width:24px;height:24px;border:5px solid #fff;border-radius:50%;'
          'position:absolute;top:9px;left:9px"></div></div></div>')
    col = '<div style="display:flex;flex-direction:column;align-items:center;gap:18px">{0}<div style="color:#fff;font-size:22px">{1}</div></div>'
    return ('<div style="display:flex;justify-content:center;gap:60px">'
            + col.format(yt, "YOUTUBE") + col.format(tk, "TIKTOK") + col.format(ig, "INSTAGRAM")
            + '</div>')


def endcard_vertical_html() -> str:
    """Endcard 1080x1920 en la plantilla del canal (pixel, REC/CH, fila social),
    con TarroBot de protagonista. Conversa con Retrotarros_EndCard_*.png."""
    NAVY = "#0e0a20"
    px = "font-family:'Press Start 2P'"
    return (
        f'<div class="stage" style="width:1080px;height:1920px;background:{NAVY};display:block;'
        f'{px}">'
        '<div style="position:absolute;inset:0;background:repeating-linear-gradient(0deg,'
        'rgba(0,0,0,.18) 0 2px,transparent 2px 4px);opacity:.4"></div>'
        f'<div style="position:absolute;top:70px;left:64px;border:3px solid {MG};padding:18px 26px;'
        f'color:{MG};font-size:26px;letter-spacing:2px;text-shadow:0 0 10px rgba(255,46,136,.6)">@RETROTARROS</div>'
        f'<div style="position:absolute;top:80px;right:230px;color:{MG};font-size:26px;display:flex;'
        f'align-items:center;gap:12px"><div style="width:18px;height:18px;border-radius:50%;background:{MG}"></div>REC</div>'
        f'<div style="position:absolute;top:80px;right:64px;color:{YE};font-size:26px">CH 04</div>'
        '<div style="position:absolute;top:300px;left:0;width:1080px;display:flex;flex-direction:column;align-items:center">'
        + mascota_svg("feliz", 520)
        + f'<div style="color:#fff;font-size:64px;letter-spacing:4px;margin-top:30px;'
        f'text-shadow:0 0 16px rgba(0,229,255,.6)">TARRO<span style="color:{CY}">BOT</span></div>'
        + f'<div style="color:{YE};font-size:22px;margin-top:22px">MODEL TB-20XX</div></div>'
        + f'<div style="position:absolute;top:1180px;left:0;width:1080px;text-align:center;color:{MG};'
        f'font-size:72px;letter-spacing:6px;text-shadow:0 0 16px rgba(255,46,136,.6)">SIGUENOS</div>'
        + f'<div style="position:absolute;top:1300px;left:180px;width:720px;height:3px;background:{MG}"></div>'
        + '<div style="position:absolute;top:1420px;left:0;width:1080px">' + _social_icons() + '</div>'
        + f'<div style="position:absolute;top:1720px;left:0;width:1080px;text-align:center;color:{MG};'
        f'font-size:52px;letter-spacing:4px;text-shadow:0 0 16px rgba(255,46,136,.6)">@RETROTARROS</div>'
        + '</div>')


def _wm(size_px: int, ls: int = 5) -> str:
    return f'<div class="wm" style="font-size:{size_px}px;letter-spacing:{ls}px">TARRO<b>BOT</b></div>'


# ── Definicion de cada asset: (archivo, w, h, transparente, html) ────────
def assets() -> list[dict]:
    a = []

    # 1) AVATAR / PFP 800 (linea V2: anillo + pill)
    a.append(dict(file="avatar-800.png", w=800, h=800, transp=False, html=(
        '<div class="stage bg-dark" style="width:800px;height:800px">'
        '<div class="ring" style="width:760px;height:760px"></div>'
        + mascota_svg("neutral", 360)
        + '<div class="wm pill" style="font-size:60px;letter-spacing:5px;margin-top:20px">TARRO<b>BOT</b></div>'
        + '</div>')))

    # 2) LOGO horizontal (mascota + wordmark) - dark y transparente
    def logo_h():
        return ('<div class="stage %BG%" style="width:1200px;height:520px;flex-direction:row;gap:40px">'
                + mascota_svg("neutral", 360)
                + '<div class="wm" style="font-size:150px;letter-spacing:6px">TARRO<b>BOT</b></div>'
                + '</div>')
    a.append(dict(file="logo-horizontal-dark.png", w=1200, h=520, transp=False,
                  html=logo_h().replace("%BG%", "bg-dark")))
    a.append(dict(file="logo-horizontal-transparent.png", w=1200, h=520, transp=True,
                  html=logo_h().replace("%BG%", "transparent")))

    # 3) LOGO apilado - dark y transparente
    def logo_s():
        return ('<div class="stage %BG%" style="width:760px;height:840px">'
                + mascota_svg("neutral", 440)
                + '<div class="wm" style="font-size:120px;letter-spacing:6px;margin-top:18px">TARRO<b>BOT</b></div>'
                + '</div>')
    a.append(dict(file="logo-stacked-dark.png", w=760, h=840, transp=False,
                  html=logo_s().replace("%BG%", "bg-dark")))
    a.append(dict(file="logo-stacked-transparent.png", w=760, h=840, transp=True,
                  html=logo_s().replace("%BG%", "transparent")))

    # 4) EXPRESIONES (sticker pack) - transparente 512
    for face in FACES:
        a.append(dict(file=f"expresiones/{face}.png", w=512, h=512, transp=True, html=(
            '<div class="stage transparent" style="width:512px;height:512px">'
            + mascota_svg(face, 440) + '</div>')))

    # 5) BANNER YouTube 2560x1440 (zona segura central ~1546x423)
    a.append(dict(file="banner-youtube-2560x1440.png", w=2560, h=1440, transp=False, html=(
        '<div class="stage bg-wide" style="width:2560px;height:1440px">'
        '<div class="grid"></div>'
        '<div style="display:flex;flex-direction:row;align-items:center;gap:60px;z-index:2">'
        + mascota_svg("feliz", 420)
        + '<div style="display:flex;flex-direction:column;align-items:flex-start">'
        + '<div class="wm" style="font-size:200px;letter-spacing:8px">TARRO<b>BOT</b></div>'
        + f'<div class="tag" style="font-size:34px;margin-top:22px;color:{YE}">LA MASCOTA DE RETROTARROS</div>'
        + '</div></div></div>')))

    # 6) BANNER X / Twitter 1500x500
    a.append(dict(file="banner-x-1500x500.png", w=1500, h=500, transp=False, html=(
        '<div class="stage bg-wide" style="width:1500px;height:500px">'
        '<div class="grid"></div>'
        '<div style="display:flex;flex-direction:row;align-items:center;gap:44px;z-index:2">'
        + mascota_svg("neutral", 300)
        + '<div style="display:flex;flex-direction:column;align-items:flex-start">'
        + '<div class="wm" style="font-size:130px;letter-spacing:6px">TARRO<b>BOT</b></div>'
        + f'<div class="tag" style="font-size:22px;margin-top:16px;color:{YE}">RETRO AL 100 POR CIENTO</div>'
        + '</div></div></div>')))

    # 7) POST cuadrado 1080
    a.append(dict(file="post-1080.png", w=1080, h=1080, transp=False, html=(
        '<div class="stage bg-dark" style="width:1080px;height:1080px">'
        '<div class="grid"></div>'
        + mascota_svg("wow", 540)
        + '<div class="wm" style="font-size:128px;letter-spacing:6px;margin-top:24px">TARRO<b>BOT</b></div>'
        + f'<div class="tag" style="font-size:26px;margin-top:22px">RETROTARROS</div>'
        + '</div>')))

    # 8) STORY / cover short 1080x1920
    a.append(dict(file="story-1080x1920.png", w=1080, h=1920, transp=False, html=(
        '<div class="stage bg-dark" style="width:1080px;height:1920px;justify-content:center;gap:10px">'
        '<div class="grid"></div>'
        '<div class="ring" style="width:880px;height:880px;top:360px"></div>'
        + mascota_svg("feliz", 520)
        + '<div class="wm" style="font-size:150px;letter-spacing:8px;margin-top:40px">TARRO<b>BOT</b></div>'
        + f'<div class="tag" style="font-size:30px;margin-top:28px">LA MASCOTA DE RETROTARROS</div>'
        + '</div>')))

    # 9) ENDCARDS YouTube 1920x1080 (pantalla final, ultimos ~20s).
    # Las zonas de video y suscripcion van VACIAS (marco/contorno) porque
    # YouTube monta los elementos clicables encima. TarroBot invita a la accion.
    def _slot(x, y, w, h):  # marco de elemento de video (16:9), interior vacio
        return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'border:4px solid {CY};border-radius:12px;box-shadow:0 0 30px rgba(0,229,255,.35);'
                f'background:rgba(6,3,15,.25)"></div>')

    def _slot_label(x, y, w, txt):
        return (f'<div class="tag" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;'
                f'text-align:center;font-size:20px;color:{YE}">{txt}</div>')

    def _subzone(x, y):  # dropzone circular para el boton de suscripcion
        return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:200px;height:200px;'
                f'border:4px dashed rgba(0,229,255,.6);border-radius:50%;'
                f'box-shadow:0 0 26px rgba(255,46,136,.3)"></div>'
                f'<div class="wm pill" style="position:absolute;left:{x-40}px;top:{y+214}px;'
                f'width:280px;text-align:center;font-size:34px;letter-spacing:3px">SUSCRIBETE</div>')

    # 9a) Endcard clasica: 2 videos a la derecha + suscripcion + mascota
    endcard_2v = (
        '<div class="stage bg-wide" style="width:1920px;height:1080px;display:block">'
        '<div class="grid"></div>'
        '<div class="wm" style="position:absolute;top:64px;left:0;width:1920px;text-align:center;'
        'font-size:104px;letter-spacing:6px">GRACIAS POR <b>VER</b></div>'
        + mascota_svg("feliz", 340).replace('class="mascot" ',
            'class="mascot" style="position:absolute;left:150px;top:560px" ')
        + _subzone(560, 600)
        + _slot(1180, 175, 620, 349) + _slot_label(1180, 138, 620, "PROXIMO VIDEO")
        + _slot(1180, 610, 620, 349) + _slot_label(1180, 573, 620, "MAS RETRO")
        + '</div>')
    a.append(dict(file="endcards/endcard-2videos.png", w=1920, h=1080, transp=False, html=endcard_2v))

    # 9b) Endcard 1 video grande + suscripcion
    endcard_1v = (
        '<div class="stage bg-wide" style="width:1920px;height:1080px;display:block">'
        '<div class="grid"></div>'
        '<div class="wm" style="position:absolute;top:64px;left:0;width:1920px;text-align:center;'
        'font-size:104px;letter-spacing:6px">SIGUE A <b>TARROBOT</b></div>'
        + mascota_svg("wow", 320).replace('class="mascot" ',
            'class="mascot" style="position:absolute;left:170px;top:600px" ')
        + _subzone(560, 640)
        + _slot(980, 230, 820, 461) + _slot_label(980, 193, 820, "MIRA ESTE VIDEO")
        + '</div>')
    a.append(dict(file="endcards/endcard-1video.png", w=1920, h=1080, transp=False, html=endcard_1v))

    # 9c) Endcard VERTICAL estilo canal (1080x1920) - conversa con redes sociales
    a.append(dict(file="endcards/endcard-vertical.png", w=1080, h=1920, transp=False,
                  html=endcard_vertical_html()))

    return a


def generar(progress=print) -> list[Path]:
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "expresiones").mkdir(parents=True, exist_ok=True)

    # guardar mascota.svg standalone (fuente)
    svg_src = mascota_svg("neutral", 512).replace('class="mascot" ', '')
    (OUT / "mascota.svg").write_text(svg_src, encoding="utf-8")

    items = assets()
    hechos: list[Path] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for it in items:
            page = browser.new_page(viewport={"width": it["w"], "height": it["h"]},
                                    device_scale_factor=1)
            page.set_content(_doc(it["html"]))
            page.wait_for_timeout(700)  # fuentes + glow
            dst = OUT / it["file"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            page.locator(".stage").screenshot(path=str(dst), omit_background=it["transp"])
            page.close()
            hechos.append(dst)
            progress(f"[branding] {it['file']}")
        browser.close()
    return hechos


def contact_sheet(progress=print) -> Path:
    """Hoja de contacto con todo el kit, para revisar de un vistazo."""
    from playwright.sync_api import sync_playwright
    files = [
        ("Avatar / PFP", "avatar-800.png"),
        ("Logo horizontal", "logo-horizontal-dark.png"),
        ("Logo apilado", "logo-stacked-dark.png"),
        ("Banner YouTube", "banner-youtube-2560x1440.png"),
        ("Banner X", "banner-x-1500x500.png"),
        ("Post 1080", "post-1080.png"),
        ("Story 1080x1920", "story-1080x1920.png"),
        ("Endcard vertical (canal)", "endcards/endcard-vertical.png"),
        ("Endcard 2 videos (YT)", "endcards/endcard-2videos.png"),
        ("Endcard 1 video (YT)", "endcards/endcard-1video.png"),
    ]
    expr = [(f, f"expresiones/{f}.png") for f in FACES]

    import base64
    def card(label, rel):
        p = OUT / rel
        b64 = base64.b64encode(p.read_bytes()).decode() if p.exists() else ""
        uri = f"data:image/png;base64,{b64}"
        return (f'<div class="card"><img src="{uri}"/><div class="lbl">{label}</div></div>')

    body = (
        f'<div class="sheet">'
        f'<div class="title">KIT BRANDING · TARRO<b style="color:{CY}">BOT</b></div>'
        f'<div class="row">' + "".join(card(l, r) for l, r in files) + '</div>'
        f'<div class="subtitle">EXPRESIONES (sticker pack)</div>'
        f'<div class="row">' + "".join(card(f.upper(), r) for f, r in expr) + '</div>'
        f'</div>')
    css = (FONTS +
           f"*{{margin:0;box-sizing:border-box}}body{{background:{DK}}}"
           ".sheet{padding:40px;width:1700px}"
           f".title{{font-family:Orbitron;font-weight:900;color:#fff;font-size:54px;"
           f"letter-spacing:4px;margin-bottom:28px;text-shadow:0 0 18px rgba(255,46,136,.5)}}"
           f".subtitle{{font-family:'Press Start 2P';color:{YE};font-size:20px;margin:34px 0 18px}}"
           ".row{display:flex;flex-wrap:wrap;gap:20px}"
           f".card{{background:#0d0820;border:2px solid rgba(0,229,255,.25);border-radius:12px;"
           f"padding:12px;display:flex;flex-direction:column;align-items:center;gap:10px}}"
           ".card img{height:200px;width:auto;border-radius:6px;background:#000}"
           f".lbl{{font-family:'Share Tech Mono',monospace;color:#cfe;font-size:15px}}")
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'

    dst = OUT / "contact-sheet.png"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1780, "height": 1400}, device_scale_factor=1)
        pg.set_content(html)
        pg.wait_for_timeout(900)
        pg.locator(".sheet").screenshot(path=str(dst))
        b.close()
    progress(f"[branding] {dst.name}")
    return dst


def main():
    ap = argparse.ArgumentParser(description="Genera el kit de branding de TarroBot")
    ap.add_argument("--sheet", action="store_true", help="solo regenera la hoja de contacto")
    args = ap.parse_args()
    try:
        if not args.sheet:
            hechos = generar()
            print(f"OK: {len(hechos)} assets en {OUT}")
        contact_sheet()
        print(f"OK: contact-sheet -> {OUT / 'contact-sheet.png'}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
