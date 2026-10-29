"""Pruebas de scripts/resena_lint.py (y de su integracion en resena_deck.py).

Sin pytest: se corre con `python scripts/test_resena_lint.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.
"""
from __future__ import annotations
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resena_lint as L  # noqa: E402

CONTEXTO_OK = (
    "Llegamos a un momento en que los juegos de PC buscaban ser mas que una "
    "demostracion tecnica y apostaban por ideas nuevas. Este titulo tomo esa "
    "apuesta, la llevo a un genero que casi nadie exploraba y logro que muchos "
    "jugadores se quedaran pegados a la pantalla durante horas."
)

DATA_VALIDA = {
    "juego": "Juego de Prueba",
    "img_key": "juego-de-prueba-inexistente",
    "gancho_sub": "Un gancho corto para la portada",
    "consola": "PC",
    "anio": "1999",
    "developer": "Estudio Ejemplo",
    "genero": "Accion",
    "en_coleccion": False,
    "grafica": "clasica",
    "contexto_texto": CONTEXTO_OK,
    "jugabilidad_dato": "Controlas a un personaje y resuelves misiones con el mouse.",
    "audiovisual_dato": "Graficos 2D coloridos y musica pegajosa.",
    "veredicto_tag": "JUEGAZO",
    "veredicto_resumen": "Hay que jugarlo por su diseno y por lo que nos hizo sentir.",
    "notas": {
        "portada": {"titulo": "INTRO", "lineas": ["Presentate hablando."]},
        "ficha": {"titulo": "FICHA", "lineas": [
            "Salio solo en PC. No tuvo version arcade previa: nacio directo en computador.",
        ]},
        "contexto": {"titulo": "EPOCA", "lineas": [
            "DETALLE QUE SE CORTO DE PANTALLA: datos extra del desarrollo.",
            "TRAMA RESUMIDA: es un sandbox sin historia lineal.",
        ]},
        "comparativa": {"titulo": "COMPARATIVA", "lineas": ["Original contra su secuela."]},
        "jugabilidad": {"titulo": "JUGABILIDAD", "lineas": [
            "Mecanica uno: se controla con el mouse.",
            "Mecanica dos: hay un inventario con objetos.",
            "Mecanica tres: se sube de nivel al completar misiones.",
        ]},
        "audiovisual": {"titulo": "AUDIOVISUAL", "lineas": ["Musica y graficos."]},
        "veredicto": {"titulo": "VEREDICTO", "lineas": ["Por que esta nota."]},
        "cierre": {"titulo": "CIERRE", "lineas": ["Proximo juego."]},
    },
}


def _data(**cambios) -> dict:
    d = copy.deepcopy(DATA_VALIDA)
    d.update(cambios)
    return d


def _hay(mensajes: list[str], fragmento: str) -> bool:
    return any(fragmento.lower() in m.lower() for m in mensajes)


# ---------------------------------------------------------------- Task 1

def test_valida_sin_errores():
    errores, _ = L.revisar(_data(), "resena-juego")
    assert errores == [], errores


def test_veredicto_fuera_de_escala():
    errores, _ = L.revisar(_data(veredicto_tag="FUNDACIONAL DEL GENERO"), "resena-juego")
    assert _hay(errores, "veredicto"), errores


def test_veredicto_con_espacios_y_minusculas():
    errores, _ = L.revisar(_data(veredicto_tag=" juegazo "), "resena-juego")
    assert errores == [], errores


def test_tilde_en_pantalla():
    errores, _ = L.revisar(_data(contexto_texto="Una historia épica sobre el pasado."), "resena-juego")
    assert _hay(errores, "contexto_texto"), errores
    errores, _ = L.revisar(_data(anio="Año 1999"), "resena-juego")
    assert errores == [], errores  # la ñ esta permitida


def test_falta_trama():
    d = _data()
    d["notas"]["contexto"]["lineas"] = ["Solo detalle, sin la trama."]
    errores, _ = L.revisar(d, "resena-juego")
    assert _hay(errores, "TRAMA RESUMIDA"), errores


def test_falta_arcade():
    d = _data()
    d["notas"]["ficha"]["lineas"] = ["Salio solo en PC."]
    errores, _ = L.revisar(d, "resena-juego")
    assert _hay(errores, "arcade"), errores
    d["notas"]["ficha"]["lineas"] = ["Version ARCADE: no existe."]
    errores, _ = L.revisar(d, "resena-juego")
    assert errores == [], errores


def test_sufijo_pedido():
    pedido = {"cta": "Y eso hicimos."}
    errores, _ = L.revisar(_data(pedido=pedido), "resena-juego")
    assert _hay(errores, "-pedido"), errores
    errores, _ = L.revisar(_data(), "resena-juego-pedido")
    assert _hay(errores, "-pedido"), errores
    errores, _ = L.revisar(_data(pedido=pedido), "resena-juego-pedido")
    assert errores == [], errores


def test_sin_notas_no_falla():
    d = _data()
    del d["notas"]
    errores, _ = L.revisar(d, "resena-juego")
    assert isinstance(errores, list)
    errores, _ = L.revisar(_data(notas=None), "resena-juego")
    assert isinstance(errores, list)


def test_campos_ausentes_o_none():
    d = _data(gancho_sub=None)
    d.pop("cierre_sub", None)
    errores, avisos = L.revisar(d, "resena-juego")
    assert errores == [], errores


# ---------------------------------------------------------------- Task 2

def test_valida_sin_avisos():
    _, avisos = L.revisar(_data(), "resena-juego")
    assert avisos == [], avisos


def test_aviso_contexto_largo():
    _, avisos = L.revisar(_data(contexto_texto=" ".join(["palabra"] * 76)), "resena-juego")
    assert _hay(avisos, "76 palabras"), avisos
    _, avisos = L.revisar(_data(contexto_texto=" ".join(["palabra"] * 70)), "resena-juego")
    assert not _hay(avisos, "contexto_texto"), avisos


def test_aviso_tildes_en_notas():
    d = _data()
    d["notas"]["portada"]["lineas"] = ["Presentate, él habla primero."]
    errores, avisos = L.revisar(d, "resena-juego")
    assert errores == [], errores
    assert _hay(avisos, "tilde en notas"), avisos


def test_aviso_critica_en_pantalla():
    _, avisos = L.revisar(_data(veredicto_resumen="No compite ni de cerca con otros."), "resena-juego")
    assert _hay(avisos, "no compite"), avisos
    d = _data()
    d["notas"]["veredicto"]["lineas"] = ["Critica de la epoca: no compite ni de cerca."]
    _, avisos = L.revisar(d, "resena-juego")
    assert avisos == [], avisos


def test_aviso_orden_plataformas():
    d = _data(consola="PC · PS2")
    _, avisos = L.revisar(d, "resena-juego")
    assert _hay(avisos, "primera"), avisos
    d["notas"]["ficha"]["lineas"].append("Primera plataforma: PC, luego PS2. Sin arcade.")
    _, avisos = L.revisar(d, "resena-juego")
    assert not _hay(avisos, "primera"), avisos


def test_aviso_jugabilidad_corta():
    d = _data()
    d["notas"]["jugabilidad"]["lineas"] = ["Una linea.", "Dos lineas."]
    _, avisos = L.revisar(d, "resena-juego")
    assert _hay(avisos, "jugabilidad"), avisos


def test_aviso_bloques_faltantes():
    d = _data()
    del d["notas"]["cierre"]
    _, avisos = L.revisar(d, "resena-juego")
    assert _hay(avisos, "cierre"), avisos


def test_aviso_por_confirmar_sin_campo():
    d = _data()
    d["notas"]["audiovisual"]["lineas"].append("Cifra de ventas: por confirmar en otra fuente.")
    _, avisos = L.revisar(d, "resena-juego")
    assert _hay(avisos, "por_confirmar"), avisos
    d["por_confirmar"] = ["Cifra de ventas"]
    _, avisos = L.revisar(d, "resena-juego")
    assert not _hay(avisos, "por_confirmar"), avisos


def test_aviso_caja_chica():
    import tempfile
    from PIL import Image
    original = L.RUTA_CAJAS
    with tempfile.TemporaryDirectory() as tmp:
        L.RUTA_CAJAS = Path(tmp)
        try:
            Image.new("RGB", (256, 360)).save(Path(tmp) / "juego-de-prueba-inexistente.jpg")
            _, avisos = L.revisar(_data(), "resena-juego")
            assert _hay(avisos, "256 px"), avisos
            Image.new("RGB", (600, 800)).save(Path(tmp) / "juego-de-prueba-inexistente.jpg")
            _, avisos = L.revisar(_data(), "resena-juego")
            assert not _hay(avisos, "caja"), avisos
        finally:
            L.RUTA_CAJAS = original


# ---------------------------------------------------------------- Task 3

# SHA-256 del texto (saltos de linea normalizados al leer) del HTML que producia
# generar_resena(DATA_VALIDA) ANTES de la integracion.
HASH_ANTERIOR = "3f2c83398dfb4a3b2872ad1960533666f514166ad9fcc5d5d92b8ed6734b8e9c"
SLUG_TMP = "_test-lint-tmp"


def _ruta_tmp() -> Path:
    import resena_deck as D
    return D.REPO / "studio" / "resenas" / f"{SLUG_TMP}.html"


def _generar(data: dict, **kw) -> str:
    import resena_deck as D
    try:
        return D.generar_resena(data, SLUG_TMP, **kw).read_text(encoding="utf-8")
    finally:
        if _ruta_tmp().exists():
            _ruta_tmp().unlink()


def test_generar_con_errores_lanza_y_no_escribe():
    import resena_deck as D
    try:
        D.generar_resena(_data(veredicto_tag="X"), SLUG_TMP)
    except ValueError as exc:
        assert "veredicto" in str(exc).lower()
    else:
        raise AssertionError("debia lanzar ValueError")
    assert not _ruta_tmp().exists()


def test_lint_false_permite_generar():
    html = _generar(_data(veredicto_tag="X"), lint=False)
    assert "<!DOCTYPE html>" in html


def test_env_off():
    import os
    os.environ["RESENA_LINT"] = "off"
    try:
        html = _generar(_data(veredicto_tag="X"))
    finally:
        os.environ.pop("RESENA_LINT", None)
    assert "<!DOCTYPE html>" in html


def test_por_confirmar_en_portada():
    html = _generar(_data(por_confirmar=["Ventas de 1998", "Version de consola"]))
    marca = "POR CONFIRMAR ANTES DE GRABAR"
    assert marca in html
    assert html.index(marca) < html.index("<h4>INTRO</h4>")
    assert "Ventas de 1998" in html and "Version de consola" in html
    assert marca not in _generar(_data())


def test_por_confirmar_escapa_html():
    html = _generar(_data(por_confirmar=["Ventas <b>1&2</b>"]))
    assert "Ventas &lt;b&gt;1&amp;2&lt;/b&gt;" in html
    assert "<b>1&2" not in html


def test_ficha_familia():
    html = _generar(_data(en_coleccion="familia", familia_texto="Si tenemos MySims Kingdom (DS)"))
    assert '<div class="ficha-owned faltan">NO ESTA EN LA COLECCION</div>' in html
    assert '<div class="ficha-familia">Si tenemos MySims Kingdom (DS)</div>' in html
    html = _generar(_data(en_coleccion="familia"))
    assert '<div class="ficha-owned faltan">NO ESTA EN LA COLECCION</div>' in html
    assert 'class="ficha-familia"' not in html


def test_ficha_booleanos_sin_cambio():
    html = _generar(_data(en_coleccion=True))
    assert '<div class="ficha-owned">EN LA COLECCION</div>' in html
    assert 'class="ficha-familia"' not in html
    html = _generar(_data(en_coleccion=False))
    assert '<div class="ficha-owned faltan">NO ESTA EN LA COLECCION</div>' in html
    assert 'class="ficha-familia"' not in html


def test_salida_identica_sin_campos_nuevos():
    import hashlib
    html = _generar(_data())
    assert hashlib.sha256(html.encode("utf-8")).hexdigest() == HASH_ANTERIOR


# ---------------------------------------------------------------- Revision final

def test_trama_en_titulo_del_bloque():
    d = _data()
    d["notas"]["contexto"] = {
        "titulo": "EPOCA · TRAMA RESUMIDA (para llevar el hilo)",
        "lineas": ["Solo detalle, la trama va en el titulo del bloque."],
    }
    errores, _ = L.revisar(d, "resena-juego")
    assert errores == [], errores
    d["notas"]["contexto"] = {"titulo": "EPOCA", "lineas": ["Trama resumida: sandbox sin historia."]}
    errores, _ = L.revisar(d, "resena-juego")
    assert errores == [], errores  # sin distinguir mayusculas


def test_familia_texto_con_tilde():
    d = _data(en_coleccion="familia", familia_texto="Sí tenemos MySims Kingdom (DS)")
    errores, _ = L.revisar(d, "resena-juego")
    assert _hay(errores, "familia_texto"), errores


def _driver_temporal(carpeta: Path, linea_data: str) -> Path:
    ruta = carpeta / "gen_resena_prueba.py"
    ruta.write_text(
        "import test_resena_lint as T\n"
        "from resena_deck import generar_resena\n"
        f"generar_resena({linea_data}, 'resena-prueba')\n",
        encoding="utf-8",
    )
    return ruta


def test_capturar_driver():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ruta = _driver_temporal(Path(tmp), "T._data()")
        capturado = L.capturar_driver(str(ruta))
        assert len(capturado) == 1, capturado
        assert capturado[0][1] == "resena-prueba"
        assert capturado[0][0]["juego"] == "Juego de Prueba"
        vacio = Path(tmp) / "sin_llamada.py"
        vacio.write_text("x = 1\n", encoding="utf-8")
        assert L.capturar_driver(str(vacio)) == []
    assert not _ruta_tmp().parent.joinpath("resena-prueba.html").exists()


def test_cli_driver_con_errores():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ruta = _driver_temporal(Path(tmp), "T._data(veredicto_tag='X')")
        assert L.main([str(ruta)]) == 1
    assert not _ruta_tmp().parent.joinpath("resena-prueba.html").exists()


def test_cli_driver_valido():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        ruta = _driver_temporal(Path(tmp), "T._data()")
        assert L.main([str(ruta)]) == 0
    assert L.main([]) == 2  # uso incorrecto
    assert not _ruta_tmp().parent.joinpath("resena-prueba.html").exists()


# ---------------------------------------------------------------- Grafica nueva

VINETAS_OK = [["CONTROLAS CON EL MOUSE", "Clic en un objeto y eliges la accion"],
              ["OCHO NECESIDADES", "Hambre, baño, energia y mas"],
              ["CONSTRUYE TU CASA", "20.000 simoleones para empezar"]]


def test_grafica_valor_invalido():
    errores, _ = L.revisar(_data(grafica="otra"), "resena-juego")
    assert _hay(errores, "grafica"), errores


def test_grafica_ausente_avisa():
    d = _data()
    del d["grafica"]
    _, avisos = L.revisar(d, "resena-juego")
    assert _hay(avisos, 'grafica="nueva"'), avisos
    for valor in ("clasica", "nueva"):
        _, avisos = L.revisar(_data(grafica=valor), "resena-juego")
        assert not _hay(avisos, "sin la marca grafica"), avisos


def test_vinetas_cantidad():
    assert _hay(L.revisar(_data(jugabilidad_vinetas=VINETAS_OK[:2]), "resena-juego")[0], "jugabilidad_vinetas")
    assert _hay(L.revisar(_data(jugabilidad_vinetas=VINETAS_OK + [["D", "d"]]), "resena-juego")[0], "jugabilidad_vinetas")
    assert L.revisar(_data(jugabilidad_vinetas=VINETAS_OK), "resena-juego")[0] == []


def test_vinetas_tilde_y_critica():
    malas = [["ACCIÓN", "texto"]] + VINETAS_OK[1:]
    assert _hay(L.revisar(_data(jugabilidad_vinetas=malas), "resena-juego")[0], "jugabilidad_vinetas")
    duras = [["CONTROLES", "Un manejo aburrido"]] + VINETAS_OK[1:]
    errores, avisos = L.revisar(_data(jugabilidad_vinetas=duras), "resena-juego")
    assert errores == [] and _hay(avisos, "aburrido"), (errores, avisos)


def test_textos_nuevos_con_tilde():
    assert _hay(L.revisar(_data(audiovisual_compositor="Jérry Martin"), "resena-juego")[0], "audiovisual_compositor")
    assert _hay(L.revisar(_data(proxima={"juego": "Épico", "consola": "PS2", "anio": "2005"}), "resena-juego")[0], "proxima")


def test_nueva_sin_vinetas_ni_plataformas_avisa():
    _, avisos = L.revisar(_data(grafica="nueva"), "resena-juego")
    assert _hay(avisos, "jugabilidad_vinetas"), avisos
    _, avisos = L.revisar(_data(grafica="nueva", consola="PC · PS2"), "resena-juego")
    assert _hay(avisos, "campo plataformas"), avisos
    _, avisos = L.revisar(_data(grafica="nueva", consola="PC · PS2", plataformas=[["PC", "2000"], ["PS2", "2003"]]), "resena-juego")
    assert not _hay(avisos, "campo plataformas"), avisos


def test_vinetas_forma_invalida():
    for malas in ([None, 5, ["x"]],
                  [["A", 1], ["B", "b"], ["C", "c"]],
                  [["", ""], ["", ""], ["", ""]],
                  [["A", "a"], ["B", "b"], ["C"]]):
        errores, _ = L.revisar(_data(grafica="nueva", jugabilidad_vinetas=malas), "resena-juego")
        assert _hay(errores, "jugabilidad_vinetas"), (malas, errores)
    assert L.revisar(_data(grafica="nueva", jugabilidad_vinetas=VINETAS_OK), "resena-juego")[0] == []


def test_salida_identica_sin_la_marca():
    """El caso real de los 49 drivers existentes: sin la clave grafica el HTML no cambia."""
    import hashlib
    d = _data()
    del d["grafica"]
    html = _generar(d)
    assert hashlib.sha256(html.encode("utf-8")).hexdigest() == HASH_ANTERIOR


def test_textos_nuevos_mal_formados_no_fallan():
    d = _data(jugabilidad_vinetas=[None, 5, ["solo uno"]], proxima="texto", plataformas=[None, ["PC"]])
    errores, avisos = L.revisar(d, "resena-juego")
    assert isinstance(errores, list) and isinstance(avisos, list)


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
