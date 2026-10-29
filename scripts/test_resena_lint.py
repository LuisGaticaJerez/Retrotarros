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
