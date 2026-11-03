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


def _preparar(data: dict, slug: str) -> Path:
    """Genera el deck con la base congelada y cajas temporales (las de data['_cajas']) y deja
    el HTML y las cajas en su lugar; quien llama borra con _limpiar(slug)."""
    from PIL import Image
    base_original = T.BASE
    T.BASE = BASE_CONGELADA
    destino = _dir_img(slug)
    try:
        destino.mkdir(parents=True, exist_ok=True)
        formas = data.get("_formas", FORMAS)
        for i, titulo in enumerate(data.get("_cajas", [])):
            w, h = formas[i % len(formas)]
            Image.new("RGB", (w, h), (30 + 15 * i % 200, 40, 90)).save(destino / f"{T._slug(titulo)}.jpg")
        return T.generar_top(data, slug)
    finally:
        T.BASE = base_original


def _generar(data: dict, slug: str) -> str:
    """Como _preparar, pero devuelve el HTML y borra todo lo que creo."""
    try:
        return _preparar(data, slug).read_text(encoding="utf-8")
    finally:
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


# ---------------------------------------------------------------- Task 2: marca y enganches

def test_marca_invalida_error():
    for valor in ("Nueva", "nuevo", None):
        try:
            _generar({**_data_mundial(), "grafica": valor}, SLUG_M)
        except ValueError:
            continue
        raise AssertionError(f"grafica={valor!r} no lanzo ValueError")


def test_nueva_agrega_css():
    html = _generar({**_data_mundial(), "grafica": "nueva"}, SLUG_M)
    assert ".g-nueva{}" in html
    assert ".game-why{font-size:32px !important" in html   # letra grande para TV intacta
    assert ".game-price{" in html


def _modulo_cargado(marca: str | None) -> str:
    """Genera un deck en un proceso limpio y dice si top_grafica quedo importado."""
    import subprocess
    extra = "" if marca is None else f', "grafica": "{marca}"'
    codigo = (
        "import sys; sys.path.insert(0, r'%s'); import test_top_grafica as t; "
        "t._generar({**t._data_mundial()%s}, t.SLUG_M); print('top_grafica' in sys.modules)"
    ) % (str(Path(__file__).resolve().parent), extra)
    return subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, check=True).stdout.strip()


def test_modulo_nuevo_solo_con_la_marca():
    assert _modulo_cargado(None) == "False"
    assert _modulo_cargado("clasica") == "False"
    assert _modulo_cargado("nueva") == "True"


# ---------------------------------------------------------------- Task 3: portada y divisores

def _nueva(data: dict, slug: str = SLUG_M) -> str:
    return _generar({**data, "grafica": "nueva"}, slug)


def _secciones(html: str) -> list[str]:
    """Un string por <section class="slide ...>, en orden."""
    return ['<section class="slide' + s for s in html.split('<section class="slide')[1:]]


def _celdas_mosaico(seccion: str) -> list[str]:
    """Las celdas <i ...></i> del primer mosaico de la seccion, en orden."""
    import re
    ini = seccion.index('class="g-mos')
    fin = seccion.index("</div>", ini)
    return re.findall(r"<i [^>]*></i>", seccion[ini:fin])


def test_portada_nueva_con_mosaico():
    html = _nueva(_data_mundial())
    portada = _secciones(html)[0]
    assert portada.startswith('<section class="slide active g-nueva">')
    assert 'class="g-mos"' in portada
    assert len(_celdas_mosaico(portada)) == 10


def test_divisores_nueva_con_tarjeta_y_color():
    d = _data_mundial()
    del d["cliffhanger"]["color"]                       # sin color: cian por defecto
    secs = _secciones(_nueva(d))
    divisores = [s for s in secs if 'class="divider"' in s]
    assert len(divisores) == 3
    assert divisores[0].startswith('<section class="slide g-nueva g-div g-cy">')   # intro, cian
    assert divisores[1].startswith('<section class="slide g-nueva g-div g-mg">')   # analisis, magenta
    assert divisores[2].startswith('<section class="slide g-nueva g-div g-cy">')   # cliffhanger sin color
    assert all('class="g-mos tenue"' in s for s in divisores)
    assert sum(1 for s in _secciones(_nueva(_data_precios(), SLUG_P)) if 'class="g-mos tenue"' in s) == 4


def test_menos_de_6_cajas_sin_mosaico():
    html = _nueva(_data_mundial(cajas=5))
    assert "g-mos" not in html.replace(".g-mos", "")     # el CSS menciona .g-mos; el HTML no
    assert "g-div" not in html.replace(".g-div", "")
    assert '<section class="slide active">' in html


def test_mosaico_determinista_y_barajado():
    import re
    d = _data_mundial()
    h1, h2 = _nueva(d), _nueva(d)
    assert h1 == h2
    orden = re.findall(r"url\(img/[^)]*juego-(\d+)\.jpg\)", _secciones(h1)[0])
    assert sorted(orden) == sorted(str(i) for i in range(1, 11))
    assert orden != [str(i) for i in range(10, 0, -1)] and orden != [str(i) for i in range(1, 11)]


def test_mosaico_con_8_items_completa_10_celdas():
    portada = _secciones(_nueva(_data_mundial(n=8, cajas=8)))[0]
    assert len(_celdas_mosaico(portada)) == 10


def test_celda_sin_caja_usa_color_de_etiqueta():
    celdas = _celdas_mosaico(_secciones(_nueva(_data_mundial(cajas=7)))[0])
    sin_caja = [c for c in celdas if 'class="g-lb lb-default"' in c]
    assert len(celdas) == 10 and len(sin_caja) == 3, celdas


# ---------------------------------------------------------------- Task 4: slide de juego, fondo y chips

def test_chips_ano_amarillo_y_sin_precio():
    import top_grafica as G
    h = G.chips({"meta": "NES · 1992 · ACTIVE ENTERPRISES · NO LANZADO · ~USD 1.926"}, "NES")
    assert h.count('<span class="g-chip') == 4, h
    assert '<span class="g-chip y">1992</span>' in h
    assert "USD" not in h


def test_chips_demasiadas_partes_devuelve_vacio():
    import top_grafica as G
    assert G.chips({"meta": "A · B · C · D · E · F"}, "NES") == ""


def test_chips_desde_ano_y_editor():
    import top_grafica as G
    h = G.chips({"ano": 1999, "editor": "Konami (Team Silent)"}, "PS1")
    assert h == ('<div class="game-meta g-chips"><span class="g-chip">PS1</span>'
                 '<span class="g-chip y">1999</span><span class="g-chip">KONAMI (TEAM SILENT)</span></div>')


def test_item_nueva_fondo_con_caja_y_sin_caja():
    items = [s for s in _secciones(_nueva(_data_mundial(cajas=9))) if 'class="slide-hybrid' in s]
    assert len(items) == 10
    assert all(s.startswith('<section class="slide g-nueva">') for s in items)
    assert '<div class="g-bg" style="background-image:url(img/' in items[0]
    assert '<div class="g-bg g-lb lb-default"></div>' in items[-1]      # el #1 no tiene caja


def test_item_nueva_quita_rotulo_por_defecto():
    html = _nueva(_data_mundial())
    assert 'class="game-block-label' not in html
    d = _data_mundial()
    d["items"][0]["block_label"] = "EN 1 LISTA"                          # rotulo explicito (Top Peores): se conserva
    assert '<div class="game-block-label cy">EN 1 LISTA</div>' in _nueva(d)


def test_item_nueva_no_toca_tarrovision_ni_precio():
    import re
    for data, slug in ((_data_mundial(), SLUG_M), (_data_precios(), SLUG_P)):
        clasica, nueva = _generar(data, slug), _nueva(data, slug)
        tv = r'<div class="tv-wrap">(.*?)</div>\n      </div>'
        assert re.findall(tv, clasica, re.S) == re.findall(tv, nueva, re.S) != []
        assert re.findall(r'<div class="game-price">(.*?)</div>', clasica) == \
               re.findall(r'<div class="game-price">(.*?)</div>', nueva)


# ---------------------------------------------------------------- Task 5: barra de progreso

def _items(html: str) -> list[str]:
    return [s for s in _secciones(html) if 'class="slide-hybrid' in s]


def _barra(seccion: str) -> str:
    import re
    m = re.search(r'<div class="g-barra"[^>]*>(.*?)</div></div>', seccion, re.S)
    assert m, "la seccion no trae g-barra"
    return m.group(1) + "</div>"


def test_ancho_rel():
    import top_grafica as G
    assert G.ancho_rel((200, 300)) == 0.667
    assert G.ancho_rel((240, 240)) == 1.0
    assert G.ancho_rel((300, 200)) == 1.5
    assert G.ancho_rel((100, 400)) == 0.6      # limite inferior
    assert G.ancho_rel((400, 100)) == 1.7      # limite superior
    assert G.ancho_rel(None) == 1.0


def test_barra_miniaturas_estados():
    b = _barra(_items(_nueva(_data_mundial()))[2])          # el #8: ya se vieron #10 y #9
    assert b.count('class="g-th r"') == 2 and b.count('class="g-th cur"') == 1 and b.count('class="g-th f"') == 7
    futuras = [x for x in b.split('<div class="g-th ')[1:] if x.startswith("f")]
    assert len(futuras) == 7 and all("background-image" not in x for x in futuras)
    assert '<div class="g-th r" style="--w:0.667"><i style="background-image:url(img/' in b   # vertical
    assert 'style="--w:1.500"' in b and 'style="--w:1.000"' in b                                # horizontal y cuadrada


def test_barra_numeros_precios():
    import re
    items = _items(_nueva(_data_precios(), SLUG_P))
    assert len(items) == 14
    b = _barra(items[0])
    assert "g-th" not in b
    assert b.count('class="g-pip') == 14 and b.count('class="g-sep"') == 2
    assert '<div class="g-pip cur">10</div>' in b
    assert len(re.findall(r'class="g-pip rr [rcuf]+">R<', b)) == 3
    assert '<div class="g-pip gg f">★</div>' in b
    assert '<div class="g-pip gg cur">★</div>' in _barra(items[-1])         # slide del grial


def test_barra_8_items():
    assert _barra(_items(_nueva(_data_mundial(n=8, cajas=8)))[0]).count('class="g-th') == 8


def test_barra_imagen_ilegible_cuadrada():
    d = _data_mundial()
    d["items"][0]["img"] = "img/no-existe.jpg"             # apunta a un archivo que no existe
    b = _barra(_items(_nueva(d))[0])
    assert b.startswith('<div class="g-th cur" style="--w:1.000">')


def test_barra_igual_en_todas_las_slides():
    import re
    def forma(b: str) -> str:
        b = re.sub(r'<i style="background-image:url\([^)]*\)"></i>', "", b)
        return re.sub(r'class="g-(th|pip)[^"]*"', r'class="g-\1"', b)
    for data, slug in ((_data_mundial(), SLUG_M), (_data_precios(), SLUG_P)):
        formas = {forma(_barra(s)) for s in _items(_nueva(data, slug))}
        assert len(formas) == 1, "la barra cambia de forma entre slides"


def _unidad_y_ancho(seccion: str) -> tuple[float, float]:
    """(--u en px, ancho total en px) de la barra de una seccion, calculado como lo calcula el CSS."""
    import re
    u = float(re.search(r'class="g-barra" style="--u:([\d.]+)px;', seccion).group(1))
    b = _barra(seccion)
    n = b.count('class="g-th') + b.count('class="g-pip')
    seps = b.count('class="g-sep"')
    ws = [float(x) for x in re.findall(r'--w:([\d.]+)', b)]
    elementos = sum(ws) * u if ws else n * u
    return u, elementos + 6 * (n - 1) + 15 * seps


def test_barra_se_achica_si_no_cabe():
    # diez cajas muy apaisadas (1,7 de ancho relativo): la barra de 72 px de alto mediria ~1280 px
    u, ancho = _unidad_y_ancho(_items(_nueva(_data_mundial(_formas=[(400, 100)])))[0])
    assert u < 72 and ancho <= 801, (u, ancho)
    # 17 casillas numeradas (6 rarezas): tambien se achican
    d = _data_precios()
    d["rarezas"] += [{"title": f"Rareza {i}", "ano": 1990, "editor": "E", "price": "USD 1", "badge_text": "X",
                      "color": "cy", "why": "w"} for i in (4, 5, 6)]
    u, ancho = _unidad_y_ancho(_items(_nueva(d, SLUG_P))[0])
    assert u < 40 and ancho <= 801, (u, ancho)


def test_barra_tamano_normal_no_se_achica():
    u, _ = _unidad_y_ancho(_items(_nueva(_data_mundial()))[0])
    assert u == 72
    u, _ = _unidad_y_ancho(_items(_nueva(_data_precios(), SLUG_P))[0])
    assert u == 40


def _dx(seccion: str) -> float:
    import re
    m = re.search(r'class="g-barra" style="--u:[\d.]+px;--dx:(-?[\d.]+)px"', seccion)
    assert m, "la barra no trae --dx"
    return float(m.group(1))


def test_barra_se_corre_si_el_precio_es_muy_ancho():
    # NES Top Precios: el grial vale "USD 3.000.000" (caja de unos 492 px arriba a la derecha) y hay 17 casillas
    d = _data_precios()
    d["rarezas"] += [{"title": f"Rareza {i}", "ano": 1990, "editor": "E", "price": "USD 1", "badge_text": "X",
                      "color": "cy", "why": "w"} for i in (4, 5, 6)]
    d["grial"]["price"] = "USD 3.000.000"
    seccion = _items(_nueva(d, SLUG_P))[0]
    u, ancho = _unidad_y_ancho(seccion)
    dx = _dx(seccion)
    derecha, izquierda = dx + ancho / 2, dx - ancho / 2          # bordes de la barra respecto del centro de la cabecera
    assert derecha <= 875 - 492 - 100, f"la barra llega a {derecha:.0f}px: toca el precio"
    assert izquierda >= -875 + 360 + 100, f"la barra llega a {izquierda:.0f}px: toca la etiqueta"
    assert u >= 28, f"las casillas quedaron demasiado chicas ({u}px)"


def test_barra_sin_precio_ancho_queda_centrada():
    assert _dx(_items(_nueva(_data_mundial()))[0]) == 0
    assert _dx(_items(_nueva(_data_precios(), SLUG_P))[0]) == 0


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
