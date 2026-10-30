"""Agrega a la descripcion de cada video largo un bloque "Sigue con" para encadenar la biblioteca del canal.

El bloque son dos lineas antes de los hashtags: el video recomendado (el de mas horas de su misma lista) y el enlace a la lista.
Seguro por defecto: sin --aplicar solo muestra el antes y el despues. Antes de escribir guarda un respaldo con la metadata real.
Diseno: docs/superpowers/specs/2026-10-30-encadenar-biblioteca-design.md
"""
from __future__ import annotations
import unicodedata

from youtube_aplicar import RESTO_RE

MARCA = "Sigue con:"
# palabra clave del titulo de la lista (sin tildes, en minuscula) -> texto de la linea de la lista
ETIQUETAS = (
    ("rese", "Todas las reseñas"),
    ("ranking", "Todos los rankings"),
    ("coleccion", "Todas las colecciones"),
    ("abriendo", "Todos los Abriendo el tarro"),
    ("special", "Todos los specials"),
    ("saga", "Todas las sagas"),
)


def _plano(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


def etiqueta_lista(titulo_lista: str) -> str | None:
    t = _plano(titulo_lista)
    for clave, texto in ETIQUETAS:
        if clave in t:
            return texto
    return None


def elegir_destinos(listas: list[dict], minutos: dict[str, int], titulos: dict[str, str]) -> dict[str, dict]:
    """Para cada video de una lista conocida con 2 o mas videos: el video de la misma lista con mas minutos que no sea el propio."""
    out: dict[str, dict] = {}
    for lista in listas:
        etiqueta = etiqueta_lista(lista["titulo"])
        videos = lista["videos"]
        if etiqueta is None or len(videos) < 2:
            continue
        for v in videos:
            mejor = max((x for x in videos if x != v), key=lambda x: minutos.get(x, 0))
            out[v] = {"destino_id": mejor, "destino_titulo": titulos.get(mejor, mejor),
                      "lista_id": lista["id"], "lista_etiqueta": etiqueta}
    return out


def bloque_enlaces(d: dict) -> str:
    return (f"{MARCA} {d['destino_titulo']} https://youtu.be/{d['destino_id']}\n"
            f"{d['lista_etiqueta']}: https://www.youtube.com/playlist?list={d['lista_id']}")


def insertar_bloque(desc: str, bloque: str) -> str:
    """Pone el bloque antes de la linea final de hashtags; si ya tiene "Sigue con:" no cambia nada."""
    if MARCA in desc:
        return desc
    lineas = desc.rstrip().split("\n")
    ultima = lineas[-1].strip()
    if "#" in ultima and not RESTO_RE.sub("", ultima):
        cuerpo = "\n".join(l.rstrip() for l in lineas[:-1]).rstrip()
        return (cuerpo + "\n\n" if cuerpo else "") + bloque + "\n\n" + ultima
    cuerpo = desc.rstrip()
    return (cuerpo + "\n\n" if cuerpo else "") + bloque
