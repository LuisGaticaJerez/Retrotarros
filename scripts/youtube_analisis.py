"""Analisis de rendimiento del canal con datos reales (YouTube Data API, solo lectura): vistas, likes, comentarios, duracion y edad.

Cruza con el tipo de video de la propuesta de hashtags (resena, mundial, precios, ...). Escribe data/youtube/analisis-AAAA-MM-DD.json
y un resumen en .md. Solo lee: no cambia nada en el canal. Uso: python scripts/youtube_analisis.py
"""
import json
import re
import statistics as st
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import youtube_aplicar as A  # noqa: E402

REPO = A.REPO
ISO_DUR = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def dur(s: str) -> int:
    h, m, sec = ISO_DUR.match(s).groups()
    return int(h or 0) * 3600 + int(m or 0) * 60 + int(sec or 0)


def cargar() -> list[dict]:
    props = {p["id"]: p for p in json.loads(sorted((REPO / "data" / "youtube").glob("propuesta-*.json"))[-1].read_text(encoding="utf-8"))["videos"]}
    yt = A.servicio()
    ids = list(props)
    out = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute()
        for it in r["items"]:
            sn, stt = it["snippet"], it["statistics"]
            pub = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
            dias = max(1, (datetime.now(timezone.utc) - pub).days)
            v = int(stt.get("viewCount", 0))
            out.append({"id": it["id"], "titulo": sn["title"], "tipo": props[it["id"]]["tipo"], "publicado": sn["publishedAt"][:10], "dias": dias,
                        "segundos": dur(it["contentDetails"]["duration"]), "vistas": v, "likes": int(stt.get("likeCount", 0)),
                        "comentarios": int(stt.get("commentCount", 0)), "vistas_por_dia": round(v / dias, 2)})
    return out


def main() -> None:
    d = cargar()
    hoy = date.today().isoformat()
    (REPO / "data" / "youtube" / f"analisis-{hoy}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(d)} videos | vistas totales {sum(v['vistas'] for v in d)} | likes {sum(v['likes'] for v in d)} | comentarios {sum(v['comentarios'] for v in d)}")


if __name__ == "__main__":
    main()
