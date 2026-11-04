"""Pruebas de la TarroVision nueva y ancha (scripts/tarrovision.py, resena_deck.py, saga_deck.py).

Sin pytest: se corre con `python scripts/test_tarrovision.py`. Toda funcion `test_*` se
ejecuta; sale con codigo 1 si alguna falla. Las pruebas visuales (Chromium) se saltan si
Playwright no esta instalado.

Los hashes de regresion se calcularon sobre el HTML de ANTES de agregar el modulo: protegen
a los episodios ya grabados o publicados (sin la marca data["tarrovision"] todo sale igual).
"""
from __future__ import annotations
import hashlib
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resena_deck as D  # noqa: E402
import saga_deck as S  # noqa: E402
import tarrovision as TV  # noqa: E402
from test_resena_grafica import VINETAS  # noqa: E402
from test_resena_lint import _data  # noqa: E402

SLUG_TMP = "_test-tarrovision-tmp"
GOLDEN = {
    "resena_clasica": "3f2c83398dfb4a3b2872ad1960533666f514166ad9fcc5d5d92b8ed6734b8e9c",
    "resena_grafica_nueva_sin_marca": "69427fb0785a7de61d0ec5d04c23f9b343edbf7c4391c64496e17896bad514c4",
    "saga_css": "686b88674c122ffc6d9ff0bc289d9eba7fcb3a089ce486f51b1a8c0d127d9451",
    "saga_gameplay": "43bccef6c8a5e1d022f56ca9a7c8f936e724fd7e6aa356f8113fffbdab9ffa76",
    "saga_dual": "09844e3e12a3c7de9e5a5a7f1887d1c58ae3d5239cc4e9d8d65f79f881bfc3a2",
    "saga_tv": "c00d318c8c80fa877c557a253e3f3fea065669c70d64362fe9a0c0a4bfc8063f",
}
JUEGO_SAGA = {"title": "Juego", "console": "SNES", "year": "1995", "dato": "Un dato.", "owned": True}


def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _generar(data: dict, **kw) -> str:
    """Genera la reseña con un slug temporal, devuelve el HTML y borra el archivo."""
    ruta = D.REPO / "studio" / "resenas" / f"{SLUG_TMP}.html"
    try:
        return D.generar_resena(data, SLUG_TMP, **kw).read_text(encoding="utf-8")
    finally:
        if ruta.exists():
            ruta.unlink()


# ------------------------------------------------- regresion de lo clasico

def test_resena_clasica_identica():
    assert _h(_generar(_data(grafica="clasica"))) == GOLDEN["resena_clasica"]


def test_resena_clasica_explicita_identica():
    assert _h(_generar(_data(grafica="clasica", tarrovision="clasica"))) == GOLDEN["resena_clasica"]


def test_resena_grafica_nueva_sin_marca_identica():
    assert _h(_generar(_data(grafica="nueva"))) == GOLDEN["resena_grafica_nueva_sin_marca"]


def test_saga_clasica_identica():
    assert _h(S.CSS) == GOLDEN["saga_css"]
    assert _h(S._slide_gameplay(3, JUEGO_SAGA, 2)) == GOLDEN["saga_gameplay"]
    assert _h(S._slide_gameplay_dual(4, 1, 2)) == GOLDEN["saga_dual"]
    assert _h(S._tv(5)) == GOLDEN["saga_tv"]


# ------------------------------------------------- modulo

def test_variante_valida_e_invalida():
    assert TV.variante({}) == "clasica"
    for v in TV.VARIANTES:
        assert TV.variante({"tarrovision": v}) == v
    for malo in ("grande", "NUEVA", "", None, 3):
        try:
            TV.variante({"tarrovision": malo})
        except ValueError:
            continue
        raise AssertionError(f"debio fallar con {malo!r}")


def test_css_clasica_vacio_y_tv_clasica_no_se_genera_aca():
    assert TV.css("clasica") == ""
    try:
        TV.tv(1, "clasica")
    except ValueError:
        return
    raise AssertionError("tv() solo genera nueva o ancha")


def test_css_nueva_4_3_y_ancha_16_9():
    nueva, ancha = TV.css("nueva"), TV.css("ancha")
    assert ".tarrovision.tvn{" in nueva and ".tarrovision.tvn{" in ancha
    assert "aspect-ratio:4/3" in nueva and ".tvn.cuatro3" in nueva and "16/9" not in nueva
    assert "aspect-ratio:16/9" in ancha and ".tvn.ancha" in ancha and "4/3" not in ancha
    assert ".gp-tv.tvw" in nueva and ".gp-tv.tvw" in ancha


def test_tv_marcas_y_sin_tildes():
    for v, ancha in (("nueva", False), ("ancha", True)):
        h = TV.tv(7, v)
        assert 'class="tarrovision tvn' in h and ("tvn ancha" in h) == ancha
        assert "CH 07" in h and "tv-noscreen" in h and ("16:9" in h) == ancha
        assert all(ord(c) < 128 for c in h.replace("&middot;", "")), "tildes o simbolos no ASCII en el HTML"


# ------------------------------------------------- generadores

def test_resena_nueva_y_ancha_marcas():
    nueva = _generar(_data(grafica="nueva", jugabilidad_vinetas=VINETAS, tarrovision="nueva"))
    ancha = _generar(_data(grafica="nueva", jugabilidad_vinetas=VINETAS, tarrovision="ancha"))
    assert nueva.count("tarrovision tvn cuatro3") == 4 and "tarrovision tvn ancha" not in nueva
    assert nueva.count('class="gp-tv tvw"') == 2 and 'class="dual-grid tvw"' in nueva
    assert ancha.count("tarrovision tvn ancha") == 4 and "cuatro3" not in ancha.split("<body>")[1]
    assert ancha.count('class="gp-tv tvw"') == 2 and ancha.count('class="dual-cell tvw"') == 2
    assert 'class="dual-grid tvw"' in ancha and 'class="dual-grid"' not in ancha


def test_resena_marca_invalida_falla():
    try:
        _generar(_data(grafica="nueva", tarrovision="gigante"))
    except ValueError:
        return
    raise AssertionError("debio fallar con una marca invalida")


def test_saga_nueva_y_ancha():
    g = _slide_ok = S._slide_gameplay(3, JUEGO_SAGA, 2, "ancha")
    assert 'class="gp-tv tvw"' in g and "tarrovision tvn ancha" in g
    d = S._slide_gameplay_dual(4, 1, 2, "ancha")
    assert 'class="dual-grid tvw"' in d and d.count("dual-cell tvw") == 2
    n = S._slide_gameplay(3, JUEGO_SAGA, 2, "nueva")
    assert "tarrovision tvn cuatro3" in n and 'class="gp-tv tvw"' in n
    assert _h(S._slide_gameplay(3, JUEGO_SAGA, 2, "clasica")) == GOLDEN["saga_gameplay"]


# ------------------------------------------------- visual (Chromium)

def _medidas(html_path: Path, indices) -> dict:
    from playwright.sync_api import sync_playwright
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(html_path.as_uri())
        pg.wait_for_timeout(400)
        for i in indices:
            pg.evaluate(f"go({i})")
            pg.wait_for_timeout(350)
            res[i] = pg.evaluate("""()=>{const d=document.querySelector('.deck').getBoundingClientRect();
              return [...document.querySelectorAll('.slide.active .tarrovision')].map(t=>{
                const a=t.getBoundingClientRect(),c=t.querySelector('.tv-screen-inner').getBoundingClientRect();
                return {ratio:c.width/c.height, w:c.width, h:c.height,
                        dentro:a.left>=d.left-1&&a.right<=d.right+1&&a.top>=d.top-1&&a.bottom<=d.bottom+1}})}""")
        b.close()
    return res


def _correr_visual(tv: str):
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        print("  (sin Playwright: prueba visual omitida)")
        return None
    ruta = D.generar_resena(_data(grafica="nueva", jugabilidad_vinetas=VINETAS, tarrovision=tv), SLUG_TMP)
    try:
        # slides: 1 portada, 2 ficha, 3 contexto, 4 comparativa, 5 jugabilidad, 6 audiovisual
        return _medidas(ruta, (3, 4, 5))
    finally:
        ruta.unlink()


def test_visual_ancha_16_9_exacta_y_dentro_del_slide():
    m = _correr_visual("ancha")
    if m is None:
        return
    for i, tvs in m.items():
        assert tvs, f"slide {i} sin TarroVision"
        for t in tvs:
            assert abs(t["ratio"] - 16 / 9) < 0.01, (i, t)
            assert t["dentro"], (i, t)
    # mas grande que la clasica (960x623) en el slide de gameplay
    assert m[4][0]["w"] >= 1100 and m[4][0]["h"] >= 600, m[4]
    assert len(m[3]) == 2 and abs(m[3][0]["w"] - m[3][1]["w"]) < 1


def test_visual_nueva_4_3_exacta_y_dentro_del_slide():
    m = _correr_visual("nueva")
    if m is None:
        return
    for i, tvs in m.items():
        assert tvs, f"slide {i} sin TarroVision"
        for t in tvs:
            assert abs(t["ratio"] - 4 / 3) < 0.01, (i, t)
            assert t["dentro"], (i, t)
    assert m[4][0]["h"] >= 600, m[4]            # gameplay: pantalla 4:3 grande (la clasica mide 960x623)
    assert len(m[3]) == 2 and abs(m[3][0]["w"] - m[3][1]["w"]) < 1


def main() -> int:
    fallas = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn):
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
