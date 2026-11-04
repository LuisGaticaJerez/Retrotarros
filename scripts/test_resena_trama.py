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


def test_cinematica_suma_tv_16_9_y_conserva_la_grafica():
    d = _con_trama()
    d["trama"]["cinematica"] = True
    html = _generar(d)
    assert 'class="trama con-tv"' in html and 'class="tr-tv"' in html
    assert "tarrovision tvn ancha" in html and ".tarrovision.tvn.ancha" in html   # TV 16:9 y su CSS, aunque el DATA no la pida
    assert html.count('class="tr-acto"') == 3 and "tr-premisa" in html and 'class="tr-p"' in html and "SIN SPOILERS" in html
    # sin cinematica no hay TV en la slide
    sin = _generar(_con_trama())
    assert 'class="trama con-tv"' not in sin and 'class="tr-tv"' not in sin


def test_lint_cinematica_debe_ser_booleano():
    d = _con_trama()
    d["trama"]["cinematica"] = "si"
    errores, _ = L.revisar(d, "x")
    assert any("trama.cinematica" in e for e in errores)
    d["trama"]["cinematica"] = True
    errores, _ = L.revisar(d, "x")
    assert not any("cinematica" in e for e in errores)


def test_visual_cinematica_16_9_exacta_y_dentro_del_slide():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  (sin Playwright: prueba visual omitida)")
        return
    d = _con_trama()
    d["trama"]["cinematica"] = True
    ruta = D.generar_resena(d, SLUG_TMP)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1920, "height": 1080})
            pg.goto(ruta.as_uri())
            pg.wait_for_timeout(400)
            pg.evaluate("go(3)")
            pg.wait_for_timeout(350)
            m = pg.evaluate("""()=>{const s=document.querySelector('.slide.active'),dk=document.querySelector('.deck').getBoundingClientRect(),
              t=s.querySelector('.tarrovision').getBoundingClientRect(),c=s.querySelector('.tv-screen-inner').getBoundingClientRect(),
              l=s.querySelector('.tr-lado').getBoundingClientRect(),p=s.querySelector('.tr-p')?.getBoundingClientRect();
              return {ratio:c.width/c.height,w:c.width,tvdentro:t.top>=dk.top&&t.bottom<=dk.bottom&&t.left>=0,
                      ladodentro:l.top>=dk.top&&l.bottom<=dk.bottom&&l.right<=1920,sin_cruce:t.right<=l.left,
                      persdentro:!p||p.bottom<=dk.bottom}}""")
            b.close()
    finally:
        ruta.unlink()
    assert abs(m["ratio"] - 16 / 9) < 0.01 and m["w"] >= 1000, m
    assert m["tvdentro"] and m["ladodentro"] and m["sin_cruce"] and m["persdentro"], m


def test_trama_desde_json_externo(tmp_path=None):
    """data/resenas/trama.json aporta la trama a un DATA que no la trae (reseñas regeneradas desde drivers viejos)."""
    import json
    import tempfile
    entrada = {"trama": copy.deepcopy(TRAMA), "notas": {"trama": dict(NOTAS_TRAMA)}}
    with tempfile.TemporaryDirectory() as d:
        ruta = Path(d) / "trama.json"
        ruta.write_text(json.dumps({SLUG_TMP: entrada}), encoding="utf-8")
        previo = D.TRAMAS_JSON
        D.TRAMAS_JSON = ruta
        try:
            html = _generar(_data(grafica="nueva"))
            assert html.count('class="tr-acto"') == 3 and "<h4>LA TRAMA</h4>" in html
            # un DATA que ya trae su trama manda sobre el JSON
            propio = _con_trama()
            propio["trama"]["premisa"] = "Premisa propia del driver."
            assert "Premisa propia del driver." in _generar(propio)
            # otro slug no recibe nada
            D.TRAMAS_JSON = Path(d) / "no-existe.json"
            assert "tr-premisa" not in _generar(_data(grafica="nueva"))
        finally:
            D.TRAMAS_JSON = previo


def test_json_committed_es_valido_y_sin_tildes():
    import json
    import re
    datos = json.loads(D.TRAMAS_JSON.read_text(encoding="utf-8"))
    assert len(datos) >= 19
    for slug, e in datos.items():
        assert slug.startswith("resena-"), slug
        data = {"trama": e["trama"], "notas": {"trama": e["notas"]["trama"]}}
        assert L._errores_trama(data) == [], (slug, L._errores_trama(data))
        assert D._trama(data) is not None, slug
        texto = json.dumps(e, ensure_ascii=False)
        assert not re.search("[\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00c1\u00c9\u00cd\u00d3\u00da\u00dc]", texto), f"tilde en {slug}"
        assert len(e["notas"]["trama"]["lineas"]) >= 3, slug


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
