"""Pruebas de scripts/resena_kit.py (esqueleto y revision del kit de YouTube).

Sin pytest: se corre con `python scripts/test_resena_kit.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.
"""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resena_kit as K  # noqa: E402
from test_resena_lint import _data  # noqa: E402

CTA = "🔔 Suscríbete a RETROTARROS para más reseñas retro: nostalgia + juegos + música."
COLA = ("retroreseñas, reseña retro, retrogaming, juegos retro, nostalgia gamer, "
        "¿envejeció bien?, retrotarros")


def _driver(carpeta: Path, llamadas: list[str]) -> Path:
    """Driver temporal que llama a generar_resena una vez por cada slug dado."""
    ruta = carpeta / "gen_resena_prueba.py"
    cuerpo = "".join(f"generar_resena(T._data(), '{s}')\n" for s in llamadas)
    ruta.write_text(
        "import test_resena_lint as T\nfrom resena_deck import generar_resena\n" + cuerpo,
        encoding="utf-8",
    )
    return ruta


# ---------------------------------------------------------------- Task 2

def test_hashtag_juego():
    assert K.hashtag_juego(_data(juego="Commandos: Behind Enemy Lines")) == "#Commandos"
    assert K.hashtag_juego(_data(juego="The Sims")) == "#TheSims"
    assert K.hashtag_juego(_data(juego="Pokémon Rojo/Azul")) == "#PokémonRojoAzul"
    assert K.hashtag_juego(_data(juego="Disney's Aladdin")) == "#DisneysAladdin"
    assert K.hashtag_juego(_data(hashtag_juego="#Doom2")) == "#Doom2"
    assert K.hashtag_juego(_data(hashtag_juego="Doom2")) == "#Doom2"


def test_hashtag_consola():
    assert K.hashtag_consola(_data(consola="SNES · Sega Genesis")) == "#SNES"
    assert K.hashtag_consola(_data(consola="PC · Mac · PlayStation 2")) == "#PC"
    assert K.hashtag_consola(_data(consola="Sega Genesis")) == "#SegaGenesis"
    assert K.hashtag_consola(_data(consola="")) == ""
    d = _data()
    del d["consola"]
    assert K.hashtag_consola(d) == ""


def test_hashtags_linea():
    assert K.hashtags(_data()) == "#RetroReseñas #JuegoDePrueba #PC #Retrogaming #Retrotarros"


def test_tags():
    lista = [t.strip() for t in K.tags(_data()).split(",")]
    assert "juego de prueba reseña" in lista
    assert "juego de prueba 1999" in lista
    assert "estudio ejemplo" in lista
    assert COLA in K.tags(_data())
    assert K.tags(_data()).endswith(
        "[REDACTAR: sumar tags propios del juego: personas, secuela, términos]")
    assert len(lista) == len(set(lista)), "hay tags duplicados"
    t = K.tags(_data(developer="Pyro Studios (publica Eidos Interactive)"))
    assert "pyro studios" in t and "eidos" not in t
    d = _data()
    for campo in ("developer", "genero", "consola"):
        d.pop(campo)
    assert COLA in K.tags(d)  # sin esos campos no lanza excepcion


def test_esqueleto_estructura():
    kit = K.esqueleto(_data(), "resena-juego", "2026-10-28")
    assert "Volvemos a 1999 para revisar Juego de Prueba" in kit
    assert CTA in kit
    assert "#RetroReseñas #JuegoDePrueba #PC #Retrogaming #Retrotarros" in kit
    assert "**Slug:** `resena-juego`" in kit
    assert "**Última actualización:** 2026-10-28" in kit
    assert kit.count("[REDACTAR") >= 6
    assert "agradecer a quien lo pidió" not in kit
    kit = K.esqueleto(_data(pedido={"cta": "x"}), "resena-juego-pedido", "2026-10-28")
    assert "agradecer a quien lo pidió" in kit


def test_crear_no_sobrescribe():
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / "kits"
        driver = _driver(Path(tmp), ["resena-prueba"])
        assert K.crear(str(driver), carpeta=carpeta, hoy="2026-10-28") == 0
        kit = carpeta / "descripcion-resena-prueba.md"
        assert kit.exists()
        kit.write_text("editado a mano", encoding="utf-8")
        assert K.crear(str(driver), carpeta=carpeta, hoy="2026-10-28") == 2
        assert kit.read_text(encoding="utf-8") == "editado a mano"


def test_crear_dos_llamadas():
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / "kits"
        carpeta.mkdir()
        previo = carpeta / "descripcion-resena-uno.md"
        previo.write_text("ya existia", encoding="utf-8")
        driver = _driver(Path(tmp), ["resena-uno", "resena-dos"])
        assert K.crear(str(driver), carpeta=carpeta, hoy="2026-10-28") == 2
        assert previo.read_text(encoding="utf-8") == "ya existia"
        assert (carpeta / "descripcion-resena-dos.md").exists()


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
