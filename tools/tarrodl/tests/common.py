"""Utilidades compartidas de las pruebas de TarroDL (se corren desde tools/tarrodl)."""
import json
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tarrodl  # noqa: E402


def isolate(tmp) -> None:
    """Apunta config, log y carpetas de TarroDL a un temporal para no tocar los del usuario."""
    tmp = Path(tmp)
    tarrodl.CONFIG_DIR = tmp / "cfg"
    tarrodl.CONFIG_FILE = tarrodl.CONFIG_DIR / "config.json"
    tarrodl.LOG_FILE = tarrodl.CONFIG_DIR / "t.log"
    tarrodl.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (tmp / "dl").mkdir(parents=True, exist_ok=True)
    tarrodl.out_base = lambda: tmp / "dl"
    tarrodl.clips_base = lambda: tmp / "clips"
    for h in list(tarrodl.log.handlers):
        h.close()
        tarrodl.log.removeHandler(h)
    tarrodl.setup_logging()


def make_video(path, seconds, size="160x120", fps=30, audio=True) -> Path:
    """Video sintetico (testsrc2 + tono) con ffmpeg lavfi."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [tarrodl.find_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "lavfi", "-i", f"testsrc2=size={size}:rate={fps}:duration={seconds}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"] + (["-c:a", "aac"] if audio else []) + [str(path)]
    r = subprocess.run(cmd, capture_output=True, text=True, creationflags=tarrodl.NOWIN)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])
    return path


def make_audio_only(path, seconds) -> Path:
    """Archivo .mp4 sin pista de video (solo tono): lo que dejaria una pista suelta de yt-dlp."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([tarrodl.find_tool("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                        f"sine=frequency=440:duration={seconds}", "-c:a", "aac", str(path)], capture_output=True, text=True, creationflags=tarrodl.NOWIN)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])
    return path


def start_server():
    """Servidor HTTP real en un puerto libre. Devuelve (server, call); call(path, body=None) -> (status, json)."""
    srv = ThreadingHTTPServer(("127.0.0.1", 0), tarrodl.Handler)
    tarrodl.PORT = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def call(path, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{tarrodl.PORT}{path}", data=None if body is None else json.dumps(body).encode(),
                                     method="GET" if body is None else "POST")
        req.add_header("X-Token", tarrodl.TOKEN)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            data = e.read()
            e.close()
            return e.code, json.loads(data or b"{}")
    return srv, call
