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
    assert K.hashtag_consola(_data(consola="Sega Genesis")) == "#MegaDrive"  # alias del canal
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


# ---------------------------------------------------------------- Task 3

def _esq() -> str:
    return K.esqueleto(_data(), "resena-juego", "2026-10-28")


def _completo(kit: str | None = None) -> str:
    """El esqueleto con cada marcador reemplazado por texto (como lo dejaria quien redacta)."""
    import re
    return re.sub(r"\[REDACTAR[^\]]*\]", "uno, dos, tres, cuatro", kit or _esq())


def _tags_ok() -> str:
    return K.tags(_data()).replace(K.MARCADOR_TAGS, "uno, dos, tres, cuatro")


def _hay(mensajes: list[str], fragmento: str) -> bool:
    return any(fragmento.lower() in m.lower() for m in mensajes)


def test_esqueleto_incluye_bloque_sigue_con():
    kit = _esq()
    sigue = "Sigue con: [REDACTAR: video sugerido al publicar]"
    lista = "Todas las reseñas: https://www.youtube.com/playlist?list=PLOBtQJdDMEDA"
    assert sigue in kit and lista in kit
    assert kit.index(CTA) < kit.index(sigue) < kit.index(lista) < kit.index("#RetroReseñas")


def test_revisar_marca_pendiente_el_sigue_con():
    kit = _completo().replace("Sigue con: uno, dos, tres, cuatro", "Sigue con: [REDACTAR: video sugerido al publicar]")
    assert _hay(K.revisar_kit(kit), "[REDACTAR")


def test_revisar_esqueleto_falla():
    assert _hay(K.revisar_kit(_esq()), "[REDACTAR")


def test_revisar_kit_completo():
    assert K.revisar_kit(_completo()) == [], K.revisar_kit(_completo())


def test_revisar_tags_largos():
    kit = _completo().replace(_tags_ok(), ", ".join(["a" * 30] * 18))
    errores = K.revisar_kit(kit)
    assert _hay(errores, "500"), errores


def test_revisar_cantidad_tags():
    base = _completo()
    pocos = base.replace(_tags_ok(), ", ".join(f"t{i}" for i in range(14)))
    muchos = base.replace(_tags_ok(), ", ".join(f"t{i}" for i in range(26)))
    assert _hay(K.revisar_kit(pocos), "tags"), K.revisar_kit(pocos)
    assert _hay(K.revisar_kit(muchos), "tags"), K.revisar_kit(muchos)


def test_revisar_hashtags():
    base = _completo()
    linea = K.hashtags(_data())
    ok4 = base.replace(linea, "#RetroReseñas #JuegoDePrueba #Retrogaming #Retrotarros")
    assert K.revisar_kit(ok4) == [], K.revisar_kit(ok4)
    seis = base.replace(linea, "#RetroReseñas #A #B #C #D #Retrotarros")
    assert _hay(K.revisar_kit(seis), "hashtags")
    primero = base.replace(linea, "#Retro #A #B #Retrogaming #Retrotarros")
    assert _hay(K.revisar_kit(primero), "#RetroReseñas")
    ultimo = base.replace(linea, "#RetroReseñas #A #B #Retrogaming #Otro")
    assert _hay(K.revisar_kit(ultimo), "#Retrotarros")


def test_revisar_falta_cta_o_comentario():
    base = _completo()
    sin_cta = base.replace(CTA, "")
    assert _hay(K.revisar_kit(sin_cta), "suscri"), K.revisar_kit(sin_cta)
    ini = base.index("## Comentario fijado")
    fin = base.index("---\n\n**Slug")
    sin_comentario = base[:ini] + base[fin:]
    assert _hay(K.revisar_kit(sin_comentario), "comentario fijado")


def test_revisar_voseo():
    base = _completo()
    assert _hay(K.revisar_kit(base.replace("Cuéntanos", "Decime, tenés")), "voseo")
    assert _hay(K.revisar_kit(base.replace("Cuéntanos", "Contanos vos")), "voseo")
    assert not _hay(K.revisar_kit(base.replace("Cuéntanos", "Con la voz de")), "voseo")


def test_revisar_crlf_y_tags_en_varias_lineas():
    kit = _completo().replace(_tags_ok(), _tags_ok().replace(", ", ",\n"))
    assert K.revisar_kit(kit.replace("\n", "\r\n")) == []


def test_cli_revisar():
    with tempfile.TemporaryDirectory() as tmp:
        malo = Path(tmp) / "malo.md"
        malo.write_text(_esq(), encoding="utf-8")
        bueno = Path(tmp) / "bueno.md"
        bueno.write_text(_completo(), encoding="utf-8")
        assert K.main(["--revisar", str(malo)]) == 1
        assert K.main(["--revisar", str(bueno)]) == 0
        assert K.main(["--revisar", str(Path(tmp) / "no-existe.md")]) == 2


# ---------------------------------------------------------------- Revision final

def test_hashtag_consola_con_parentesis_y_alias():
    casos = {
        "Super Nintendo (SNES)": "#SNES",
        "PC (Windows)": "#PC",
        "MS-DOS (PC) · Super Nintendo (SNES)": "#PC",
        "PlayStation 2": "#PS2",
        "Sega Genesis / Mega Drive": "#MegaDrive",
        "Arcade (Neo Geo MVS)": "#NeoGeo",
        "Nintendo Entertainment System": "#NES",
    }
    for consola, esperado in casos.items():
        assert K.hashtag_consola(_data(consola=consola)) == esperado, (consola, K.hashtag_consola(_data(consola=consola)))


def test_anio_compuesto_usa_el_primer_anio():
    kit = K.esqueleto(_data(anio="1987 (arcade) / 1988 (NES)"), "resena-juego", "2026-10-28")
    assert "Volvemos a 1987 para revisar Juego de Prueba" in kit
    assert "Juego de Prueba (1987):" in kit
    assert "juego de prueba 1987" in K.tags(_data(anio="1987 (arcade) / 1988 (NES)"))
    assert "(arcade)" not in K.tags(_data(anio="1987 (arcade) / 1988 (NES)"))


def test_tags_plataformas_y_developer_limpios():
    t = K.tags(_data(consola="Super Nintendo (SNES) · Sega Genesis / Mega Drive", developer="Rare, Ltd."))
    lista = [x.strip() for x in t.split(",")]
    for x in ("super nintendo", "sega genesis", "mega drive", "rare ltd."):
        assert x in t, (x, t)
    assert not any("(" in x or ")" in x or "/" in x for x in lista), lista
    assert "ltd." not in lista


def test_tags_genero_compuesto_se_separa():
    lista = [x.strip() for x in K.tags(_data(genero="Accion / RPG (hibrido)")).split(",")]
    assert "accion" in lista and "rpg" in lista, lista
    assert not any("/" in x or "(" in x for x in lista), lista


def test_esqueleto_pide_confirmar_datos_mecanicos():
    kit = K.esqueleto(_data(), "resena-juego", "2026-10-28")
    aviso = "[REDACTAR: confirmar con tildes el nombre del juego, el año y los hashtags (#Juego #Consola)]"
    assert aviso in kit
    assert kit.index(aviso) < kit.index(K.hashtags(_data()))


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
