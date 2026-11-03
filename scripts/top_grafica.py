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

import top_deck as T


def _inyectar(html: str, viejo: str, nuevo: str) -> str:
    """Reemplaza `viejo` por `nuevo` una sola vez; RuntimeError si `viejo` no esta."""
    if viejo not in html:
        raise RuntimeError(f"top_grafica: no encontre {viejo!r} en el HTML clasico")
    return html.replace(viejo, nuevo, 1)


def css_nueva() -> str:
    """CSS de la grafica nueva; se agrega al final del bloque de estilo compartido."""
    return ".g-nueva{}\n"


def slide_portada(num: int, data: dict, out_slug: str) -> str:
    return T._slide_portada(num, data)


def slide_divisor(num: int, d: dict, data: dict, out_slug: str) -> str:
    return T._slide_divider(num, d)


def slide_item(num: int, it: dict, consola: str, ch: int, box: str, out_slug: str,
               data: dict, indice: int) -> str:
    return T._slide_item(num, it, consola, ch=ch, box=box, out_slug=out_slug)
