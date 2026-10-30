"""Restaura el idioma de audio de los videos que las actualizaciones de octubre dejaron en en-US.

Las herramientas viejas reenviaban titulo, descripcion y etiquetas pero no defaultAudioLanguage, y YouTube lo puso en en-US.
Solo toca los videos que HOY estan en en-US: les devuelve el idioma que tenian segun el respaldo (o es-419 si no tenian ninguno,
porque todo el canal habla en espanol). Titulo, descripcion, etiquetas y categoria quedan igual.
Seguro por defecto: sin --aplicar solo muestra el antes y el despues. Con --aplicar guarda un respaldo y pide escribir SI.
Datos: data/youtube/idioma-audio-a-restaurar-*.json (llave "restaurar": {video: idioma original o null}).
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

import youtube_aplicar as A
from youtube_enlazar import _usar_credencial_del_repo_principal

REPO = Path(__file__).resolve().parent.parent
POR_DEFECTO = "es-419"   # el canal habla en espanol latino
EN_INGLES = "en-US"


def plan_restauracion(snips: dict[str, dict], restaurar: dict[str, str | None]) -> list[tuple[str, str, str]]:
    """(video, idioma actual, idioma nuevo) solo para los videos que hoy estan en en-US."""
    return [(vid, EN_INGLES, restaurar.get(vid) or POR_DEFECTO)
            for vid, sn in snips.items() if sn.get("defaultAudioLanguage") == EN_INGLES]


def cuerpo_restauracion(video_id: str, sn: dict, idioma: str) -> dict:
    """Mismo snippet que ya tiene el video, solo con el idioma de audio nuevo."""
    return A.cuerpo_snippet(video_id, sn, defaultAudioLanguage=idioma)


def cargar_objetivos(repo: Path) -> tuple[list[str], dict[str, str | None]]:
    """Ids de todos los videos del inventario y el idioma original guardado."""
    datos = repo / "data" / "youtube"
    ultimo = lambda patron: json.loads(sorted(datos.glob(patron))[-1].read_text(encoding="utf-8"))
    ids = [v["id"] for v in ultimo("inventario-*.json")["videos"]]
    return ids, ultimo("idioma-audio-a-restaurar-*.json")["restaurar"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true")
    a = ap.parse_args()
    ids, restaurar = cargar_objetivos(REPO)
    _usar_credencial_del_repo_principal()
    yt = A.servicio()
    snips = A.leer_snippets(yt, ids)
    plan = plan_restauracion(snips, restaurar)
    for vid, antes, despues in plan:
        print(f"{vid} | {snips[vid]['title'][:55]:55} | {antes} -> {despues}")
    print(f"\n{len(plan)} videos en {EN_INGLES} de {len(snips)} leidos.")
    if not a.aplicar:
        print("Modo prueba: no se escribio nada. Usa --aplicar para escribir.")
        return
    resp = REPO / "data" / "youtube" / f"respaldo-api-{time.strftime('%Y-%m-%d-%H%M%S')}.json"   # solo al aplicar; nunca pisa uno anterior
    resp.write_text(json.dumps({v: snips[v] for v, _a, _n in plan}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Respaldo con la metadata real de {len(plan)} videos -> {resp}")
    if input(f"Escribir {len(plan)} cambios en YouTube (cuesta {50 * len(plan)} de 10000 unidades de cuota)? escribe SI: ").strip() != "SI":
        sys.exit("Cancelado.")
    ok = 0
    for vid, _antes, despues in plan:
        try:
            yt.videos().update(part="snippet", body=cuerpo_restauracion(vid, snips[vid], despues)).execute()
            ok += 1
            print(f"OK {vid}")
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {vid}: {e}")
            if "quota" in str(e).lower():
                break
        time.sleep(0.5)
    print(f"Listo: {ok} de {len(plan)} aplicados.")


if __name__ == "__main__":
    main()
