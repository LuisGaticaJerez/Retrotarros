"""aplicar_grafica_nueva.py - Pasa un HTML de ranking YA generado a la grafica nueva (scripts/top_grafica.py).

Parchea el HTML sin necesitar el driver de `.cache` (que suele estar desactualizado respecto de lo commiteado:
regenerar desde el driver haria perder notas y ajustes hechos despues). Reconstruye de cada slide lo que
top_grafica necesita (caja, posicion, metadatos, precio, rotulo) y le aplica las mismas funciones que usa
generar_top con grafica="nueva": migrar(HTML clasico) da exactamente lo mismo que generarlo con la marca
(lo comprueba scripts/test_top_grafica.py).

Uso:
  python scripts/aplicar_grafica_nueva.py <slug> [<slug> ...]            # modo prueba (solo informa)
  python scripts/aplicar_grafica_nueva.py <slug> ... --aplicar           # escribe los HTML

REGLA (Luis 2026-11-03): solo rankings sin grabar ni publicar. NUNCA usar en rankings grabados, programados o
publicados (ver data/youtube/estado-canal.json y la memoria grabados-sin-publicar). No hay vuelta atras
automatica: se revierte con git.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import top_deck as T  # noqa: E402
import top_grafica as G  # noqa: E402

REPO = T.REPO
SECCION_RE = re.compile(r'<section class="slide[^"]*">.*?</section>', re.DOTALL)
ROTULOS_POR_DEFECTO = {"TOP", "PODIO", "EL TRONO"}
CSS_FIN = "</style>\n</head>"
# Desde el 2026-11-14 los layouts de caja agregan un <script id="g-fit"> entre el </style> y el </head>.
CSS_FIN_RE = re.compile(r"</style>\n(?:<script id=\"g-fit\">.*?</script>\n)?</head>", re.DOTALL)


def _buscar(patron: str, texto: str, grupo: int = 1, flags: int = re.DOTALL) -> str | None:
    m = re.search(patron, texto, flags)
    return m.group(grupo) if m else None


def _num(seccion: str) -> int:
    return int(_buscar(r'<span class="slide-num">(\d+)</span>', seccion))


def _parsear_juego(seccion: str) -> tuple[str, dict]:
    """(tipo, item) de un slide de juego: tipo es retail, rareza o grial. El item trae solo lo que
    top_grafica lee: img, lb, meta, price, block_label y (retail) pos."""
    cabecera = _buscar(r'<div class="hybrid-head">(.*?)</div>\n      <div class="hybrid-body">', seccion) or ""
    it: dict = {
        "img": _buscar(r'<img class="cart-img-bg" src="([^"]+)"', seccion),
        "lb": _buscar(r'<div class="cart-img-wrap (lb-[\w-]+)">', seccion) or "lb-default",
        "meta": _buscar(r'<div class="game-meta">(.*?)</div>', seccion) or "",
    }
    precio = _buscar(r'<div class="game-price">(.*?)</div>', cabecera)
    if precio:
        it["price"] = precio
    rotulo = _buscar(r'<div class="game-block-label (?:cy|mg)">(.*?)</div>', cabecera)
    if rotulo and rotulo not in ROTULOS_POR_DEFECTO:
        it["block_label"] = rotulo
    if "HOLY</span> GRAIL" in cabecera:
        return "grial", it
    if "font-size:24px;letter-spacing:2px;line-height:1.15;" in cabecera:
        return "rareza", it
    pos = _buscar(r'<span class="hash">#</span>(\d+)', cabecera)
    if pos is None:
        raise ValueError(f"slide {_num(seccion):02d}: no encontre la posicion (#N) ni la etiqueta de rareza o grial")
    it["pos"] = int(pos)
    return "retail", it


def migrar(html: str, slug: str) -> str:
    """HTML clasico de un ranking -> el mismo ranking con la grafica nueva. ValueError si ya la tiene."""
    if "g-nueva" in html:
        raise ValueError("el HTML ya tiene la grafica nueva")
    if len(CSS_FIN_RE.findall(html)) != 1:
        raise ValueError(f"esperaba un solo bloque de estilos compartido, hay {len(CSS_FIN_RE.findall(html))}")
    secciones = SECCION_RE.findall(html)
    items: list[dict] = []
    rarezas: list[dict] = []
    grial = None
    for s in secciones:
        if 'class="slide-hybrid' in s:
            tipo, it = _parsear_juego(s)
            if tipo == "retail":
                items.append(it)
            elif tipo == "rareza":
                rarezas.append(it)
            else:
                grial = it
    if not items:
        raise ValueError("no encontre slides de juego")
    data = {"items": items, "rarezas": rarezas}
    if grial:
        data["grial"] = grial

    indice = 0

    def sustituir(m: re.Match) -> str:
        nonlocal indice
        s = m.group(0)
        num = _num(s)
        if 'class="slide-hybrid' in s:
            _, it = _parsear_juego(s)
            nuevo = G.item_html(s, num, it, "", slug, data, indice)
            indice += 1
            return nuevo
        if 'class="portada"' in s:
            return G.portada_html(s, num, data, slug)
        if 'class="divider"' in s:
            color = _buscar(r'<div class="pre (\w+)">', s) or "cy"
            return G.divisor_html(s, num, {"color": color}, data, slug)
        return s

    resultado = SECCION_RE.sub(sustituir, html)
    m = CSS_FIN_RE.search(resultado)
    return resultado[: m.start()] + G.css_nueva() + resultado[m.start():]


def _ruta(slug: str) -> Path:
    hits = list((REPO / "studio" / "rankings").glob(f"*/{slug}.html"))
    if not hits:
        raise SystemExit(f"No encuentro studio/rankings/*/{slug}.html")
    return hits[0]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--aplicar", action="store_true", help="escribe los HTML (sin esto solo informa)")
    args = ap.parse_args()
    falla = 0
    for slug in args.slugs:
        ruta = _ruta(slug)
        html = ruta.read_text(encoding="utf-8")
        try:
            nuevo = migrar(html, slug)
        except ValueError as exc:
            print(f"{slug}: OMITIDO ({exc})")
            falla += 1
            continue
        print(f"{slug}: {'APLICADO' if args.aplicar else 'se aplicaria'} ({len(html)} -> {len(nuevo)} caracteres, "
              f"{nuevo.count('g-barra')} barras)")
        if args.aplicar:
            ruta.write_text(nuevo, encoding="utf-8")
    return 1 if falla else 0


if __name__ == "__main__":
    sys.exit(main())
