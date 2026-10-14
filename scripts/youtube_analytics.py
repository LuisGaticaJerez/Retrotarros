"""Lee YouTube Analytics del canal (SOLO LECTURA): impresiones, CTR, retencion, fuentes de trafico y suscriptores ganados por video.

Necesita el permiso extra yt-analytics.readonly en la pantalla de consentimiento y volver a autorizar una vez (abre el navegador).
Guarda el token en .cache/youtube/token-analytics.json (fuera de git, permisos de solo el dueño). No cambia nada en el canal.
Uso: python scripts/youtube_analytics.py [--dias 90]
Salida: data/youtube/analytics-AAAA-MM-DD.json
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CACHE = REPO / ".cache" / "youtube"
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"]


def servicios():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    token, secret = CACHE / "token-analytics.json", CACHE / "client_secret.json"
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not secret.exists():
                sys.exit(f"Falta {secret}.")
            creds = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(port=0)
        CACHE.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(token), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return build("youtubeAnalytics", "v2", credentials=creds), build("youtube", "v3", credentials=creds)


def consulta(an, inicio: str, fin: str, metricas: str, dims: str | None = None, filtros: str | None = None, orden: str | None = None, maxr: int | None = None):
    p = {"ids": "channel==MINE", "startDate": inicio, "endDate": fin, "metrics": metricas}
    for k, v in (("dimensions", dims), ("filters", filtros), ("sort", orden), ("maxResults", maxr)):
        if v:
            p[k] = v
    r = an.reports().query(**p).execute()
    cols = [c["name"] for c in r.get("columnHeaders", [])]
    return [dict(zip(cols, row)) for row in r.get("rows", [])]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=90)
    a = ap.parse_args()
    an, _ = servicios()
    fin = date.today() - timedelta(days=2)   # Analytics tiene 1-2 dias de retraso
    ini = fin - timedelta(days=a.dias)
    m_base = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost,likes,comments,shares"
    out = {"desde": str(ini), "hasta": str(fin)}
    out["canal_total"] = consulta(an, str(ini), str(fin), m_base)
    out["por_video"] = consulta(an, str(ini), str(fin), m_base, dims="video", orden="-views", maxr=200)
    out["fuentes_de_trafico"] = consulta(an, str(ini), str(fin), "views,estimatedMinutesWatched", dims="insightTrafficSourceType", orden="-views")
    out["por_tipo_de_contenido"] = consulta(an, str(ini), str(fin), "views,estimatedMinutesWatched,subscribersGained", dims="creatorContentType")
    try:   # impresiones y CTR de miniatura: solo existen para videos largos y no siempre estan disponibles
        out["impresiones_por_video"] = consulta(an, str(ini), str(fin), "videoThumbnailImpressions,videoThumbnailImpressionsClickRate", dims="video", orden="-videoThumbnailImpressions", maxr=200)
    except Exception as e:  # noqa: BLE001
        out["impresiones_por_video"] = {"error": str(e)[:300]}
    try:
        out["origen_en_el_canal"] = consulta(an, str(ini), str(fin), "views", dims="insightPlaybackLocationType", orden="-views")
    except Exception as e:  # noqa: BLE001
        out["origen_en_el_canal"] = {"error": str(e)[:300]}
    dest = REPO / "data" / "youtube" / f"analytics-{date.today().isoformat()}.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK ->", dest, "| videos con datos:", len(out["por_video"]), "| periodo", ini, "a", fin)


if __name__ == "__main__":
    main()
