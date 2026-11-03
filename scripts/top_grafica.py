"""
top_grafica.py - Retrotarros Studio Suite
=========================================
Grafica nueva de los rankings (Top Mundial, Top Precios, Top Peores, Infravalorados).
Se activa SOLO con data["grafica"] = "nueva" en generar_top() (scripts/top_deck.py);
sin la marca este modulo ni se importa y el HTML sale identico al de siempre.

Cada funcion de slide parte del HTML clasico de top_deck y le aplica reemplazos
exactos (_inyectar): si el HTML clasico cambia, falla en voz alta en vez de generar
algo a medias. Diseno: docs/superpowers/specs/2026-11-02-rankings-grafica-design.md

Sin tildes en el HTML (regla de assets visuales del canal).
"""
from __future__ import annotations

import random
import re

import top_deck as T

MIN_CAJAS_MOSAICO = 6      # con menos cajas el mosaico no se usa y portada/divisores salen como hoy
CELDAS_MOSAICO = 10        # grilla de 5 x 2
CHIPS_PRINCIPALES = 3      # consola, ano y editor van como chips; lo demas (fuentes, evidencia) en una linea gris
# estimado de lo que ocupan los chips (px a 1920 de ancho): si pasan de MAX_FILAS_CHIPS filas empujan al
# TarroVision hacia abajo (medido en Top Peores con listas de fuentes), asi que se conserva la linea de hoy
ANCHO_CHIPS_PX, CHIP_BASE_PX, CHIP_PX_CARACTER, CHIP_GAP_PX, MAX_FILAS_CHIPS = 460, 32, 15, 10, 2
MIN_ANCHO_REL, MAX_ANCHO_REL = 0.6, 1.7   # limites de la proporcion de las miniaturas de la barra
# medidas de la barra, en px a 1920 de ancho (deben coincidir con el CSS de css_nueva)
ALTO_MINIATURA, LADO_CASILLA = 72, 40
GAP_BARRA = 6              # separacion entre elementos
ANCHO_SEP = 15             # separador entre grupos: 3 px de linea + 6 px de margen por lado
MAX_BARRA_PX = 800         # ancho maximo de la barra
# zona libre de la cabecera (px, a 1920 de ancho; la cabecera mide 1750 y su mitad es 875)
MITAD_CABECERA_PX = 875
MAX_ETIQUETA_PX = 360      # ancho maximo de la etiqueta de la izquierda (igual al max-width de .game-pos en css_nueva)
HOLGURA_PX = 100           # separacion minima entre la barra y la etiqueta / el precio
PX_POR_CARACTER, PX_CAJA = 36, 42   # estimado (conservador) del ancho de la caja del precio o rotulo de la derecha


def _inyectar(html: str, viejo: str, nuevo: str) -> str:
    """Reemplaza `viejo` por `nuevo` una sola vez; RuntimeError si `viejo` no esta."""
    if viejo not in html:
        raise RuntimeError(f"top_grafica: no encontre {viejo!r} en el HTML clasico")
    return html.replace(viejo, nuevo, 1)


def css_nueva() -> str:
    """CSS de la grafica nueva; se agrega al final del bloque de estilo compartido."""
    return (
        ".g-nueva{}\n"
        ".g-nueva .slide-num{z-index:3}\n"
        # mosaico de cajas (portada y divisores)
        ".g-mos{position:absolute;inset:-20px;display:grid;grid-template-columns:repeat(5,1fr);"
        "grid-template-rows:repeat(2,1fr);filter:blur(10px) brightness(.35) saturate(1.2);z-index:0}\n"
        ".g-mos.tenue{filter:blur(12px) brightness(.24) saturate(1.2)}\n"
        ".g-mos i{display:block;background-size:cover;background-position:center}\n"
        ".g-mos i.g-lb{background:linear-gradient(135deg,var(--label-1,#2D1B69),var(--label-2,#4a2a99))}\n"
        ".slide.g-nueva .portada,.slide.g-nueva .divider{position:relative;z-index:2}\n"
        ".slide.g-nueva .portada{text-shadow:0 0 30px #000,0 0 10px #000}\n"
        # divisores: texto dentro de una tarjeta de vidrio con borde de neon
        ".slide.g-div{display:flex;align-items:center;justify-content:center}\n"
        ".slide.g-div .divider{height:auto;width:min(1500px,78%);padding:48px 64px;"
        "background:rgba(6,3,15,.72);border:3px solid;border-radius:14px}\n"
        ".slide.g-div.g-cy .divider{border-color:var(--cy);box-shadow:0 0 40px rgba(0,229,255,.3)}\n"
        ".slide.g-div.g-mg .divider{border-color:var(--mg);box-shadow:0 0 40px rgba(255,46,136,.3)}\n"
        # slide de juego: fondo con la caja y chips de datos
        ".g-bg{position:absolute;inset:-40px;background-size:cover;background-position:center;"
        "filter:blur(22px) brightness(.3) saturate(1.3);z-index:0}\n"
        ".g-bg.g-lb{background:linear-gradient(135deg,var(--label-1,#2D1B69),var(--label-2,#4a2a99));"
        "filter:blur(22px) brightness(.45)}\n"
        ".slide.g-nueva .slide-hybrid{position:relative;z-index:2}\n"
        ".g-chips{display:flex;flex-wrap:wrap;gap:10px}\n"
        ".g-extra{margin-top:6px}\n"
        ".g-chip{font-family:'Orbitron';font-weight:700;font-size:22px;letter-spacing:1px;padding:6px 14px;"
        "border:2px solid rgba(0,229,255,.7);border-radius:6px;color:var(--cy);background:rgba(6,3,15,.55)}\n"
        ".g-chip.y{background:var(--ye);color:var(--dk);border-color:var(--ye);box-shadow:0 0 16px rgba(255,210,63,.5)}\n"
        # barra de progreso: centrada y fija en la cabecera (px a 1920 x 1080)
        ".slide.g-nueva .hybrid-head{position:relative}\n"
        ".slide.g-nueva .hybrid-head .game-pos{max-width:360px}\n"
        ".g-barra{position:absolute;left:50%;top:50%;transform:translate(calc(-50% + var(--dx,0px)),-50%);display:flex;"
        "align-items:center;gap:6px;z-index:5}\n"
        ".g-th{position:relative;height:var(--u);width:calc(var(--u)*var(--w));flex:none;border:2px solid rgba(0,229,255,.75);"
        "border-radius:4px;overflow:hidden;background:#0c0720}\n"
        ".g-th i{position:absolute;inset:0;background-size:cover;background-position:center}\n"
        ".g-th em{position:absolute;left:4px;bottom:0;font-style:normal;font-family:'Orbitron';font-weight:900;"
        "font-size:19px;color:#fff;text-shadow:0 0 4px #000,0 0 4px #000}\n"
        ".g-th.f{border-color:rgba(255,255,255,.2)}\n"
        ".g-th.f em{color:rgba(255,255,255,.45)}\n"
        ".g-th.cur{border-color:var(--ye);box-shadow:0 0 18px rgba(255,210,63,.8)}\n"
        ".g-th.cur em{color:var(--ye)}\n"
        ".g-pip{width:var(--u);height:var(--u);flex:none;display:flex;align-items:center;justify-content:center;"
        "border:2px solid rgba(0,229,255,.75);background:rgba(0,229,255,.18);border-radius:4px;"
        "font-family:'Orbitron';font-weight:900;font-size:16px;color:#fff}\n"
        ".g-pip.f{border-color:rgba(255,255,255,.2);background:transparent;color:rgba(255,255,255,.35)}\n"
        ".g-pip.rr{border-color:rgba(255,46,136,.8);color:var(--mg);background:transparent}\n"
        ".g-pip.gg{border-color:rgba(255,210,63,.85);color:var(--ye);background:transparent}\n"
        ".g-pip.cur{background:var(--ye);color:var(--dk);border-color:var(--ye);box-shadow:0 0 18px rgba(255,210,63,.8)}\n"
        ".g-sep{width:3px;height:30px;flex:none;margin:0 6px;background:rgba(255,255,255,.28)}\n"
    )


def _todos(data: dict) -> list[dict]:
    """Items del ranking en el orden de los slides: retail, rarezas y grial."""
    return list(data.get("items", [])) + list(data.get("rarezas", [])) + ([data["grial"]] if data.get("grial") else [])


def mosaico(data: dict, out_slug: str, tenue: bool) -> str:
    """Mosaico 5 x 2 con las cajas del ranking, en un orden barajado de forma determinista
    (semilla = out_slug) para no revelar el ranking. "" si hay menos de MIN_CAJAS_MOSAICO cajas.
    Un item sin caja aporta una celda con el degradado de su etiqueta (lb-*)."""
    todos = _todos(data)
    if sum(1 for it in todos if it.get("img")) < MIN_CAJAS_MOSAICO:
        return ""
    orden = list(todos)
    random.Random(out_slug).shuffle(orden)
    celdas = []
    for k in range(CELDAS_MOSAICO):
        it = orden[k % len(orden)]
        if it.get("img"):
            celdas.append(f'<i style="background-image:url({it["img"]})"></i>')
        else:
            celdas.append(f'<i class="g-lb {it.get("lb", "lb-default")}"></i>')
    return f'<div class="g-mos{" tenue" if tenue else ""}">' + "".join(celdas) + "</div>"


def _con_mosaico(html: str, num: int, mos: str) -> str:
    marca = f'<span class="slide-num">{num:02d}</span>\n'
    return _inyectar(html, marca, marca + f"    {mos}\n")


def portada_html(html: str, num: int, data: dict, out_slug: str) -> str:
    """Aplica la grafica nueva al HTML clasico de la portada (lo usan slide_portada y el migrador)."""
    mos = mosaico(data, out_slug, tenue=False)
    if not mos:
        return html
    html = _inyectar(html, '<section class="slide active">', '<section class="slide active g-nueva">')
    return _con_mosaico(html, num, mos)


def divisor_html(html: str, num: int, d: dict, data: dict, out_slug: str) -> str:
    """Aplica la grafica nueva al HTML clasico de un divisor; d es su dict (solo se lee "color")."""
    mos = mosaico(data, out_slug, tenue=True)
    if not mos:
        return html
    color = d.get("color", "cy")
    html = _inyectar(html, '<section class="slide">', f'<section class="slide g-nueva g-div g-{color}">')
    return _con_mosaico(html, num, mos)


def slide_portada(num: int, data: dict, out_slug: str) -> str:
    return portada_html(T._slide_portada(num, data), num, data, out_slug)


def slide_divisor(num: int, d: dict, data: dict, out_slug: str) -> str:
    return divisor_html(T._slide_divider(num, d), num, d, data, out_slug)


def _filas_chips(partes: list[str]) -> int:
    """Filas que ocuparian los chips en la columna del titulo (estimado)."""
    filas, ancho = 1, 0
    for p in partes:
        w = CHIP_BASE_PX + CHIP_PX_CARACTER * len(p)
        if ancho and ancho + CHIP_GAP_PX + w > ANCHO_CHIPS_PX:
            filas, ancho = filas + 1, w
        else:
            ancho += (CHIP_GAP_PX if ancho else 0) + w
        filas += -(-w // ANCHO_CHIPS_PX) - 1      # un chip mas ancho que la columna se parte en varias lineas
    return filas


DEV_RE = re.compile(r"^(.+?)\s*\((DEV\.[^()]*|PORT[^()]*)\)$")


def chips(it: dict, consola: str) -> str:
    """Metadatos del juego: consola, ano (en amarillo) y editor como chips; el desarrollador entre
    parentesis ("(DEV. X)") y todo lo que venga despues (fuentes, evidencia) en una linea gris debajo.
    Parte de it["meta"] (separado por "·") o de consola, ano y editor, igual que el slide clasico.
    Descarta toda parte con "USD" (el precio ya sale grande aparte). "" si no queda nada o los chips
    no caben en MAX_FILAS_CHIPS filas (empujarian al TarroVision): el slide conserva la linea de hoy."""
    meta = it.get("meta") or " · ".join(
        str(x) for x in [consola, it.get("ano"), (it.get("editor") or "").upper()] if x)
    partes = [p.strip() for p in meta.split("·") if p.strip() and "USD" not in p]
    principales, resto = partes[:CHIPS_PRINCIPALES], partes[CHIPS_PRINCIPALES:]
    if len(principales) == CHIPS_PRINCIPALES:
        m = DEV_RE.match(principales[-1])
        if m:
            principales[-1] = m.group(1)
            resto.insert(0, m.group(2))
    if not principales or _filas_chips(principales) > MAX_FILAS_CHIPS:
        return ""
    ano = next((i for i, p in enumerate(principales) if re.match(r"\d{4}", p)), None)
    spans = "".join(f'<span class="g-chip{" y" if i == ano else ""}">{p}</span>' for i, p in enumerate(principales))
    extra = f'<div class="game-meta g-extra">{" · ".join(resto)}</div>' if resto else ""
    return f'<div class="game-meta g-chips">{spans}</div>{extra}'


def _fondo(it: dict) -> str:
    """Fondo del slide: la caja del juego desenfocada, o el degradado de su etiqueta si no hay caja."""
    if it.get("img"):
        return f'<div class="g-bg" style="background-image:url({it["img"]})"></div>'
    return f'<div class="g-bg g-lb {it.get("lb", "lb-default")}"></div>'


def secuencia(data: dict) -> list[tuple[str, dict]]:
    """(tipo, item) en el orden de los slides de juego: retail, rarezas y grial."""
    return ([("retail", it) for it in data.get("items", [])]
            + [("rareza", it) for it in data.get("rarezas", [])]
            + ([("grial", data["grial"])] if data.get("grial") else []))


def tipo_barra(data: dict) -> str:
    """Top Precios (trae rarezas o grial): casillas numeradas, porque con hasta 17 elementos las
    miniaturas no caben entre la etiqueta y el precio. El resto: miniaturas."""
    return "numeros" if data.get("rarezas") or data.get("grial") else "miniaturas"


def ancho_rel(sz: tuple[int, int] | None) -> float:
    """Ancho relativo de una miniatura de alto fijo: ancho/alto de la caja, limitado a 0,6 .. 1,7.
    Sin tamano (caja ausente o ilegible): cuadrada."""
    if not sz:
        return 1.0
    return round(min(MAX_ANCHO_REL, max(MIN_ANCHO_REL, sz[0] / sz[1])), 3)


def _ancho_derecha(data: dict) -> int:
    """Ancho estimado (px) de la caja mas ancha que va arriba a la derecha en el ranking: el precio
    (_price_of) o un block_label explicito. 0 si ningun slide trae nada ahi."""
    mayor = 0
    for _, it in secuencia(data):
        texto = re.sub(r"<[^>]+>", "", T._price_of(it) or it.get("block_label") or "")
        if texto:
            mayor = max(mayor, len(texto) * PX_POR_CARACTER + PX_CAJA)
    return mayor


def barra(data: dict, indice: int, out_slug: str) -> str:
    """Barra de progreso de la cabecera: un elemento por slide de juego. Los ya vistos (r) muestran
    su caja, el actual (cur) va encendido y los que faltan (f) en oscuro liso pero con su ancho real
    (asi la barra no se mueve al revelarse cada uno)."""
    seq = secuencia(data)
    numeros = tipo_barra(data) == "numeros"
    n = len(seq)
    anchos = [ancho_rel(T._img_size(it, out_slug)) for _, it in seq]
    seps = len({tipo for tipo, _ in seq}) - 1 if numeros else 0
    # la barra va en la zona libre de la cabecera, a >= HOLGURA_PX de la etiqueta de la izquierda y del
    # precio o rotulo de la derecha (el mas ancho del ranking, asi no se mueve entre slides)
    izq = -(MITAD_CABECERA_PX - MAX_ETIQUETA_PX - HOLGURA_PX)
    der = MITAD_CABECERA_PX - _ancho_derecha(data) - HOLGURA_PX if _ancho_derecha(data) else -izq
    ancho_max = min(MAX_BARRA_PX, der - izq)
    # unidad (alto de la miniatura o lado de la casilla): la normal, o menos si la barra pasaria de ancho_max
    fijo = GAP_BARRA * (n - 1) + ANCHO_SEP * seps
    u = (min(LADO_CASILLA, (ancho_max - fijo) // n) if numeros
         else min(ALTO_MINIATURA, int((ancho_max - fijo) // sum(anchos))))
    ancho = (n * u if numeros else sum(anchos) * u) + fijo
    dx = round(min(max(0, izq + ancho / 2), der - ancho / 2))      # centrada si cabe; si no, lo minimo que haga falta
    piezas = []
    previo = None
    for i, (tipo, it) in enumerate(seq):
        est = "r" if i < indice else ("cur" if i == indice else "f")
        if numeros:
            if previo is not None and tipo != previo:
                piezas.append('<div class="g-sep"></div>')
            previo = tipo
            grupo = {"retail": "", "rareza": "rr ", "grial": "gg "}[tipo]
            texto = {"retail": it.get("pos", ""), "rareza": "R", "grial": "★"}[tipo]
            piezas.append(f'<div class="g-pip {grupo}{est}">{texto}</div>')
        else:
            img = f'<i style="background-image:url({it["img"]})"></i>' if it.get("img") and i <= indice else ""
            piezas.append(f'<div class="g-th {est}" style="--w:{anchos[i]:.3f}">{img}<em>{it.get("pos", "")}</em></div>')
    return f'<div class="g-barra" style="--u:{u}px;--dx:{dx}px">' + "".join(piezas) + "</div>"


def item_html(html: str, num: int, it: dict, consola: str, out_slug: str, data: dict, indice: int) -> str:
    """Aplica la grafica nueva al HTML clasico de un slide de juego (lo usan slide_item y el migrador)."""
    html = _inyectar(html, '<section class="slide">', '<section class="slide g-nueva">')
    html = _inyectar(html, '<div class="hybrid-head">', '<div class="hybrid-head">' + barra(data, indice, out_slug))
    marca = f'<span class="slide-num">{num:02d}</span>\n'
    html = _inyectar(html, marca, marca + f"    {_fondo(it)}\n")
    chips_html = chips(it, consola)
    if chips_html:
        html, n = re.subn(r'<div class="game-meta">.*?</div>', lambda m: chips_html, html, count=1, flags=re.S)
        if not n:
            raise RuntimeError("top_grafica: no encontre game-meta en el HTML clasico")
    # el rotulo por defecto (TOP / PODIO / EL TRONO) lo reemplaza la barra de progreso;
    # un block_label explicito (ej. "EN 1 LISTA" en Top Peores) se conserva
    return re.sub(r'<div class="game-block-label (?:cy|mg)">(?:TOP|PODIO|EL TRONO)</div>', "", html)


def slide_item(num: int, it: dict, consola: str, ch: int, box: str, out_slug: str,
               data: dict, indice: int) -> str:
    html = T._slide_item(num, it, consola, ch=ch, box=box, out_slug=out_slug)
    return item_html(html, num, it, consola, out_slug, data, indice)
