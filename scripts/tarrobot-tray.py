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

IMPORTANTE (anti-fallo-silencioso):
  Bajo pythonw.exe no hay consola, asi que stdout/stderr se pierden. Si el
  arranque falla (dependencia faltante, puerto ocupado, error al importar
  tarrobot-live), el proceso moriria SIN dejar rastro y sin avisar a nadie.
  Por eso este script:
    1. Redirige stdout/stderr a logs/tarrobot-tray.log
    2. Captura cualquier crash de arranque y lo escribe al log
    3. Muestra un MessageBox de Windows para que el fallo sea VISIBLE
    4. Chequea el puerto antes de arrancar (8765 ocupado = causa comun)

Requiere:
  pip install pystray pillow
"""

import os
import sys
import socket
import datetime
import threading
import traceback
import webbrowser
import importlib.util
from pathlib import Path

_HERE = Path(__file__).parent

# ============================================================
#  Infraestructura anti-fallo-silencioso (debe ir ANTES de todo
#  import que pueda fallar, como uvicorn o tarrobot-live).
# ============================================================
_LOG_DIR = _HERE.parent / "logs"
try:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    _LOG_PATH = _LOG_DIR / "tarrobot-tray.log"
except Exception:
    _LOG_PATH = _HERE / "tarrobot-tray.log"


def _log(msg):
    """Escribe una linea al log con timestamp. Nunca lanza."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[{}] {}".format(ts, msg)
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    try:
        print(line)
    except Exception:
        pass


def _redirect_streams_to_log():
    """Bajo pythonw, sys.stdout/stderr son None: los mandamos al log."""
    try:
        f = open(_LOG_PATH, "a", encoding="utf-8", buffering=1)
        sys.stdout = f
        sys.stderr = f
    except Exception:
        pass


# pythonw.exe deja stdout/stderr en None -> redirigir para capturar tracebacks
if sys.stdout is None or sys.stderr is None:
    _redirect_streams_to_log()


def _show_error_box(title, text):
    """MessageBox de Windows para que un fallo de arranque sea visible.
    No depende de tener consola. Si falla (no-Windows), no pasa nada."""
    try:
        import ctypes
        # 0x10 = MB_ICONERROR
        ctypes.windll.user32.MessageBoxW(0, str(text)[:1500], str(title), 0x10)
    except Exception:
        pass


def _fatal(titulo, exc):
    """Loguea el traceback completo, avisa al usuario y termina."""
    tb = traceback.format_exc()
    _log("FATAL: {}\n{}".format(titulo, tb))
    msg = (
        "{}\n\n"
        "Detalle: {}\n\n"
        "Log completo en:\n{}".format(titulo, exc, _LOG_PATH)
    )
    _show_error_box("TarroBot - error al arrancar", msg)
    sys.exit(1)


def _port_in_use(port):
    """True si algo ya esta escuchando en 127.0.0.1:port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        return s.connect_ex(("127.0.0.1", int(port))) == 0
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


# ============================================================
#  Imports que pueden fallar (uvicorn, tarrobot-live) - guardados
# ============================================================
_log("=== TarroBot tray: arranque ===")

try:
    import uvicorn
except Exception as e:
    _fatal("No se pudo importar uvicorn. Reinstala las dependencias "
           "(corre install.bat de nuevo).", e)

# Importar tarrobot-live como modulo (tiene guion en el nombre, no se puede
# hacer "from tarrobot-live import ...", usamos importlib)
_LIVE_PY = _HERE / "tarrobot-live.py"
try:
    if not _LIVE_PY.exists():
        raise FileNotFoundError("No existe {}".format(_LIVE_PY))
    spec = importlib.util.spec_from_file_location("tarrobot_live", _LIVE_PY)
    tl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tl)
except Exception as e:
    _fatal("Fallo al cargar tarrobot-live.py. Puede faltar una dependencia "
           "o haber un error en los datos/pautas.", e)

try:
    app = tl.app
    PORT = tl.PORT
    get_local_ip = tl.get_local_ip
except Exception as e:
    _fatal("tarrobot-live.py se cargo pero le faltan app/PORT/get_local_ip.", e)


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
            _log("[tray] no pude abrir {}: {}".format(url, e))
    return _abrir


def salir(icon, item):
    """Detiene el tray y termina el proceso entero."""
    _log("[tray] salir solicitado por el usuario")
    icon.stop()
    # Forzar exit porque uvicorn no responde a SIGINT en algunos casos
    os._exit(0)


def main():
    import pystray

    ip = get_local_ip()

    # 0. Chequeo previo: si el puerto ya esta ocupado, otra instancia de
    #    TarroBot (u otro programa) lo tiene. Arrancar uvicorn fallaria en
    #    silencio dentro del thread y el icono apareceria "vivo" pero muerto.
    if _port_in_use(PORT):
        _log("Puerto {} ya esta en uso.".format(PORT))
        _show_error_box(
            "TarroBot ya esta corriendo",
            "El puerto {} ya esta ocupado.\n\n"
            "Probablemente TarroBot ya esta abierto (busca el icono en la "
            "bandeja del sistema, al lado del reloj).\n\n"
            "Si no lo ves, reinicia el PC y vuelve a abrir TarroBot.".format(PORT),
        )
        sys.exit(0)

    # 1. Arrancar uvicorn en thread separado (daemon = muere con el proceso).
    #    Capturamos cualquier fallo del server para que NO sea invisible.
    def run_server():
        try:
            _log("Levantando uvicorn en 0.0.0.0:{}".format(PORT))
            uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
        except Exception as e:
            tb = traceback.format_exc()
            _log("ERROR en el server uvicorn:\n{}".format(tb))
            _show_error_box(
                "TarroBot - el servidor se cayo",
                "El servidor interno fallo al arrancar.\n\n"
                "Detalle: {}\n\nLog: {}".format(e, _LOG_PATH),
            )
            # Matar el proceso entero: sin server, el tray no sirve.
            os._exit(1)

    server_thread = threading.Thread(target=run_server, daemon=True, name="uvicorn-server")
    server_thread.start()

    # 2. Crear el tray icon con menu
    titulo = "TarroBot - {}:{}".format(ip, PORT)
    icono = crear_icono_tarrobot()

    menu = pystray.Menu(
        pystray.MenuItem("Abrir TarroBot (TV)",       abrir_url("http://localhost:{}/?mode=fullscreen".format(PORT)), default=True),
        pystray.MenuItem("Abrir panel control",        abrir_url("http://localhost:{}/control".format(PORT))),
        pystray.MenuItem("Abrir overlay (OBS)",        abrir_url("http://localhost:{}/?mode=overlay".format(PORT))),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("IP local: {}:{}".format(ip, PORT),  None, enabled=False),
        pystray.MenuItem("Panel desde el celu",        abrir_url("http://{}:{}/control".format(ip, PORT))),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Salir TarroBot",             salir),
    )

    icon = pystray.Icon("tarrobot", icono, titulo, menu)
    _log("Tray icon listo. TarroBot operativo en {}:{}".format(ip, PORT))
    icon.run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _fatal("Error inesperado en el tray.", e)
