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

import top_deck as T

MIN_CAJAS_MOSAICO = 6      # con menos cajas el mosaico no se usa y portada/divisores salen como hoy
CELDAS_MOSAICO = 10        # grilla de 5 x 2


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


def slide_portada(num: int, data: dict, out_slug: str) -> str:
    html = T._slide_portada(num, data)
    mos = mosaico(data, out_slug, tenue=False)
    if not mos:
        return html
    html = _inyectar(html, '<section class="slide active">', '<section class="slide active g-nueva">')
    return _con_mosaico(html, num, mos)


def slide_divisor(num: int, d: dict, data: dict, out_slug: str) -> str:
    html = T._slide_divider(num, d)
    mos = mosaico(data, out_slug, tenue=True)
    if not mos:
        return html
    color = d.get("color", "cy")
    html = _inyectar(html, '<section class="slide">', f'<section class="slide g-nueva g-div g-{color}">')
    return _con_mosaico(html, num, mos)


def slide_item(num: int, it: dict, consola: str, ch: int, box: str, out_slug: str,
               data: dict, indice: int) -> str:
    return T._slide_item(num, it, consola, ch=ch, box=box, out_slug=out_slug)
