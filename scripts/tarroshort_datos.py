#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tarroshort_datos.py — Genera un TarroShort de DATOS CURIOSOS conducido por TarroBot.

Lane nueva (distinta a los tarroshorts derivados de un episodio top/coleccion):
TarroBot presenta un TEMA libre, suelta 5 datos y REACCIONA al gameplay que se
muestra en cada TarroVision (placeholder para meter el video en CapCut).

Dos modos (flag "modo"):
  - "countdown": ranking #5 -> #1 con rank-badge (ej. "Los 5 Zelda mas feos").
  - "lista":     5 datos sueltos con etiqueta "DATO N" (ej. "5 datos locos de Zelda").

Clona el CSS/JS canonico de studio/_template-tarroshort.html (1080x1920, safe zones).
La investigacion (datos + reacciones) se cura a mano en el driver .cache/gen_*.py.

Salidas:
  - studio/tarroshort-<slug>.html        (deck vertical para grabar/renderizar)
  - studio/shorts/guion-<slug>.txt       (lineas habladas de TarroBot para el TTS)

Uso (desde un driver):
    from tarroshort_datos import generar_short_datos
    generar_short_datos(DATA, "datos-zelda-feos")
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "studio" / "_template-tarroshort.html"


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _slide_intro(d: dict) -> str:
    intro = d["intro"]
    pre = _esc(intro.get("pre", "RETROTARROS"))
    # titulo: parte fija + parte resaltada en magenta
    t_pre = _esc(intro.get("titulo_pre", ""))
    t_mg = _esc(intro.get("titulo_mg", ""))
    if t_pre:
        titulo = f'{t_pre}<br><span class="mg">{t_mg}</span>'
    else:
        titulo = f'<span class="mg">{t_mg}</span>'
    saludo = _esc(intro.get("saludo", ""))
    return (
        '  <section class="slide active intro">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        f'    <div class="pre">{pre}</div>\n'
        f'    <div class="titulo">{titulo}</div>\n'
        f'    <div class="saludo">{saludo}</div>\n'
        '  </section>'
    )


def _slide_item(d: dict, it: dict, idx: int) -> str:
    modo = d.get("modo", "countdown")
    # marcador superior derecho: rank-badge (countdown) o etiqueta (lista)
    if modo == "countdown":
        rank = it.get("rank", "")
        marca = f'<div class="rank-badge"><span class="hash">#</span>{rank}</div>'
    else:
        tag = _esc(it.get("tag", f"DATO {idx}"))
        marca = f'<div class="item-tag">{tag}</div>'

    foto = it.get("foto", "")
    img = (f'<img src="{foto}" alt="" onerror="this.style.display=\'none\'">'
           if foto else "")
    name = _esc(it.get("name", ""))
    meta = _esc(it.get("meta", ""))
    linea = _esc(it.get("linea", ""))
    meta_html = f'    <div class="item-meta">{meta}</div>\n' if meta else ""
    return (
        '  <section class="slide item">\n'
        '    <div class="item-top">\n'
        '      <div class="tb-mini"><svg class="tb-mascot"><use href="#tarrobot-mascot"/></svg></div>\n'
        f'      {marca}\n'
        '    </div>\n'
        '    <!-- TV: marco vacio. Aca va el gameplay en CapCut. -->\n'
        f'    <div class="item-photo">{img}</div>\n'
        f'    <div class="item-name">{name}</div>\n'
        f'{meta_html}'
        f'    <div class="item-line">{linea}</div>\n'
        '  </section>'
    )


def _slide_cierre(d: dict) -> str:
    c = d["cierre"]
    cta_pre = _esc(c.get("cta_pre", "SIGUE A"))
    cta_mg = _esc(c.get("cta_mg", "RETROTARROS"))
    sub = _esc(c.get("sub", ""))
    return (
        '  <section class="slide cierre">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        f'    <div class="cta">{cta_pre} <span class="mg">{cta_mg}</span></div>\n'
        f'    <div class="sub">{sub}</div>\n'
        '  </section>'
    )


def _guion(d: dict, slug: str) -> str:
    """Texto plano con las lineas habladas de TarroBot, en orden, para el TTS."""
    L = [f"GUION TARROBOT — {d['intro'].get('titulo_mg','')} ({slug})", ""]
    L.append("[INTRO]")
    L.append(d["intro"].get("saludo", ""))
    L.append("")
    for i, it in enumerate(d["items"], start=1):
        etq = (f"#{it.get('rank','')}" if d.get("modo") == "countdown"
               else it.get("tag", f"DATO {i}"))
        L.append(f"[{etq}] {it.get('name','')}")
        L.append(it.get("linea", ""))
        L.append("")
    L.append("[CIERRE]")
    L.append(d["cierre"].get("sub", ""))
    L.append("")
    return "\n".join(L)


def generar_short_datos(data: dict, slug: str) -> Path:
    base = BASE.read_text(encoding="utf-8")
    head = base[: base.index("<body>") + len("<body>")]
    # bloque de la mascota (symbol SVG) — desde el comentario hasta su </svg>
    m0 = base.index("<!-- Mascota TarroBot")
    m1 = base.index("</svg>", base.index("</symbol>")) + len("</svg>")
    mascota = base[m0:m1]
    foot = base[base.index('<nav class="footer">'):]

    items = data["items"]
    slides = [_slide_intro(data)]
    for i, it in enumerate(items, start=1):
        slides.append(_slide_item(data, it, i))
    slides.append(_slide_cierre(data))

    # title del documento
    tema = data["intro"].get("titulo_mg", slug)
    head = re.sub(r"<title>.*?</title>",
                  f"<title>RETROTARROS · TARROSHORT · {tema}</title>", head, flags=re.DOTALL)

    deck = ('\n\n' + mascota + '\n\n<div class="deck" id="deck">\n\n'
            + "\n\n".join(slides) + '\n\n</div>\n\n')

    out = REPO / "studio" / f"tarroshort-{slug}.html"
    out.write_text(head + deck + foot, encoding="utf-8")

    # guion para TTS
    gdir = REPO / "studio" / "shorts"
    gdir.mkdir(parents=True, exist_ok=True)
    gout = gdir / f"guion-{slug}.txt"
    gout.write_text(_guion(data, slug), encoding="utf-8")

    print("OK ->", out)
    print("GUION ->", gout)
    print("slides:", len(slides), "| modo:", data.get("modo", "countdown"))
    return out
