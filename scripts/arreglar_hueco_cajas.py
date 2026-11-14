"""Arregla el hueco entre la caja y el "por que" en los decks con layout de caja alta o ancha (2026-11-14).

Hasta esa fecha la fila de la caja era 1fr y la caja se topaba en --bh, asi que en 1080p sobraba espacio y el texto
quedaba abajo. El generador (top_deck._box_css) ya sale arreglado; este script parchea decks ya generados reutilizando
esa misma funcion: reemplaza el CSS viejo exacto por el nuevo.

Uso:  python scripts/arreglar_hueco_cajas.py <slug> [<slug> ...]          (modo prueba)
      python scripts/arreglar_hueco_cajas.py <slug> ... --aplicar         (escribe)
      python scripts/arreglar_hueco_cajas.py --todos [--aplicar]          (todos los decks con layout de caja)
Solo sin grabar ni publicar: confirmar con Luis antes de aplicarlo a un deck.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import top_deck  # noqa: E402
from _studio_layout import STUDIO, find_html  # noqa: E402


def _v2(nuevo: str, box: str) -> str:
    """CSS de la primera version del arreglo (caja sin factor), para actualizar decks ya parchados."""
    return nuevo.replace(f"height:{top_deck._cart_h(box)} !important;max-height:{top_deck._cart_mx(box)} !important;",
                         "height:min(var(--bh),40vh) !important;max-height:var(--bh) !important;")


def _v1(nuevo: str, box: str) -> str:
    """CSS original (antes del 2026-11-14): fila de la caja 1fr, caja al 100 % de su fila."""
    v = _v2(nuevo, box)
    v = v.replace("grid-template-rows:auto auto 1fr !important;", "grid-template-rows:auto 1fr auto !important;")
    v = v.replace("height:min(var(--bh),40vh) !important;", "height:100% !important;")
    v = v.replace("height:auto !important;min-height:auto !important}", "height:auto !important;min-height:0 !important}")
    return "\n".join(l for l in v.split("\n") if ".game-why{align-self:stretch" not in l)


def parchear(html: str):
    """Devuelve (nuevo_html, cajas_cambiadas). Acepta decks sin parchar, con la primera version o ya al dia."""
    cambiadas = []
    con_layout = False
    for box in ("alta", "ancha"):
        nuevo = top_deck._box_css(box)
        if nuevo in html:
            con_layout = True
            continue
        for viejo in (_v2(nuevo, box), _v1(nuevo, box)):
            if viejo != nuevo and viejo in html:
                html = html.replace(viejo, nuevo)
                cambiadas.append(box)
                con_layout = True
                break
    if con_layout and top_deck.FIT_JS not in html:
        html = re.sub(r'<script id="g-fit">.*?</script>\n', "", html, flags=re.DOTALL)
        html = html.replace("</head>", top_deck.FIT_JS + "</head>", 1)
        cambiadas.append("fit-js")
    return html, cambiadas


def main(argv):
    aplicar = "--aplicar" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--todos" in argv:
        rutas = sorted(p for p in STUDIO.glob("rankings/*/*.html"))
    else:
        rutas = [Path(find_html(s)) for s in args]
    n = 0
    for p in rutas:
        s = p.read_text(encoding="utf-8")
        t, cajas = parchear(s)
        if cajas:
            n += 1
            print(("APLICADO " if aplicar else "prueba   ") + p.stem, cajas)
            if aplicar:
                p.write_text(t, encoding="utf-8", newline="")
    print(f"{n} deck(s) con cambio" + ("" if aplicar else " (modo prueba, usa --aplicar)"))


if __name__ == "__main__":
    main(sys.argv[1:])
