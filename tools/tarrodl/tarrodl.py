"""TarroDL - descargador personal de gameplays (yt-dlp + ffmpeg) con front local estilo TarroBot.

Servidor HTTP en 127.0.0.1 que sirve ui/index.html y abre una ventana de Edge en modo app.
Solo libreria estandar: yt-dlp y ffmpeg se llaman como programas externos (asi se
actualizan sin recompilar el exe).

Uso en desarrollo:  python tarrodl.py [--no-browser] [--port 8765]
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import math
import os
import random
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import unicodedata
import urllib.request
import uuid
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import RotatingFileHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

APP = "TarroDL"
VERSION = "1.0"
DEFAULT_OUT = r"D:\Recursos Retrotarros\videos"
CONFIG_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "tarrodl.log"
QUIET_ROUTES = {"ping"}
log = logging.getLogger("tarrodl")
RES = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
NOWIN = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

TOKEN = secrets.token_urlsafe(16)
PORT = 0
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
URL_RE = re.compile(r"^https?://\S+$", re.I)
CONTAINERS = {"mp4", "mkv", "mp3", "m4a"}
VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}
# lineas de `ffmpeg -progress pipe:1`: no sirven en el log ni en el detalle del job
FF_PROGRESS_RE = re.compile(r"^(out_time|out_time_us|out_time_ms|bitrate|total_size|frame|fps|stream_\d|dup_frames|drop_frames|speed|progress)=")
ANTI_SLOW_RATE = "8M"   # velocidad minima aceptable antes de pedir un enlace nuevo a YouTube
CLIP_MIN_SEC, CLIP_MAX_SEC = 60, 180
PIECE_MIN_SEC, PIECE_MAX_SEC = 10, 60
MOSAIC_MIN_SEC, MOSAIC_MAX_SEC = 60, 900          # mosaico multi-video: largo total del clip
MOSAIC_MIN_VIDEOS, MOSAIC_MAX_VIDEOS = 2, 12
MOSAIC_HEIGHTS = (720, 1080)
MOSAIC_SHARES = ("parejo", "proporcional")
STATE = {"last_ping": time.time(), "bye_at": None, "seen": False}

JOBS: dict[str, dict] = {}
PROCS: dict[str, subprocess.Popen] = {}   # proceso externo vivo de cada job (para poder cancelarlo)
CLEANUPS: dict[str, object] = {}          # funcion que borra lo que un job dejo a medias si lo cancelan


class Cancelled(Exception):
    """El usuario cancelo el proceso (boton CANCELAR)."""


class ApiError(Exception):
    pass


# ---------- utilidades ----------

def setup_logging() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(message)s"))
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    threading.excepthook = lambda a: log.error("hilo %s fallo", a.thread, exc_info=(a.exc_type, a.exc_value, a.exc_traceback))


def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def out_base() -> Path:
    return Path(load_config().get("output_base") or DEFAULT_OUT)


def clips_base() -> Path:
    return Path(load_config().get("clips_base") or (out_base() / "clips"))


def folders_state() -> dict:
    """Carpetas vigentes y si Luis ya las eligio (guardadas en config.json) o son las de por defecto."""
    cfg = load_config()
    return {"output_base": str(out_base()), "output_saved": bool(cfg.get("output_base")),
            "clips_base": str(clips_base()), "clips_saved": bool(cfg.get("clips_base"))}


def find_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA", "")
    pkgs = Path(local) / "Microsoft" / "WinGet" / "Packages"
    cands = [Path(local) / "Microsoft" / "WinGet" / "Links" / f"{name}.exe"]
    for pat in (f"*/{name}.exe", f"*/*/bin/{name}.exe", f"*/*/{name}.exe"):
        cands += [Path(p) for p in glob.glob(str(pkgs / pat))]
    for c in cands:
        if c.exists():
            return str(c)
    return None


def run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, creationflags=NOWIN)


def slugify(text: str, limit: int = 40) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:limit].rstrip("-") or "gameplay"


def clean_url(raw: object) -> str:
    url = str(raw or "").strip()
    if not URL_RE.match(url) or len(url) > 500:
        raise ApiError("El link no parece una URL valida (debe empezar con http:// o https://).")
    return url


def clean_slug(raw: object) -> str:
    slug = str(raw or "").strip()
    if not SLUG_RE.match(slug):
        raise ApiError("El nombre debe ir en kebab-case: minusculas, numeros y guiones (ej. starfox-64).")
    return slug


def need_tool(name: str, label: str | None = None) -> str:
    path = find_tool(name)
    if not path:
        raise ApiError(f"{label or name} no esta instalado.")
    return path


# ---------- jobs ----------

class Pool:
    """Cupos de ejecucion: cuantos trabajos de un tipo corren a la vez; el resto espera en cola (FIFO)."""

    def __init__(self, name: str, limit: int):
        self.name, self.limit, self.active, self.waiting = name, limit, 0, []
        self.cond = threading.Condition()


MAX_DOWNLOADS_DEFAULT, MAX_DOWNLOADS_RANGE = 3, (1, 6)
POOLS = {"dl": Pool("dl", MAX_DOWNLOADS_DEFAULT),   # descargas: hasta N a la vez (configurable)
         "clips": Pool("clips", 1)}                 # clips/mosaicos: de a uno (el mosaico recodifica y usa mucho CPU)


def max_downloads() -> int:
    try:
        n = int(load_config().get("max_downloads", MAX_DOWNLOADS_DEFAULT))
    except (TypeError, ValueError):
        n = MAX_DOWNLOADS_DEFAULT
    return max(MAX_DOWNLOADS_RANGE[0], min(MAX_DOWNLOADS_RANGE[1], n))


def apply_settings() -> None:
    pool = POOLS["dl"]
    with pool.cond:
        pool.limit = max_downloads()
        pool.cond.notify_all()


def new_job(kind: str) -> dict:
    job = {"id": uuid.uuid4().hex[:8], "kind": kind, "state": "running", "percent": 0, "queue_pos": 0, "pool": None,
           "text": "Iniciando...", "meta": "", "log": deque(maxlen=60), "result": {}, "cancel": False, "indeterminate": False}
    JOBS[job["id"]] = job
    return job


def running_jobs() -> bool:
    return any(j["state"] in ("running", "queued") for j in list(JOBS.values()))


def pool_acquire(pool: Pool, job: dict) -> None:
    """Espera un cupo. Mientras espera el job queda 'queued' con su puesto; si lo cancelan, sale con Cancelled."""
    with pool.cond:
        pool.waiting.append(job["id"])
        try:
            while True:
                if job.get("cancel"):
                    raise Cancelled()
                pos = pool.waiting.index(job["id"])
                free = pool.limit - pool.active
                if pos < free:
                    break
                job["queue_pos"] = pos - free + 1
                job["text"] = f"En cola, puesto {job['queue_pos']}"
                pool.cond.wait(0.5)
        finally:
            if job["id"] in pool.waiting:
                pool.waiting.remove(job["id"])
        pool.active += 1
        job["state"], job["queue_pos"], job["text"] = "running", 0, "Iniciando..."


def pool_release(pool: Pool) -> None:
    with pool.cond:
        pool.active -= 1
        pool.cond.notify_all()


def spawn(job: dict, fn, pool: str | None = None) -> dict:
    if pool:
        job["pool"], job["state"], job["text"] = pool, "queued", "En cola..."

    def wrapper():
        t0, acquired = time.time(), False
        try:
            if pool:
                pool_acquire(POOLS[pool], job)
                acquired, t0 = True, time.time()
            log.info("job %s (%s) inicia", job["id"], job["kind"])
            fn(job)
            if job["state"] == "running":
                job["state"] = "done"
                job["percent"] = 100
            log.info("job %s (%s) OK en %.1fs: %s", job["id"], job["kind"], time.time() - t0, job["text"])
        except Cancelled:
            removed = run_cleanup(job)
            job["state"] = "cancelled"
            job["text"] = "Cancelado." + (f" Se borro lo que quedo a medias ({removed})." if removed else "")
            job["meta"] = ""
            log.info("job %s (%s) CANCELADO por el usuario en %.1fs: %s", job["id"], job["kind"], time.time() - t0, job["text"])
        except ApiError as e:
            job["state"], job["text"] = "error", str(e)
            log.warning("job %s (%s) ERROR en %.1fs: %s", job["id"], job["kind"], time.time() - t0, e)
        except Exception as e:  # noqa: BLE001
            job["state"], job["text"] = "error", f"Error inesperado: {e}"
            job["log"].append(traceback.format_exc())
            log.exception("job %s (%s) fallo inesperado", job["id"], job["kind"])
        finally:
            if acquired:
                pool_release(POOLS[pool])
    threading.Thread(target=wrapper, daemon=True).start()
    return {"job": job["id"]}


def check_cancel(job: dict) -> None:
    if job.get("cancel"):
        raise Cancelled()


def kill_tree(p: subprocess.Popen) -> None:
    """Mata el proceso y sus hijos (yt-dlp lanza ffmpeg al unir pistas)."""
    subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, creationflags=NOWIN)


def delete_files(paths: list[Path]) -> list[str]:
    """Borra archivos; en Windows el archivo puede seguir bloqueado un instante tras matar el proceso."""
    removed = []
    for f in paths:
        for _ in range(12):
            try:
                if f.exists():
                    f.unlink()
                    removed.append(f.name)
                break
            except OSError:
                time.sleep(0.5)
        else:
            log.warning("no pude borrar %s (sigue en uso)", f)
    return removed


def run_cleanup(job: dict) -> str:
    fn = CLEANUPS.pop(job["id"], None)
    if not fn:
        return ""
    removed = fn()
    log.info("job %s limpieza tras cancelar: %s", job["id"], removed)
    n = len(removed)
    return f"{n} archivo{'s' if n != 1 else ''}" if n else ""


def stream(cmd: list[str], job: dict, on_line) -> int:
    check_cancel(job)
    log.info("job %s cmd: %s", job["id"], subprocess.list2cmdline(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", creationflags=NOWIN)
    PROCS[job["id"]] = p
    if job.get("cancel"):  # cancelaron justo mientras arrancaba
        kill_tree(p)
    for line in p.stdout:
        line = line.rstrip()
        if line:
            noisy = bool(FF_PROGRESS_RE.match(line))
            if not noisy:
                job["log"].append(line)
                if not line.startswith("TDL|"):
                    log.info("job %s | %s", job["id"], line[:400])
            on_line(line)
    code = p.wait()
    PROCS.pop(job["id"], None)
    log.info("job %s proceso termino con codigo %s", job["id"], code)
    check_cancel(job)
    return code


def num(text: str) -> float | None:
    """Numero que yt-dlp imprimio en la plantilla de progreso ('NA'/'None' si no lo sabe)."""
    try:
        return float(str(text).strip())
    except ValueError:
        return None


def fmt_bytes(n: float | None) -> str:
    if n is None:
        return "?"
    for unit, size in (("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)):
        if n >= size:
            v = n / size
            return f"{v:.2f} {unit}".replace(".", ",") if unit == "GB" else f"{v:.1f} {unit}".replace(".", ",")
    return f"{int(n)} B"


def fmt_eta(sec: float | None) -> str:
    if sec is None:
        return "?"
    sec = int(sec)
    h, rest = divmod(sec, 3600)
    m, s = divmod(rest, 60)
    return f"{h} h {m:02d} min" if h else f"{m}:{s:02d}"


def live_size(path: Path) -> int:
    """Tamano real de un archivo que otro proceso esta escribiendo (os.stat en Windows puede ir atrasado)."""
    try:
        with open(path, "rb") as fh:
            return fh.seek(0, os.SEEK_END)
    except OSError:
        try:
            return path.stat().st_size
        except OSError:
            return 0


def monitor_merge(job: dict, base: Path, slug: str, expected: float, stop: threading.Event) -> None:
    """Avance de la union video+audio (yt-dlp -> ffmpeg no informa progreso): tamano del temporal / tamano esperado."""
    while not stop.wait(0.7):
        files = [f for f in base.glob(f"{slug}.temp.*") if f.is_file()]
        size = max((live_size(f) for f in files), default=0)
        if expected and size:
            frac = min(size / expected, 0.99)
            job.update(percent=frac * 100, indeterminate=False, text=f"Uniendo video y audio: {frac * 100:.0f}%",
                       meta=f"{fmt_bytes(size)} de ~{fmt_bytes(expected)}")


def view_job(job: dict) -> dict:
    return {**job, "log": list(job["log"])}


# ---------- API ----------

_VERSION_CACHE: dict[str, str | None] = {}

HEALTH_FILE = CONFIG_DIR / "health.json"
PROBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
RELEASES_URL = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
HEALTH: dict = {"state": "checking", "summary": "Revisando YouTube...", "advice": []}
ADVICE = [
    (r"confirm you.{0,3}re not a bot|sign in to confirm",
     "YouTube pide verificar que no eres un bot. Primero ACTUALIZAR YT-DLP; si persiste, cambia de red o usa cookies del navegador."),
    (r"HTTP Error 429|Too Many Requests",
     "YouTube limito las peticiones (429). Espera unos minutos o cambia de red; no es un problema de la app."),
    (r"HTTP Error 403|Forbidden",
     "YouTube rechazo la descarga (403): casi siempre es yt-dlp desactualizado. Pulsa ACTUALIZAR YT-DLP."),
    (r"n challenge|nsig|JS runtime|js_runtime|JavaScript runtime|Signature extraction|player JS",
     "YouTube cambio su reproductor. Pulsa ACTUALIZAR YT-DLP; si sigue fallando instala un runtime JS: winget install DenoLand.Deno"),
    (r"Unable to extract|Unsupported URL|extractor error",
     "yt-dlp no entiende la pagina: YouTube cambio algo. Pulsa ACTUALIZAR YT-DLP y reintenta."),
    (r"getaddrinfo|timed out|Temporary failure|Network is unreachable|Unable to download webpage|URLError|ConnectionError",
     "Parece un problema de internet, no de YouTube. Revisa la conexion."),
    (r"video (is )?unavailable|Private video|members-only|age.restricted|has been removed",
     "El problema es de ese video (privado, borrado, con edad o region), no de la app ni de YouTube en general."),
    (r"ffmpeg|ffprobe", "Falla en ffmpeg: revisa que siga instalado (winget install Gyan.FFmpeg)."),
]


def match_advice(text: str) -> str | None:
    for pattern, advice in ADVICE:
        if re.search(pattern, text or "", re.I):
            return advice
    return None


def diagnose(text: str) -> str:
    return match_advice(text) or "Error no reconocido: actualiza yt-dlp y, si persiste, revisa el detalle en tarrodl.log."


def ytdlp_version(yt: str) -> str | None:
    if yt not in _VERSION_CACHE:
        try:
            _VERSION_CACHE[yt] = run([yt, "--version"], timeout=20).stdout.strip() or None
        except Exception:
            log.exception("no pude leer la version de yt-dlp")
            _VERSION_CACHE[yt] = None
    return _VERSION_CACHE[yt]


def version_tuple(v: str | None) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


def latest_ytdlp() -> str | None:
    try:
        req = urllib.request.Request(RELEASES_URL, headers={"User-Agent": APP, "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r).get("tag_name")
    except Exception as e:  # noqa: BLE001
        log.warning("no pude consultar la ultima version de yt-dlp en GitHub: %s", e)
        return None


def load_health() -> dict:
    try:
        return json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def compare_health(prev: dict, cur: dict) -> tuple[list[str], list[str]]:
    """Devuelve (cambios detectados, acciones recomendadas) respecto de la revision anterior."""
    if not prev:
        return [], []
    changes, actions = [], []
    if prev.get("ytdlp") != cur.get("ytdlp"):
        changes.append(f"yt-dlp cambio de {prev.get('ytdlp')} a {cur.get('ytdlp')}")
    if prev.get("probe_ok") and not cur.get("probe_ok"):
        changes.append("la sonda funcionaba la ultima vez y ahora FALLA: YouTube cambio algo (o no hay internet)")
        actions.append("Si hay internet: pulsa ACTUALIZAR YT-DLP y reinicia la app.")
    if cur.get("probe_ok") and prev.get("probe_ok") is False:
        changes.append("la sonda vuelve a funcionar (la vez anterior fallaba)")
    if cur.get("probe_ok") and prev.get("probe_ok"):
        for key, label in (("max_height", "resolucion maxima"), ("h264_max_height", "resolucion maxima en H.264")):
            if prev.get(key) is not None and cur.get(key) != prev[key]:
                changes.append(f"{label} disponible cambio de {prev[key]}p a {cur.get(key)}p")
                if cur.get(key, 0) < prev[key]:
                    actions.append(f"YouTube ofrece menos calidad ({label}: {cur.get(key)}p). Los videos pueden bajar en menor resolucion que antes.")
        if abs(cur.get("formats", 0) - prev.get("formats", 0)) >= 5:
            changes.append(f"cantidad de formatos cambio de {prev.get('formats')} a {cur.get('formats')}")
    for w in sorted(set(cur.get("warnings", [])) - set(prev.get("warnings", []))):
        changes.append(f"advertencia nueva de yt-dlp: {w[:300]}")
        actions.append(match_advice(w) or "Advertencia desconocida: copia la linea del log y revisala antes de que rompa descargas.")
    if prev.get("js_runtime") != cur.get("js_runtime"):
        changes.append(f"runtime JS (deno/node/bun) cambio de {prev.get('js_runtime')} a {cur.get('js_runtime')}")
    return changes, actions


def startup_check() -> None:
    t0 = time.time()
    try:
        yt = find_tool("yt-dlp")
        if not yt:
            HEALTH.update(state="fail", summary="yt-dlp no esta instalado", advice=["Pulsa INSTALAR YT-DLP."])
            log.error("SALUD YOUTUBE: FALLA | yt-dlp no esta instalado")
            return
        HEALTH.update(state="checking", summary="Revisando YouTube...", advice=[])
        cur: dict = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "ytdlp": ytdlp_version(yt),
                     "js_runtime": next((n for n in ("deno", "node", "bun") if find_tool(n)), None)}
        advice: list[str] = []
        cur["latest"] = latest_ytdlp()
        if cur["latest"] and version_tuple(cur["latest"]) > version_tuple(cur["ytdlp"]):
            advice.append(f"Hay un yt-dlp mas nuevo ({cur['latest']}; instalado {cur['ytdlp']}). Pulsa ACTUALIZAR YT-DLP: "
                          "YouTube cambia seguido y las versiones viejas dejan de funcionar.")

        p0 = time.time()
        r = run([yt, "--no-playlist", "--encoding", "utf-8", "-J", "--", PROBE_URL], timeout=120)
        cur["probe_seconds"] = round(time.time() - p0, 1)
        cur["warnings"] = [ln.strip() for ln in r.stderr.splitlines() if ln.startswith(("WARNING", "ERROR"))]
        if r.returncode == 0:
            formats = json.loads(r.stdout).get("formats", [])
            video = [f for f in formats if f.get("vcodec") not in (None, "none") and f.get("height")]
            cur.update(probe_ok=True, formats=len(formats), max_height=max((f["height"] for f in video), default=0),
                       h264_max_height=max((f["height"] for f in video if str(f.get("vcodec", "")).startswith("avc1")), default=0))
        else:
            cur.update(probe_ok=False, probe_error=(cur["warnings"][-1] if cur["warnings"] else r.stderr.strip()[-300:]))
            log.warning("la sonda de YouTube fallo (codigo %s). stderr completo: %s", r.returncode, r.stderr.strip()[-2000:])
            advice.append(diagnose(r.stderr))

        prev = load_health()
        if not prev:
            log.info("SALUD YOUTUBE: primera revision, se guarda la linea base para comparar la proxima vez")
        changes, actions = compare_health(prev, cur)
        advice += [a for a in actions if a not in advice]
        state = "fail" if not cur["probe_ok"] else ("warn" if advice else "ok")
        summary = (f"yt-dlp {cur['ytdlp']} | sonda OK en {cur['probe_seconds']}s: {cur['formats']} formatos, hasta "
                   f"{cur['max_height']}p (H.264 hasta {cur['h264_max_height']}p)") if cur["probe_ok"] else \
                  f"yt-dlp {cur['ytdlp']} | la sonda de YouTube fallo: {cur.get('probe_error', '')[:200]}"
        HEALTH.update(state=state, summary=summary, advice=advice)
        cur["state"] = state
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        HEALTH_FILE.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")

        log.info("SALUD YOUTUBE: %s | %s | js_runtime=%s | ultima_ytdlp=%s | advertencias=%d | revision en %.1fs",
                 state.upper(), summary, cur["js_runtime"] or "ninguno", cur["latest"] or "?", len(cur["warnings"]), time.time() - t0)
        for w in cur["warnings"]:
            log.info("SALUD YOUTUBE advertencia de yt-dlp: %s", w[:500])
        for c in changes:
            log.warning("CAMBIO DETECTADO: %s", c)
        for a in advice:
            log.warning("ACCION RECOMENDADA: %s", a)
    except Exception as e:  # noqa: BLE001
        HEALTH.update(state="warn", summary=f"No pude completar la revision de YouTube: {e}", advice=[])
        log.exception("la revision de salud de YouTube fallo")


def api_status(_body=None) -> dict:
    yt = find_tool("yt-dlp")
    return {"ytdlp": ytdlp_version(yt) if yt else None, "ffmpeg": bool(find_tool("ffmpeg")),
            **folders_state(), "max_downloads": max_downloads(), "health": HEALTH}


def api_analyze(body: dict) -> dict:
    url = clean_url(body.get("url"))
    yt = need_tool("yt-dlp")
    r = run([yt, "--no-playlist", "--encoding", "utf-8", "-J", "--", url], timeout=90)
    if r.returncode != 0:
        log.warning("analyze fallo (codigo %s) url=%s stderr=%s", r.returncode, url, r.stderr.strip()[-1500:])
        errs = [ln for ln in r.stderr.splitlines() if ln.startswith("ERROR")]
        msg = errs[-1] if errs else (r.stderr.strip().splitlines() or ["No se pudo leer el video."])[-1]
        advice = diagnose(r.stderr)
        log.warning("DIAGNOSTICO analyze: %s", advice)
        raise ApiError(f"{msg} | Que hacer: {advice}")
    info = json.loads(r.stdout)
    heights = sorted({f["height"] for f in info.get("formats", [])
                      if f.get("height") and f.get("vcodec") not in (None, "none")}, reverse=True)
    return {"title": info.get("title") or "", "channel": info.get("channel") or info.get("uploader") or "",
            "duration": info.get("duration"), "thumbnail": info.get("thumbnail"),
            "heights": heights, "slug": slugify(info.get("title") or "gameplay")}


def api_download(body: dict) -> dict:
    url, slug = clean_url(body.get("url")), clean_slug(body.get("slug"))
    container = str(body.get("container") or "mp4")
    if container not in CONTAINERS:
        raise ApiError("Formato no soportado.")
    try:
        height = max(144, min(4320, int(body.get("height") or 1080)))
    except (TypeError, ValueError):
        raise ApiError("Calidad invalida.")
    yt, ff = need_tool("yt-dlp"), need_tool("ffmpeg")
    audio = container in ("mp3", "m4a")
    clip_plan = body.get("clips") or None
    if clip_plan:
        if audio:
            raise ApiError("Los clips necesitan un video: elige MP4 o MKV, o quita el plan de clips.")
        validate_clip_plan(clip_plan)
    base = out_base()
    base.mkdir(parents=True, exist_ok=True)
    final = base / f"{slug}.{container}"
    if final.exists():
        raise ApiError(f"Ya existe {final.name} en la carpeta de salida. Cambia el nombre o borra el archivo.")
    if any(j["kind"] == "download" and j["state"] in ("running", "queued") and j.get("target") == str(final)
           for j in list(JOBS.values())):
        raise ApiError(f"Ya hay otra descarga en la cola que va a crear {final.name}. Cambia el nombre.")

    cmd = [yt, "--no-playlist", "--newline", "--encoding", "utf-8",
           "--ffmpeg-location", str(Path(ff).parent),
           "--progress-template", "download:TDL|%(progress._percent_str)s|%(progress.speed)s|%(progress.eta)s|%(progress.downloaded_bytes)s"
           "|%(progress.total_bytes)s|%(progress.total_bytes_estimate)s",
           "-o", str(base / f"{slug}.%(ext)s")]
    if audio:
        cmd += ["-f", "bestaudio/best", "-x", "--audio-format", container, "--audio-quality", "0"]
    else:
        cmd += ["-f", f"bv*[height<={height}]+ba/b[height<={height}]", "--merge-output-format", container]
        if body.get("h264", True):
            cmd += ["-S", "vcodec:h264,acodec:aac"]
    if body.get("anti_slow", True):
        # YouTube a veces asigna un enlace lento (2-4 MB/s) a una conexion que podria bajar a 30+ MB/s.
        # Con esto yt-dlp pide un enlace nuevo y retoma donde iba si la velocidad cae bajo el limite.
        cmd += ["--throttled-rate", ANTI_SLOW_RATE]
    cmd += ["--", url]

    job = new_job("download")
    job["target"] = str(final)
    links_add(url, slug, container, body.get("height") or "")
    started = time.time()

    def cleanup_download() -> list[str]:
        # todo lo que esta descarga creo: <slug>.f298.mp4.part, <slug>.mp4.part, .ytdl, pistas sueltas...
        mine = [f for f in base.glob(f"{slug}.*") if f.is_file() and f.stat().st_ctime >= started - 2]
        return delete_files(mine)

    def work(j):
        CLEANUPS[j["id"]] = cleanup_download
        if final.exists():  # otra descarga de la cola lo creo mientras esperaba su turno
            raise ApiError(f"Ya existe {final.name} en la carpeta de salida. Cambia el nombre o borra el archivo.")
        stages, stage = (1 if audio else 2), 0
        seen_dest: set[str] = set()
        track_total: dict[int, float] = {}
        stop_merge = threading.Event()

        def on_line(line: str):
            nonlocal stage
            if line.startswith("[download] Destination:"):
                # al pedir un enlace nuevo yt-dlp repite la linea con el mismo archivo: no es otra pista
                dest = line.split("Destination:", 1)[1].strip()
                if dest not in seen_dest:
                    seen_dest.add(dest)
                    stage += 1
            elif "below throttle limit" in line:
                j["meta"] = "YouTube limito la velocidad: pidiendo un enlace nuevo y retomando..."
            elif line.startswith("TDL|"):
                _, pct, speed, eta, done, total, estimate = (line.split("|") + [""] * 6)[:7]
                try:
                    p = float(pct.strip().rstrip("%"))
                except ValueError:
                    return
                n = max(stage, 1)
                kind = "audio" if audio or n == 2 else "video"
                j["percent"] = min(99, ((n - 1) + p / 100) / stages * 100)
                j["text"] = (f"Descargando {kind}: {p:.0f}%" if stages == 1 else
                             f"Descargando {kind} (pista {n} de {stages}): {p:.0f}%")
                size_total = num(total) or num(estimate)
                if size_total:
                    track_total[n] = size_total
                size = f"{fmt_bytes(num(done))} de {fmt_bytes(size_total)}" if size_total else f"{fmt_bytes(num(done))} descargados"
                if not num(total) and size_total:
                    size += " (aprox.)"
                parts = [size]
                if num(speed):
                    parts.append(f"{fmt_bytes(num(speed))}/s")
                if num(eta) is not None and eta.strip() not in ("", "NA", "None"):
                    parts.append(f"quedan {fmt_eta(num(eta))}")
                j["meta"] = "  ·  ".join(parts)
            elif line.startswith("[Merger]"):
                # ffmpeg une las pistas sin avisar avance: se mide por el tamano del archivo temporal
                j.update(percent=0, indeterminate=True, text="Uniendo video y audio...", meta="")
                threading.Thread(target=monitor_merge, args=(j, base, slug, sum(track_total.values()), stop_merge),
                                 daemon=True).start()
            elif line.startswith(("[ExtractAudio]", "[VideoConvertor]")):
                j.update(percent=0, indeterminate=True, text="Convirtiendo el audio (puede tardar un momento)...", meta="")

        try:
            code = stream(cmd, j, on_line)
        finally:
            stop_merge.set()
        j["indeterminate"] = False
        if code != 0:
            errs = [ln for ln in j["log"] if ln.startswith("ERROR")]
            base_msg = errs[-1] if errs else f"yt-dlp fallo (codigo {code})."
            advice = diagnose("\n".join(j["log"]))
            log.warning("DIAGNOSTICO descarga: %s", advice)
            raise ApiError(f"{base_msg} | Que hacer: {advice}")
        out = final if final.exists() else max(base.glob(f"{slug}.*"), key=lambda p: p.stat().st_mtime, default=None)
        if not out:
            raise ApiError("La descarga termino pero no encuentro el archivo.")
        size = out.stat().st_size / 1048576
        j["text"], j["meta"] = f"Listo: {out.name} ({size:.0f} MB)", ""
        j["result"] = {"file": str(out)}
        if clip_plan:  # encadenado: los clips parten solos al terminar la descarga (en la cola de clips)
            try:
                j["result"]["clips_job"] = api_clips({**clip_plan, "file": str(out)})["job"]
                log.info("job %s encadeno clips: job %s", j["id"], j["result"]["clips_job"])
            except ApiError as e:
                j["result"]["clips_error"] = str(e)
                log.warning("job %s: no pude encadenar los clips: %s", j["id"], e)

    return spawn(job, work, pool="dl")


def probe_duration(ffprobe: str, src: Path) -> float:
    r = run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], timeout=60)
    try:
        return float(r.stdout.strip())
    except ValueError:
        raise ApiError("No pude leer la duracion del video (¿archivo corrupto?).")


def plan_clips(duration: float, length: int, max_clips: int) -> list[float]:
    n = int(duration // length)
    if n < 1:
        return []
    if 0 < max_clips < n:
        if max_clips == 1:
            return [(duration - length) / 2]
        step = (duration - length) / (max_clips - 1)
        return [i * step for i in range(max_clips)]
    return [float(i * length) for i in range(n)]


def fmt_len(sec: int) -> str:
    m, s = divmod(sec, 60)
    if m and s:
        return f"{m}m{s:02d}s"
    return f"{m}m" if m else f"{s}s"


AUTO_CLIP_EVERY_SEC = 600   # en automatico: un mosaico por cada ~10 min de video


def plan_mosaic(span: float, length: int, piece: int, n_clips: int) -> tuple[list[list[float]], float]:
    """Cada clip se arma con k trozos repartidos parejo dentro de su ventana de la seccion.

    `span` es el largo de la seccion elegida (inicios relativos a ella). k = length // piece, asi
    cada trozo dura length / k >= piece (nunca menos de lo pedido) y el clip suma exactamente
    `length`. n_clips = 0 es automatico: un mosaico por cada ~10 min de seccion (un gameplay de
    1 hora da varios mosaicos, uno de 10 min da uno), sin pasar de los que caben sin repetir
    material. Devuelve (inicios por clip, duracion de cada trozo); lista vacia si la seccion no
    alcanza para `length` segundos por clip.
    """
    k = max(1, length // piece)
    p = length / k
    fit = int(span // length)
    if fit < 1:
        return [], p
    n = n_clips if n_clips > 0 else min(fit, max(1, round(span / AUTO_CLIP_EVERY_SEC)))
    win = span / n
    if win < length:
        return [], p
    step = win / k
    return [[c * win + j * step + (step - p) / 2 for j in range(k)] for c in range(n)], p


def resolve_range(body: dict, duration: float) -> tuple[float, float]:
    """Seccion del video de la que se cortan los clips (por defecto, todo el video)."""
    try:
        a = float(body["range_start"]) if body.get("range_start") not in (None, "") else 0.0
        b = float(body["range_end"]) if body.get("range_end") not in (None, "") else duration
    except (TypeError, ValueError):
        raise ApiError("La seccion del video (desde/hasta) no es valida.")
    a, b = max(0.0, a), min(duration, b)
    if b - a < 1:
        raise ApiError("La seccion elegida es muy corta: 'hasta' tiene que ser mayor que 'desde'.")
    return a, b


def plan_section(mode: str, duration: float, a: float, b: float, length: int, piece: int,
                 max_clips: int) -> tuple[list[list[float]], float]:
    """Plan de cortes con inicios absolutos: (clips -> inicios de sus trozos, duracion de cada trozo)."""
    if mode == "mosaico":
        clips, seg = plan_mosaic(b - a, length, piece, max_clips)
    else:
        clips, seg = [[s] for s in plan_clips(b - a, length, max_clips)], float(length)
    return [[a + s for s in c] for c in clips], seg


def validate_mosaic_params(n_videos: int, total: int, piece: int, share: str, seed: int, height: int) -> None:
    if not MOSAIC_MIN_VIDEOS <= n_videos <= MOSAIC_MAX_VIDEOS:
        raise ApiError(f"El mosaico lleva entre {MOSAIC_MIN_VIDEOS} y {MOSAIC_MAX_VIDEOS} videos.")
    if not MOSAIC_MIN_SEC <= total <= MOSAIC_MAX_SEC:
        raise ApiError(f"El mosaico debe durar entre {MOSAIC_MIN_SEC // 60} y {MOSAIC_MAX_SEC // 60} minutos.")
    if not PIECE_MIN_SEC <= piece <= min(PIECE_MAX_SEC, total):
        raise ApiError(f"Cada trozo del mosaico debe durar entre {PIECE_MIN_SEC} y {min(PIECE_MAX_SEC, total)} segundos.")
    if share not in MOSAIC_SHARES:
        raise ApiError("El reparto entre videos es parejo o proporcional.")
    if seed < 0:
        raise ApiError("La semilla del reparto no es valida.")
    if height not in MOSAIC_HEIGHTS:
        raise ApiError("La resolucion del mosaico es 720 o 1080.")


def _allocate(k: int, weights: list[float], caps: list[int], lens: list[float]) -> list[int]:
    """Reparte k trozos por cuota entera + resto mayor; el que supera su capacidad se queda en ella y el exceso se reparte de nuevo."""
    alloc = [0] * len(weights)
    while True:
        free = [i for i in range(len(weights)) if alloc[i] < caps[i]]
        left = k - sum(alloc)
        if left <= 0 or not free:
            return alloc
        tw = sum(weights[i] for i in free)
        quota = {i: left * weights[i] / tw for i in free}
        base = {i: int(quota[i]) for i in free}
        for i in sorted(free, key=lambda i: (-(quota[i] - base[i]), -lens[i], i))[:left - sum(base.values())]:
            base[i] += 1
        over = [i for i in free if base[i] > caps[i] - alloc[i]]
        if not over:
            for i in free:
                alloc[i] += base[i]
            return alloc
        for i in over:
            alloc[i] = caps[i]


def plan_multi(videos: list[dict], total: int, piece: int, share: str, seed: int) -> dict:
    """Mosaico con trozos de varios videos, intercalados (v1, v2, v3... y vuelta a v1).

    `videos`: [{file, duration, a, b}] con la seccion a..b ya resuelta. k = total // piece trozos de
    p = total / k segundos (nunca menos que `piece`); cada trozo lleva un numero entero de frames a 30 fps
    (`frames`) y el total suma exacto. Cada video recibe sus trozos (parejo, o
    proporcional al largo de su seccion) sin pasar de lo que cabe sin solaparse; dentro del video van
    repartidos en ranuras iguales (seed 0 centrados, seed > 0 corridos al azar de forma reproducible).
    """
    k = max(1, total // piece)
    p = total / k
    pf = math.ceil(p * 30 - 1e-9) / 30   # lo que ocupa un trozo una vez redondeado a frames de 30 fps (nunca menos que p)
    caps = [int((v["b"] - v["a"]) / pf + 1e-9) for v in videos]
    if sum(caps) < k:
        raise ApiError(f"Los videos no alcanzan para {fmt_len(total)} sin repetir material. "
                       f"Amplia secciones, agrega videos o baja el largo total.")
    lens = [v["b"] - v["a"] for v in videos]
    counts = _allocate(k, [1.0] * len(videos) if share == "parejo" else lens, caps, lens)
    lanes = []
    for idx, (v, m) in enumerate(zip(videos, counts)):
        starts = []
        if m:
            w = (v["b"] - v["a"]) / m
            margin = max(0.0, w - pf)
            rng = random.Random(f"{seed}:{idx}")
            starts = [v["a"] + j * w + (margin / 2 if seed == 0 else rng.uniform(0, margin)) for j in range(m)]
        lanes.append({"file": v["file"], "duration": v["duration"], "range": [v["a"], v["b"]], "starts": starts})
    sequence = []
    for turn in range(max(counts, default=0)):
        for idx, lane in enumerate(lanes):
            if turn < len(lane["starts"]):
                n = len(sequence)   # frames enteros por trozo: los k trozos suman exactamente total * 30
                sequence.append({"video": idx, "start": lane["starts"][turn], "at": (total * 30 * n // k) / 30,
                                 "frames": total * 30 * (n + 1) // k - total * 30 * n // k})
    return {"pieces": k, "seg": p, "lanes": lanes, "sequence": sequence}


def next_clip_index(out_dir: Path, stem: str) -> int:
    """Primer numero libre para <stem>_clipN (sigue la numeracion si ya hay clips de ese video)."""
    pat = re.compile(re.escape(stem) + r"_clip(\d+)\.[A-Za-z0-9]+$", re.I)
    used = [int(m.group(1)) for f in out_dir.iterdir() if (m := pat.match(f.name))]
    return max(used, default=0) + 1


def has_video(fp: str, src: Path) -> bool:
    r = run([fp, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)],
            timeout=60)
    return bool(r.stdout.strip())


def has_audio(fp: str, src: Path) -> bool:
    r = run([fp, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)],
            timeout=60)
    return bool(r.stdout.strip())


def validate_clip_params(mode: str, length: int, piece: int) -> None:
    if not CLIP_MIN_SEC <= length <= CLIP_MAX_SEC:
        raise ApiError(f"Los clips deben durar entre {CLIP_MIN_SEC // 60} y {CLIP_MAX_SEC // 60} minutos.")
    if mode == "mosaico" and not PIECE_MIN_SEC <= piece <= min(PIECE_MAX_SEC, length):
        raise ApiError(f"Cada trozo del mosaico debe durar entre {PIECE_MIN_SEC} y {min(PIECE_MAX_SEC, length)} segundos.")


def validate_clip_plan(plan: dict) -> None:
    """Revisa un plan de clips (el que viaja encadenado a una descarga) antes de aceptarla."""
    mode = str(plan.get("mode") or "seguido")
    if mode not in ("seguido", "mosaico"):
        raise ApiError("Modo de clip desconocido (seguido o mosaico).")
    try:
        length, piece = int(plan.get("length_sec")), int(plan.get("piece_sec") or 15)
        max(0, int(plan.get("max_clips") or 0))
    except (TypeError, ValueError):
        raise ApiError("Duracion, trozos o cantidad de clips invalida.")
    validate_clip_params(mode, length, piece)


def api_plan(body: dict) -> dict:
    """Vista previa: de que partes del video saldria cada trozo (misma logica que api_clips).

    Sirve con un archivo ya descargado o, antes de descargar, con la duracion que informo YouTube (`duration`)."""
    duration = None
    if body.get("file"):
        src = Path(str(body.get("file")).strip().strip('"'))
        if not src.is_file() or src.suffix.lower() not in VIDEO_EXTS:
            raise ApiError("El archivo no existe o no es un video (mp4, mkv, webm, mov, avi).")
    else:
        src = None
        try:
            duration = float(body.get("duration"))
        except (TypeError, ValueError):
            raise ApiError("Falta el video o su duracion.")
        if duration < 1:
            raise ApiError("El video dura menos de un segundo.")
    mode = str(body.get("mode") or "seguido")
    try:
        length, piece = int(body.get("length_sec")), int(body.get("piece_sec") or 15)
        max_clips = max(0, int(body.get("max_clips") or 0))
    except (TypeError, ValueError):
        raise ApiError("Duracion, trozos o cantidad de clips invalida.")
    validate_clip_params(mode, length, piece)
    if duration is None:
        duration = probe_duration(need_tool("ffprobe", "ffprobe (viene con ffmpeg)"), src)
    a, b = resolve_range(body, duration)
    clips, seg = plan_section(mode, duration, a, b, length, piece, max_clips)
    return {"duration": duration, "range": [a, b], "clips": clips, "seg": seg}


def api_clips(body: dict) -> dict:
    src = Path(str(body.get("file") or "").strip().strip('"'))
    if not src.is_file() or src.suffix.lower() not in VIDEO_EXTS:
        raise ApiError("El archivo no existe o no es un video (mp4, mkv, webm, mov, avi).")
    mode = str(body.get("mode") or "seguido")
    if mode not in ("seguido", "mosaico"):
        raise ApiError("Modo de clip desconocido (seguido o mosaico).")
    try:
        if body.get("length_sec") is not None:
            length = int(body["length_sec"])
        else:  # compatibilidad con el selector viejo de 1/2/3 minutos
            length = int(body.get("length_min")) * 60
        piece = int(body.get("piece_sec") or 15)
        max_clips = max(0, int(body.get("max_clips") or 0))
    except (TypeError, ValueError):
        raise ApiError("Duracion, trozos o cantidad de clips invalida.")
    validate_clip_params(mode, length, piece)
    ff, fp = need_tool("ffmpeg"), need_tool("ffprobe", "ffprobe (viene con ffmpeg)")
    out_dir = clips_base()
    label = fmt_len(length)
    job = new_job("clips")

    def work(j):
        duration = probe_duration(fp, src)
        a, b = resolve_range(body, duration)
        plan, p = plan_section(mode, duration, a, b, length, piece, max_clips)
        log.info("job %s %s: src=%s duracion=%.1fs seccion=%.0f-%.0fs largo=%ss trozo=%ss->%.2fs max=%s clips=%s inicios=%s",
                 j["id"], mode, src, duration, a, b, length, piece, p, max_clips, len(plan),
                 [[round(s) for s in c] for c in plan])
        if not plan:
            raise ApiError(f"La seccion elegida dura {(b - a) / 60:.1f} min: no alcanza para "
                           f"{f'{max_clips} clip(s)' if max_clips else 'un clip'} de {label}"
                           f"{' sin repetir material' if mode == 'mosaico' else ''}. "
                           f"Amplia la seccion, baja la cantidad de clips o acorta la duracion.")
        out_dir.mkdir(parents=True, exist_ok=True)
        ext = ".mp4" if mode == "mosaico" else src.suffix.lower()
        first = next_clip_index(out_dir, src.stem)
        paths = [out_dir / f"{src.stem}_clip{first + i}{ext}" for i in range(len(plan))]
        log.info("job %s clips a %s: %s", j["id"], out_dir, [p_.name for p_ in paths])
        audio = has_audio(fp, src) if mode == "mosaico" else True
        current: list[Path] = []   # clip en curso: es lo unico que queda a medias si cancelan (los terminados se conservan)
        CLEANUPS[j["id"]] = lambda: delete_files(current)
        for i, (starts_i, path) in enumerate(zip(plan, paths), 1):
            check_cancel(j)
            current[:] = [path]
            base_pct = (i - 1) / len(plan) * 100
            if mode == "seguido":
                j["text"], j["percent"] = f"Cortando clip {i} de {len(plan)}...", base_pct
                r = run([ff, "-hide_banner", "-loglevel", "error", "-n", "-ss", f"{starts_i[0]:.3f}", "-i", str(src),
                         "-t", str(length), "-c", "copy", "-avoid_negative_ts", "make_zero", str(path)])
                if r.returncode != 0:
                    log.warning("job %s ffmpeg clip %s fallo: %s", j["id"], i, r.stderr.strip()[-1500:])
                    raise ApiError(f"ffmpeg fallo en el clip {i}: {r.stderr.strip()[-200:]}")
                current.clear()
                continue
            j["text"], j["percent"] = f"Armando mosaico {i} de {len(plan)} ({len(starts_i)} trozos, recodifica)...", base_pct
            cmd = [ff, "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1", "-n"]
            for st in starts_i:
                cmd += ["-ss", f"{st:.3f}", "-t", f"{p:.3f}", "-i", str(src)]
            parts = [f"[{k}:v:0]setpts=PTS-STARTPTS[v{k}]" + (f";[{k}:a:0]asetpts=PTS-STARTPTS[a{k}]" if audio else "")
                     for k in range(len(starts_i))]
            joined = "".join(f"[v{k}][a{k}]" if audio else f"[v{k}]" for k in range(len(starts_i)))
            parts.append(f"{joined}concat=n={len(starts_i)}:v=1:a={1 if audio else 0}[v]" + ("[a]" if audio else ""))
            cmd += ["-filter_complex", ";".join(parts), "-map", "[v]"] + (["-map", "[a]"] if audio else [])
            cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
            cmd += (["-c:a", "aac", "-b:a", "192k"] if audio else []) + ["-movflags", "+faststart", str(path)]

            def on_line(line, base=base_pct):
                if line.startswith("out_time_us="):
                    try:
                        frac = min(1.0, int(line.split("=", 1)[1]) / 1e6 / length)
                    except ValueError:
                        return
                    j["percent"] = base + frac * (100 / len(plan))
            code = stream(cmd, j, on_line)
            if code != 0:
                path.unlink(missing_ok=True)
                tail = " | ".join(list(j["log"])[-3:])
                raise ApiError(f"ffmpeg fallo armando el mosaico {i}: {tail[-250:]}")
            current.clear()
        kind = "mosaicos" if mode == "mosaico" else "clips"
        j["text"] = f"Listo: {len(plan)} {kind} de {label} ({paths[0].name}" + (f" ... {paths[-1].name}" if len(paths) > 1 else "") + f") en {out_dir}"
        j["result"] = {"dir": str(out_dir), "count": len(plan)}

    return spawn(job, work, pool="clips")


# ---------- mosaico multi-video ----------

YT_TRACK_RE = re.compile(r"\.f\d+\.", re.I)   # pista suelta de yt-dlp (<slug>.f137.mp4): video o audio solo, no sirve para el mosaico
PROBE_CACHE: dict[tuple, dict] = {}   # (ruta, mtime, tamano) -> {duration, audio}: no se vuelve a medir un archivo que no cambio


def norm_path(raw: object) -> str:
    """Ruta comparable: absoluta y sin diferencias de mayusculas ni de barras (Windows)."""
    return os.path.normcase(os.path.abspath(str(raw).strip().strip('"')))


def check_video_file(raw: object) -> Path:
    src = Path(str(raw or "").strip().strip('"'))
    if not src.is_file():
        raise ApiError(f"No encuentro el archivo {src.name or raw}.")
    if src.suffix.lower() not in VIDEO_EXTS:
        raise ApiError(f"{src.name} no es un video (mp4, mkv, webm, mov, avi, m4v).")
    return src


def probe_video(src: Path) -> dict:
    st = src.stat()
    key = (norm_path(src), st.st_mtime_ns, st.st_size)
    if key not in PROBE_CACHE:
        fp = need_tool("ffprobe", "ffprobe (viene con ffmpeg)")
        try:
            if not has_video(fp, src):
                raise ApiError("no tiene pista de video (¿es solo audio o una pista suelta de yt-dlp?).")
            PROBE_CACHE[key] = {"duration": probe_duration(fp, src), "audio": has_audio(fp, src)}
        except ApiError as e:
            raise ApiError(f"{src.name}: {e}")
    return PROBE_CACHE[key]


def clean_mosaic_name(raw: object) -> str:
    text = str(raw or "").strip()
    return slugify(text, 60) if text else "mosaico"


def resolve_mosaic_request(body: dict) -> dict:
    """Valida el pedido y calcula el plan. La vista previa y el render pasan por aqui: mismo plan siempre."""
    vids = body.get("videos")
    if not isinstance(vids, list):
        raise ApiError("Faltan los videos del mosaico.")
    try:
        total, piece = int(body.get("total_sec")), int(body.get("piece_sec") or 15)
        seed, height = int(body.get("seed") or 0), int(body.get("height") or 1080)
    except (TypeError, ValueError):
        raise ApiError("Largo total, trozo, semilla o resolucion invalidos.")
    share = str(body.get("share") or "parejo")
    validate_mosaic_params(len(vids), total, piece, share, seed, height)
    seen, items = set(), []
    for entry in vids:
        if not isinstance(entry, dict):
            raise ApiError("Lista de videos invalida.")
        src = check_video_file(entry.get("file"))
        if norm_path(src) in seen:
            raise ApiError(f"El video {src.name} esta repetido en la lista.")
        seen.add(norm_path(src))
        info = probe_video(src)
        a, b = resolve_range(entry, info["duration"])
        items.append({"file": str(src), "duration": info["duration"], "a": a, "b": b, "audio": info["audio"]})
    return {"videos": items, "total": total, "piece": piece, "share": share, "seed": seed, "height": height,
            "name": clean_mosaic_name(body.get("name")), "plan": plan_multi(items, total, piece, share, seed)}


def api_probe(body: dict) -> dict:
    files = body.get("files")
    if not isinstance(files, list) or not files or len(files) > 50:
        raise ApiError("Faltan los archivos a medir.")
    out = []
    for raw in files:
        src = check_video_file(raw)
        info = probe_video(src)
        out.append({"file": str(src), "name": src.name, "duration": info["duration"], "audio": info["audio"]})
    return {"videos": out}


def api_mosaic_plan(body: dict) -> dict:
    r = resolve_mosaic_request(body)
    return {**r["plan"], "total": r["total"]}


def api_session_files(_body=None) -> dict:
    """Videos que hay en la carpeta de descargas (sin los temporales de una descarga en curso), los mas nuevos primero."""
    base, files = out_base(), []
    if base.is_dir():
        for f in base.iterdir():
            if f.is_file() and f.suffix.lower() in VIDEO_EXTS and ".temp." not in f.name.lower() and not YT_TRACK_RE.search(f.name):
                st = f.stat()
                files.append({"file": str(f), "name": f.name, "size": st.st_size, "mtime": st.st_mtime})
    files.sort(key=lambda x: -x["mtime"])
    return {"files": files[:50]}


# ---------- links recientes: un .txt con los links de las descargas de las ultimas 48 h (para poder retomarlas) ----------
LINKS_TTL = 48 * 3600
LINKS_LOCK = threading.Lock()
LINKS_HEADER = ("# TarroDL: links de las descargas de las ultimas 48 horas (sirven para retomar una descarga que quedo a medias).\n"
                "# Cada linea: fecha | link | nombre | formato | calidad. Las lineas con mas de 48 horas se borran solas.\n")


def _links_line(when: str, url: str, slug: str, container: str, height) -> str:
    clean = lambda x: str(x).replace(" | ", " / ").replace("\r", " ").replace("\n", " ").strip()
    return f"{when} | {clean(url)} | {clean(slug)} | {clean(container)} | {clean(height)}\n"


def links_file() -> Path:
    return CONFIG_DIR / "links-recientes.txt"


def _links_parse(text: str, now: float) -> list[dict]:
    out = []
    for ln in text.splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = [x.strip() for x in ln.split(" | ")]
        if len(parts) < 3:
            continue
        try:
            ts = time.mktime(time.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            continue
        if now - ts <= LINKS_TTL:
            out.append({"ts": ts, "when": parts[0], "url": parts[1], "slug": parts[2],
                        "container": parts[3] if len(parts) > 3 else "", "height": parts[4] if len(parts) > 4 else ""})
    return out


def links_recent(now: float | None = None) -> list[dict]:
    """Links guardados de las ultimas 48 h. Reescribe el archivo sin las lineas vencidas (y sin el archivo si no hay nada)."""
    now = now or time.time()
    f = links_file()
    with LINKS_LOCK:
        try:
            text = f.read_text(encoding="utf-8") if f.exists() else ""
        except OSError:
            return []
        keep = _links_parse(text, now)
        lines_before = sum(1 for ln in text.splitlines() if ln.strip() and not ln.startswith("#"))
        if lines_before != len(keep):
            try:
                if keep:
                    f.write_text(LINKS_HEADER + "".join(_links_line(k["when"], k["url"], k["slug"], k["container"], k["height"]) for k in keep), encoding="utf-8")
                else:
                    f.unlink()
            except OSError as e:
                log.warning("no pude limpiar %s: %s", f, e)
        return keep


def links_add(url: str, slug: str, container: str, height) -> None:
    """Anota un link de descarga (al encolarla). Nunca debe romper la descarga: cualquier fallo solo se registra."""
    try:
        links_recent()  # limpia lo vencido antes de sumar
        line = _links_line(time.strftime("%Y-%m-%d %H:%M:%S"), url, slug, container, height)
        f = links_file()
        with LINKS_LOCK:
            f.parent.mkdir(parents=True, exist_ok=True)
            new = not f.exists()
            with open(f, "a", encoding="utf-8") as fh:
                if new:
                    fh.write(LINKS_HEADER)
                fh.write(line)
    except Exception as e:  # noqa: BLE001
        log.warning("no pude guardar el link reciente: %s", e)


def api_open_links(_body=None) -> dict:
    f = links_file()
    links_recent()
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(LINKS_HEADER, encoding="utf-8")
    os.startfile(str(f))  # type: ignore[attr-defined]
    return {"path": str(f)}


# restos de una descarga a medias: <slug>.f298.mp4.part / <slug>.mp4.part / .ytdl / .part-FragN / <slug>.temp.mp4 / pista suelta <slug>.f298.mp4
PARTIAL_RES = (
    re.compile(r"^(?P<slug>.+?)(?:\.f[\w-]+)?\.[A-Za-z0-9]{2,4}\.(?:part(?:-Frag\d+)?|ytdl)$", re.I),
    re.compile(r"^(?P<slug>.+?)\.part(?:-Frag\d+)?$", re.I),
    re.compile(r"^(?P<slug>.+?)\.temp\.[A-Za-z0-9]{2,4}$", re.I),
    re.compile(r"^(?P<slug>.+?)\.f\d+[\w-]*\.[A-Za-z0-9]{2,4}$", re.I),
)


def scan_partials() -> tuple[Path, list[dict]]:
    """Restos de descargas a medias en la carpeta de descargas, agrupados por nombre de video (cada grupo trae sus Path)."""
    base = out_base()
    groups: dict[str, dict] = {}
    if base.is_dir():
        for f in base.iterdir():
            if not f.is_file():
                continue
            m = next((r.match(f.name) for r in PARTIAL_RES if r.match(f.name)), None)
            if not m:
                continue
            st = f.stat()
            g = groups.setdefault(m.group("slug"), {"slug": m.group("slug"), "files": [], "paths": [], "size": 0, "mtime": 0.0})
            g["files"].append({"name": f.name, "size": st.st_size, "mtime": st.st_mtime})
            g["paths"].append(f)
            g["size"] += st.st_size
            g["mtime"] = max(g["mtime"], st.st_mtime)
    active = {Path(j["target"]).stem for j in list(JOBS.values())
              if j.get("kind") == "download" and j.get("state") in ("running", "queued") and j.get("target")}
    recent = links_recent()
    items = []
    for g in groups.values():
        g["files"].sort(key=lambda x: x["name"])
        g["active"] = g["slug"] in active
        g["final_exists"] = any((base / f"{g['slug']}.{c}").is_file() for c in CONTAINERS)
        g["resumable"] = not g["active"] and not g["final_exists"] and any(".part" in x["name"].lower() for x in g["files"])
        match = [k for k in recent if k["slug"] == g["slug"]]
        g["link"] = max(match, key=lambda k: k["ts"])["url"] if match else ""
        items.append(g)
    items.sort(key=lambda g: -g["mtime"])
    return base, items


def api_partials(_body=None) -> dict:
    """Lista los restos de descargas inconclusas. 'retomable' = el nombre final aun no existe, asi que volver a
    descargar con el mismo nombre y calidad continua desde donde iba (yt-dlp retoma los .part)."""
    base, items = scan_partials()
    return {"folder": str(base), "exists": base.is_dir(), "items": [{k: v for k, v in g.items() if k != "paths"} for g in items]}


def api_partials_delete(body: dict) -> dict:
    """Borra los restos de UN video ({slug}) o de todos ({all: true}). Vuelve a escanear: solo toca archivos que siguen
    siendo restos dentro de la carpeta de descargas, y nunca los de una descarga en curso."""
    slug, everything = body.get("slug"), bool(body.get("all"))
    if not everything and not isinstance(slug, str):
        raise ApiError("Falta indicar que video limpiar.")
    base, items = scan_partials()
    chosen = [g for g in items if everything or g["slug"] == slug]
    if not everything and not chosen:
        raise ApiError("Esos restos ya no estan en la carpeta.")
    deleted, skipped = [], []
    for g in chosen:
        if g["active"]:
            skipped.append(g["slug"])
            continue
        deleted += delete_files([p for p in g["paths"] if p.parent == base])
    log.info("partials: borrados %s | omitidos (en curso) %s", deleted, skipped)
    return {"deleted": deleted, "skipped": skipped}


MOSAIC_AFMT = "aformat=sample_rates=48000:sample_fmts=fltp:channel_layouts=stereo"


def mosaic_filter(sequence: list[dict], audio: list[bool], seg: float, height: int) -> str:
    """Filtro de ffmpeg (para -filter_complex_script): normaliza cada trozo (resolucion con barras, 30 fps, audio
    estereo 48 kHz; silencio si el video no tiene audio) y los une. La entrada i corresponde a sequence[i]."""
    w = height * 16 // 9
    lines = []
    for i, piece in enumerate(sequence):
        n = piece.get("frames") or round(seg * 30)
        lines.append(f"[{i}:v:0]scale={w}:{height}:force_original_aspect_ratio=decrease,"
                     f"pad={w}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,trim=end_frame={n},setpts=PTS-STARTPTS[v{i}]")
        if audio[piece["video"]]:
            lines.append(f"[{i}:a:0]aresample=48000,{MOSAIC_AFMT},atrim=duration={n / 30:.6f},asetpts=PTS-STARTPTS[a{i}]")
        else:
            lines.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={n / 30:.6f},{MOSAIC_AFMT},asetpts=PTS-STARTPTS[a{i}]")
    joined = "".join(f"[v{i}][a{i}]" for i in range(len(sequence)))
    lines.append(f"{joined}concat=n={len(sequence)}:v=1:a=1[v][a]")
    return ";\n".join(lines)


def unique_name(out_dir: Path, name: str, ext: str = ".mp4") -> Path:
    """<nombre>.mp4, y si existe <nombre>_2.mp4, _3... (nunca pisa nada)."""
    path, n = out_dir / f"{name}{ext}", 2
    while path.exists():
        path, n = out_dir / f"{name}_{n}{ext}", n + 1
    return path


def api_mosaic(body: dict) -> dict:
    req = resolve_mosaic_request(body)   # valida y revisa los archivos ANTES de crear el job
    ff = need_tool("ffmpeg")
    plan, total, name, height = req["plan"], req["total"], req["name"], req["height"]
    out_dir = clips_base()
    job = new_job("mosaic")

    def work(j):
        for v in req["videos"]:
            check_video_file(v["file"])
        out_dir.mkdir(parents=True, exist_ok=True)
        path = unique_name(out_dir, name)
        seq = plan["sequence"]
        fd, tmp_name = tempfile.mkstemp(suffix=".ffgraph")
        tmp = Path(tmp_name)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(mosaic_filter(seq, [v["audio"] for v in req["videos"]], plan["seg"], height))
        CLEANUPS[j["id"]] = lambda: delete_files([path, tmp])
        log.info("job %s mosaico: %s trozos de %.2fs de %s videos -> %s (%sp, reparto %s, semilla %s)",
                 j["id"], len(seq), plan["seg"], len(req["videos"]), path, height, req["share"], req["seed"])
        j["text"] = f"Armando mosaico ({len(seq)} trozos de {len(req['videos'])} videos, recodifica)..."
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1", "-n"]
        for piece in seq:
            cmd += ["-ss", f"{piece['start']:.3f}", "-t", f"{piece['frames'] / 30 + 0.1:.3f}", "-i", req["videos"][piece["video"]]["file"]]
        cmd += ["-filter_complex_script", str(tmp), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(path)]

        def on_line(line):
            if line.startswith("out_time_us="):
                try:
                    j["percent"] = min(99.0, int(line.split("=", 1)[1]) / 1e6 / total * 100)
                except ValueError:
                    pass
        code = stream(cmd, j, on_line)
        if code != 0:
            delete_files([path, tmp])
            tail = " | ".join(list(j["log"])[-3:])
            raise ApiError(f"ffmpeg fallo armando el mosaico: {tail[-250:]}")
        delete_files([tmp])
        CLEANUPS.pop(j["id"], None)
        j["text"] = f"Listo: {path.name} ({fmt_len(total)}) en {out_dir}"
        j["result"] = {"dir": str(out_dir), "file": path.name, "count": 1}

    return spawn(job, work, pool="clips")


def api_cancel(body: dict) -> dict:
    job = JOBS.get(str(body.get("job") or ""))
    if not job or job["state"] not in ("running", "queued"):
        raise ApiError("Ese proceso ya termino, no hay nada que cancelar.")
    job["cancel"] = True
    job["text"] = "Cancelando..."
    for pool in POOLS.values():
        with pool.cond:
            pool.cond.notify_all()
    log.info("job %s: el usuario pidio CANCELAR (%s)", job["id"], job["kind"])
    p = PROCS.get(job["id"])
    if p:
        kill_tree(p)
    return {}


def api_queue_move(body: dict) -> dict:
    """Sube o baja un trabajo que espera en la cola (direction: up | down | top)."""
    job = JOBS.get(str(body.get("job") or ""))
    direction = str(body.get("direction") or "")
    if not job or job["state"] != "queued" or not job.get("pool"):
        raise ApiError("Ese trabajo ya no esta esperando en la cola.")
    if direction not in ("up", "down", "top"):
        raise ApiError("Direccion invalida (up, down o top).")
    pool = POOLS[job["pool"]]
    with pool.cond:
        if job["id"] not in pool.waiting:
            raise ApiError("Ese trabajo ya no esta esperando en la cola.")
        i = pool.waiting.index(job["id"])
        j = {"up": max(0, i - 1), "down": min(len(pool.waiting) - 1, i + 1), "top": 0}[direction]
        pool.waiting.insert(j, pool.waiting.pop(i))
        pool.cond.notify_all()
    log.info("job %s movido en la cola (%s): puesto %s -> %s", job["id"], direction, i + 1, j + 1)
    return {}


def api_settings(body: dict) -> dict:
    if "max_downloads" in body:
        try:
            n = int(body["max_downloads"])
        except (TypeError, ValueError):
            raise ApiError("Cantidad de descargas invalida.")
        lo, hi = MAX_DOWNLOADS_RANGE
        if not lo <= n <= hi:
            raise ApiError(f"Las descargas a la vez van de {lo} a {hi}.")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps({**load_config(), "max_downloads": n}, indent=2), encoding="utf-8")
        apply_settings()
        log.info("descargas a la vez: %s", n)
    return {"max_downloads": max_downloads()}


def api_update(_body=None) -> dict:
    yt = need_tool("yt-dlp")
    job = new_job("update")

    def work(j):
        if stream([yt, "-U"], j, lambda ln: j.update(text=ln[:120])) != 0:
            raise ApiError("No se pudo actualizar yt-dlp (si lo instalaste con winget, usa: winget upgrade yt-dlp.yt-dlp).")
        _VERSION_CACHE.clear()
        threading.Thread(target=startup_check, daemon=True).start()
        j["text"] = "yt-dlp actualizado."

    return spawn(job, work)


def api_install(_body=None) -> dict:
    winget = shutil.which("winget")
    if not winget:
        raise ApiError("winget no esta disponible. Instala yt-dlp a mano.")
    job = new_job("install")

    def work(j):
        cmd = [winget, "install", "--id=yt-dlp.yt-dlp", "-e", "--accept-package-agreements", "--accept-source-agreements"]
        if stream(cmd, j, lambda ln: j.update(text=ln[:120])) != 0 or not find_tool("yt-dlp"):
            raise ApiError("La instalacion de yt-dlp fallo. Revisa el detalle.")
        _VERSION_CACHE.clear()
        threading.Thread(target=startup_check, daemon=True).start()
        j["text"] = "yt-dlp instalado."

    return spawn(job, work)


# Ventana "duena" invisible, siempre encima y activa: sin ella el dialogo (lanzado desde un proceso sin
# ventana) queda escondido detras de la ventana del programa y parece que "no abre nada".
PICK_PREAMBLE = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.FormBorderStyle = 'None'
$owner.StartPosition = 'CenterScreen'
$owner.Size = New-Object System.Drawing.Size(1, 1)
$owner.Opacity = 0
$owner.Show()
$owner.Activate()
"""

PICK_SCRIPT = PICK_PREAMBLE + r"""
$d = New-Object System.Windows.Forms.FolderBrowserDialog
$d.Description = if ($env:TARRODL_TITLE) { $env:TARRODL_TITLE } else { "Carpeta donde guardar los videos" }
$d.ShowNewFolderButton = $true
if ($env:TARRODL_START) { $d.SelectedPath = $env:TARRODL_START }
if ($d.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $d.SelectedPath }
$owner.Close()
"""


def save_config_key(key: str, path: Path) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({**load_config(), key: str(path)}, indent=2), encoding="utf-8")


def api_pickfolder(body: dict) -> dict:
    which = str(body.get("which") or "out")
    if which not in ("out", "clips"):
        raise ApiError("Carpeta desconocida (out o clips).")
    key, start, title = (("output_base", out_base(), "Carpeta donde guardar los videos descargados") if which == "out"
                         else ("clips_base", clips_base(), "Carpeta donde dejar los clips"))
    ps = shutil.which("powershell")
    if not ps:
        raise ApiError("No encontre PowerShell para abrir el selector de carpetas.")
    log.info("abriendo selector de carpeta (%s), inicio en %s", which, start)
    r = subprocess.run([ps, "-NoProfile", "-STA", "-Command", PICK_SCRIPT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, creationflags=NOWIN,
                       env={**os.environ, "TARRODL_START": str(start), "TARRODL_TITLE": title})
    chosen = r.stdout.strip()
    if not chosen:
        log.info("selector de carpeta (%s) cancelado (stderr=%s)", which, r.stderr.strip()[-300:])
        return {"cancelled": True, **folders_state()}
    path = Path(chosen)
    if not path.is_dir():
        raise ApiError("Esa carpeta no existe.")
    save_config_key(key, path)
    log.info("carpeta %s guardada: %s", key, path)
    return folders_state()


PICK_VIDEO_SCRIPT = PICK_PREAMBLE + r"""
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = "Elige el video a cortar"
$d.Filter = "Videos|*.mp4;*.mkv;*.webm;*.mov;*.avi;*.m4v|Todos los archivos|*.*"
if ($env:TARRODL_START -and (Test-Path -LiteralPath $env:TARRODL_START)) { $d.InitialDirectory = $env:TARRODL_START }
if ($d.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) { Write-Output $d.FileName }
$owner.Close()
"""


def api_pickvideo(body: dict) -> dict:
    ps = shutil.which("powershell")
    if not ps:
        raise ApiError("No encontre PowerShell para abrir el selector de archivos.")
    start = out_base()
    hint = Path(str(body.get("start") or "").strip().strip('"'))
    if hint.is_file():
        start = hint.parent
    log.info("abriendo selector de video, inicio en %s", start)
    r = subprocess.run([ps, "-NoProfile", "-STA", "-Command", PICK_VIDEO_SCRIPT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, creationflags=NOWIN,
                       env={**os.environ, "TARRODL_START": str(start)})
    chosen = r.stdout.strip()
    if not chosen:
        log.info("selector de video cancelado (stderr=%s)", r.stderr.strip()[-300:])
        return {"cancelled": True}
    path = Path(chosen)
    if not path.is_file() or path.suffix.lower() not in VIDEO_EXTS:
        raise ApiError("Ese archivo no es un video (mp4, mkv, webm, mov, avi).")
    log.info("video elegido para clips: %s", path)
    return {"file": str(path)}


PICK_VIDEOS_SCRIPT = PICK_PREAMBLE + r"""
$d = New-Object System.Windows.Forms.OpenFileDialog
$d.Title = "Elige los videos para el mosaico"
$d.Multiselect = $true
$d.Filter = "Videos|*.mp4;*.mkv;*.webm;*.mov;*.avi;*.m4v|Todos los archivos|*.*"
if ($env:TARRODL_START -and (Test-Path -LiteralPath $env:TARRODL_START)) { $d.InitialDirectory = $env:TARRODL_START }
if ($d.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) { $d.FileNames | ForEach-Object { Write-Output $_ } }
$owner.Close()
"""


def parse_picked(stdout: str) -> list[str]:
    """Rutas que devolvio el selector (una por linea), solo las que son videos."""
    lines = [ln.strip() for ln in stdout.splitlines() if ln.strip()]
    return [ln for ln in lines if Path(ln).suffix.lower() in VIDEO_EXTS]


def api_pickvideos(body: dict) -> dict:
    ps = shutil.which("powershell")
    if not ps:
        raise ApiError("No encontre PowerShell para abrir el selector de archivos.")
    start = out_base()
    log.info("abriendo selector multiple de videos, inicio en %s", start)
    r = subprocess.run([ps, "-NoProfile", "-STA", "-Command", PICK_VIDEOS_SCRIPT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=600, creationflags=NOWIN,
                       env={**os.environ, "TARRODL_START": str(start)})
    files = parse_picked(r.stdout)
    if not files:
        log.info("selector multiple cancelado o sin videos (stderr=%s)", r.stderr.strip()[-300:])
        return {"cancelled": True}
    log.info("videos elegidos para el mosaico: %s", files)
    return {"files": files}


def api_clientlog(body: dict) -> dict:
    log.warning("front: %s", str(body.get("msg") or "")[:800])
    return {}


def api_openlog(_body=None) -> dict:
    if not LOG_FILE.exists():
        raise ApiError("Todavia no hay log.")
    subprocess.Popen(["explorer", f"/select,{LOG_FILE}"])
    return {"path": str(LOG_FILE)}


def api_open(body: dict) -> dict:
    path = Path(str(body.get("path") or "").strip())
    if path.is_dir():
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif path.is_file():
        subprocess.Popen(["explorer", f"/select,{path}"])
    else:
        raise ApiError("Esa ruta ya no existe.")
    return {}


def api_ping(_body=None) -> dict:
    STATE.update(last_ping=time.time(), bye_at=None, seen=True)
    return {}


def api_bye(_body=None) -> dict:
    STATE["bye_at"] = time.time() + 8
    return {}


ROUTES = {
    ("GET", "status"): api_status, ("POST", "analyze"): api_analyze, ("POST", "download"): api_download,
    ("POST", "clips"): api_clips, ("POST", "plan"): api_plan, ("POST", "cancel"): api_cancel, ("POST", "queue_move"): api_queue_move, ("POST", "settings"): api_settings, ("POST", "update"): api_update, ("POST", "install"): api_install,
    ("POST", "pickfolder"): api_pickfolder, ("POST", "pickvideo"): api_pickvideo, ("POST", "pickvideos"): api_pickvideos, ("POST", "probe"): api_probe,
    ("POST", "mosaic_plan"): api_mosaic_plan, ("POST", "mosaic"): api_mosaic, ("GET", "session_files"): api_session_files, ("GET", "partials"): api_partials, ("POST", "partials_delete"): api_partials_delete, ("POST", "open_links"): api_open_links, ("POST", "open"): api_open,
    ("POST", "clientlog"): api_clientlog, ("POST", "openlog"): api_openlog, ("POST", "ping"): api_ping,
    ("POST", "bye"): api_bye,
}


# ---------- servidor ----------

class Handler(BaseHTTPRequestHandler):
    server_version = APP

    def log_message(self, *args):
        pass

    def _send(self, code: int, payload: bytes, ctype: str = "application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, code: int, data: dict):
        self._send(code, json.dumps(data, default=str).encode("utf-8"))

    def _host_ok(self) -> bool:
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def do_GET(self):
        if not self._host_ok():
            return self._json(403, {"error": "host no permitido"})
        url = urlparse(self.path)
        icons = {"/favicon.ico": "image/x-icon", "/favicon.svg": "image/svg+xml", "/favicon-256.png": "image/png"}
        if url.path in icons:
            icon = RES / "ui" / url.path.lstrip("/")
            return self._send(200, icon.read_bytes(), icons[url.path]) if icon.is_file() else self._send(204, b"", icons[url.path])
        if url.path in ("/", "/index.html"):
            html = (RES / "ui" / "index.html").read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
        if url.path == "/api/jobs":
            if self.headers.get("X-Token") != TOKEN:
                return self._json(403, {"error": "token invalido"})
            ids = [i for i in (parse_qs(url.query).get("ids") or [""])[0].split(",") if i]
            return self._json(200, {i: view_job(JOBS[i]) for i in ids if i in JOBS})
        if url.path == "/api/job":
            if self.headers.get("X-Token") != TOKEN:
                return self._json(403, {"error": "token invalido"})
            job = JOBS.get((parse_qs(url.query).get("id") or [""])[0])
            return self._json(200, view_job(job)) if job else self._json(404, {"error": "job desconocido"})
        self._dispatch("GET", url.path)

    def do_POST(self):
        self._dispatch("POST", urlparse(self.path).path)

    def _dispatch(self, method: str, path: str):
        route = path.removeprefix("/api/")
        if not self._host_ok() or self.headers.get("X-Token") != TOKEN:
            log.warning("403 %s %s host=%s", method, path, self.headers.get("Host"))
            return self._json(403, {"error": "acceso denegado"})
        fn = ROUTES.get((method, route))
        if not fn:
            log.warning("404 %s %s", method, path)
            return self._json(404, {"error": "ruta desconocida"})
        t0, body = time.time(), {}
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}") if method == "POST" else {}
            code, result = 200, fn(body)
        except ApiError as e:
            code, result = 400, {"error": str(e)}
        except Exception as e:  # noqa: BLE001
            log.exception("500 %s /%s body=%s", method, route, body)
            code, result = 500, {"error": f"Error interno: {e}"}
        if route not in QUIET_ROUTES:
            level = logging.INFO if code == 200 else logging.WARNING
            log.log(level, "%s /%s -> %s (%d ms) body=%s%s", method, route, code, (time.time() - t0) * 1000,
                    json.dumps(body, ensure_ascii=False)[:300], f" error={result['error']}" if code != 200 else "")
        self._json(code, result)


def find_browser() -> str | None:
    for p in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if Path(p).exists():
            return p
    return None


def main() -> None:
    global PORT
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--port", type=int, default=0)
    args = ap.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    PORT = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{PORT}/"
    browser = None if args.no_browser else find_browser()
    log.info("=== %s %s inicia | frozen=%s python=%s | puerto=%s | salida=%s | yt-dlp=%s | ffmpeg=%s | navegador=%s",
             APP, VERSION, getattr(sys, "frozen", False), sys.version.split()[0], PORT, out_base(),
             find_tool("yt-dlp"), find_tool("ffmpeg"), browser or ("ninguno" if args.no_browser else "webbrowser"))

    apply_settings()
    links_recent()  # al abrir TarroDL se borran los links con mas de 48 h
    threading.Thread(target=startup_check, daemon=True).start()

    if not args.no_browser:
        if browser:
            subprocess.Popen([browser, f"--app={url}", "--window-size=1120,900",
                              f"--user-data-dir={CONFIG_DIR / 'browser'}", "--no-first-run",
                              "--no-default-browser-check"])
        else:
            webbrowser.open(url)

    while True:
        time.sleep(2)
        if running_jobs():
            continue
        now = time.time()
        if STATE["bye_at"] and now > STATE["bye_at"]:
            log.info("cierre: se cerro la ventana")
            break
        if now - STATE["last_ping"] > (150 if STATE["seen"] else 90):
            log.info("cierre: sin senal de la ventana (%s)", "timeout" if STATE["seen"] else "nunca se conecto")
            break


if __name__ == "__main__":
    setup_logging()
    try:
        main()
    except Exception:
        log.exception("la app se cayo")
        raise
