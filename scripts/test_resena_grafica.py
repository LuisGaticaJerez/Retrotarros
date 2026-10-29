"""Pruebas de la grafica nueva de las reseñas (scripts/resena_deck.py).

Sin pytest: se corre con `python scripts/test_resena_grafica.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resena_deck as D  # noqa: E402
from test_resena_lint import _data  # noqa: E402

SLUG_TMP = "_test-grafica-tmp"
VINETAS = [["CONTROLAS CON EL MOUSE", "Clic en un objeto y eliges la accion"],
           ["OCHO NECESIDADES", "Hambre, baño, energia y mas"],
           ["CONSTRUYE TU CASA", "20.000 simoleones para empezar"]]


def _generar(data: dict, **kw) -> str:
    """Genera con un slug temporal, devuelve el HTML y borra el archivo."""
    ruta = D.REPO / "studio" / "resenas" / f"{SLUG_TMP}.html"
    try:
        return D.generar_resena(data, SLUG_TMP, **kw).read_text(encoding="utf-8")
    finally:
        if ruta.exists():
            ruta.unlink()


# ---------------------------------------------------------------- Task 2

def test_portada_nueva_con_caja():
    html = _generar(_data(grafica="nueva", img_key="the-sims"))
    assert 'class="portada-fondo"' in html and 'class="portada-caja"' in html


def test_portada_nueva_sin_caja():
    html = _generar(_data(grafica="nueva"))  # img_key inexistente
    assert 'class="portada-fondo"' not in html and 'class="portada-caja"' not in html


def test_portada_clasica_sin_cambios():
    html = _generar(_data(grafica="clasica", img_key="the-sims"))
    assert 'class="portada-fondo"' not in html and 'class="portada-caja"' not in html


def test_veredicto_nueva_escala():
    html = _generar(_data(grafica="nueva", veredicto_tag=" juegazo "))
    assert html.count('class="ver-pill') == 4
    assert html.count('class="ver-pill on"') == 1
    assert '<div class="ver-pill on">JUEGAZO</div>' in html
    orden = [html.index(f">{t}</div>", html.index('class="ver-escala"'))
             for t in ("IMPRESCINDIBLE", "JUEGAZO", "MEMORABLE", "COLECCIONABLE")]
    assert orden == sorted(orden), orden


def test_veredicto_nueva_tag_fuera_de_escala():
    html = _generar(_data(grafica="nueva", veredicto_tag="X"), lint=False)
    assert html.count('class="ver-pill') == 4
    assert html.count('class="ver-pill on"') == 0


def test_veredicto_clasica_sin_escala():
    assert 'class="ver-escala"' not in _generar(_data(grafica="clasica"))


# ---------------------------------------------------------------- runner

def main() -> int:
    pruebas = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    fallas = 0
    for nombre, fn in pruebas:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fallas += 1
            print(f"FALLA {nombre}: {type(exc).__name__}: {exc}")
    if fallas:
        print(f"{fallas} de {len(pruebas)} pruebas fallaron")
        return 1
    print(f"OK {len(pruebas)} pruebas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
