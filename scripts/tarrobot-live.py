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
import time
from contextlib import asynccontextmanager
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

# Saludos geek random (chileno neutro, sin tildes)
SALUDOS_GEEK = [
    "Hola hola humanos! Insertando moneda virtual.",
    "Bip bop. Sistema TarroBot iniciado correctamente.",
    "Saludos, gamers. Cargando datos curiosos...",
    "Buenos pixels, equipo!",
    "Press start. Aqui estoy.",
    "Listo para soltar trivia. ¿Que se cuenta hoy?",
    "Hola Luis, hola Koko. TarroBot a la orden.",
    "Conectado y listo. Que empiece la sesion.",
    "Wii hoo! TarroBot en linea.",
    "Buenas, retrotarristas. Datos curiosos en 3, 2, 1...",
    "Reportandome al estudio. ¿Que vamos a investigar?",
    "Frecuencia 42 megahertz. TarroBot transmitiendo.",
    "Insertando token. Hola, hola!",
    "Memoria llena, sed de datos. Pregunta lo que quieras.",
    "Sistema operativo: Curiosidad version 8 bits. Listo.",
]

# Despedidas cortas random
DESPEDIDAS_CORTAS = [
    "Chao chao. Apagando luces de la TV.",
    "Hasta la proxima, retrotarristas!",
    "Modo sleep activado. Hasta luego!",
    "Bip. Bop. Power off.",
    "Nos vemos en el proximo episodio.",
    "Salvo partida. Hasta pronto!",
    "Game over para hoy. Chao!",
    "Continue en el proximo capitulo. Chao!",
    "Apagando consola. Hasta la proxima!",
    "Eyectando cartucho. Nos vemos!",
]

# ─────────────────────────────────────────────────────────────────────────
# Idle tracker — TarroBot se aburre y se duerme solo
# ─────────────────────────────────────────────────────────────────────────

class ActivityTracker:
    """Lleva cuenta del tiempo desde el ultimo input del usuario."""
    def __init__(self):
        self.last_input_ts: float = time.time()
        self.current_idle_state: str = "idle"
        self.is_speaking: bool = False  # True mientras hay audio reproduciendose

    def mark_input(self):
        self.last_input_ts = time.time()
        self.current_idle_state = "idle"

    def mark_speaking(self, val: bool):
        self.is_speaking = val
        if val:
            self.mark_input()  # hablar tambien reinicia el timer

    def get_idle_state(self) -> str:
        elapsed = time.time() - self.last_input_ts
        if elapsed < IDLE_BORED_AFTER:
            return "idle"
        if elapsed < IDLE_DROWSY_AFTER:
            return "bored"
        if elapsed < IDLE_SLEEP_AFTER:
            return "drowsy"
        return "sleep"


# Thresholds en segundos (configurables aca)
IDLE_BORED_AFTER = 30    # 30s sin input → bored
IDLE_DROWSY_AFTER = 60   # 60s sin input → drowsy
IDLE_SLEEP_AFTER = 120   # 120s sin input → sleep

tracker = ActivityTracker()


async def idle_worker():
    """
    Background task: cada 5s revisa el tiempo desde el ultimo input.
    Si toca cambiar de estado idle y nadie esta hablando, dispara WS.
    """
    while True:
        await asyncio.sleep(5)
        if tracker.is_speaking:
            continue  # no interrumpir mientras habla
        new_state = tracker.get_idle_state()
        if new_state != tracker.current_idle_state:
            tracker.current_idle_state = new_state
            try:
                await manager.broadcast_live({"tipo": "estado-idle", "estado": new_state})
            except Exception as e:
                print(f"[idle_worker] error broadcast: {e}")


@asynccontextmanager
async def lifespan(app):
    # Startup: lanzar el worker
    task = asyncio.create_task(idle_worker())
    yield
    # Shutdown: cancelar
    task.cancel()


app = FastAPI(title="TarroBot Live", lifespan=lifespan)

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

    tracker.mark_input()  # reset idle timer
    tracker.current_idle_state = estado
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

    tracker.mark_speaking(True)
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


async def _hablar_frase(texto: str, estado: str, label: str, voz: str) -> Optional[str]:
    """
    Genera TTS de una frase suelta (sin tema asociado) y dispara WS.
    Usado por /api/saludar y /api/despedir.
    Retorna la URL del audio o None si fallo.
    """
    import time
    fake_dato = {
        "id": f"frase-{int(time.time() * 1000)}",
        "tema": "frase",
        "texto": texto,
        "estado": estado,
        "consola": "", "ano": 0, "editor": "",
    }
    mp3 = await asyncio.to_thread(generar_tts, fake_dato, voz)
    audio_url = f"/audio/{mp3.name}" if mp3 else None

    tracker.mark_speaking(True)
    await manager.broadcast_live({
        "tipo": "hablar",
        "estado": estado,
        "texto": texto,
        "label": label,
        "meta": "",
        "audio_url": audio_url,
        "tema": "",
    })
    return audio_url


def generar_opinion_llm(tema: str) -> Optional[dict]:
    """Llama Claude para que TarroBot opine de un tema. Retorna {texto, estado}."""
    try:
        import anthropic
    except ImportError:
        return None
    import os
    import re as _re
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Eres TarroBot, mascota del canal de YouTube Retrotarros sobre videojuegos retro.
Tu humano te pregunta: "¿Que opinas de {tema}?"

Devuelve una OPINION corta y con personalidad (1-2 oraciones, max 200 caracteres total).
Tambien decide el estado emocional que mejor calza.

Reglas:
- Español chileno neutro con TUTEO (tu/tienes/sabes). NO uses voseo argentino.
- SIN tildes (a/e/i/o/u sin acento).
- Tono curioso, opinion clara, vibe retrogaming.
- Estados validos: happy, excited, fact, winking, confused, sad, angry, thinking, talking.
  * Bueno → happy o excited
  * Malo → sad, angry o confused
  * Raro/curioso → confused o thinking
  * Iconico → fact o excited

Devuelve SOLO un JSON valido (sin markdown), formato:
{{"texto": "...", "estado": "..."}}
"""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        print(f"[opinar] error: {e}")
        return None


@app.post("/api/opinar")
async def opinar(payload: dict):
    """
    Claude opina sobre un tema con tono y estado emocional sugerido.
    Body: { "tema": "Sonic 06", "voz": "catalina" }
    """
    import random as _rnd
    tema = (payload.get("tema") or "").strip()
    if not tema:
        return JSONResponse({"error": "tema vacio"}, status_code=400)

    voz = resolver_voz(payload.get("voz") or "catalina")
    tracker.mark_input()

    result = await asyncio.to_thread(generar_opinion_llm, tema)
    if not result:
        return JSONResponse({"error": "fallo Claude API. Verifica ANTHROPIC_API_KEY y creditos."}, status_code=500)

    texto = result.get("texto", f"No tengo opinion sobre {tema} todavia.")
    estado = result.get("estado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    audio_url = await _hablar_frase(texto, estado, f"¿QUE OPINO DE {tema.upper()}?", voz)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url, "tema": tema}


@app.post("/api/precio")
async def precio(payload: dict):
    """
    Reacciona segun valor USD. No usa LLM, son frases pregeneradas.
    Body: { "valor_usd": 4500, "juego": "DKC Competition Cart" (opcional), "voz": ... }
    """
    try:
        valor = int(payload.get("valor_usd", 0))
    except (TypeError, ValueError):
        return JSONResponse({"error": "valor_usd invalido"}, status_code=400)

    juego = (payload.get("juego") or "").strip()
    voz = resolver_voz(payload.get("voz") or "catalina")
    tracker.mark_input()

    # Reaccion segun rango
    if valor >= 20000:
        estado = "confused"
        texto = f"USD {valor:,}? Eso ya no es coleccionismo, es un museo. Imposible de pagar."
    elif valor >= 10000:
        estado = "excited"
        texto = f"USD {valor:,}! Eso es plata para un auto. Locura total."
    elif valor >= 5000:
        estado = "excited"
        texto = f"USD {valor:,} es una locura. Mind blown total!"
    elif valor >= 2000:
        estado = "fact"
        texto = f"USD {valor:,} ya es para coleccionistas serios. Cartucho serio."
    elif valor >= 500:
        estado = "thinking"
        texto = f"USD {valor:,} esta caro pero no es escandaloso. Razonable para piezas raras."
    elif valor >= 100:
        estado = "talking"
        texto = f"USD {valor:,} es precio normal para retrogaming en buen estado."
    elif valor > 0:
        estado = "happy"
        texto = f"USD {valor:,}? Eso es chollo, comprate dos!"
    else:
        estado = "confused"
        texto = "Sin precio no puedo opinar. Decime cuanto sale."

    if juego:
        texto = f"{juego} a USD {valor:,}? " + texto

    audio_url = await _hablar_frase(texto, estado, "REACCION PRECIO", voz)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/random")
async def random_dato(payload: dict):
    """
    Elige un dato random de la base local, filtrado opcionalmente por categoria.
    Body: { "categoria": "all|consola|juego|musica|nfr", "voz": ... }
    """
    import random as _rnd
    categoria = (payload.get("categoria") or "all").lower()
    voz = resolver_voz(payload.get("voz") or "catalina")
    tracker.mark_input()

    db = cargar_db()
    if not db.get("datos"):
        return JSONResponse({"error": "DB vacia"}, status_code=404)

    # Filtrado por categoria (heuristica por consola)
    candidatos = db["datos"]
    if categoria == "consola":
        candidatos = [d for d in db["datos"] if d.get("consola", "").lower() in ("nes", "snes", "n64", "genesis", "dreamcast", "arcade")]
    elif categoria == "juego":
        # juegos especificos (no compositores ni "multi")
        candidatos = [d for d in db["datos"] if d.get("consola", "").lower() not in ("", "multi")]
    elif categoria == "musica":
        # heuristica simple: textos que mencionan "banda sonora", "compositor", "musica"
        kw = ["banda sonora", "compositor", "musica", "soundtrack", "sound"]
        candidatos = [d for d in db["datos"] if any(k in d.get("texto", "").lower() for k in kw)]

    if not candidatos:
        candidatos = db["datos"]  # fallback

    dato = _rnd.choice(candidatos)

    mp3 = await asyncio.to_thread(generar_tts, dato, voz)
    audio_url = f"/audio/{mp3.name}" if mp3 else None

    tracker.mark_speaking(True)
    await manager.broadcast_live({
        "tipo": "hablar",
        "estado": dato["estado"],
        "texto": dato["texto"],
        "label": f"DATO RANDOM · {categoria.upper()}",
        "meta": " · ".join(s for s in [dato.get("consola", ""), str(dato.get("ano", "") or ""), dato.get("editor", "")] if s and s != "0"),
        "audio_url": audio_url,
        "tema": dato["tema"],
    })

    return {"ok": True, "dato": dato, "audio_url": audio_url}


@app.post("/api/saludar")
async def saludar(payload: dict):
    """Reproduce un saludo geek random con estado excited."""
    import random
    voz = resolver_voz(payload.get("voz") or "catalina")
    tracker.mark_input()
    texto = random.choice(SALUDOS_GEEK)
    audio_url = await _hablar_frase(texto, "excited", "HOLA HOLA", voz)
    return {"ok": True, "texto": texto, "audio_url": audio_url}


@app.post("/api/despedir")
async def despedir(payload: dict):
    """Reproduce una despedida corta random con estado winking."""
    import random
    voz = resolver_voz(payload.get("voz") or "catalina")
    tracker.mark_input()
    texto = random.choice(DESPEDIDAS_CORTAS)
    audio_url = await _hablar_frase(texto, "winking", "HASTA LUEGO", voz)
    return {"ok": True, "texto": texto, "audio_url": audio_url}


@app.post("/api/audio-finished")
async def audio_finished():
    """El cliente HTML llama esto cuando termina de reproducir un MP3."""
    tracker.mark_speaking(False)
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────
# STT (Speech-to-Text con Whisper) + Intent parsing
# ─────────────────────────────────────────────────────────────────────────

_whisper_model = None
WHISPER_MODEL_SIZE = "small"  # base es rapido pero impreciso. small da +90% accuracy en es.

# Prompt de contexto: le dice a Whisper que esperamos vocabulario retrogaming.
# Esto mejora notablemente reconocimiento de nombres propios y "TarroBot".
WHISPER_PROMPT = (
    "El usuario habla con TarroBot, asistente del canal Retrotarros sobre videojuegos retro. "
    "Puede mencionar: Mario, Zelda, Sonic, Donkey Kong, EarthBound, Final Fantasy, Chrono Trigger, "
    "Metroid, Pokemon, Nintendo, Sega, SNES, NES, N64, Genesis, Atari, arcade, cartucho, consola, "
    "GoldenEye, Banjo, Kazooie, Yoshi, Star Fox, Mario Kart, Smash Bros, Paper Mario, "
    "Majora's Mask, Ocarina of Time, JAWS, Castlevania, Mega Man, Killer Instinct, "
    "Doom, Wolfenstein, Tetris, Pac-Man, Pong, Frogger, Q*bert, Dig Dug, BurgerTime, Karnov, "
    "Tapper, Lakitu, Bowser, Link, Samus, Solid Snake, Crash Bandicoot, Spyro. "
    "El usuario habla en español chileno y le hace preguntas tipo: "
    "Hola TarroBot. Chao TarroBot. Cuentame de Super Mario 64. "
    "Que opinas de Sonic 06. Este vale 5000 dolares. Dame un dato random."
)


def get_whisper():
    """Lazy load del modelo Whisper. Primera llamada toma ~5-10s con small."""
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print(f"[STT] cargando modelo Whisper '{WHISPER_MODEL_SIZE}'... (~5-10s primera vez)")
        _whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
        print(f"[STT] modelo Whisper '{WHISPER_MODEL_SIZE}' listo")
    return _whisper_model


def transcribir_audio_sync(audio_bytes: bytes) -> str:
    """Transcribe audio bytes a texto con Whisper + initial_prompt de contexto."""
    import tempfile
    import os as _os

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        model = get_whisper()
        result = model.transcribe(
            tmp_path,
            language="es",
            fp16=False,
            temperature=0.0,                # mas determinista, menos alucina
            initial_prompt=WHISPER_PROMPT,  # contexto de vocabulario retrogaming
            condition_on_previous_text=False,  # no se "atora" con audio anterior
            no_speech_threshold=0.4,        # mas tolerante a silencios al final
        )
        texto = result.get("text", "").strip()
        print(f"[STT] transcripcion: '{texto}'")
        return texto
    finally:
        try:
            _os.unlink(tmp_path)
        except Exception:
            pass


def parsear_intent(texto: str) -> dict:
    """
    Heuristica: detecta accion desde texto transcrito y extrae parametros.
    Devuelve {"accion": str, "params": dict}.
    """
    import re as _re
    t = texto.lower().strip()
    # quitar signos
    t_clean = _re.sub(r"[¿¡\?\!\.\,]", " ", t).strip()

    # 1. Despedida (chequear primero para no confundir con "chao" en medio de frase)
    for kw in ["chao", "adios", "adiós", "bye", "hasta luego", "nos vemos"]:
        if kw in t_clean:
            return {"accion": "despedir", "params": {}}

    # 2. Opinar (antes que saludar porque "opinas" puede contener "h" como "hola")
    if any(x in t_clean for x in ["que opinas", "opinas", "que piensas", "te parece", "tu opinion"]):
        # Extraer tema despues de "de" o "sobre" o "del"
        m = _re.search(r"(?:de|sobre|del|de la|del?)\s+(.+?)$", t_clean)
        if m:
            tema = m.group(1).strip()
            return {"accion": "opinar", "params": {"tema": tema}}
        return {"accion": "opinar", "params": {"tema": texto.strip()}}

    # 3. Precio
    if any(x in t_clean for x in ["precio", "vale", "cuanto cuesta", "dolares", "dólares", "usd"]):
        # Extraer numero
        m = _re.search(r"(\d[\d\.,]*)\s*(mil|k)?", t_clean)
        if m:
            num_str = m.group(1).replace(",", "").replace(".", "")
            try:
                valor = int(num_str)
                # Si dice "mil" o "k" multiplicar por 1000
                if m.group(2) and m.group(2) in ("mil", "k"):
                    valor *= 1000
                return {"accion": "precio", "params": {"valor_usd": valor}}
            except ValueError:
                pass

    # 4. Random
    if any(x in t_clean for x in ["random", "azar", "cualquier", "sorprendeme", "sorpréndeme"]):
        # Sub-categoria
        if "consola" in t_clean: cat = "consola"
        elif "musica" in t_clean or "música" in t_clean: cat = "musica"
        elif "juego" in t_clean: cat = "juego"
        else: cat = "all"
        return {"accion": "random", "params": {"categoria": cat}}

    # 5. Saludo
    if any(t_clean.startswith(kw) for kw in ["hola", "hello", "buenas", "que tal", "qué tal"]):
        return {"accion": "saludar", "params": {}}

    # 6. Cuentame de X
    m = _re.search(r"(?:cuentame|cuéntame|cuenta|cuentanos|cuéntanos|habla|hablame|háblame|dime|que sabes|qué sabes)\s+(?:de\s+|sobre\s+|acerca de\s+)?(.+?)$", t_clean)
    if m:
        tema = m.group(1).strip()
        if tema:
            return {"accion": "cuentame", "params": {"tema": tema, "generate_if_missing": True}}

    # Fallback: tratar todo como tema de cuentame
    return {"accion": "cuentame", "params": {"tema": texto.strip(), "generate_if_missing": True}}


@app.post("/api/listen")
async def listen(request: Request):
    """
    Recibe audio del browser (mic del celu/PC), transcribe con Whisper local,
    parsea intent y dispara el endpoint correspondiente.
    Body: raw bytes (audio webm/opus).
    """
    audio_bytes = await request.body()
    if not audio_bytes or len(audio_bytes) < 1000:
        return JSONResponse({"error": "audio vacio o muy corto"}, status_code=400)

    tracker.mark_input()

    # Transcribir
    try:
        texto = await asyncio.to_thread(transcribir_audio_sync, audio_bytes)
    except Exception as e:
        return JSONResponse({"error": f"transcripcion fallo: {e}"}, status_code=500)

    if not texto:
        return JSONResponse({"transcript": "", "error": "no se reconocio voz"}, status_code=400)

    # Parsear intent
    intent = parsear_intent(texto)
    accion = intent["accion"]
    params = intent["params"]

    # Ejecutar la accion correspondiente
    try:
        if accion == "saludar":
            result = await saludar({})
        elif accion == "despedir":
            result = await despedir({})
        elif accion == "opinar":
            result = await opinar(params)
        elif accion == "precio":
            result = await precio(params)
        elif accion == "random":
            result = await random_dato(params)
        elif accion == "cuentame":
            result = await cuentame(params)
        else:
            result = {"ok": False, "error": "intent desconocido"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    # Si el endpoint devolvio JSONResponse, sacar el body
    if hasattr(result, "body"):
        try:
            result = json.loads(result.body.decode())
        except Exception:
            result = {"ok": False, "error": "respuesta interna invalida"}

    return {
        "ok": True,
        "transcript": texto,
        "accion": accion,
        "params": params,
        "result": result,
    }


@app.get("/api/ping")
async def ping():
    return {"ok": True, "live_clients": len(manager.live_clients), "idle_state": tracker.current_idle_state, "is_speaking": tracker.is_speaking}


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
