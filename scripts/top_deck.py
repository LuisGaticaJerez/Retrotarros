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
import sys
sys.path.insert(0, str(REPO / "scripts"))
from _studio_layout import episode_category

BASE = REPO / "studio" / "rankings" / "top-mundial" / "snes-top-mundial.html"


def _tv(ch: int) -> str:
    return (
        '<div class="tarrovision">\n'
        f'          <div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>\n'
        '          <div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen"><div class="tv-noscreen-big">NO SIGNAL</div><div class="tv-noscreen-sub">Inserta gameplay aqui</div></div></div></div>\n'
        '          <div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>\n'
        '        </div>'
    )


def _slug(s: str) -> str:
    import re as _re
    s = s.lower()
    for a, b in {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n","ü":"u"}.items():
        s = s.replace(a, b)
    return _re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _notas(bloque: dict | None) -> str:
    """<aside class="notas"> por slide -- capa de teleprompter (tecla N), NUNCA
    sale en capture-slides.py. bloque = {'titulo':.., 'lineas':[...], 'cue': '...'}.
    Debe dar MAS info de la que ya esta en pantalla (regla Luis 2026-06-15)."""
    if not bloque:
        return ""
    titulo = _esc(bloque.get("titulo", "NOTAS"))
    lineas = "".join(f'<div class="n-line">{_esc(t)}</div>' for t in bloque.get("lineas", []))
    cue = f'<div class="n-cue">{_esc(bloque["cue"])}</div>' if bloque.get("cue") else ""
    return f'<aside class="notas"><h4>{titulo}</h4>{lineas}{cue}</aside>'


def _auto_img(it: dict, out_slug: str) -> None:
    """Si no hay 'img', busca <categoria-episodio>/img/<out_slug>/<slug(title)>.jpg
    -- relativo a donde el HTML realmente aterriza (episode_category), no a la
    raiz plana de studio/. Bug historico: quedo apuntando a la raiz plana tras
    la migracion de carpetas por categoria (2026-07-29, Luis lo detecto porque
    las cajas de Atari 2600 no cargaban en la captura)."""
    if it.get("img"):
        return
    cand = REPO / "studio" / episode_category(out_slug) / "img" / out_slug / f"{_slug(it['title'])}.jpg"
    if cand.exists():
        it["img"] = f"img/{out_slug}/{_slug(it['title'])}.jpg"


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


def _left(it: dict) -> str:
    """Lado izquierdo del head: posicion (#N), etiqueta (rarezas) o HOLY GRAIL."""
    if it.get("grial"):
        return ('<div class="game-pos mg" style="font-size:34px;letter-spacing:3px;">'
                '<span class="hash" style="font-size:14px;">HOLY</span> GRAIL</div>')
    if it.get("badge_text"):
        color = it.get("color", "mg")
        return (f'<div class="game-pos {color}" style="font-size:24px;letter-spacing:2px;line-height:1.15;">'
                f'{it["badge_text"]}</div>')
    pos = it["pos"]
    color = "mg" if pos <= 3 else "cy"
    return f'<div class="game-pos {color}"><span class="hash">#</span>{pos}</div>'


def _price_of(it: dict):
    """Extrae el precio (USD ...) de price / precio_short / meta. None si no hay."""
    if it.get("price"):
        return str(it["price"]).strip()
    src = it.get("precio_short") or it.get("meta") or ""
    m = re.search(r"USD[\s ]*[\d.,]+\s*\+?", src)
    if not m:
        return None
    return re.sub(r"\s+", " ", m.group(0)).strip()


def _right(it: dict) -> str:
    """Lado derecho del head. En precios: PRECIO grande. Si no, etiqueta de bloque."""
    price = _price_of(it)
    if price:
        return f'<div class="game-price">{price}</div>'
    if it.get("block_label"):
        color = "mg" if (not it.get("badge_text") and it.get("pos", 99) <= 3) else "cy"
        return f'<div class="game-block-label {color}">{it["block_label"]}</div>'
    if it.get("badge_text") or it.get("grial"):
        return ""  # rarezas/grial sin precio (ej. especiales): sin etiqueta derecha
    pos = it["pos"]
    podio = pos <= 3
    color = "mg" if podio else "cy"
    label = "EL TRONO" if pos == 1 else ("PODIO" if podio else "TOP")
    return f'<div class="game-block-label {color}">{label}</div>'


def _slide_item(num: int, it: dict, consola: str, ch: int | None = None) -> str:
    ch = ch if ch is not None else it.get("pos", 1)
    meta = it.get("meta") or " · ".join(
        str(x) for x in [consola, it.get("ano"), (it.get("editor") or "").upper()] if x)
    head = _left(it) + _right(it)
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
        f'{_notas(it.get("notas"))}'
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
        f'{_notas(p.get("notas"))}'
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
        f'{_notas(d.get("notas"))}'
        '  </section>'
    )


def generar_top(data: dict, out_slug: str) -> Path:
    base = BASE.read_text(encoding="utf-8")
    head = base[: base.index("<body>") + len("<body>")]
    foot = base[base.index('<nav class="footer">'):]

    # CSS del PRECIO grande en la esquina superior derecha (top de precios)
    # + CAPA DE NOTAS DE LECTURA (teleprompter, tecla N) -- regla obligatoria del
    # canal para HTML de ranking del formato nuevo (CLAUDE.md, patron psvita-top-mundial.html).
    # top_deck.py nunca la tuvo implementada hasta este fix (Luis 2026-08-06: "no
    # pusiste las notas" en los episodios de Atari 2600).
    price_css = (
        "<style>\n"
        ".game-price{font-family:'Orbitron';font-weight:900;font-size:48px;line-height:1;"
        "color:var(--ye);text-shadow:3px 3px 0 #000, 0 0 26px rgba(255,210,63,.7);"
        "letter-spacing:1px;white-space:nowrap;border:3px solid var(--ye);"
        "padding:8px 18px;border-radius:6px;background:rgba(255,210,63,.07);align-self:flex-start}\n"
        ".notas{position:absolute;top:0;right:0;width:460px;height:100%;z-index:150;display:none;"
        "flex-direction:column;gap:10px;padding:26px 22px 30px;overflow-y:auto;"
        "background:linear-gradient(90deg,rgba(6,3,15,.55) 0%,rgba(6,3,15,.96) 26%);"
        "border-left:2px solid var(--ye);backdrop-filter:blur(2px)}\n"
        "body.read-mode .slide.active .notas{display:flex}\n"
        ".notas h4{font-family:'Press Start 2P';font-size:9px;color:var(--ye);letter-spacing:2px;margin-top:4px}\n"
        ".notas h4:first-child{margin-top:0}\n"
        ".notas .n-line{font-family:'Share Tech Mono';font-size:14.5px;line-height:1.5;"
        "color:rgba(255,255,255,.92);border-left:3px solid var(--cy);padding:3px 0 3px 11px}\n"
        ".notas .n-cue{border-left-color:var(--mg);color:var(--ye)}\n"
        ".notas .n-cue b{color:#fff}\n"
        ".read-indicator{position:fixed;top:64px;right:16px;z-index:300;font-family:'Press Start 2P';"
        "font-size:8px;color:#000;background:var(--ye);padding:6px 10px;border-radius:3px;display:none;"
        "box-shadow:0 0 14px rgba(255,210,63,.5)}\n"
        "body.read-mode .read-indicator{display:block}\n"
        "</style>\n</head>"
    )
    head = head.replace("</head>", price_css, 1)
    head += '\n<div class="read-indicator">● MODO LECTURA (N)</div>\n'

    consola = data.get("consola", "NES")
    slides = []
    n = 1
    slides.append(_slide_portada(n, data)); n += 1
    slides.append(_slide_divider(n, data["intro"])); n += 1
    for it in data["items"]:           # ya ordenados #10 -> #1
        _auto_img(it, out_slug)
        slides.append(_slide_item(n, it, consola)); n += 1
    # Apartado RAREZAS (variantes / no-retail) - opcional
    ch = 1
    if data.get("rarezas"):
        if data.get("rarezas_divider"):
            slides.append(_slide_divider(n, data["rarezas_divider"])); n += 1
        for it in data["rarezas"]:
            _auto_img(it, out_slug)
            slides.append(_slide_item(n, it, consola, ch=ch)); n += 1; ch += 1
    # SANTO GRIAL - opcional (slide unico)
    if data.get("grial"):
        g = dict(data["grial"]); g["grial"] = True
        _auto_img(g, out_slug)
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

    # Nav-hint + script: agregar boton/tecla N para el modo lectura (notas). El BASE
    # (snes-top-mundial.html) no lo trae, asi que se inyecta aca por texto.
    foot = foot.replace(
        '<div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR</div>',
        '<div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR · '
        '<kbd id="notasBtn" style="cursor:pointer" title="Mostrar/ocultar notas">N</kbd> NOTAS</div>',
        1,
    )
    foot = foot.replace(
        "  if (e.key === 'End') { go(total - 1); }\n});",
        "  if (e.key === 'End') { go(total - 1); }\n"
        "  if (e.key === 'n' || e.key === 'N') { setRead(!document.body.classList.contains('read-mode')); }\n"
        "});\n"
        "function setRead(on) { document.body.classList.toggle('read-mode', on); }\n"
        "if (new URLSearchParams(location.search).get('notas') === '1') setRead(true);\n"
        "const notasBtn = document.getElementById('notasBtn');\n"
        "if (notasBtn) notasBtn.addEventListener('click', () => setRead(!document.body.classList.contains('read-mode')));",
        1,
    )

    out_dir = REPO / "studio" / episode_category(out_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
    out.write_text(head + hdr + foot, encoding="utf-8")
    return out
