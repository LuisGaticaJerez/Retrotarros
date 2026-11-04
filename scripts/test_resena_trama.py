"""Pruebas de la slide LA TRAMA de las reseñas (scripts/resena_deck.py y resena_lint.py).

Sin pytest: se corre con `python scripts/test_resena_trama.py`. Sale con codigo 1 si alguna falla.
La slide es opcional: solo existe si el DATA trae `trama` (no todos los juegos tienen lore).
"""
from __future__ import annotations
import copy
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resena_deck as D  # noqa: E402
import resena_lint as L  # noqa: E402
from test_resena_lint import _data  # noqa: E402
from test_tarrovision import GOLDEN, _h  # noqa: E402

SLUG_TMP = "_test-trama-tmp"
TRAMA = {
    "premisa": "Un heroe busca a su familia mientras un reino se parte en dos.",
    "actos": [["EL MUNDO", "Un continente dividido."], ["EL CONFLICTO", "Un grupo roba un secreto."],
              ["LA META", "Recuperarlo y elegir un bando."]],
    "personajes": [["HEROE", "el protagonista"], ["SOMBRA", "el rival"]],
}
NOTAS_TRAMA = {"titulo": "LA TRAMA", "lineas": ["TRAMA RESUMIDA: tres lineas.", "Detalle extra."]}


def _con_trama(**extra) -> dict:
    d = _data(grafica="nueva", trama=copy.deepcopy(TRAMA), **extra)
    d["notas"] = dict(d["notas"])
    d["notas"]["trama"] = dict(NOTAS_TRAMA)
    return d


def _generar(data: dict, **kw) -> str:
    ruta = D.REPO / "studio" / "resenas" / f"{SLUG_TMP}.html"
    try:
        return D.generar_resena(data, SLUG_TMP, **kw).read_text(encoding="utf-8")
    finally:
        if ruta.exists():
            ruta.unlink()


def test_sin_trama_no_cambia_nada():
    html = _generar(_data(grafica="clasica"))
    assert _h(html) == GOLDEN["resena_clasica"]
    assert "tr-premisa" not in html and ".tr-acto" not in html


def test_con_trama_va_entre_contexto_y_comparativa():
    html = _generar(_con_trama())
    assert html.count('class="tr-acto"') == 3 and html.count('class="tr-p"') == 2
    orden = [html.index(m) for m in ("CONTEXTO DE EPOCA</div>", 'class="tr-tag"', ">COMPARATIVA<")]
    assert orden == sorted(orden), orden
    assert "<h4>LA TRAMA</h4>" in html and "SIN SPOILERS" in html


def test_titulo_personalizable_y_personajes_opcionales():
    d = _con_trama()
    d["trama"]["titulo"] = "El lore"
    del d["trama"]["personajes"]
    html = _generar(d)
    assert ">EL LORE</div>" in html and 'class="tr-pers"' not in html


def test_trama_mal_formada_no_genera_slide_y_el_lint_avisa():
    d = _con_trama()
    d["trama"]["actos"] = d["trama"]["actos"][:2]
    errores, _ = L.revisar(d, "x")
    assert any("trama.actos debe tener 3" in e for e in errores)
    assert 'class="tr-acto"' not in _generar(d, lint=False)


def test_lint_errores_de_forma():
    for mod, frag in (
        (lambda t: t.pop("premisa"), "trama.premisa"),
        (lambda t: t.update(personajes=[["A", "b"]] * 5), "hasta 4"),
        (lambda t: t.update(personajes=[["A"]]), "[nombre, rol]"),
        (lambda t: t.update(titulo=" "), "trama.titulo"),
    ):
        d = _con_trama()
        mod(d["trama"])
        errores, _ = L.revisar(d, "x")
        assert any(frag in e for e in errores), (frag, errores)
    errores, _ = L.revisar(_data(trama="texto"), "x")
    assert any("dict" in e for e in errores)


def test_lint_tildes_y_critica_en_la_trama():
    d = _con_trama()
    d["trama"]["premisa"] = "Un héroe malo busca su pasado."
    errores, avisos = L.revisar(d, "x")
    assert any("tilde" in e and "trama.premisa" in e for e in errores)
    assert any("critica" in a and "trama.premisa" in a for a in avisos)


def test_lint_trama_resumida_vale_en_notas_de_trama():
    d = _con_trama()
    d["notas"]["contexto"] = {"titulo": "EPOCA", "lineas": ["Solo contexto."]}
    errores, _ = L.revisar(d, "x")
    assert not any("TRAMA RESUMIDA" in e for e in errores), errores
    d["notas"]["trama"] = {"titulo": "LA TRAMA", "lineas": ["Sin la marca."]}
    errores, _ = L.revisar(d, "x")
    assert any("TRAMA RESUMIDA" in e and "notas.trama" in e for e in errores)


def test_lint_pide_el_bloque_de_notas_de_trama():
    d = _con_trama()
    del d["notas"]["trama"]
    _, avisos = L.revisar(d, "x")
    assert any("falta el bloque de notas 'trama'" in a for a in avisos)
    _, avisos = L.revisar(_data(), "x")
    assert not any("'trama'" in a for a in avisos)


def main() -> int:
    fallas = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn) and fn.__module__ == "__main__":
            try:
                fn()
                print(f"ok    {nombre}")
            except Exception:
                fallas += 1
                print(f"FALLA {nombre}")
                traceback.print_exc()
    print(f"\n{'TODO OK' if not fallas else str(fallas) + ' falla(s)'}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
