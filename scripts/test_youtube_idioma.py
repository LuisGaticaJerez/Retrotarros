"""Pruebas de scripts/youtube_idioma.py (restaurar el idioma de audio que las actualizaciones de octubre dejaron en en-US).

Sin pytest: se corre con `python scripts/test_youtube_idioma.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import youtube_idioma as I  # noqa: E402

ORIGINAL = {"a": "es-419", "b": None}


def _sn(audio, **extra):
    return {"title": "T", "description": "D", "categoryId": "20", "defaultAudioLanguage": audio, **extra}


def test_plan_restaura_al_original_guardado():
    plan = I.plan_restauracion({"a": _sn("en-US")}, ORIGINAL)
    assert plan == [("a", "en-US", "es-419")]


def test_plan_sin_original_o_con_original_vacio_usa_espanol_latino():
    plan = I.plan_restauracion({"b": _sn("en-US"), "z": _sn("en-US")}, ORIGINAL)
    assert plan == [("b", "en-US", "es-419"), ("z", "en-US", "es-419")]


def test_plan_ignora_los_que_no_estan_en_ingles():
    snips = {"a": _sn("es-419"), "b": _sn(None), "c": {"title": "T", "categoryId": "20"}}
    assert I.plan_restauracion(snips, ORIGINAL) == []


def test_cuerpo_cambia_solo_el_idioma_de_audio():
    sn = _sn("en-US", tags=["x"], defaultLanguage="es")
    cuerpo = I.cuerpo_restauracion("a", sn, "es-419")
    assert cuerpo == {"id": "a", "snippet": {"title": "T", "description": "D", "categoryId": "20", "tags": ["x"],
                                            "defaultLanguage": "es", "defaultAudioLanguage": "es-419"}}


def _correr_main(argv, respuesta="NO"):
    """Corre I.main() con API falsa en carpeta temporal; devuelve (respaldos, ids escritos)."""
    import builtins
    import tempfile
    snips = {"a": _sn("en-US"), "c": _sn("es-419")}
    escritos: list[str] = []

    class Videos:
        def update(self, part, body):
            escritos.append(body["id"])
            return type("R", (), {"execute": lambda s: {}})()

    class Yt:
        def videos(self):
            return Videos()

    original = (I.REPO, I.A.servicio, I.A.leer_snippets, I.cargar_objetivos, sys.argv, builtins.input)
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / "data" / "youtube"
        carpeta.mkdir(parents=True)
        I.REPO = Path(tmp)
        I.A.servicio = lambda: Yt()
        I.A.leer_snippets = lambda yt, ids: snips
        I.cargar_objetivos = lambda repo: (["a", "c"], ORIGINAL)
        sys.argv = ["youtube_idioma.py", *argv]
        builtins.input = lambda *_: respuesta
        try:
            try:
                I.main()
            except SystemExit:
                pass
            return sorted(p.name for p in carpeta.glob("respaldo-api-*.json")), escritos
        finally:
            I.REPO, I.A.servicio, I.A.leer_snippets, I.cargar_objetivos, sys.argv, builtins.input = original


def test_main_en_prueba_no_escribe_ni_guarda_respaldo():
    assert _correr_main([]) == ([], [])


def test_main_aplicar_sin_confirmar_guarda_respaldo_y_no_escribe():
    respaldos, escritos = _correr_main(["--aplicar"], respuesta="NO")
    assert len(respaldos) == 1 and escritos == []


def test_main_aplicar_confirmado_escribe_solo_los_que_estan_en_ingles():
    respaldos, escritos = _correr_main(["--aplicar"], respuesta="SI")
    assert len(respaldos) == 1 and escritos == ["a"]


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
