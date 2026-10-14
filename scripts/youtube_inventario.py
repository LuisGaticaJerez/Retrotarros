"""Inventario de metadata del canal (solo lectura, sin credenciales): titulo, descripcion, hashtags y etiquetas de cada video.

Usa yt-dlp sobre las pestañas Videos, Shorts y En vivo de @Retrotarros. Guarda un JSON de respaldo y una tabla resumen.
Uso: python scripts/youtube_inventario.py [--canal @Retrotarros] [--salida data/youtube/inventario-AAAA-MM-DD.json]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HASHTAG_RE = re.compile(r"(?<![\w#])#[\wÁÉÍÓÚÜÑáéíóúüñ]+")
PESTANAS = ("videos", "shorts", "streams")


def run(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def listar(yt: str, canal: str) -> dict[str, str]:
    """id -> pestaña, sin repetir (un video puede aparecer en dos pestañas)."""
    ids: dict[str, str] = {}
    for tab in PESTANAS:
        r = run([yt, "--flat-playlist", "--print", "%(id)s", f"https://www.youtube.com/{canal}/{tab}"])
        for line in r.stdout.splitlines():
            vid = line.strip()
            if re.fullmatch(r"[\w-]{11}", vid):
                ids.setdefault(vid, tab)
        print(f"  {tab}: {sum(1 for v in ids.values() if v == tab)} videos", flush=True)
    return ids


def leer(yt: str, vid: str, tab: str) -> dict:
    r = run([yt, "--no-playlist", "--skip-download", "-j", "--encoding", "utf-8", f"https://www.youtube.com/watch?v={vid}"])
    if r.returncode != 0:
        return {"id": vid, "pestana": tab, "error": (r.stderr.strip().splitlines() or ["?"])[-1][:200]}
    d = json.loads(r.stdout)
    desc = d.get("description") or ""
    return {"id": vid, "pestana": tab, "titulo": d.get("title"), "duracion": d.get("duration"), "fecha": d.get("upload_date"),
            "vistas": d.get("view_count"), "descripcion": desc, "hashtags_descripcion": HASHTAG_RE.findall(desc),
            "etiquetas": d.get("tags") or [], "categoria": (d.get("categories") or [None])[0]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canal", default="@Retrotarros")
    ap.add_argument("--salida", default=str(REPO / "data" / "youtube" / f"inventario-{date.today().isoformat()}.json"))
    a = ap.parse_args()
    yt = shutil.which("yt-dlp")
    if not yt:
        sys.exit("No encuentro yt-dlp en el PATH.")
    print("Listando el canal...", flush=True)
    ids = listar(yt, a.canal)
    print(f"{len(ids)} videos en total. Leyendo cada uno...", flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        videos = list(ex.map(lambda kv: leer(yt, kv[0], kv[1]), ids.items()))
    videos.sort(key=lambda v: (v.get("fecha") or "", v["id"]), reverse=True)
    out = Path(a.salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"canal": a.canal, "fecha": date.today().isoformat(), "videos": videos}, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = [v for v in videos if "error" not in v]
    print(f"OK -> {out} | {len(ok)} leidos, {len(videos) - len(ok)} con error")
    for v in videos:
        if "error" in v:
            print("  ERROR", v["id"], v["error"])


if __name__ == "__main__":
    main()
