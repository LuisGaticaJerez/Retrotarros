"""Agrega a la descripcion de cada video largo un bloque "Sigue con" para encadenar la biblioteca del canal.

El bloque son dos lineas antes de los hashtags: el video recomendado (el de mas horas de su misma lista) y el enlace a la lista.
Seguro por defecto: sin --aplicar solo muestra el antes y el despues. Antes de escribir guarda un respaldo con la metadata real.
Diseno: docs/superpowers/specs/2026-10-30-encadenar-biblioteca-design.md
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import youtube_aplicar as A
from youtube_aplicar import RESTO_RE

REPO = Path(__file__).resolve().parent.parent

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
    titulo = re.sub(r"\s*\|\s*retro[^|]*$", "", d["destino_titulo"], flags=re.I)   # quita el sufijo de formato ("| Retroreseñas")
    return (f"{MARCA} {titulo} https://youtu.be/{d['destino_id']}\n"
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


def cargar_entradas(repo: Path) -> tuple[list[dict], dict[str, int], dict[str, str]]:
    """Listas, minutos vistos por video y titulos, desde los archivos mas recientes de data/youtube."""
    datos = repo / "data" / "youtube"
    ultimo = lambda patron: json.loads(sorted(datos.glob(patron))[-1].read_text(encoding="utf-8"))
    listas = ultimo("listas-*.json")
    minutos = {vid: x["min_org"] for vid, x in ultimo("organicas-y-subs-por-video-*.json").items()}   # sin anuncios: horas validas
    titulos = {v["id"]: v["titulo"] for v in ultimo("inventario-*.json")["videos"]}
    return listas, minutos, titulos


def construir_propuesta(snips: dict[str, dict], destinos: dict[str, dict]) -> list[tuple[str, str, str]]:
    """(video, descripcion actual, descripcion nueva) solo para los videos con destino y con cambio."""
    out = []
    for vid, sn in snips.items():
        if vid not in destinos:
            continue
        antes = sn.get("description", "")
        despues = insertar_bloque(antes, bloque_enlaces(destinos[vid]))
        if despues != antes:
            out.append((vid, antes, despues))
    return out


def cuerpo_actualizacion(video_id: str, sn: dict, descripcion: str) -> dict:
    """videos().update reemplaza el snippet completo: se reenvian titulo, categoria, etiquetas e idioma tal como vienen."""
    return A.cuerpo_snippet(video_id, sn, description=descripcion)


def _usar_credencial_del_repo_principal() -> None:
    """En un worktree la credencial vive en el .cache del repo principal (fuera de git)."""
    for base in (REPO, *REPO.parents):
        if (base / ".cache" / "youtube" / "client_secret.json").exists():
            A.CACHE = base / ".cache" / "youtube"
            return


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", default="", help="ids separados por coma; sin esto, todos los videos con destino")
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    listas, minutos, titulos = cargar_entradas(REPO)
    destinos = elegir_destinos(listas, minutos, titulos)
    pedidos = [x for x in a.solo.split(",") if x] or list(destinos)
    ids = [i for i in pedidos if i in destinos]
    if len(ids) != len(pedidos):
        print("AVISO: sin destino (no estan en una lista conocida):", [i for i in pedidos if i not in destinos])
    _usar_credencial_del_repo_principal()
    yt = A.servicio()
    snips = A.leer_snippets(yt, ids)
    prop = construir_propuesta(snips, destinos)
    for vid, _antes, despues in prop:
        d = destinos[vid]
        print(f"\n== {vid} | {snips[vid]['title'][:60]}")
        print(f"   SUGIERE: {d['destino_titulo'][:60]} ({d['destino_id']})")
        print("   DESCRIPCION NUEVA:\n" + "\n".join("     " + l for l in despues.split("\n")))
    print(f"\n{len(prop)} videos cambiarian de {len(snips)}.")
    if not a.aplicar:
        print("Modo prueba: no se escribio nada. Usa --aplicar para escribir.")
        return
    resp = REPO / "data" / "youtube" / f"respaldo-api-{time.strftime('%Y-%m-%d-%H%M%S')}.json"   # solo al aplicar; nunca pisa un respaldo anterior
    resp.write_text(json.dumps(snips, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Respaldo con la metadata real de {len(snips)} videos -> {resp}")
    if input(f"Escribir {len(prop)} cambios en YouTube (cuesta {50 * len(prop)} de 10000 unidades de cuota)? escribe SI: ").strip() != "SI":
        sys.exit("Cancelado.")
    ok = 0
    for vid, _antes, despues in prop:
        try:
            yt.videos().update(part="snippet", body=cuerpo_actualizacion(vid, snips[vid], despues)).execute()
            ok += 1
            print(f"OK {vid}")
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {vid}: {e}")
            if "quota" in str(e).lower():
                break
        time.sleep(0.5)
    print(f"Listo: {ok} de {len(prop)} aplicados.")


if __name__ == "__main__":
    main()
