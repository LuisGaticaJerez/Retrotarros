"""Pruebas de la grafica nueva de las colecciones (scripts/coleccion_grafica.py) y del generador clasico.

Sin pytest: se corre con `python scripts/test_coleccion_grafica.py`. Toda funcion `test_*` se ejecuta;
sale con codigo 1 si alguna falla.

  python scripts/test_coleccion_grafica.py --golden   regenera fixtures_coleccion_grafica/golden.json
                                                       (solo con el generador CLASICO vigente)

Las pruebas no dependen de imagenes ni de decks del estudio: usan una base HTML congelada
(fixtures_coleccion_grafica/base_congelada.html) y escriben en carpetas temporales (nunca en
studio/ ni en docs/descripciones/).
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coleccion_deck as D  # noqa: E402

AQUI = Path(__file__).resolve().parent
FIX = AQUI / "fixtures_coleccion_grafica"
BASE_CONGELADA = FIX / "base_congelada.html"
GOLDEN_JSON = FIX / "golden.json"
DATOS = AQUI.parent / "data" / "colecciones"
SLUG = "zz-prueba-coleccion"


def _data(ncat: int = 3, hardware: bool = True, **extra) -> dict:
    cats = []
    for i in range(1, ncat + 1):
        cats.append({
            "name": f"CATEGORIA {i}", "count": 4 + i,
            "juegos": [f"Juego {i}-{k}" for k in range(1, 5 + i)],
            "joyas": [{"title": f"JOYA {i} {k}", "ano": 1985 + k, "editor": "EDITOR"} for k in range(1, 4)],
        })
    d = {
        "doc_title": "PRUEBA · Coleccion completa", "header_tag": "ESTUDIO · PRUEBA · COLECCION",
        "portada": {"tag": "GENERACION 3 · PRUEBA", "title_vs": "COLECCION", "title_rest": "PRUEBA",
                    "sub": "EL CATALOGO COMPLETO", "count": "X JUEGOS"},
        "categorias": cats,
        "balance": {"row1": [{"label": "JUEGOS", "big": "99", "sub": "cartuchos en la coleccion", "color": "mg"},
                             {"label": "CATEGORIAS", "big": "99", "sub": "generos cubiertos", "color": "cy"},
                             {"label": "JOYAS", "big": "99", "sub": "destacadas", "color": "ye"}],
                    "row2": [{"label": "CONSOLA", "big": "PRUEBA", "sub": "la de prueba", "color": "mg"}]},
        "cierre": {"pre": "PROXIMO CAPITULO", "title": "SIGUE LA SAGA", "sub": "Texto del cierre sin tildes."},
    }
    if hardware:
        d["hardware_titulo"] = "HARDWARE"
        d["hardware_sub"] = "EL FIERRO DE PRUEBA"
        d["hardware"] = [{"name": f"EQUIPO {k}", "tag": "TAG", "color": ["mg", "cy", "ye"][k % 3], "desc": f"Descripcion {k}."}
                         for k in range(3)]
    d.update(extra)
    return d


def _con_base_congelada(fn):
    original = D.BASE
    D.BASE = BASE_CONGELADA
    try:
        return fn()
    finally:
        D.BASE = original


def _generar(data: dict, cajas: int = 0, out: Path | None = None, **kw) -> str:
    """Genera en una carpeta temporal (con `cajas` imagenes de prueba para las primeras joyas) y devuelve el HTML."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp) if out is None else out
        if cajas:
            (tmp / "img" / SLUG).mkdir(parents=True, exist_ok=True)
            n = 0
            for c in data["categorias"]:
                for j in c["joyas"]:
                    if n < cajas:
                        key = re.sub(r"[^a-z0-9]+", "-", j["title"].lower()).strip("-")
                        (tmp / "img" / SLUG / f"{key}.jpg").write_bytes(b"x")
                        n += 1
        ruta = _con_base_congelada(lambda: D.generar_deck(data, SLUG, out_dir=tmp, lista=False, **kw))
        return ruta.read_text(encoding="utf-8")


def _hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _golden() -> dict:
    return json.loads(GOLDEN_JSON.read_text(encoding="utf-8"))


def _cuerpo(h: str) -> str:
    return h[h.index("<body>"):]


# ---------------------------------------------------------------- clasico intacto

def test_clasica_golden():
    assert _hash(_generar(_data())) == _golden()["completo"]


def test_clasica_golden_sin_hardware_ni_fila_2():
    d = _data(hardware=False)
    del d["balance"]["row2"]
    assert _hash(_generar(d)) == _golden()["sin_hardware"]


def test_marca_clasica_explicita_es_identica():
    assert _hash(_generar(_data(grafica="clasica"))) == _golden()["completo"]


def test_marca_invalida_lanza_valueerror():
    try:
        _generar(_data(grafica="nuevo"))
    except ValueError:
        return
    raise AssertionError("no lanzo ValueError con grafica invalida")


def test_clasica_no_importa_el_modulo_nuevo():
    codigo = (
        "import sys; sys.path.insert(0, %r); import coleccion_deck as D, tempfile, pathlib; "
        "D.BASE = pathlib.Path(%r); t = pathlib.Path(tempfile.mkdtemp()); "
        "d = %r; D.generar_deck(d, 'zz', out_dir=t, lista=False); "
        "assert 'coleccion_grafica' not in sys.modules, 'se importo el modulo nuevo'"
    ) % (str(AQUI), str(BASE_CONGELADA), _data())
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-400:]


# ---------------------------------------------------------------- grafica nueva

def test_nueva_misma_estructura_de_slides():
    for ncat, hw in ((3, True), (6, True), (9, False), (4, True)):
        clasica = _generar(_data(ncat, hw))
        nueva = _generar(_data(ncat, hw, grafica="nueva"))
        assert clasica.count('<section class="slide') == nueva.count('<section class="slide'), (ncat, hw)
        assert nueva.count('<section class="slide') == 2 + 2 * ncat + (1 if hw else 0) + 2


def test_nueva_marca_las_slides_y_cambia_el_html():
    clasica = _generar(_data())
    nueva = _generar(_data(grafica="nueva"))
    assert clasica != nueva
    assert 'g-nueva' in nueva and 'g-nueva' not in clasica
    assert "COLECCION RETROTARROS" in nueva


def test_nueva_mosaico_solo_con_seis_cajas_o_mas():
    con = _generar(_data(grafica="nueva"), cajas=6)
    sin = _generar(_data(grafica="nueva"), cajas=5)
    assert 'class="g-mos' in con and 'class="g-mos' not in sin
    assert 'g-mos tenue' in con          # el cierre usa el mosaico tenue


def test_nueva_cajas_y_respaldo():
    h = _generar(_data(grafica="nueva"), cajas=4)
    assert h.count('class="g-caja"') == 4                    # 4 con caja real (una por joya)
    assert h.count('g-caja fb') == 9 - 4                     # el resto, placa de respaldo
    assert f"img/{SLUG}/joya-1-1.jpg" in h


def test_nueva_totales_se_calculan_desde_las_categorias():
    d = _data(grafica="nueva")                               # balance tipeado con 99: no debe aparecer
    h = _generar(d)
    juegos = sum(c["count"] for c in d["categorias"])
    assert f"<b>{juegos}</b><p>cartuchos en la coleccion</p>" in h
    assert "<b>99</b>" not in h


def test_nueva_sin_hardware_no_hay_slide_de_hardware():
    assert 'class="g-hard"' not in _generar(_data(hardware=False, grafica="nueva"))
    assert 'class="g-hard"' in _generar(_data(grafica="nueva"))


def test_nueva_hardware_con_foto():
    d = _data(grafica="nueva")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "img" / SLUG).mkdir(parents=True)
        (tmp / "img" / SLUG / "hw-equipo-1.jpg").write_bytes(b"x")
        h = _generar(d, out=tmp)
    assert f'<img src="img/{SLUG}/hw-equipo-1.jpg"' in h and h.count("g-hfoto sin") == 2


def test_nueva_tarrovision_del_triple():
    assert "tvn cuatro3" in _generar(_data(grafica="nueva"))
    h = _generar(_data(grafica="nueva", tarrovision="ancha"))
    assert "tvn ancha" in h and "tvn cuatro3" not in _cuerpo(h)
    assert "tvn cuatro3" in _generar(_data(grafica="nueva", tarrovision="clasica"))   # clasica cae al 4:3 nuevo
    try:
        _generar(_data(grafica="nueva", tarrovision="otra"))
    except ValueError:
        return
    raise AssertionError("no lanzo ValueError con tarrovision invalida")


def test_nueva_paneo_siempre_ancha():
    h = _cuerpo(_generar(_data(grafica="nueva")))
    assert h.count('class="gp-tv tvw"') == 3 and h.count("tvn ancha") == 3


def test_nueva_cierre_con_proximo_y_sin_proximo():
    sin = _generar(_data(grafica="nueva"))
    con = _generar(_data(grafica="nueva", proximo={"titulo": "NES TOP MUNDIAL", "consola": "NES", "tag": "RANKING"}))
    assert "SIGUE CON" not in sin and "Texto del cierre sin tildes." in sin
    assert "SIGUE CON" in con and "NES TOP MUNDIAL" in con


def test_nueva_notas_solo_si_hay_contenido():
    d = _data(ncat=2, grafica="nueva")
    h = _generar(d)
    assert h.count('<aside class="notas">') == 2             # paneos con 'juegos'
    assert "CATALOGO DE LA CATEGORIA" in h and "Juego 1-1" in h
    for c in d["categorias"]:
        del c["juegos"]
    assert '<aside class="notas">' not in _generar(d)
    d["categorias"][0]["joyas"][0]["nota"] = "dato extra"
    assert "JOYA 1 1: dato extra" in _generar(d)


def test_nueva_notas_apagadas_por_defecto():
    h = _generar(_data(grafica="nueva"))
    assert ".g-nueva .notas{display:none}" in h
    assert "classList.toggle('read-mode')" in h               # tecla N


def test_nueva_sin_tildes_en_pantalla():
    cuerpo = _cuerpo(_generar(_data(grafica="nueva")))
    malas = re.findall(r"[áéíóúÁÉÍÓÚ]", re.sub(r"<script>.*?</script>", "", cuerpo, flags=re.S))
    assert not malas, malas


def test_nueva_no_muta_el_data_del_driver():
    d = _data(grafica="nueva")
    antes = copy.deepcopy(d)
    _generar(d, cajas=3)
    assert d == antes


def test_nueva_escapa_el_html_de_los_titulos():
    d = _data(grafica="nueva")
    d["categorias"][0]["joyas"][0]["title"] = "A & B <C>"
    h = _generar(d)
    assert "A &amp; B &lt;C&gt;" in h


def test_nueva_indice_de_9_categorias_usa_el_compacto():
    assert 'g-igrid r3' in _generar(_data(9, grafica="nueva"))
    assert 'g-igrid r3' not in _generar(_data(6, grafica="nueva"))


def test_nueva_respeta_la_proporcion_de_las_cajas():
    from PIL import Image
    import coleccion_grafica as G
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        Image.new("RGB", (378, 263)).save(tmp / "a.jpg")
        Image.new("RGB", (100, 200)).save(tmp / "b.png")
        (tmp / "c.jpg").write_bytes(b"no es una imagen")
        assert abs(G._aspecto(tmp / "a.jpg") - 378 / 263) < 0.001
        assert G._aspecto(tmp / "b.png") == 0.5
        assert G._aspecto(tmp / "c.jpg") == G.AR_VERTICAL and G._aspecto(tmp / "no-existe.jpg") == G.AR_VERTICAL
    # en el deck: la caja apaisada lleva su --ar y la tira de miniaturas se achica para entrar en la tarjeta
    d = _data(grafica="nueva")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "img" / SLUG).mkdir(parents=True)
        for k in (1, 2, 3):
            Image.new("RGB", (378, 263)).save(tmp / "img" / SLUG / f"joya-1-{k}.jpg")
        h = _generar(d, out=tmp)
    assert "--ar:1.437" in h
    th = [int(x) for x in re.findall(r'class="g-ithumbs" style="--th:(\d+)px"', h)]
    assert th[0] < 150 and th[1] == 150, th            # 3 apaisadas no caben a 150 px de alto; las verticales (respaldo) si


# ---------------------------------------------------------------- datos versionados

def test_datos_versionados_de_las_colecciones():
    archivos = sorted(DATOS.glob("*-coleccion.json"))
    assert len(archivos) >= 4, archivos
    for ruta in archivos:
        d = json.loads(ruta.read_text(encoding="utf-8"))
        cats = d["categorias"]
        assert all(len(c["joyas"]) == 3 for c in cats), ruta.name
        assert sum(c["count"] for c in cats) == int(d["balance"]["row1"][0]["big"]), ruta.name
        assert len(cats) == int(d["balance"]["row1"][1]["big"]), ruta.name
        assert sum(len(c["joyas"]) for c in cats) == int(d["balance"]["row1"][2]["big"]), ruta.name
        for marca in ({"grafica": "clasica"}, {"grafica": "nueva"}):   # los datos generan en las dos graficas
            _generar({**d, **marca})


def main() -> int:
    if "--golden" in sys.argv:
        sin = _data(hardware=False)
        del sin["balance"]["row2"]
        golden = {"completo": _hash(_generar(_data())), "sin_hardware": _hash(_generar(sin))}
        GOLDEN_JSON.write_text(json.dumps(golden, indent=2) + "\n", encoding="utf-8")
        print(f"golden escrito en {GOLDEN_JSON}: {golden}")
        return 0
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
