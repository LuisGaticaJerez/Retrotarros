"""Estado actual del canal con la API (SOLO LECTURA): publicados, programados con su fecha, no listados y privados.

Guarda data/youtube/estado-canal.json (el ultimo) y una copia por dia en data/youtube/historial/estado-AAAA-MM-DD.json, y muestra los
cambios contra la corrida anterior (videos nuevos publicados, nuevos programados, fechas que cambiaron).
Usa el token de .cache/youtube/token.json (el de youtube_aplicar.py). Si caduco, vuelve a abrir el navegador para autorizar.
Al terminar hace un commit local (sin push) solo del estado y su historial, para que no quede huerfano. --no-commit lo omite.
Uso: python scripts/youtube_estado.py [--no-commit]
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import youtube_aplicar as A  # noqa: E402

REPO = A.REPO
DEST = REPO / "data" / "youtube"
CANAL_UPLOADS = "UUMTWPCGLwJV1L262vCdCz9g"   # playlist de subidas del canal Retrotarros (UC... -> UU...)


def leer_todo(yt) -> list[dict]:
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=CANAL_UPLOADS, maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok:
            break
    out = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,status,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute()
        for it in r["items"]:
            sn, st, ss = it["snippet"], it["status"], it.get("statistics", {})
            pub_at = st.get("publishAt")
            estado = "publicado" if st["privacyStatus"] == "public" else ("programado" if pub_at else st["privacyStatus"])
            out.append({"id": it["id"], "titulo": sn["title"], "estado": estado, "privacidad": st["privacyStatus"], "publicacion_programada": pub_at,
                        "subido": sn["publishedAt"], "vistas": int(ss.get("viewCount", 0)), "duracion": it["contentDetails"]["duration"]})
    out.sort(key=lambda v: (v["publicacion_programada"] or v["subido"]), reverse=True)
    return out


def main() -> None:
    yt = A.servicio()
    videos = leer_todo(yt)
    previo_p = DEST / "estado-canal.json"
    previo = {v["id"]: v for v in json.loads(previo_p.read_text(encoding="utf-8"))["videos"]} if previo_p.exists() else {}
    hoy = date.today().isoformat()
    datos = {"fecha": hoy, "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"), "videos": videos}
    previo_p.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    (DEST / "historial").mkdir(exist_ok=True)
    (DEST / "historial" / f"estado-{hoy}.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    por = {}
    for v in videos:
        por.setdefault(v["estado"], []).append(v)
    print("RESUMEN:", {k: len(x) for k, x in por.items()}, "| total", len(videos))
    print("\nPROGRAMADOS (fecha de publicacion):")
    for v in sorted(por.get("programado", []), key=lambda v: v["publicacion_programada"]):
        print("  ", v["publicacion_programada"][:16].replace("T", " "), "UTC |", v["titulo"][:70])
    if previo:
        nuevos = [v for v in videos if v["id"] not in previo]
        publicados = [v for v in videos if v["estado"] == "publicado" and v["id"] in previo and previo[v["id"]]["estado"] != "publicado"]
        cambios = [v for v in videos if v["id"] in previo and v["estado"] == "programado" and previo[v["id"]]["publicacion_programada"] != v["publicacion_programada"]]
        print("\nCAMBIOS desde", json.loads(previo_p.read_text(encoding='utf-8'))["fecha"] if False else "la corrida anterior:")
        print("  videos nuevos:", [v["titulo"][:45] for v in nuevos])
        print("  pasaron a publicado:", [v["titulo"][:45] for v in publicados])
        print("  fecha programada cambio:", [v["titulo"][:45] for v in cambios])
    else:
        print("\n(primera corrida: sin base para comparar)")
    if "--no-commit" not in sys.argv:
        commitear(hoy)


def commitear(hoy: str) -> None:
    """Commit local (sin push) SOLO de data/youtube/estado-canal.json y su historial, para que el estado no quede huerfano
    y las otras sesiones lo vean. No toca nada mas del arbol de trabajo ni de otros archivos en staging."""
    import subprocess
    rutas = ["data/youtube/estado-canal.json", "data/youtube/historial"]
    def git(*a):
        return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if not git("status", "--porcelain", "--", *rutas).stdout.strip():
        print("\nCommit: sin cambios en el estado, nada que commitear.")
        return
    a = git("add", "--", *rutas)
    c = git("commit", "-m", f"chore(canal): estado del canal {hoy}", "--", *rutas) if a.returncode == 0 else a
    if c.returncode == 0:
        print("\nCommit local hecho:", git("log", "-1", "--format=%h %s").stdout.strip(), "(sin push)")
    else:
        print("\nNo pude commitear el estado:", (c.stderr or c.stdout).strip())


if __name__ == "__main__":
    main()
