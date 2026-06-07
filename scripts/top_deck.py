"""
top_deck.py - Retrotarros Studio Suite
======================================
Genera el HTML deck de un episodio "Top 10" (mundial/precios) clonando el estilo
canonico del canal. Reusa el CSS/JS EXACTO de studio/snes-top-mundial.html y
reconstruye el contenido desde un dict de datos.

Estructura (identica a snes-top-mundial / -precios):
  01 PORTADA -> 02 DIVIDER intro -> 10 slides HIBRIDAS (#10..#1)
  -> DIVIDER analisis -> DIVIDER cliffhanger

Sin box art? usa cart-fallback (etiqueta de color con el nombre) en vez de <img>.
Para precios, cada item puede traer "precio" (se muestra como block-label mg).

Uso:
  from top_deck import generar_top
  generar_top(DATA, "nes-top-mundial")

Sin tildes en el HTML (regla de assets visuales del canal). La ñ si se permite.
"""
from __future__ import annotations
import re
from pathlib import Path


def _repo() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent.parent] + list(here.parents):
        if (p / "studio").is_dir() and (p / "scripts").is_dir():
            return p
    return here.parent.parent


REPO = _repo()
BASE = REPO / "studio" / "snes-top-mundial.html"


def _tv(ch: int) -> str:
    return (
        '<div class="tarrovision">\n'
        f'          <div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>\n'
        '          <div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen"><div class="tv-noscreen-big">NO SIGNAL</div><div class="tv-noscreen-sub">Inserta gameplay aqui</div></div></div></div>\n'
        '          <div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>\n'
        '        </div>'
    )


def _cart(it: dict, consola: str) -> str:
    """Cartucho con etiqueta de color (cart-fallback) o imagen si hay 'img'."""
    lb = it.get("lb", "lb-default")
    if it.get("img"):
        img = it["img"]
        body = (f'<div class="cart-img-wrap {lb}"><img class="cart-img-bg" src="{img}" alt="" aria-hidden="true">'
                f'<img src="{img}" alt="{it["title"]} box art"></div>')
    else:
        sub = it.get("fallback_sub", consola)
        body = (f'<div class="cart-img-wrap {lb}"><div class="cart-fallback">'
                f'<div class="title">{it["title"]}</div><div class="sub">{sub}</div></div></div>')
    return ('<div class="cart">\n'
            f'          {body}\n'
            f'          <div class="cart-console">{consola}</div>\n'
            '        </div>')


def _badge(it: dict) -> str:
    """Posicion + etiqueta de bloque. Podio (#1-3) en mg, resto cy.
    Para precios, label puede ser el precio."""
    pos = it["pos"]
    podio = pos <= 3
    color = "mg" if podio else "cy"
    label = it.get("block_label")
    if not label:
        if pos == 1:
            label = "EL TRONO"
        elif podio:
            label = "PODIO"
        else:
            label = "TOP"
    return (f'<div class="game-pos {color}"><span class="hash">#</span>{pos}</div>'
            f'<div class="game-block-label {color}">{label}</div>')


def _badge_text(it: dict) -> str:
    """Badge de texto (rarezas/grial): game-pos con label en vez de #numero."""
    color = it.get("color", "mg")
    if it.get("grial"):
        return ('<div class="game-pos mg" style="font-size:34px;letter-spacing:3px;">'
                '<span class="hash" style="font-size:14px;">HOLY</span> GRAIL</div>')
    txt = it["badge_text"]
    return (f'<div class="game-pos {color}" style="font-size:24px;letter-spacing:2px;line-height:1.15;">'
            f'{txt}</div>')


def _slide_item(num: int, it: dict, consola: str, ch: int | None = None) -> str:
    ch = ch if ch is not None else it.get("pos", 1)
    meta = it.get("meta") or " · ".join(
        str(x) for x in [consola, it.get("ano"), (it.get("editor") or "").upper()] if x)
    head = _badge_text(it) if (it.get("badge_text") or it.get("grial")) else _badge(it)
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="slide-hybrid">\n'
        f'      <div class="hybrid-head">{head}</div>\n'
        '      <div class="hybrid-body">\n'
        f'        <div class="cart-wrap">{_cart(it, consola)}</div>\n'
        f'        <div class="tv-wrap">{_tv(ch)}</div>\n'
        '      </div>\n'
        f'      <div class="hybrid-title"><div class="game-title">{it["title"]}</div><div class="game-meta">{meta}</div></div>\n'
        f'      <div class="game-why"><span class="lbl">{it.get("why_label","▶ POR QUE")}</span>{it["why"]}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _slide_portada(num: int, data: dict) -> str:
    p = data["portada"]
    return (
        '  <section class="slide active">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="portada">\n'
        f'      <div class="ep-tag">{p["tag"]}</div>\n'
        f'      <div class="ep-title">{p["title"]}</div>\n'
        f'      <div class="ep-sub">{p["sub"]}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _slide_divider(num: int, d: dict) -> str:
    color = d.get("color", "cy")
    style = f' style="font-size:{d["title_size"]}px;"' if d.get("title_size") else ""
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="divider">\n'
        f'      <div class="pre {color}">{d["pre"]}</div>\n'
        f'      <div class="title {color}"{style}>{d["title"]}</div>\n'
        f'      <div class="sub">{d["sub"]}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def generar_top(data: dict, out_slug: str) -> Path:
    base = BASE.read_text(encoding="utf-8")
    head = base[: base.index("<body>") + len("<body>")]
    foot = base[base.index('<nav class="footer">'):]

    consola = data.get("consola", "NES")
    slides = []
    n = 1
    slides.append(_slide_portada(n, data)); n += 1
    slides.append(_slide_divider(n, data["intro"])); n += 1
    for it in data["items"]:           # ya ordenados #10 -> #1
        slides.append(_slide_item(n, it, consola)); n += 1
    # Apartado RAREZAS (variantes / no-retail) - opcional
    ch = 1
    if data.get("rarezas"):
        if data.get("rarezas_divider"):
            slides.append(_slide_divider(n, data["rarezas_divider"])); n += 1
        for it in data["rarezas"]:
            slides.append(_slide_item(n, it, consola, ch=ch)); n += 1; ch += 1
    # SANTO GRIAL - opcional (slide unico)
    if data.get("grial"):
        g = dict(data["grial"]); g["grial"] = True
        slides.append(_slide_item(n, g, consola, ch=ch)); n += 1
    slides.append(_slide_divider(n, data["analisis"])); n += 1
    slides.append(_slide_divider(n, data["cliffhanger"])); n += 1

    hdr = (
        '\n\n<header>\n'
        '  <div class="hdr-logo">RETROTARROS</div>\n'
        f'  <div class="hdr-tag">{data["header_tag"]}</div>\n'
        '  <div class="hdr-rec"><div class="dot"></div>EN VIVO</div>\n'
        '</header>\n\n'
        '<div class="deck" id="deck">\n\n'
        + "\n\n".join(slides) +
        '\n\n</div>\n\n'
    )
    head = re.sub(r"<title>.*?</title>",
                  f'<title>RETROTARROS · {data["doc_title"]}</title>', head, flags=re.DOTALL)
    out = REPO / "studio" / f"{out_slug}.html"
    out.write_text(head + hdr + foot, encoding="utf-8")
    return out
