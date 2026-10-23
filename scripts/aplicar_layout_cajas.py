"""aplicar_layout_cajas.py - Pasa un HTML de ranking YA generado al layout de cajas grandes (alta / ancha).

Parchea el HTML sin necesitar el driver de `.cache`: agrega la clase `box-alta` / `box-ancha` a cada
`slide-hybrid`, fija el tamano de la caja con las variables --bw/--bh y mete el CSS de `top_deck._box_css`
dentro del bloque de estilos compartido. El layout se elige por la forma de la mayoria de las cajas
(igual que `top_deck._pick_box_layout`). Es idempotente: un HTML que ya tiene el layout se salta.

Uso:
  python scripts/aplicar_layout_cajas.py <slug> [<slug> ...]            # modo prueba (solo informa)
  python scripts/aplicar_layout_cajas.py <slug> ... --aplicar           # escribe los HTML
  python scripts/aplicar_layout_cajas.py <slug> ... --aplicar --layout ancha   # fuerza el layout

REGLA (Luis 2026-10-23): solo rankings nuevos o reforjados. NO usar en rankings ya grabados o publicados
que no se vayan a reforjar (ver data/youtube/estado-canal.json y la memoria reforge-rango-fechas).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import top_deck as T  # noqa: E402
from PIL import Image  # noqa: E402

REPO = T.REPO
SECTION_RE = re.compile(r'(<section class="slide[^"]*">.*?</section>)', re.DOTALL)
IMG_RE = re.compile(r'<img class="cart-img-bg" src="([^"]+)"')
WHY_RE = re.compile(r'<div class="game-why"><span class="lbl">.*?</span>(.*?)</div>', re.DOTALL)


def _find(slug: str) -> Path:
    hits = list((REPO / "studio" / "rankings").glob(f"*/{slug}.html"))
    if not hits:
        raise SystemExit(f"No encuentro studio/rankings/*/{slug}.html")
    return hits[0]


def _size(base: Path, src: str):
    try:
        with Image.open(base.parent / src) as im:
            return im.size
    except Exception:
        return None


def parchear(slug: str, forzar: str | None, aplicar: bool) -> str:
    f = _find(slug)
    html = f.read_text(encoding="utf-8")
    if "slide-hybrid box-" in html:
        return f"{slug}: ya tiene el layout, se salta"
    secciones = SECTION_RE.findall(html)
    datos = []   # (seccion, src, chars)
    for sec in secciones:
        if 'class="slide-hybrid"' not in sec:
            continue
        m = IMG_RE.search(sec)
        w = WHY_RE.search(sec)
        chars = len(re.sub(r"<[^>]+>", "", w.group(1))) if w else 0
        datos.append((sec, m.group(1) if m else None, chars))
    sizes = [_size(f, d[1]) if d[1] else None for d in datos]
    conocidos = [s for s in sizes if s]
    if forzar:
        layout = forzar
    elif not conocidos:
        layout = "clasica"
    else:
        tall = sum(1 for w, h in conocidos if h / w >= 1.15)
        layout = "alta" if tall > len(conocidos) - tall else "ancha"
    if layout == "clasica":
        return f"{slug}: sin imagenes de caja, se deja clasico"
    nuevo = html
    for (sec, src, chars), sz in zip(datos, sizes):
        bw, bh = T._fit_dims(sz, chars, layout)
        s2 = sec.replace('<div class="slide-hybrid">', f'<div class="slide-hybrid box-{layout}">', 1)
        s2 = s2.replace('<div class="cart">', f'<div class="cart" style="--bw:{bw}px;--bh:{bh}px">', 1)
        nuevo = nuevo.replace(sec, s2, 1)
    # CSS: dentro del bloque compartido, justo antes de su cierre
    bloque = T._SHARED_CSS_BLOCK_RE.search(nuevo)
    if not bloque:
        return f"{slug}: NO encontre el bloque de estilos compartido, no se toca"
    b = bloque.group(0)
    b2 = b[: -len("</style>\n</head>")] + T._box_css(layout) + "</style>\n</head>"
    nuevo = nuevo.replace(b, b2, 1)
    if aplicar:
        f.write_text(nuevo, encoding="utf-8")
    return f"{slug}: layout {layout}, {len(datos)} slides" + ("" if aplicar else " (prueba, no se escribio)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--layout", choices=["alta", "ancha"])
    a = ap.parse_args()
    for s in a.slugs:
        print(parchear(s, a.layout, a.aplicar))


if __name__ == "__main__":
    main()
