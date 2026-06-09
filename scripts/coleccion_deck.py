"""
coleccion_deck.py - Retrotarros Studio Suite
=============================================
Genera el HTML deck de un episodio "Coleccion" (panorama por categorias) clonando
el estilo canonico del canal. Reusa el CSS/JS EXACTO de un deck base existente
(studio/n64-coleccion.html) y reconstruye solo el contenido desde un dict de datos.

Estructura del deck (identica a snes/n64-coleccion):
  01 PORTADA -> 02 INDICE -> por cada categoria: PANEO + TRIPLE(3 joyas)
  -> HARDWARE -> BALANCE -> CIERRE

Uso:
  from coleccion_deck import generar_deck
  generar_deck(DATA, "nes-coleccion")     # escribe studio/nes-coleccion.html

Sin tildes en el HTML (regla de assets visuales del canal).
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
BASE = REPO / "studio" / "n64-coleccion.html"  # fuente de CSS/JS canonico


def _dots(label: str, width: int = 44) -> str:
    n = max(3, width - len(label))
    return "·" * n


def _tv(ch: int, noscreen_big: str = "", noscreen_sub: str = "") -> str:
    """Una TarroVision vacia (placeholder noscreen, para montar gameplay en post)."""
    inner = '<div class="tv-noscreen"></div>'
    if noscreen_big:
        inner = (f'<div class="tv-noscreen"><div class="tv-noscreen-big">{noscreen_big}</div>'
                 f'<div class="tv-noscreen-sub">{noscreen_sub}</div></div>')
    return (
        '<div class="tarrovision">\n'
        f'        <div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>\n'
        f'        <div class="tv-screen"><div class="tv-screen-inner">{inner}</div></div>\n'
        '        <div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>\n'
        '      </div>'
    )


def _slide_paneo(num: int, cat_idx: int, total_cats: int, name: str, count: int, ch: int) -> str:
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="slide-paneo">\n'
        '      <div class="paneo-banner">\n'
        f'        <div class="paneo-cat-num">CAT {cat_idx:02d}/{total_cats:02d}</div>\n'
        f'        <div class="paneo-cat-name">{name}</div>\n'
        f'        <div class="paneo-cat-count">{count} TITULOS</div>\n'
        '      </div>\n'
        f'      <div class="paneo-tv-wrap">{_tv(ch)}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _slide_triple(num: int, name: str, joyas: list) -> str:
    cells = []
    for i, j in enumerate(joyas, start=1):
        meta = " · ".join([str(x) for x in [j.get("ano"), j.get("editor")] if x])
        cells.append(
            '        <div class="triple-cell">\n'
            f'          <div class="tv-fit">{_tv(i)}</div>\n'
            f'          <div class="tv-namebox ye"><div class="tv-title">{j["title"]}</div><div class="tv-meta">{meta}</div></div>\n'
            '        </div>'
        )
    return (
        '  <section class="slide slide-triple">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="slide-triple-inner">\n'
        f'      <div class="triple-head"><div class="tv-block-label">{name} · 3 JOYAS DESTACADAS</div></div>\n'
        '      <div class="triple-grid">\n'
        + "\n".join(cells) + "\n"
        '      </div>\n'
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
        f'      <div class="ep-title"><span class="vs">{p["title_vs"]}</span> {p["title_rest"]}</div>\n'
        f'      <div class="ep-sub">{p["sub"]}</div>\n'
        f'      <div class="ep-count">{p["count"]}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _slide_indice(num: int, data: dict) -> str:
    cats = data["categorias"]
    total = sum(c["count"] for c in cats)
    items = []
    for i, c in enumerate(cats, start=1):
        active = " active" if i == 1 else ""
        cur = '<span class="idx-cursor">▶</span>'
        items.append(
            f'        <div class="idx-item{active}">\n'
            f'          {cur}\n'
            f'          <span class="idx-num">{i:02d}</span>\n'
            f'          <span>{c["name"]} <span class="idx-dots">{_dots(c["name"])}</span></span>\n'
            f'          <span class="idx-count">{c["count"]} TITULOS</span>\n'
            '        </div>'
        )
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="idx">\n'
        '      <div class="idx-title">SELECCIONA TU CATEGORIA</div>\n'
        '      <div class="idx-list">\n'
        + "\n".join(items) + "\n"
        '      </div>\n'
        f'      <div class="idx-total">─── {total} JUEGOS ───</div>\n'
        '      <div class="idx-hint">▶ PRESS START TO BEGIN PANORAMA</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _slide_hardware(num: int, data: dict) -> str:
    cards = []
    for h in data["hardware"]:
        cards.append(
            f'      <div class="consola-card {h["color"]}">\n'
            f'        <h3>{h["name"]}</h3>\n'
            f'        <span class="tag">{h["tag"]}</span>\n'
            f'        <p>{h["desc"]}</p>\n'
            '      </div>'
        )
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        f'    <h1>{data["hardware_titulo"]}</h1>\n'
        f'    <h2 class="mg">{data["hardware_sub"]}</h2>\n'
        '    <div class="consolas-grid">\n'
        + "\n".join(cards) + "\n"
        '    </div>\n'
        '  </section>'
    )


def _slide_balance(num: int, data: dict) -> str:
    b = data["balance"]
    row1 = "".join(
        f'<div class="num-card {c["color"]}"><h3>{c["label"]}</h3><span class="big">{c["big"]}</span><p>{c["sub"]}</p></div>'
        for c in b["row1"])
    row2 = "".join(
        f'<div class="num-card {c["color"]}"><h3>{c["label"]}</h3><span class="big">{c["big"]}</span><p>{c["sub"]}</p></div>'
        for c in b["row2"])
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <h1>BALANCE FINAL</h1>\n'
        '    <h2 class="mg">LA COLECCION EN NUMEROS</h2>\n'
        f'    <div class="numbers-grid">{row1}</div>\n'
        f'    <div class="numbers-grid" style="grid-template-columns:repeat({len(b["row2"])},1fr);max-width:880px;margin-top:18px;">{row2}</div>\n'
        '  </section>'
    )


def _slide_cierre(num: int, data: dict) -> str:
    c = data["cierre"]
    return (
        '  <section class="slide">\n'
        f'    <span class="slide-num">{num:02d}</span>\n'
        '    <div class="divider">\n'
        f'      <div class="pre cy">{c["pre"]}</div>\n'
        f'      <div class="title cy" style="font-size:58px;">{c["title"]}</div>\n'
        f'      <div class="sub">{c["sub"]}</div>\n'
        '    </div>\n'
        '  </section>'
    )


def _escribir_lista_md(data: dict, out_slug: str) -> Path:
    """Escribe docs/lista-paneo-<slug>.md con el catalogo por categoria.

    Cada categoria puede traer 'juegos' (lista completa de titulos) para el
    detalle por paneo; si no la trae, se listan solo las 3 joyas + el conteo.
    Las joyas se marcan con una estrella. Pensado para consultar/compartir al
    grabar los paneos de camara.
    """
    cats = data["categorias"]
    portada = data.get("portada", {})
    titulo = data.get("doc_title", out_slug)
    total_juegos = sum(c.get("count", len(c.get("juegos", []))) for c in cats)

    L = []
    L.append(f"# Lista de paneo · {titulo}")
    L.append("")
    L.append(f"> Catalogo completo por categoria de la coleccion **{out_slug}**.")
    L.append("> Generado automaticamente por `scripts/coleccion_deck.py` al armar el deck.")
    L.append("> La estrella marca las 3 joyas destacadas (van en TarroVision triple).")
    L.append("")
    L.append(f"**Total:** {total_juegos} juegos · {len(cats)} categorias · {len(cats)*3} joyas")
    L.append("")
    L.append("---")
    L.append("")
    def _norm(s: str) -> str:
        n = "".join(ch for ch in s.lower() if ch.isalnum())
        if n.startswith("the"):  # ignora articulo inicial (THE LEGEND OF ZELDA ~ Legend of Zelda)
            n = n[3:]
        return n

    def _common_prefix(a: str, b: str) -> int:
        n = 0
        for x, y in zip(a, b):
            if x != y:
                break
            n += 1
        return n

    for ci, c in enumerate(cats, start=1):
        juegos = c.get("juegos")
        L.append(f"## [{ci:02}] {c['name']}  ({c.get('count', len(juegos or []))})")
        L.append("")
        if juegos:
            # Emparejar cada joya curada con su juego real por mejor coincidencia
            # (las joyas vienen en mayusculas y a veces abreviadas).
            norm_juegos = [_norm(g) for g in juegos]
            joya_idx = set()
            for j in c.get("joyas", []):
                nj = _norm(j["title"])
                best, best_score = None, 0
                for i, ng in enumerate(norm_juegos):
                    if i in joya_idx:
                        continue
                    score = _common_prefix(nj, ng)
                    if score > best_score:
                        best, best_score = i, score
                if best is not None and best_score >= 5:
                    joya_idx.add(best)
            joyas_en_lista = [g for i, g in enumerate(juegos) if i in joya_idx]
            resto = [g for i, g in enumerate(juegos) if i not in joya_idx]
            for g in joyas_en_lista:
                L.append(f"- ⭐ {g}")
            for g in resto:
                L.append(f"- {g}")
        else:
            for j in c.get("joyas", []):
                L.append(f"- ⭐ {j['title']}")
            otros = c.get("count", 0) - len(c.get("joyas", []))
            if otros > 0:
                L.append(f"- _(+{otros} mas en el paneo — sin detalle de titulos en este deck)_")
        L.append("")

    hw = data.get("hardware")
    if hw:
        L.append("---")
        L.append("")
        L.append(f"## Hardware — {data.get('hardware_sub', 'Fierro')}")
        L.append("")
        for h in hw:
            L.append(f"- {h['name']}")
        L.append("")

    out_md = REPO / "docs" / f"lista-paneo-{out_slug}.md"
    out_md.write_text("\n".join(L), encoding="utf-8")
    return out_md


def generar_deck(data: dict, out_slug: str) -> Path:
    base = BASE.read_text(encoding="utf-8")
    # CSS + head: todo hasta <body>
    head = base[: base.index("<body>") + len("<body>")]
    # script + cierre: desde <nav class="footer"> hasta el final
    foot = base[base.index('<nav class="footer">'):]

    cats = data["categorias"]
    total_cats = len(cats)
    slides = []
    n = 1
    slides.append(_slide_portada(n, data)); n += 1
    slides.append(_slide_indice(n, data)); n += 1
    for ci, c in enumerate(cats, start=1):
        slides.append(_slide_paneo(n, ci, total_cats, c["name"], c["count"], ci)); n += 1
        slides.append(_slide_triple(n, c["name"], c["joyas"])); n += 1
    slides.append(_slide_hardware(n, data)); n += 1
    slides.append(_slide_balance(n, data)); n += 1
    slides.append(_slide_cierre(n, data)); n += 1

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

    # ajustar <title>
    head = re.sub(r"<title>.*?</title>",
                  f'<title>RETROTARROS · {data["doc_title"]}</title>', head, flags=re.DOTALL)

    out = REPO / "studio" / f"{out_slug}.html"
    out.write_text(head + hdr + foot, encoding="utf-8")

    # REGLA: cada coleccion genera ademas su lista MD por categoria (consultar/compartir)
    lista = _escribir_lista_md(data, out_slug)
    print("LISTA ->", lista)

    return out
