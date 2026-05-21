"""
tarrobot-tray.py
Wrapper de TarroBot Live que corre como icono de bandeja (tray).

Diferencia con tarrobot-live.py:
  - tarrobot-live.py    -> server con cmd visible (modo debug)
  - tarrobot-tray.py    -> server detras de un tray icon (modo produccion)

Como funciona:
  - Lanza uvicorn en un thread separado (daemon)
  - El main thread corre pystray con icono en la bandeja
  - El menu del tray permite: abrir TV/panel, ver IP, salir
  - Sin ventana cmd visible (se arranca con pythonw.exe desde TarroBot.bat)

Requiere:
  pip install pystray pillow
"""

import os
import sys
import threading
import webbrowser
import importlib.util
from pathlib import Path

import uvicorn

# Importar tarrobot-live como modulo (tiene guion en el nombre, no se puede
# hacer "from tarrobot-live import ...", usamos importlib)
_HERE = Path(__file__).parent
_LIVE_PY = _HERE / "tarrobot-live.py"
spec = importlib.util.spec_from_file_location("tarrobot_live", _LIVE_PY)
tl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tl)

app = tl.app
PORT = tl.PORT
get_local_ip = tl.get_local_ip


def crear_icono_tarrobot():
    """Genera un icono pixel-art tipo TarroBot en una TV CRT (64x64 RGBA)."""
    from PIL import Image, ImageDraw
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Cuerpo TV: marco cyan exterior
    d.rectangle([2, 6, 61, 56], fill=(0, 229, 255))
    # Pantalla interior negra
    d.rectangle([6, 10, 57, 50], fill=(10, 8, 32))
    # Marco interno (efecto CRT)
    d.rectangle([8, 12, 55, 48], outline=(255, 46, 136), width=1)
    # Ojos pixelados amarillos
    d.rectangle([16, 22, 24, 30], fill=(255, 210, 63))
    d.rectangle([38, 22, 46, 30], fill=(255, 210, 63))
    # Pupilas
    d.rectangle([19, 24, 22, 28], fill=(10, 8, 32))
    d.rectangle([41, 24, 44, 28], fill=(10, 8, 32))
    # Boca tipo "talk"
    d.rectangle([22, 38, 42, 42], fill=(255, 210, 63))
    # LED rojo encendido (esquina)
    d.ellipse([4, 4, 8, 8], fill=(255, 46, 136))
    # Patas/base de la TV
    d.rectangle([14, 56, 22, 60], fill=(0, 229, 255))
    d.rectangle([42, 56, 50, 60], fill=(0, 229, 255))
    return img


def abrir_url(url):
    """Wrapper que ignora errores si no hay browser."""
    def _abrir(icon=None, item=None):
        try:
            webbrowser.open(url, new=1)
        except Exception as e:
            print(f"[tray] no pude abrir {url}: {e}")
    return _abrir


def salir(icon, item):
    """Detiene el tray y termina el proceso entero."""
    icon.stop()
    # Forzar exit porque uvicorn no responde a SIGINT en algunos casos
    os._exit(0)


def main():
    import pystray

    ip = get_local_ip()

    # 1. Arrancar uvicorn en thread separado (daemon = muere con el proceso)
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")

    server_thread = threading.Thread(target=run_server, daemon=True, name="uvicorn-server")
    server_thread.start()

    # 2. Crear el tray icon con menu
    titulo = f"TarroBot · {ip}:{PORT}"
    icono = crear_icono_tarrobot()

    menu = pystray.Menu(
        pystray.MenuItem("Abrir TarroBot (TV)",       abrir_url(f"http://localhost:{PORT}/?mode=fullscreen"), default=True),
        pystray.MenuItem("Abrir panel control",        abrir_url(f"http://localhost:{PORT}/control")),
        pystray.MenuItem("Abrir overlay (OBS)",        abrir_url(f"http://localhost:{PORT}/?mode=overlay")),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(f"IP local: {ip}:{PORT}",     None, enabled=False),
        pystray.MenuItem(f"Panel desde el celu",       abrir_url(f"http://{ip}:{PORT}/control")),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir TarroBot",             salir),
    )

    icon = pystray.Icon("tarrobot", icono, titulo, menu)
    icon.run()


if __name__ == "__main__":
    main()
