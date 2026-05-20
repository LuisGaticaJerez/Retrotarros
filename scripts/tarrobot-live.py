"""
tarrobot-live.py
Servidor en vivo de TarroBot para uso durante grabacion del canal.

Arquitectura:
  Browser source OBS  ──> http://localhost:8765/?mode=overlay
  TV CRT fisica       ──> http://localhost:8765/?mode=fullscreen
  Panel celular       ──> http://<ip-local>:8765/control
  WebSocket bidir     ──> /ws

Endpoints REST:
  POST /api/state    { "estado": "talking" }
  POST /api/cuentame { "tema": "Super Mario 64", "voz": "catalina" }
  POST /api/estado   { "estado": "fact" }   alias de /api/state

Uso:
  python scripts/tarrobot-live.py
  → abre http://localhost:8765 en OBS Browser Source
  → desde el celu, http://<tu-ip-local>:8765/control

Requiere:
  pip install fastapi uvicorn[standard] edge-tts anthropic
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Reutilizar logica del CLI tarrobot.py
sys.path.insert(0, str(Path(__file__).parent))
from tarrobot import (
    cargar_db, buscar, agregar_dato, generar_con_llm,
    generar_tts, resolver_voz,
    LABEL_POR_ESTADO, ESTADOS, VOZ_DEFAULT, PITCH_DEFAULT, RATE_DEFAULT,
    OUT_DIR,
)

REPO = Path(__file__).parent.parent
STUDIO = REPO / "studio"
LIVE_HTML = STUDIO / "_template-tarrobot-live.html"
CONTROL_HTML = STUDIO / "_template-tarrobot-control.html"

app = FastAPI(title="TarroBot Live")

# Servir los MP3 generados (en /audio/<id>.mp3)
app.mount("/audio", StaticFiles(directory=str(OUT_DIR)), name="audio")


# ─────────────────────────────────────────────────────────────────────────
# Manager de conexiones WebSocket
# ─────────────────────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.live_clients: list[WebSocket] = []   # las pantallas TarroBot (OBS, TV)
        self.control_clients: list[WebSocket] = []  # el celu / panel

    async def connect_live(self, ws: WebSocket):
        await ws.accept()
        self.live_clients.append(ws)

    async def connect_control(self, ws: WebSocket):
        await ws.accept()
        self.control_clients.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.live_clients:
            self.live_clients.remove(ws)
        if ws in self.control_clients:
            self.control_clients.remove(ws)

    async def broadcast_live(self, message: dict):
        """Envia evento a todas las pantallas TarroBot."""
        text = json.dumps(message)
        dead = []
        for ws in self.live_clients:
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()


# ─────────────────────────────────────────────────────────────────────────
# HTML routes
# ─────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_live():
    if not LIVE_HTML.exists():
        return HTMLResponse(
            "<h1>TarroBot Live</h1><p>Falta crear <code>studio/_template-tarrobot-live.html</code></p>",
            status_code=500,
        )
    return HTMLResponse(LIVE_HTML.read_text(encoding="utf-8"))


@app.get("/control", response_class=HTMLResponse)
async def serve_control():
    if not CONTROL_HTML.exists():
        return HTMLResponse(
            "<h1>Panel TarroBot</h1><p>Falta crear <code>studio/_template-tarrobot-control.html</code></p>",
            status_code=500,
        )
    return HTMLResponse(CONTROL_HTML.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────
# WebSocket
# ─────────────────────────────────────────────────────────────────────────

@app.websocket("/ws/live")
async def ws_live(websocket: WebSocket):
    await manager.connect_live(websocket)
    try:
        # Enviar estado inicial al conectar
        await websocket.send_text(json.dumps({"tipo": "estado", "estado": "idle"}))
        while True:
            # Solo necesitamos enviar; mantener conexion viva
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ─────────────────────────────────────────────────────────────────────────
# API REST
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/state")
async def set_state(payload: dict):
    """
    Cambia solo el estado visual de TarroBot.
    Body: { "estado": "idle|talking|excited|sleep|thinking|winking|confused|glitched|fact|happy|sad|angry|loading|bored|drowsy" }
    """
    estado = payload.get("estado", "idle")
    if estado not in ESTADOS + ["bored", "drowsy"]:
        return JSONResponse({"error": f"Estado invalido. Validos: {ESTADOS + ['bored', 'drowsy']}"}, status_code=400)

    await manager.broadcast_live({"tipo": "estado", "estado": estado})
    return {"ok": True, "estado": estado}


@app.post("/api/cuentame")
async def cuentame(payload: dict):
    """
    Cuenta un dato curioso sobre un tema.
    Body: { "tema": "Super Mario 64", "voz": "catalina" (opcional), "generate_if_missing": false }

    1. Busca en DB local
    2. Si no hay y generate_if_missing=true → llama Claude
    3. Genera MP3 con Edge TTS
    4. Envia WS al live: { tipo: 'hablar', estado, texto, audio_url }
    """
    tema = (payload.get("tema") or "").strip()
    if not tema:
        return JSONResponse({"error": "tema vacio"}, status_code=400)

    voz = resolver_voz(payload.get("voz") or "catalina")
    generate_if_missing = bool(payload.get("generate_if_missing", False))

    db = cargar_db()
    matches = buscar(tema, db)
    dato = None

    if matches:
        # Si hay varios matches, elige aleatorio
        import random
        dato = random.choice(matches)
    elif generate_if_missing:
        result = generar_con_llm(tema)
        if result and result.get("datos"):
            primera = result["datos"][0]
            dato = agregar_dato(
                tema, primera["texto"],
                primera.get("estado_recomendado", "talking"),
                db,
                consola=result.get("consola", ""),
                ano=int(result.get("ano", 0) or 0),
                editor=result.get("editor", ""),
                fuente="LLM-live",
            )

    if not dato:
        return JSONResponse({"error": f"sin dato para '{tema}' (usa generate_if_missing=true para llamar Claude)"}, status_code=404)

    # Generar MP3 en thread (generar_tts usa asyncio.run interno que rompe el loop)
    mp3 = await asyncio.to_thread(generar_tts, dato, voz)
    audio_url = f"/audio/{mp3.name}" if mp3 else None

    # Disparar evento al live
    await manager.broadcast_live({
        "tipo": "hablar",
        "estado": dato["estado"],
        "texto": dato["texto"],
        "label": LABEL_POR_ESTADO.get(dato["estado"], "DATO CURIOSO"),
        "meta": " · ".join(s for s in [dato.get("consola", ""), str(dato.get("ano", "") or ""), dato.get("editor", "")] if s and s != "0"),
        "audio_url": audio_url,
        "tema": dato["tema"],
    })

    return {"ok": True, "dato": dato, "audio_url": audio_url}


@app.get("/api/ping")
async def ping():
    return {"ok": True, "live_clients": len(manager.live_clients)}


# ─────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────

def get_local_ip():
    """Obtiene la IP local para que el celu pueda conectarse."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    ip = get_local_ip()
    PORT = 8765
    print("=" * 60)
    print(f"  TarroBot Live · server corriendo")
    print("=" * 60)
    print(f"")
    print(f"  OBS Browser Source (overlay transparente):")
    print(f"    http://localhost:{PORT}/?mode=overlay")
    print(f"")
    print(f"  TV CRT fisica (fondo opaco):")
    print(f"    http://localhost:{PORT}/?mode=fullscreen")
    print(f"")
    print(f"  Panel control (desde el celu en mismo WiFi):")
    print(f"    http://{ip}:{PORT}/control")
    print(f"")
    print(f"  Ping de salud:")
    print(f"    http://localhost:{PORT}/api/ping")
    print(f"")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
