"""Pruebas de la grafica nueva de los rankings (scripts/top_grafica.py).

Sin pytest: se corre con `python scripts/test_top_grafica.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.

  python scripts/test_top_grafica.py --golden   regenera fixtures_top_grafica/golden.json
                                                 (solo con el generador CLASICO vigente)

Las pruebas no dependen de imagenes ni de la base del estudio: usan una base HTML
congelada (fixtures_top_grafica/base_congelada.html) y cajas temporales que crean y
borran ellas mismas bajo studio/rankings/<categoria>/img/zz-prueba-*/.
"""
from __future__ import annotations
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import top_deck as T  # noqa: E402
from _studio_layout import episode_category  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures_top_grafica"
BASE_CONGELADA = FIX / "base_congelada.html"
GOLDEN_JSON = FIX / "golden.json"

SLUG_M = "zz-prueba-grafica-top-mundial"
SLUG_P = "zz-prueba-grafica-top-precios"
SLUG_X = "zz-prueba-grafica-top-peores"

# formas cicladas de las cajas temporales: vertical, cuadrada, horizontal
FORMAS = [(200, 300), (240, 240), (300, 200)]


def _data_base(consola: str = "NES") -> dict:
    return {
        "doc_title": "TOP PRUEBA",
        "header_tag": f"{consola} · TOP PRUEBA",
        "consola": consola,
        "portada": {"tag": "TOP 10 MUNDIAL", "title": "PRUEBA", "sub": "Subtitulo de prueba"},
        "intro": {"pre": "CONTEXTO", "title": "TITULO INTRO", "sub": "Texto de la intro", "color": "cy"},
        "analisis": {"pre": "ANALISIS DEL TOP", "title": "TITULO ANALISIS", "sub": "Texto del analisis", "color": "mg"},
        "cliffhanger": {"pre": "PROXIMAMENTE", "title": "TITULO CLIFF", "sub": "Texto del cliffhanger", "color": "cy"},
    }


def _data_mundial(n: int = 10, cajas: int = 10, **extra) -> dict:
    """Ranking de n items (#n..#1, ya ordenados) de los que los primeros `cajas` tienen caja temporal."""
    d = _data_base()
    d["items"] = [
        {"pos": n - k, "title": f"Juego {n - k}", "ano": 1985 + k, "editor": "Editor",
         "why": f"Por que el juego {n - k} esta en el top."}
        for k in range(n)
    ]
    d["_cajas"] = [it["title"] for it in d["items"][:cajas]]
    d.update(extra)
    return d


def _data_precios(**extra) -> dict:
    """10 retail con precio, 3 rarezas no-retail y un grial; todos con caja temporal."""
    d = _data_base()
    d["header_tag"] = "NES · TOP PRECIOS"
    d["portada"]["tag"] = "TOP 10 PRECIOS"
    d["items"] = [
        {"pos": 10 - k, "title": f"Retail {10 - k}", "ano": 1985 + k, "editor": "Editor",
         "price": f"USD {100 + 10 * (9 - k)}", "why": f"Por que el retail {10 - k} vale lo que vale."}
        for k in range(10)
    ]
    d["rarezas_divider"] = {"pre": "APARTADO ESPECIAL", "title": "RAREZAS Y NO-RETAIL",
                            "sub": "Van aparte con etiqueta en vez de numero.", "color": "mg"}
    d["rarezas"] = [
        {"title": f"Rareza {i}", "ano": 1990 + i, "editor": "Editor", "price": f"USD {1000 * i}",
         "badge_text": "NO-RETAIL", "color": "cy", "why": f"Por que la rareza {i} es rara."}
        for i in (1, 2, 3)
    ]
    d["grial"] = {"title": "El Grial", "ano": 1995, "editor": "Editor", "price": "USD 55.200",
                  "why": "El santo grial del ranking."}
    d["_cajas"] = ([it["title"] for it in d["items"]] + [it["title"] for it in d["rarezas"]] + ["El Grial"])
    d.update(extra)
    return d


def _dir_img(slug: str) -> Path:
    return T.REPO / "studio" / episode_category(slug) / "img" / slug


def _limpiar(slug: str) -> None:
    html = T.REPO / "studio" / episode_category(slug) / f"{slug}.html"
    if html.exists():
        html.unlink()
    d = _dir_img(slug)
    if d.exists():
        shutil.rmtree(d)


def _generar(data: dict, slug: str) -> str:
    """Genera el deck con la base congelada y cajas temporales (las de data['_cajas']),
    devuelve el HTML y borra todo lo que creo."""
    from PIL import Image
    base_original = T.BASE
    T.BASE = BASE_CONGELADA
    destino = _dir_img(slug)
    try:
        destino.mkdir(parents=True, exist_ok=True)
        for i, titulo in enumerate(data.get("_cajas", [])):
            w, h = FORMAS[i % len(FORMAS)]
            Image.new("RGB", (w, h), (30 + 15 * i % 200, 40, 90)).save(destino / f"{T._slug(titulo)}.jpg")
        salida = T.generar_top(data, slug)
        return salida.read_text(encoding="utf-8")
    finally:
        T.BASE = base_original
        _limpiar(slug)


def _hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


def _golden() -> dict:
    return json.loads(GOLDEN_JSON.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- Task 1: regresion de lo clasico

def test_clasica_golden_mundial():
    assert _hash(_generar(_data_mundial(), SLUG_M)) == _golden()["mundial"]


def test_clasica_golden_precios():
    assert _hash(_generar(_data_precios(), SLUG_P)) == _golden()["precios"]


def test_clasica_explicita_igual():
    assert _hash(_generar({**_data_mundial(), "grafica": "clasica"}, SLUG_M)) == _golden()["mundial"]


# ---------------------------------------------------------------- runner

def main() -> int:
    if "--golden" in sys.argv:
        golden = {"mundial": _hash(_generar(_data_mundial(), SLUG_M)),
                  "precios": _hash(_generar(_data_precios(), SLUG_P))}
        GOLDEN_JSON.write_text(json.dumps(golden, indent=2) + "\n", encoding="utf-8")
        print(f"golden escrito en {GOLDEN_JSON}: {golden}")
        return 0
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
        for slug in (SLUG_M, SLUG_P, SLUG_X):
            _limpiar(slug)
    if fallas:
        print(f"{fallas} de {len(pruebas)} pruebas fallaron")
        return 1
    print(f"OK {len(pruebas)} pruebas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
