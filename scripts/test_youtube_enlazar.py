"""Pruebas de scripts/youtube_enlazar.py (bloque "Sigue con" en las descripciones de YouTube).

Sin pytest: se corre con `python scripts/test_youtube_enlazar.py`. Toda funcion
`test_*` se ejecuta; sale con codigo 1 si alguna falla.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import youtube_enlazar as E  # noqa: E402

LISTA = {"id": "PL1", "titulo": "Retroreseñas", "videos": ["a", "b", "c"]}
TITULOS = {"a": "Juego A", "b": "Juego B", "c": "Juego C"}
HASHTAGS = "#RetroReseñas #Retrotarros"


# ---------------------------------------------------------------- Task 1

def test_etiqueta_lista():
    assert E.etiqueta_lista("Retroreseñas") == "Todas las reseñas"
    assert E.etiqueta_lista("Rankings") == "Todos los rankings"
    assert E.etiqueta_lista("Colecciones RetroTarros") == "Todas las colecciones"
    assert E.etiqueta_lista("G- OLD") is None


def test_elegir_destinos_mejor_distinto_del_propio():
    d = E.elegir_destinos([LISTA], {"a": 10, "b": 50, "c": 30}, TITULOS)
    assert d["b"]["destino_id"] == "c"
    assert d["a"]["destino_id"] == "b" and d["c"]["destino_id"] == "b"
    assert d["a"] == {"destino_id": "b", "destino_titulo": "Juego B", "lista_id": "PL1", "lista_etiqueta": "Todas las reseñas"}


def test_elegir_destinos_lista_de_uno_se_omite():
    sagas = {"id": "PL2", "titulo": "Sagas de videojuegos", "videos": ["z"]}
    assert E.elegir_destinos([sagas], {"z": 99}, {"z": "Zelda"}) == {}


def test_elegir_destinos_lista_desconocida_se_omite():
    vieja = {"id": "PL3", "titulo": "G- OLD", "videos": ["a", "b"]}
    assert E.elegir_destinos([vieja], {"a": 1, "b": 2}, TITULOS) == {}


def test_elegir_destinos_video_sin_horas_cuenta_cero():
    d = E.elegir_destinos([LISTA], {"a": 5}, TITULOS)   # b y c no estan en minutos
    assert d["b"]["destino_id"] == "a" and d["c"]["destino_id"] == "a"
    assert d["a"]["destino_id"] == "b"   # empate en 0 entre b y c: gana el primero de la lista


def test_bloque_enlaces():
    d = {"destino_id": "b", "destino_titulo": "Juego B", "lista_id": "PL1", "lista_etiqueta": "Todas las reseñas"}
    assert E.bloque_enlaces(d) == ("Sigue con: Juego B https://youtu.be/b\n"
                                   "Todas las reseñas: https://www.youtube.com/playlist?list=PL1")


def test_bloque_enlaces_quita_el_sufijo_de_formato_del_titulo():
    base = {"destino_id": "b", "lista_id": "PL1", "lista_etiqueta": "Todas las reseñas"}
    for titulo in ("Juego B | Retroreseñas", "Juego B | RetroReseña", "Juego B | Retrotarros"):
        assert E.bloque_enlaces({**base, "destino_titulo": titulo}).startswith("Sigue con: Juego B https://youtu.be/b"), titulo
    # un titulo con barra que no es sufijo de formato se respeta
    assert E.bloque_enlaces({**base, "destino_titulo": "A | B"}).startswith("Sigue con: A | B https://")


BLOQUE = "Sigue con: Juego B https://youtu.be/b\nTodas las reseñas: https://www.youtube.com/playlist?list=PL1"


def test_insertar_bloque_antes_de_hashtags():
    desc = f"Texto de la descripcion.\n\n{HASHTAGS}"
    assert E.insertar_bloque(desc, BLOQUE) == f"Texto de la descripcion.\n\n{BLOQUE}\n\n{HASHTAGS}"


def test_insertar_bloque_idempotente():
    una = E.insertar_bloque(f"Texto.\n\n{HASHTAGS}", BLOQUE)
    assert E.insertar_bloque(una, BLOQUE) == una


def test_insertar_bloque_sin_hashtags():
    assert E.insertar_bloque("Solo texto.", BLOQUE) == f"Solo texto.\n\n{BLOQUE}"


def test_insertar_bloque_descripcion_vacia():
    assert E.insertar_bloque("", BLOQUE) == BLOQUE


# ---------------------------------------------------------------- Task 2

DESTINOS = {"a": {"destino_id": "b", "destino_titulo": "Juego B", "lista_id": "PL1", "lista_etiqueta": "Todas las reseñas"}}


def test_cargar_entradas_lee_los_tres_archivos():
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / "data" / "youtube"
        carpeta.mkdir(parents=True)
        (carpeta / "listas-2026-10-30.json").write_text(json.dumps([LISTA]), encoding="utf-8")
        (carpeta / "horas-por-video-2026-10-30.json").write_text(
            json.dumps([{"video": "a", "estimatedMinutesWatched": 10}]), encoding="utf-8")
        (carpeta / "inventario-2026-10-29.json").write_text(
            json.dumps({"videos": [{"id": "a", "titulo": "Juego A"}]}), encoding="utf-8")
        listas, minutos, titulos = E.cargar_entradas(Path(tmp))
    assert listas == [LISTA] and minutos == {"a": 10} and titulos == {"a": "Juego A"}


def test_construir_propuesta_cambia_solo_la_descripcion():
    snips = {"a": {"description": f"Texto.\n\n{HASHTAGS}"}}
    prop = E.construir_propuesta(snips, DESTINOS)
    assert len(prop) == 1
    vid, antes, despues = prop[0]
    assert vid == "a" and antes == f"Texto.\n\n{HASHTAGS}"
    assert despues == f"Texto.\n\n{BLOQUE}\n\n{HASHTAGS}"


def test_construir_propuesta_omite_videos_que_ya_tienen_el_bloque():
    snips = {"a": {"description": f"Texto.\n\n{BLOQUE}\n\n{HASHTAGS}"}}
    assert E.construir_propuesta(snips, DESTINOS) == []


def test_construir_propuesta_omite_videos_sin_destino():
    assert E.construir_propuesta({"zzz": {"description": "Texto."}}, DESTINOS) == []


def test_cuerpo_actualizacion_conserva_tags_e_idioma():
    sn = {"title": "Titulo", "description": "vieja", "categoryId": "20", "tags": ["x", "y"], "defaultLanguage": "es"}
    cuerpo = E.cuerpo_actualizacion("a", sn, "nueva")
    assert cuerpo == {"id": "a", "snippet": {"title": "Titulo", "description": "nueva", "categoryId": "20",
                                            "tags": ["x", "y"], "defaultLanguage": "es"}}


def test_cuerpo_actualizacion_sin_tags_ni_idioma():
    cuerpo = E.cuerpo_actualizacion("a", {"title": "T", "categoryId": "20"}, "nueva")
    assert cuerpo == {"id": "a", "snippet": {"title": "T", "description": "nueva", "categoryId": "20"}}


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
