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


# ---------------------------------------------------------------- Task 3

CHIP = '<span class="chip'


def test_ficha_chips_con_plataformas():
    html = _generar(_data(grafica="nueva", plataformas=[["PC", "2000"], ["PS2", "2003"]]))
    assert html.count(CHIP) == 2
    assert html.count('<span class="chip first">') == 1
    assert "<i>2000</i>" in html and "<i>2003</i>" in html


def test_ficha_chips_desde_consola():
    html = _generar(_data(grafica="nueva", consola="PC · Mac"))
    assert html.count(CHIP) == 2 and "<i>" not in html.split('<div class="chips">')[1].split("</div>")[0]


def test_ficha_chips_una_plataforma():
    html = _generar(_data(grafica="nueva", consola="PC"))
    assert html.count(CHIP) == 1


def test_ficha_plataformas_mal_formadas():
    html = _generar(_data(grafica="nueva", plataformas=[None, ["PC"], [], ["PS2", "2003"]]), lint=False)
    assert html.count(CHIP) == 2


def test_ficha_clasica_sin_chips():
    html = _generar(_data(grafica="clasica", plataformas=[["PC", "2000"]]))
    assert 'class="chips"' not in html


def test_contexto_nueva_con_imagen():
    html = _generar(_data(grafica="nueva", img_key="the-sims"))
    assert 'class="ctx-img"' in html and "con-imagen" in html.split("</style>")[1]


def test_contexto_nueva_sin_imagen():
    html = _generar(_data(grafica="nueva"))
    assert 'class="ctx-img"' not in html and 'contexto con-imagen' not in html


def test_contexto_clasica_sin_imagen():
    html = _generar(_data(grafica="clasica", img_key="the-sims"))
    assert 'class="ctx-img"' not in html


# ---------------------------------------------------------------- Task 4

PROXIMA = {"juego": "God of War", "consola": "PlayStation 2", "anio": "2005", "img_key": "god-of-war"}


def _slide(html: str, titulo: str) -> str:
    return [s for s in html.split("<section") if titulo in s][0]


def test_jugabilidad_vinetas():
    html = _generar(_data(grafica="nueva", jugabilidad_vinetas=VINETAS))
    sec = _slide(html, "JUGABILIDAD HOY")
    assert 'class="gp-vinetas"' in sec
    assert sec.count('<div class="vineta">') == 3
    assert ">01<" in sec and ">02<" in sec and ">03<" in sec
    assert 'class="gp-dato"' not in sec


def test_jugabilidad_vinetas_cantidad_invalida():
    for malas in (VINETAS[:2], VINETAS + [["D", "d"]]):
        html = _generar(_data(grafica="nueva", jugabilidad_vinetas=malas), lint=False)
        sec = _slide(html, "JUGABILIDAD HOY")
        assert 'class="gp-vinetas"' not in sec and 'class="gp-dato"' in sec


def test_jugabilidad_clasica_ignora_vinetas():
    html = _generar(_data(grafica="clasica", jugabilidad_vinetas=VINETAS))
    assert 'class="gp-vinetas"' not in html


def test_compositor():
    html = _generar(_data(grafica="nueva", audiovisual_compositor="Jerry Martin · Marc Russo"))
    sec = _slide(html, "GRAFICOS Y SONIDO HOY")
    assert 'class="gp-compositor"' in sec and "BANDA SONORA" in sec and "Jerry Martin · Marc Russo" in sec
    assert 'class="gp-compositor"' not in _generar(_data(grafica="nueva"))


def test_cierre_proxima():
    html = _generar(_data(grafica="nueva", proxima=PROXIMA))
    assert 'class="cierre-proxima"' in html
    assert "God of War" in html and "PlayStation 2 · 2005" in html
    assert '<img class="cp-img"' in html


def test_cierre_proxima_sin_imagen_ni_campo():
    sin_img = dict(PROXIMA)
    del sin_img["img_key"]
    html = _generar(_data(grafica="nueva", proxima=sin_img))
    assert 'class="cierre-proxima"' in html and '<img class="cp-img"' not in html
    assert 'class="cierre-proxima"' not in _generar(_data(grafica="nueva"))
    assert 'class="cierre-proxima"' not in _generar(_data(grafica="nueva", proxima="texto"), lint=False)


def test_textos_nuevos_escapados():
    vin = [["<b>A&B</b>", "<i>x</i>"]] + VINETAS[1:]
    html = _generar(_data(grafica="nueva", jugabilidad_vinetas=vin,
                          audiovisual_compositor="<u>Comp & Co</u>",
                          proxima={"juego": "<s>Juego & Co</s>", "consola": "PS2", "anio": "2005"}), lint=False)
    for esperado in ("&lt;B&gt;A&amp;B&lt;/B&gt;", "&lt;i&gt;x&lt;/i&gt;", "&lt;u&gt;Comp &amp; Co&lt;/u&gt;",
                     "&lt;s&gt;Juego &amp; Co&lt;/s&gt;"):
        assert esperado in html, esperado
    for crudo in ("<b>A&B", "<u>Comp & Co", "<s>Juego & Co"):
        assert crudo not in html, crudo


def test_clasica_no_tiene_ninguna_marca_nueva():
    html = _generar(_data(grafica="clasica", img_key="the-sims", jugabilidad_vinetas=VINETAS,
                          plataformas=[["PC", "2000"]], audiovisual_compositor="X Y", proxima=PROXIMA))
    for clase in ("portada-fondo", "ver-escala", "chips", "ctx-img", "gp-vinetas", "gp-compositor", "cierre-proxima"):
        assert f'class="{clase}"' not in html, clase


# ---------------------------------------------------------------- Cajas apaisadas y altas

def _con_caja_temporal(nombre: str, ancho: int, alto: int, fn):
    """Crea studio/resenas/img/resenas/<nombre>.jpg, corre fn() y lo borra."""
    from PIL import Image
    ruta = D.REPO / "studio" / "resenas" / "img" / "resenas" / f"{nombre}.jpg"
    Image.new("RGB", (ancho, alto), (30, 30, 60)).save(ruta)
    try:
        return fn()
    finally:
        if ruta.exists():
            ruta.unlink()


def test_portada_y_contexto_caja_apaisada_se_acotan():
    html = _con_caja_temporal("_test-ancha", 400, 250,
                              lambda: _generar(_data(grafica="nueva", img_key="_test-ancha")))
    assert 'class="portada-caja" style="width:30%;height:auto"' in html
    assert 'class="ctx-img" style="width:30vw;height:auto"' in html


def test_portada_y_contexto_caja_alta_sin_estilo_en_linea():
    html = _con_caja_temporal("_test-alta", 200, 400,
                              lambda: _generar(_data(grafica="nueva", img_key="_test-alta")))
    assert 'class="portada-caja" src=' in html
    assert 'class="ctx-img" src=' in html


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
