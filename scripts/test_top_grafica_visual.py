"""Pruebas visuales de la grafica nueva de los rankings (Chromium via Playwright, 1920 x 1080).

Sin pytest: `python scripts/test_top_grafica_visual.py`. Mide con getBoundingClientRect:
  - el TarroVision no se mueve ni cambia de tamano respecto de la grafica clasica;
  - la barra de progreso queda a >= 100 px de la etiqueta de la izquierda, del precio y del
    rotulo de la derecha, y no toca el TarroVision;
  - una etiqueta larga se parte en dos lineas en vez de acercarse a la barra.
Reutiliza las fixtures de test_top_grafica.py (base congelada y cajas temporales).
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_top_grafica as TG  # noqa: E402

HOLGURA_MIN = 100   # px libres entre la barra y la etiqueta / el precio (a 1920 px de ancho)

_PAGINA = None


def _abrir(page, ruta: Path) -> None:
    page.goto(ruta.as_uri(), wait_until="networkidle")
    page.wait_for_function("document.fonts.ready")
    page.evaluate("document.body.classList.remove('read-mode')")


def _indices_juego(page) -> list[int]:
    return page.evaluate("[...document.querySelectorAll('.slide')].map((s,i)=>s.querySelector('.slide-hybrid')?i:-1).filter(i=>i>=0)")


def _rect(page, selector: str):
    return page.evaluate(
        "(sel)=>{const e=document.querySelector('.slide.active '+sel);if(!e)return null;"
        "const r=e.getBoundingClientRect();return {l:r.left,r:r.right,t:r.top,b:r.bottom,w:r.width,h:r.height}}", selector)


def _precios_17() -> dict:
    """Top Precios del caso mas apretado: 10 retail + 6 rarezas + grial = 17 casillas, con una etiqueta larga."""
    d = TG._data_precios()
    d["rarezas"] = [
        {"title": f"Rareza {i}", "ano": 1990 + i, "editor": "Editor", "price": f"USD {1000 * i}",
         "badge_text": "NO-RETAIL", "color": "cy", "why": f"Por que la rareza {i} es rara."}
        for i in range(1, 7)
    ]
    d["rarezas"][1]["badge_text"] = "PROTOTIPO NUNCA LANZADO AL PUBLICO GENERAL"
    d["grial"]["price"] = "USD 3.000.000"       # el precio mas ancho que hay (NES Top Precios)
    d["_cajas"] = ([it["title"] for it in d["items"]] + [it["title"] for it in d["rarezas"]] + ["El Grial"])
    return d


def _con_navegador(fn):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_context(viewport={"width": 1920, "height": 1080}).new_page()
            return fn(page)
        finally:
            browser.close()


def _medir_tv(page, data: dict, slug: str, grafica: str) -> list[dict]:
    ruta = TG._preparar({**data, "grafica": grafica}, slug)
    try:
        _abrir(page, ruta)
        medidas = []
        for i in _indices_juego(page):
            page.evaluate(f"go({i})")
            page.wait_for_timeout(250)
            medidas.append(_rect(page, ".tarrovision"))
        return medidas
    finally:
        TG._limpiar(slug)


# ---------------------------------------------------------------- pruebas

def test_tarrovision_identico():
    def fn(page):
        for data, slug in ((TG._data_mundial(), TG.SLUG_M), (TG._data_precios(), TG.SLUG_P)):
            a, b = _medir_tv(page, data, slug, "clasica"), _medir_tv(page, data, slug, "nueva")
            assert len(a) == len(b) and a, "no hay slides de juego"
            for i, (x, y) in enumerate(zip(a, b)):
                for k in ("l", "r", "t", "b"):
                    assert abs(x[k] - y[k]) <= 1, f"{slug} slide de juego {i}: TarroVision se movio ({k}: {x[k]} -> {y[k]})"
    _con_navegador(fn)


def _revisar_barra(page, data: dict, slug: str) -> list[dict]:
    """Devuelve, por slide de juego, las holguras medidas; lanza AssertionError si alguna es < HOLGURA_MIN."""
    ruta = TG._preparar({**data, "grafica": "nueva"}, slug)
    filas = []
    try:
        _abrir(page, ruta)
        for i in _indices_juego(page):
            page.evaluate(f"go({i})")
            page.wait_for_timeout(250)
            barra, pos, tv = _rect(page, ".g-barra"), _rect(page, ".game-pos"), _rect(page, ".tarrovision")
            precio, rotulo = _rect(page, ".game-price"), _rect(page, ".game-block-label")
            assert barra, f"{slug} slide {i}: no hay barra"
            fila = {"slide": i, "izq": barra["l"] - pos["r"] if pos else None,
                    "der": (precio["l"] - barra["r"]) if precio else ((rotulo["l"] - barra["r"]) if rotulo else None),
                    "tv": tv["t"] - barra["b"]}
            assert fila["izq"] is None or fila["izq"] >= HOLGURA_MIN, f"{slug} slide {i}: barra a {fila['izq']:.0f}px de la etiqueta"
            assert fila["der"] is None or fila["der"] >= HOLGURA_MIN, f"{slug} slide {i}: barra a {fila['der']:.0f}px del precio"
            assert fila["tv"] >= 4, f"{slug} slide {i}: la barra toca el TarroVision ({fila['tv']:.0f}px)"
            filas.append(fila)
        return filas
    finally:
        TG._limpiar(slug)


def test_barra_sin_superposicion():
    def fn(page):
        _revisar_barra(page, TG._data_mundial(), TG.SLUG_M)       # miniaturas, cajas mixtas
        _revisar_barra(page, TG._data_precios(), TG.SLUG_P)       # 14 casillas
        _revisar_barra(page, _precios_17(), TG.SLUG_P)            # 17 casillas, el caso mas apretado
    _con_navegador(fn)


def test_etiqueta_larga_se_parte():
    def fn(page):
        ruta = TG._preparar({**_precios_17(), "grafica": "nueva"}, TG.SLUG_P)
        try:
            _abrir(page, ruta)
            idx = _indices_juego(page)[11]              # la rareza #2 (10 retail + indice 1)
            page.evaluate(f"go({idx})")
            page.wait_for_timeout(250)
            pos, barra = _rect(page, ".game-pos"), _rect(page, ".g-barra")
            assert pos["h"] >= 50, f"la etiqueta larga no se partio en lineas (alto {pos['h']:.0f}px)"
            assert barra["l"] - pos["r"] >= HOLGURA_MIN
        finally:
            TG._limpiar(TG.SLUG_P)
    _con_navegador(fn)


# ---------------------------------------------------------------- runner

def main() -> int:
    pruebas = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    fallas = 0
    try:
        for nombre, fn in pruebas:
            try:
                fn()
            except Exception as exc:  # noqa: BLE001
                fallas += 1
                print(f"FALLA {nombre}: {type(exc).__name__}: {exc}")
    finally:
        for slug in (TG.SLUG_M, TG.SLUG_P, TG.SLUG_X):
            TG._limpiar(slug)
    if fallas:
        print(f"{fallas} de {len(pruebas)} pruebas fallaron")
        return 1
    print(f"OK {len(pruebas)} pruebas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
