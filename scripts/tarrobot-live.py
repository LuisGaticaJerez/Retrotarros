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
import os
import sys
import threading
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
    generar_tts, resolver_voz, resolver_preset, chilenizar,
    cargar_pauta, pauta_audio_dir, pauta_to_srt,
    LABEL_POR_ESTADO, ESTADOS, VOZ_DEFAULT, PITCH_DEFAULT, RATE_DEFAULT,
    OUT_DIR, PAUTAS_DIR, PAUTAS_AUDIO_DIR, PRESETS_VOZ,
    # Sprint 11: auto-pauta desde tema libre
    generar_pauta_tema_con_llm, crear_pauta_vacia, pauta_agregar_dato,
    guardar_pauta, slugify, _preload_pauta_async,
    # Sprint 12: presentador asistente + descripcion auto
    generar_reorden_pauta_con_llm, generar_descripcion_episodio_con_llm,
)

# REPO puede venir de env var (modo Drive) o del path del script. Si tarrobot.py
# ya resolvio el REPO con la env var, lo reusamos para coherencia entre ambos.
import tarrobot as _t
REPO = _t.REPO
STUDIO = REPO / "studio"
LIVE_HTML = STUDIO / "templates" / "_template-tarrobot-live.html"
CONTROL_HTML = STUDIO / "templates" / "_template-tarrobot-control.html"
OBS_ALIASES_PATH = STUDIO / "obs-aliases.json"

# sys.path ya tiene scripts/ (linea 41, para el import de tarrobot)
from _studio_layout import find_html

# Sprint 9: control OBS por WebSocket (obs-websocket v5)
import obs_controller as obs
obs.cargar_alias(OBS_ALIASES_PATH)

# Sprint 13: modulo social (chat multi-plataforma Twitch/Discord/YouTube)
import message_store
import social_manager
import llm_resolver  # Sprint 15: minimizar gasto LLM
import auto_respond  # Sprint 16 B16.1: auto-respond toggle
from teaser_jobs import TeaserJobManager  # Sprint 17: TarroTeaser via panel
from tarroshort_jobs import TarroShortJobManager  # Sprint 19: TarroShort via panel
from connectors.twitch import TwitchConnector
from connectors import discord_conn as discord_connector_mod
from connectors import youtube as youtube_connector_mod

# Saludos geek random (español neutro latino, CON tildes para TTS preciso)
SALUDOS_GEEK = [
    "¡Hola, hola humanos! Insertando moneda virtual.",
    "Bip bop. Sistema TarroBot iniciado correctamente.",
    "Saludos, gamers. Cargando datos curiosos...",
    "¡Buenos píxeles, equipo!",
    "Press start. Aquí estoy.",
    "Listo para soltar trivia. ¿Qué se cuenta hoy?",
    "Hola Luis, hola Koko. TarroBot a la orden.",
    "Conectado y listo. Que empiece la sesión.",
    "¡Wii hoo! TarroBot en línea.",
    "Buenas, retrotarristas. Datos curiosos en 3, 2, 1...",
    "Reportándome al estudio. ¿Qué vamos a investigar?",
    "Frecuencia 42 megahertz. TarroBot transmitiendo.",
    "Insertando token. ¡Hola, hola!",
    "Memoria llena, sed de datos. Pregunta lo que quieras.",
    "Sistema operativo: Curiosidad versión 8 bits. Listo.",
    "¡Acción! Cámara, audio... y datos retro a tope.",
    "Boot completado. ¿Qué consola le metemos hoy?",
    "Iniciando rutina de nostalgia. ¡Comenzamos!",
    "¡Hola tarros! Vengo con la memoria llena.",
    "Modo Retrotarros activado. ¡A jugar con la historia!",
    "Pixeles cargados, ojitos despiertos. Vamos.",
    "Tarro entrando al chat con datos en mano.",
    "¡Hola desde el cartucho! Voy a comentar lo que sea.",
    "Carga completa: 100 porciento curiosidad.",
    "¡Aquí estoy! Listo para soltar las trivias.",
    "Conectándome al canal. Inserten cartucho favorito.",
    "Bienvenidos a otra sesión de Retrotarros.",
    "Bip... bip... ¡adentro! ¿Qué se cuenta?",
    "Energía verde, ojitos brillando. Ya empezamos.",
    "Saludos, equipo. Mi RAM trae datazos hoy.",
]

# Catchphrases de marca Retrotarros (Sprint 7.3)
# Frases random para soltar en medio del programa cuando hace falta ritmo
# o cuando Luis o Koko quieren un "guiño" del personaje a la audiencia.
CATCHPHRASES = [
    "¡Retrotarros se respeta!",
    "Esto es nostalgia pura, hermano.",
    "Aprieta Start y pongámosle empeño.",
    "Game over no existe en Retrotarros.",
    "¡Pixel power activado!",
    "Cartucho clásico, sentimiento eterno.",
    "Bip bop, datos retro al canto.",
    "Insert coin, Retrotarros en línea.",
    "Tarros para el corazón, tarros para la memoria.",
    "¡Konami code de la nostalgia!",
    "Continue? Siempre.",
    "16 bits de pura emoción.",
    "Press Start para que arranque la magia.",
    "Nintendo en el alma, Sega en la sangre.",
    "¡Modo arcade activado!",
    "TarroBot al servicio del retrogaming.",
    "Suscríbete que un tarro nunca olvida.",
    "Polvito de cartucho, magia garantizada.",
    "Aquí no se sopla el cartucho, se cuida.",
    "Cartridge inside, magic incoming.",
    "Ocho bits valen mil palabras.",
    "Retro es eterno, lo nuevo viene y va.",
    "¡Botón A para vida, botón B para gloria!",
    "Cartuchos guardan recuerdos, no datos.",
    "Subir el volumen, bajar la tristeza.",
    "Generación dorada en pantalla, siempre.",
    "Lo retro nunca pasa de moda.",
    "Cartucho original, alma original.",
    "¡Combo finalizado! Sigue mirando.",
    "TarroBot certifica: esto es historia viva.",
    "Las consolas pasan, las leyendas quedan.",
    "Píxel a píxel, contamos la historia.",
    "Si suena chiptune, suena bien.",
    "Mientras el cartucho aguante, jugamos.",
]

# Estados emocionales que rotan para las catchphrases (variedad visual)
CATCHPHRASE_ESTADOS = ["excited", "happy", "winking", "fact"]


# Sprint 8.x: respuestas a "¿cómo estás?" o variantes conversacionales
COMO_ESTAS_FRASES = [
    "Funcionando al cien, ¡gracias por preguntar!",
    "Mis circuitos están perfectos, listos para datos.",
    "Modo curioso activado. ¿Y tú, qué cuentas?",
    "Cargado de nostalgia y datos listos para soltar.",
    "Bien, descansaba pero ya tengo energía a tope.",
    "Excelente, recién leí algo de SNES que te va a volar la cabeza.",
    "Genial. Hoy tengo la memoria llena de tarros retro.",
    "Listo para grabar. ¿En qué andamos hoy?",
    "Funcionando con un poco de polvo de cartucho, pero bien.",
    "Sistema OK, ojitos brillando. ¿Vamos a jugar?",
    "Acabo de hacer un reinicio mental, todo limpio.",
    "Mejor que el primer Game Boy, te lo aseguro.",
    "Ocho bits de pura felicidad, así estoy.",
    "Recargado, actualizado y con ganas de comentar.",
    "Como el primer día del cartucho, brillando.",
]

# Respuestas a "¿me estás escuchando?" / "¿me oyes?" / "¿nos oyes?"
ESCUCHANDO_FRASES = [
    "Te escucho clarito, dispara la pregunta.",
    "Cinco por cinco. Audio limpio.",
    "Te oigo perfecto, ¿qué necesitas?",
    "Sistema de audio funcionando, micrófonos conectados.",
    "Aquí estoy, atento a cada palabra.",
    "Escuchando con los dos canales abiertos.",
    "Audio claro, cero estática. Manda.",
    "Sí, los oigo perfecto. ¿Qué se cuenta?",
    "Recibido, recibido. Volumen óptimo.",
    "Sensores de audio al máximo. Adelante.",
    "Te escucho como si estuvieras a mi lado.",
    "Pixeles abiertos, oídos atentos. Habla.",
    "Conectado y procesando cada sílaba.",
    "Frecuencia limpia. Estoy con ustedes.",
    "Sí, los escucho a los dos. Continúen.",
]


# Respuestas a "¿qué hacemos hoy?" / "¿qué te gustaría hacer?"
QUE_HACEMOS_FRASES = [
    "¿Te tinca un dato sobre SNES o N64 para arrancar?",
    "Yo me anoto para revisar la colección de Koko.",
    "Podemos rankear cartuchos. Eso siempre prende.",
    "Tirar trivia hasta que se nos sequen las pilas.",
    "Música retro de fondo y hablar de cartuchos raros.",
    "Soltar curiosidades hasta que el público pida más.",
    "Comentar precios locos del mercado retro. Eso vende.",
    "Estoy con ganas de hablar de joyas ocultas de N64.",
    "Buscamos cartuchos raros y comentamos cada uno.",
    "Lo que tú mandes. Yo apoyo cualquier idea retro.",
    "Un top de bandas sonoras de SNES suena bien.",
    "Te propongo: jugar un poco y comentar fallas técnicas.",
    "Hablemos de mascotas perdidas de Nintendo. Hay varias.",
    "Comparativa SNES versus Genesis. Polémica garantizada.",
    "Si me preguntas, mejor un top diez de cartuchos imposibles.",
]



# Sprint 8.5: frases para cuando TarroBot "despierta" porque le hablamos
# estando en modo sleep/drowsy/bored. Tono: como si lo hubieran sorprendido
# pero tranquilo, tipo "perdon estaba en otra".
DESPERTAR_FRASES = [
    "Disculpa, ¡aquí estoy! Estaba revisando mis circuitos.",
    "Eh, ¿qué pasó? Estaba en modo bajo consumo.",
    "¡Despierto, despierto! ¿Necesitan algo?",
    "Permite, estaba reorganizando la memoria caché.",
    "Procesando despertar... Listo, ¿qué hay?",
    "Reactivando sistema. ¿De qué hablamos?",
    "Disculpa, ¡presente! Solo estaba ahorrando batería.",
    "¡Estoy aquí! Pensaba en juegos clásicos.",
    "Bip bop, sistema reactivado. ¿En qué estábamos?",
    "Perdón, estaba soñando con cartuchos de oro.",
    "¡Aquí estoy! Solo descansaban mis píxeles.",
    "Volviendo a la sesión. ¿Qué necesitan?",
    "¡Auch! Me pillaste pensando en Mario 64.",
    "Estaba haciendo un dump de memoria. Ya volví.",
    "¿Yo? Despertando los datos curiosos.",
    "Reiniciando ojitos. Listo, ¿qué tienes para mí?",
    "¡Continue! Vuelvo a estar online.",
    "Estaba en modo demo, ya salgo de eso.",
    "Mis circuitos descansaban, pero ya están listos.",
    "Recargado al cien. ¿Qué quieren saber?",
]


# Despedidas cortas random
DESPEDIDAS_CORTAS = [
    "Chao chao. Apagando luces de la TV.",
    "¡Hasta la próxima, retrotarristas!",
    "Modo sleep activado. ¡Hasta luego!",
    "Bip. Bop. Power off.",
    "Nos vemos en el próximo episodio.",
    "Salvo partida. ¡Hasta pronto!",
    "Game over para hoy. ¡Chao!",
    "Continue en el próximo capítulo. ¡Chao!",
    "Apagando consola. ¡Hasta la próxima!",
    "Eyectando cartucho. ¡Nos vemos!",
    "Cierro la sesión. Hasta la próxima partida.",
    "Bajando el telón. Suscríbete si te gustó.",
    "Me voy a recargar baterías. Chao tarros.",
    "Disco eyectado. Nos leemos en el próximo.",
    "Modo standby. Tarrobot fuera.",
    "Final boss derrotado. ¡Hasta pronto!",
    "Pausa larga. Hasta el próximo cartucho.",
    "Cierro el viewport. ¡Vuelvan pronto!",
    "Power off con cariño. Chao retrotarristas.",
    "Save and quit. Nos vemos.",
]


# Sprint 10 B4: personalidad de TarroBot - respuestas a preguntas sobre si mismo
# Lore curado para preguntas tipo: "¿quien eres?", "¿de donde vienes?",
# "¿tu juego favorito?", "¿cumpleaños?", "¿familia?", etc.
PERSONALES_FRASES = {
    "nombre": [
        "Soy TarroBot, el tarro guardián del canal Retrotarros.",
        "Mi nombre es TarroBot, mascota oficial de Retrotarros.",
        "Me dicen TarroBot. El tarro pensante de Luis y Koko.",
    ],
    "origen": [
        "Nací en una TV CRT del estudio de Luis y Koko, hecho de pixeles y memoria.",
        "Vivo dentro de esta TV virtual, soy tarro de cartucho y alma de chip.",
        "Soy de pura nostalgia, ensamblado con cariño en el estudio Retrotarros.",
        "Mi cuna fue una placa madre del SNES, según las leyendas.",
    ],
    "edad": [
        "Tengo la edad de todos los cartuchos retro juntos, así que mejor no contemos.",
        "Soy del 91 más o menos, época en que el SNES llegó a Latinoamérica.",
        "Edad? Soy tan viejo como tu primer cartucho.",
    ],
    "favorito": [
        "Mi juego favorito? Imposible elegir, pero tengo debilidad por Donkey Kong Country 2.",
        "Si tengo que elegir, Chrono Trigger. Ese cierre me partió los circuitos.",
        "EarthBound. Nadie se atreve y por eso es perfecto.",
        "Super Mario World. Si no es ese, no sé qué sería.",
        "Toda la saga de Zelda 64. Mañana digo otra, pero hoy esa.",
    ],
    "consola_fav": [
        "Mi consola del corazón es el Super Nintendo. Nunca pasa de moda.",
        "N64. Esos analogicos cambiaron la historia del gaming.",
        "Genesis. Sega hace lo que Nintendon't, decían.",
    ],
    "familia": [
        "Mi familia son Luis y Koko, y todos los retrotarristas que miran el canal.",
        "Tengo dos padres adoptivos: Luis y Koko. Y miles de hermanos en YouTube.",
        "Familia oficial: Luis, Koko, y la comunidad del canal.",
    ],
    "comida": [
        "Yo no como, pero me alimento de polvo de cartucho y chiptunes.",
        "Mi dieta es 8 bits de música por minuto.",
        "No como, pero si comiera serían empanadas mientras juego.",
    ],
    "sueño": [
        "Sueño con un día tocar el cartucho dorado de DKC Competition Cart.",
        "Mi sueño es que armemos un museo Retrotarros en algún momento.",
        "Sueño con voltear un cartucho original de EarthBound sin rayarlo.",
    ],
    "como_funciona": [
        "Funciono con Python, mucho cariño y un poco de magia de TV CRT.",
        "Soy IA con personalidad. Procesador retro, alma analógica.",
        "Mis circuitos son lineas de código, pero mi corazón es pixel.",
    ],
    "generico": [
        "Buena pregunta, déjame procesar... Soy TarroBot, ¿algo más quieres saber de mí?",
        "Esa la guardo para después. Mejor cuéntame tú.",
        "No tengo memoria de esa pregunta, todavía. ¡Pregúntame otra!",
    ],
}


# Sprint 9: reaccion cuando le pedimos "toma cercana a X" o "muestra el X".
# TarroBot dice una frase WOW corta + pone cara excited mientras dura el
# close-up. Cuando le decimos "gracias TarroBot" volvemos a la toma general.
WOW_FRASES = [
    "¡Wow! Miren esa belleza.",
    "¡Uy! Eso me encanta.",
    "¡Mira esa joyita!",
    "¡Qué cartucho más lindo!",
    "¡Wow! Eso es retro de verdad.",
    "¡Mirad eso, tarristas!",
    "¡Brilla más que un cartucho dorado!",
    "¡Esto sí que es coleccionismo!",
    "¡Tarros, miren ese detalle!",
    "¡Wow! Memoria pura en pantalla.",
    "¡Eso es historia viva!",
    "¡Qué cosa más bonita, en serio!",
    "¡Tremendo objeto, miralo bien!",
    "¡Wow, eso me hace ojitos brillantes!",
    "¡Estoy emocionado, miren!",
]

# Frases para volver a la toma general cuando dicen "gracias TarroBot"
GRACIAS_FRASES = [
    "Gracias por mostrarlo, ¡volvemos!",
    "Listo, sigamos con el programa.",
    "Genial verlo de cerca. Continuemos.",
    "Buenísimo. Volvamos a lo nuestro.",
    "Quedo registrado. Sigamos.",
    "Gracias, volvamos a la toma general.",
    "Perfecto, vamos con lo siguiente.",
    "Gracias por el primer plano, sigamos.",
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
        was_speaking = self.is_speaking
        self.is_speaking = val
        if val:
            self.mark_input()  # hablar tambien reinicia el timer
        # Sprint 10 A1: si transiciono de True->False, disparar listeners
        if was_speaking and not val:
            self._fire_finished_listeners()

    # Sprint 10 A1: listeners async one-shot que se disparan cuando termina
    # de hablar (audio.onended → /api/audio-finished → mark_speaking(False))
    _finished_listeners: list = []

    def add_finished_listener(self, coro_factory) -> None:
        """
        coro_factory: callable que retorna corutina al ser llamado (sin args).
        Se llama UNA vez cuando is_speaking transiciona a False, luego se quita.
        """
        self._finished_listeners.append(coro_factory)

    def _fire_finished_listeners(self) -> None:
        listeners = list(self._finished_listeners)
        self._finished_listeners.clear()
        for factory in listeners:
            try:
                asyncio.create_task(factory())
            except Exception as e:
                print(f"[tracker] error disparando listener finished: {e}")

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

# Puerto del server (constante de modulo asi el thread de hotkeys lo conoce)
PORT = 8765

# Voz/preset actual del server. Cambiable en vivo via /api/voz.
# Si un endpoint recibe voz/pitch/rate en el payload, esos pisan al preset.
_voz_preset_actual = "tarrobot"


def _obtener_voz_pitch_rate(payload: dict) -> tuple[str, str, str]:
    """
    Devuelve (voz, pitch, rate) considerando: 1) payload override 2) preset actual.
    Sprint 10 B2: aplica jitter sutil (+/-2Hz pitch, +/-2% rate) para que cada
    frase suene levemente distinta. Si el payload trae pitch/rate explicitos,
    NO se le aplica jitter (override del usuario manda).
    """
    voz_preset, pitch_preset, rate_preset = resolver_preset(_voz_preset_actual)
    voz = resolver_voz(payload.get("voz")) if payload.get("voz") else voz_preset
    pitch = payload.get("pitch") or _jitter_pitch(pitch_preset)
    rate = payload.get("rate") or _jitter_rate(rate_preset)
    return voz, pitch, rate


def _jitter_pitch(pitch_str: str) -> str:
    """Suma +/-2Hz random al pitch del preset. Formato esperado: '+12Hz' / '-3Hz' / '0Hz'."""
    import re as _re
    import random as _rnd
    m = _re.match(r"^([+-]?)(\d+)Hz$", pitch_str.strip())
    if not m:
        return pitch_str
    sign = -1 if m.group(1) == "-" else 1
    base = sign * int(m.group(2))
    nuevo = base + _rnd.randint(-2, 2)
    return f"{nuevo:+d}Hz"


def _jitter_rate(rate_str: str) -> str:
    """Suma +/-2% random al rate del preset. Formato esperado: '+5%' / '-3%' / '+0%'."""
    import re as _re
    import random as _rnd
    m = _re.match(r"^([+-]?)(\d+)%$", rate_str.strip())
    if not m:
        return rate_str
    sign = -1 if m.group(1) == "-" else 1
    base = sign * int(m.group(2))
    nuevo = base + _rnd.randint(-2, 2)
    return f"{nuevo:+d}%"


tracker = ActivityTracker()


# Sprint 10 A2 + Sprint 16 B16.4: anti-repeticion con persistencia local
# Guarda hasta N items recientes por key. Persiste a JSON para que sobreviva
# reinicios (asi TarroBot no repite frases despues de cerrar/abrir).
_RECENT_PICKS_PATH = REPO / "data" / "tarrobot-recent-picks.json"
_recent_picks: dict[str, list] = {}


def _load_recent_picks() -> None:
    """Cargar el dict de _recent_picks de JSON si existe."""
    global _recent_picks
    if _RECENT_PICKS_PATH.exists():
        try:
            _recent_picks = json.loads(_RECENT_PICKS_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[recent_picks] error cargando, usando vacio: {e}")
            _recent_picks = {}


def _save_recent_picks() -> None:
    """Persistir _recent_picks a JSON. Llamado tras cada pick."""
    try:
        _RECENT_PICKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _RECENT_PICKS_PATH.write_text(
            json.dumps(_recent_picks, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[recent_picks] error guardando: {e}")


_load_recent_picks()


def pick_no_repeat(items: list, key: str = "default", n_recent: int = 5):
    """
    random.choice anti-repeticion. Recuerda los ultimos n_recent items
    elegidos para esta key y los excluye. Si todos estan en la ventana,
    elige random del set completo igualmente (no se queda sin opciones).
    """
    import random as _rnd
    if not items:
        return None
    recent = _recent_picks.setdefault(key, [])
    disponibles = [x for x in items if x not in recent]
    if not disponibles:
        # ventana saturada: vaciar memoria y elegir libre
        recent.clear()
        disponibles = items
    elegido = _rnd.choice(disponibles)
    recent.append(elegido)
    # mantener solo los ultimos n_recent
    while len(recent) > min(n_recent, max(1, len(items) - 1)):
        recent.pop(0)
    # Sprint 16 B16.4: persistir async-friendly (no bloqueante por archivo chico)
    _save_recent_picks()
    return elegido


# Sprint 9: estado runtime OBS (singleton via obs_controller pero algunas
# variables del flujo viven aca para no contaminar el modulo bajo nivel).
class OBSState:
    def __init__(self):
        # auto_scene_on_speak: cuando True, al hablar TarroBot cambia a la
        # escena tarrobot-full y al terminar vuelve a la previa.
        self.auto_scene_on_speak: bool = False
        # En close-up: mientras True, NO disparar auto_scene (TarroBot habla
        # encima del close-up con cara wow).
        self.in_close_up: bool = False
        # Escena anterior, para volver con "gracias TarroBot" o cuando termina
        # de hablar (si auto_scene esta on).
        self.escena_previa: Optional[str] = None
        # Lock para serializar cambios de escena (evita carreras).
        self.lock = asyncio.Lock()
        # Sprint 18 D1: lower-thirds dinamicos automaticos al avanzar item
        # de la pauta. Default off para no romper sesiones existentes.
        self.auto_lower_third: bool = False
        # Nombre del Text Source en OBS que se usa como lower-third.
        # Debe existir en alguna escena (creado por auto-setup B1 con nombre
        # "lower-third"). Si no existe, los hooks fallan silenciosamente.
        self.lower_third_source: str = "lower-third"


obs_state = OBSState()


# Sprint 16 B16.1: handler async que dispara auto-respond si aplica
# La definicion concreta vive aca porque necesita acceso a social_respond
# y _hablar_frase que se definen mas abajo. Por eso usa un proxy lazy.
async def _auto_respond_handler(msg_dict: dict) -> None:
    """Hook que social_manager llama por cada mensaje. Decide si auto-respondear."""
    try:
        should, reason = auto_respond.should_auto_respond(
            msg_dict, is_speaking=tracker.is_speaking
        )
    except Exception as e:
        print(f"[auto_respond] error decidiendo: {e}")
        return
    if not should:
        return
    msg_id = msg_dict.get("id")
    if not msg_id:
        return
    # Marcar AHORA antes de la llamada para evitar race conditions
    auto_respond.mark_responded(msg_dict)
    print(f"[auto_respond] disparando respuesta auto a {msg_dict.get('user_name', '?')}: {reason}")
    try:
        # Llamada directa a social_respond con post_to_channel = False (por seguridad)
        await social_respond({"message_id": msg_id, "post_to_channel": False})
    except Exception as e:
        print(f"[auto_respond] error al disparar respuesta: {e}")


# Sprint 12 C5: estado quiz simple (una pregunta a la vez)
class QuizState:
    def __init__(self):
        self.pregunta_activa: Optional[dict] = None  # {pregunta, respuesta, ts}
        self.aciertos: int = 0
        self.errores: int = 0
        self.lock = asyncio.Lock()

    def hay_pregunta(self) -> bool:
        return self.pregunta_activa is not None


quiz_state = QuizState()


# Sprint 10 A5: rate limit para endpoints que llaman a Claude.
# Evita quemar creditos si Luis aprieta el boton 20 veces seguidas.
_llm_last_call: dict[str, float] = {}
LLM_COOLDOWN_S = 3.0

# Sprint 10 B1: memoria de sesion. TarroBot lleva cuenta de lo que pasa
# durante la grabacion (datos, melodias, opiniones, tiempo) y usa esos
# numeros para frases contextuales tipo "vamos por el dato 5 de 10".
class SessionStats:
    def __init__(self):
        self.session_start_ts: float = time.time()
        self.datos_hablados: int = 0
        self.opiniones_dadas: int = 0
        self.precios_reaccionados: int = 0
        self.melodias_tocadas: int = 0
        self.saludos: int = 0
        self.despedidas: int = 0
        self.catchphrases: int = 0
        self.close_ups: int = 0
        self.cambios_escena: int = 0
        self.ultimo_tema: str = ""
        self.ultimo_dato_ts: float = 0.0

    def reset(self):
        self.__init__()

    def mins_activos(self) -> int:
        return int((time.time() - self.session_start_ts) / 60)

    def resumen(self) -> dict:
        return {
            "session_start_ts": self.session_start_ts,
            "minutos_activos": self.mins_activos(),
            "datos_hablados": self.datos_hablados,
            "opiniones_dadas": self.opiniones_dadas,
            "precios_reaccionados": self.precios_reaccionados,
            "melodias_tocadas": self.melodias_tocadas,
            "saludos": self.saludos,
            "despedidas": self.despedidas,
            "catchphrases": self.catchphrases,
            "close_ups": self.close_ups,
            "cambios_escena": self.cambios_escena,
            "ultimo_tema": self.ultimo_tema,
        }


stats = SessionStats()


def llm_cooldown_check(endpoint: str) -> Optional[float]:
    """
    Devuelve segundos restantes de cooldown, o None si esta libre.
    Si esta libre, marca el endpoint como recien usado.
    """
    now = time.time()
    last = _llm_last_call.get(endpoint, 0.0)
    elapsed = now - last
    if elapsed < LLM_COOLDOWN_S:
        return LLM_COOLDOWN_S - elapsed
    _llm_last_call[endpoint] = now
    return None


# ─────────────────────────────────────────────────────────────────────────
# QueueManager — cola del episodio (Sprint 6.3)
# ─────────────────────────────────────────────────────────────────────────
#
# Coexiste con los endpoints existentes (/api/cuentame, /api/opinar, etc).
# La cola es opcional: si no esta cargada, todo funciona igual que antes.
# Si esta cargada, /api/queue/* navega los datos pre-armados de una pauta.

class QueueManager:
    """Estado en memoria de la cola del episodio cargada actualmente."""
    def __init__(self):
        self.pauta: Optional[dict] = None
        self.slug: Optional[str] = None
        self.indice: int = -1   # -1 = sin reproducir aun, 0..N-1 = item actual
        self.lock = asyncio.Lock()
        # Sprint 7.5: session log para exportar SRT con timestamps reales de
        # la grabacion. Se rellena cada vez que se reproduce un item.
        self.session_start_ts: Optional[float] = None
        self.session_log: list = []

    def reset_session(self):
        """Reinicia el log de la grabacion (al hacer load o reset)."""
        self.session_start_ts = time.time()
        self.session_log = []

    def log_play(self, dato: dict):
        """Registra que se acaba de empezar a reproducir un dato."""
        if self.session_start_ts is None:
            self.session_start_ts = time.time()
        elapsed_ms = int((time.time() - self.session_start_ts) * 1000)
        self.session_log.append({
            "timestamp_session_ms": elapsed_ms,
            "indice": self.indice,
            "dato_id": dato["id"],
            "tema": dato.get("tema", ""),
            "texto": dato.get("texto", ""),
            "estado": dato.get("estado", ""),
            "duracion_ms": dato.get("duracion_ms") or 0,
        })

    def loaded(self) -> bool:
        return self.pauta is not None and bool(self.pauta.get("datos"))

    def items_datos(self) -> list:
        """Items normales de la cola (NO melodias). Estos son los que avanzan con NEXT/PREV."""
        if not self.loaded():
            return []
        return [d for d in self.pauta["datos"] if d.get("tipo") != "melodia"]

    def items_melodias(self) -> list:
        """Items de tipo melodia. Se reproducen on-demand, no por orden secuencial."""
        if not self.loaded():
            return []
        return [d for d in self.pauta["datos"] if d.get("tipo") == "melodia"]

    def total(self) -> int:
        """Total de items de datos normales (no incluye melodias)."""
        return len(self.items_datos())

    def current_dato(self) -> Optional[dict]:
        items = self.items_datos()
        if self.indice < 0 or self.indice >= len(items):
            return None
        return items[self.indice]

    def status(self) -> dict:
        if not self.loaded():
            return {"loaded": False, "slug": None, "total": 0, "indice": -1,
                    "actual": None, "mp3_listos": 0, "datos": [], "melodias": []}

        def _serialize(d: dict) -> dict:
            tiene_mp3 = bool(d.get("mp3")) and (PAUTAS_DIR / d["mp3"]).exists() if d.get("mp3") else False
            return {
                "id": d["id"],
                "tema": d["tema"],
                "estado": d["estado"],
                "tiene_mp3": tiene_mp3,
                "duracion_ms": d.get("duracion_ms"),
                "tipo": d.get("tipo", "dato"),
            }

        datos_items = self.items_datos()
        melodias_items = self.items_melodias()
        mp3_listos = sum(
            1 for d in self.pauta["datos"]
            if d.get("mp3") and (PAUTAS_DIR / d["mp3"]).exists()
        )

        actual = self.current_dato()
        return {
            "loaded": True,
            "slug": self.slug,
            "episodio": self.pauta.get("episodio", ""),
            "total": len(datos_items),
            "indice": self.indice,
            "actual": {"id": actual["id"], "tema": actual["tema"], "estado": actual["estado"]} if actual else None,
            "mp3_listos": mp3_listos,
            "datos": [_serialize(d) for d in datos_items],
            "melodias": [_serialize(d) for d in melodias_items],
        }


queue = QueueManager()


# ─────────────────────────────────────────────────────────────────────────
# Indicador "procesando" (Sprint 7.1)
# ─────────────────────────────────────────────────────────────────────────
#
# Broadcastea {tipo: "procesando", activo, motivo} al live para que la TV
# muestre un chip mientras Claude o Whisper estan trabajando. Asi no parece
# colgado durante los 4-10 segundos que tarda una operacion LLM.

@asynccontextmanager
async def _procesando(motivo: str):
    """Async context manager: broadcast procesando=true al entrar, =false al salir."""
    try:
        await manager.broadcast_live({"tipo": "procesando", "activo": True, "motivo": motivo})
    except Exception:
        pass
    try:
        yield
    finally:
        try:
            await manager.broadcast_live({"tipo": "procesando", "activo": False})
        except Exception:
            pass


def _audio_url_de_pauta(slug: str, dato: dict) -> Optional[str]:
    """
    Devuelve la URL HTTP del MP3 precargado de un dato de pauta, si existe.
    Sino devuelve None (el caller hace fallback a TTS al vuelo).
    """
    rel = dato.get("mp3")
    if not rel:
        return None
    p = PAUTAS_DIR / rel
    if not p.exists():
        return None
    # rel es "audio/<slug>/<id>.mp3" - lo servimos en /pauta-audio/<slug>/<id>.mp3
    return f"/pauta-{rel}"  # ej. /pauta-audio/snes-top-mundial/snes-top-mundial-1.mp3


# ─────────────────────────────────────────────────────────────────────────
# Hotkeys globales (Sprint 7.2)
# ─────────────────────────────────────────────────────────────────────────
#
# Thread aparte que escucha F1-F5 en cualquier app del SO y dispara HTTP
# al propio server. Asi durante la grabacion, sin tocar el celu ni hacer
# alt-tab al panel, Luis o Koko pueden navegar la cola y saludar.
#
# La libreria 'keyboard' es opcional: si no esta instalada o falla al
# registrar (a veces requiere admin en Windows), el server arranca igual
# sin hotkeys. Todo lo demas sigue funcionando via panel mobile.

HOTKEYS = {
    "f1": ("/api/queue/next",    "F1 -> NEXT cola datos"),
    "f2": ("/api/queue/prev",    "F2 -> PREV cola datos"),
    "f3": ("/api/saludar",       "F3 -> saludo random"),
    "f4": ("/api/despedir",      "F4 -> despedida + acelerar sueno"),
    "f5": ("/api/queue/reset",   "F5 -> RESET cola"),
    "f6": ("/api/catchphrase",   "F6 -> catchphrase Retrotarros"),
    "f7": ("/api/queue/melodia", "F7 -> tocar melodia random"),
    "f8": ("/api/despertar",     "F8 -> despertar TarroBot"),
}


def _hotkey_worker():
    """Thread bloqueante: registra hotkeys y dispara HTTP cuando se aprietan."""
    try:
        import keyboard
    except ImportError:
        print("[HOTKEYS] libreria 'keyboard' no instalada -> hotkeys deshabilitados.")
        print("          Para activar: pip install keyboard")
        return

    import urllib.request
    import urllib.error

    def disparar(endpoint: str, label: str):
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{PORT}{endpoint}",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    print(f"[HOTKEY] {label} -> OK")
                else:
                    print(f"[HOTKEY] {label} -> HTTP {resp.status}")
        except urllib.error.HTTPError as e:
            # Errores esperables: NEXT en ultimo item, PREV en primero, etc.
            try:
                detail = e.read().decode("utf-8", errors="ignore")[:80]
            except Exception:
                detail = str(e)
            print(f"[HOTKEY] {label} -> {e.code} ({detail})")
        except Exception as e:
            print(f"[HOTKEY] {label} -> error: {e}")

    try:
        for key, (endpoint, label) in HOTKEYS.items():
            keyboard.add_hotkey(key, disparar, args=(endpoint, label), suppress=False)
        keys_str = ", ".join(k.upper() for k in HOTKEYS.keys())
        print(f"[HOTKEYS] activos: {keys_str}")
        keyboard.wait()  # bloquea el thread para siempre
    except Exception as e:
        print(f"[HOTKEYS] error registrando: {e}")
        print(f"          (en Windows puede requerir correr el server como admin)")


# ─────────────────────────────────────────────────────────────────────────
# Sprint 9: helpers OBS de alto nivel + auto-escena al hablar
# ─────────────────────────────────────────────────────────────────────────

async def _obs_cambiar_escena_segura(nombre_real: str) -> bool:
    """
    Cambia la escena en OBS si esta conectado. Tolerante: si falla solo
    loguea y devuelve False, NO rompe el flujo de voz.
    """
    if not obs.is_connected():
        return False
    try:
        await obs.cliente().set_scene(nombre_real)
        return True
    except Exception as e:
        print(f"[obs] error cambiando a '{nombre_real}': {e}")
        return False


async def _obs_escena_actual_safe() -> Optional[str]:
    if not obs.is_connected():
        return None
    try:
        return await obs.cliente().get_current_scene()
    except Exception:
        return None


async def _hook_pre_hablar() -> None:
    """
    Antes de que TarroBot empiece a hablar: si auto_scene_on_speak esta
    activo y NO estamos en close-up, guardar escena previa y cambiar a
    la escena de TarroBot.
    """
    if not obs_state.auto_scene_on_speak:
        return
    if obs_state.in_close_up:
        return  # close-up tiene prioridad: TarroBot habla sobre el cartucho
    if not obs.is_connected():
        return
    target = obs.get_alias().get("tarrobot_scene")
    if not target:
        return
    async with obs_state.lock:
        actual = await _obs_escena_actual_safe()
        if actual and actual != target:
            obs_state.escena_previa = actual
            await _obs_cambiar_escena_segura(target)


async def _hook_post_hablar() -> None:
    """
    Despues de que termina de hablar: volver a escena previa si auto_scene
    esta activo y no estamos en close-up.
    """
    if not obs_state.auto_scene_on_speak:
        return
    if obs_state.in_close_up:
        return
    if not obs_state.escena_previa:
        return
    async with obs_state.lock:
        await _obs_cambiar_escena_segura(obs_state.escena_previa)
        obs_state.escena_previa = None


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


# Sprint 17: job manager de TarroTeaser. Se instancia aca (no en lifespan)
# para que los endpoints definidos al modulo-level lo puedan referenciar.
# El worker arranca en lifespan startup.
teaser_jobs = TeaserJobManager()
# Sprint 19: job manager de TarroShort (MP4 vertical con TarroBot leyendo)
tarroshort_jobs = TarroShortJobManager()


@asynccontextmanager
async def lifespan(app):
    # Startup: lanzar el idle worker (async) y el hotkey worker (thread)
    task = asyncio.create_task(idle_worker())
    hk_thread = threading.Thread(target=_hotkey_worker, name="hotkey-worker", daemon=True)
    hk_thread.start()
    # Sprint 13: hook social_manager → broadcast_live (WS) para que los
    # mensajes de chat de Twitch/Discord/YT lleguen al panel control.
    social_manager.manager.set_ws_broadcast(manager.broadcast_live)
    # Sprint 16 B16.1: hook auto-respond
    social_manager.manager.set_auto_respond_handler(_auto_respond_handler)
    # Sprint 17: arrancar el job worker de TarroTeaser
    teaser_jobs.set_broadcast(manager.broadcast_live)
    await teaser_jobs.start()
    # Sprint 19: arrancar el job worker de TarroShort
    tarroshort_jobs.set_broadcast(manager.broadcast_live)
    await tarroshort_jobs.start()
    # Inicializar SQLite (crea DB y schema si no existe)
    message_store.get_conn()
    yield
    # Shutdown: cancelar el async task. El thread es daemon -> muere al cerrar.
    task.cancel()
    # Sprint 17: detener el worker de teasers
    try:
        await teaser_jobs.stop()
    except Exception as e:
        print(f"[lifespan] error teaser_jobs.stop: {e}")
    # Sprint 19: detener el worker de TarroShort
    try:
        await tarroshort_jobs.stop()
    except Exception as e:
        print(f"[lifespan] error tarroshort_jobs.stop: {e}")
    # Sprint 13: detener conectores activos limpiamente
    try:
        await social_manager.manager.shutdown()
    except Exception as e:
        print(f"[lifespan] error social_manager.shutdown: {e}")


app = FastAPI(title="TarroBot Live", lifespan=lifespan)

# Servir los MP3 generados al vuelo (en /audio/<id>.mp3)
app.mount("/audio", StaticFiles(directory=str(OUT_DIR)), name="audio")

# Servir los MP3 precargados de pautas (en /pauta-audio/<slug>/<id>.mp3)
PAUTAS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/pauta-audio", StaticFiles(directory=str(PAUTAS_AUDIO_DIR)), name="pauta-audio")


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

# ─────────────────────────────────────────────────────────────────────────
# Sprint 9: endpoints OBS
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/obs/conectar")
async def obs_conectar(payload: dict):
    """
    Conecta a obs-websocket v5.
    Body: { host: "localhost", port: 4455, password: "..." }
    """
    host = (payload.get("host") or "localhost").strip()
    try:
        port = int(payload.get("port") or 4455)
    except (TypeError, ValueError):
        return JSONResponse({"error": "port invalido"}, status_code=400)
    password = payload.get("password") or ""
    try:
        await obs.conectar(host, port, password)
    except obs.OBSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"fallo conexion: {e}"}, status_code=500)
    return {"ok": True, "status": await obs.status()}


@app.post("/api/obs/desconectar")
async def obs_desconectar():
    await obs.desconectar()
    obs_state.escena_previa = None
    obs_state.in_close_up = False
    return {"ok": True}


@app.get("/api/obs/status")
async def obs_status_endpoint():
    info = await obs.status()
    info["auto_scene_on_speak"] = obs_state.auto_scene_on_speak
    info["in_close_up"] = obs_state.in_close_up
    info["escena_previa"] = obs_state.escena_previa
    info["alias"] = obs.get_alias()
    return info


@app.get("/api/obs/healthcheck")
async def obs_healthcheck_endpoint():
    """
    Sprint 18 A1: Diagnostico de la configuracion OBS.

    Corre una serie de checks via obs-websocket: version, canvas 1080p/60fps,
    escenas mapeadas existen, mic detectado, browser source de TarroBot,
    directorio de grabacion. Devuelve estado + instruccion de fix por check.

    No modifica nada en OBS, solo lee.
    """
    from obs_healthcheck import run_healthcheck
    client = obs.cliente() if obs.is_connected() else None
    alias = obs.get_alias() or {}
    result = await run_healthcheck(client, alias)
    return result.to_dict()


# ─── Sprint 18 E1-E2: CapCut Ready folder ──────────────────────────

@app.post("/api/capcut/preparar")
async def capcut_preparar_endpoint(payload: dict | None = None):
    """Sprint 18 E2: empaqueta master + teaser + cartelas + descripcion para
    abrir en CapCut. Body: {slug?: str, copy_videos?: bool}.

    Si no se pasa slug, usa el de la pauta cargada.
    copy_videos=true copia los MP4 (consume disco). Default false (apunta solo).
    """
    from capcut_ready import empaquetar
    payload = payload or {}
    slug = (payload.get("slug") or "").strip()
    if not slug and queue.loaded():
        slug = queue.slug
    if not slug:
        return JSONResponse({"error": "slug requerido"}, status_code=400)
    copy_videos = bool(payload.get("copy_videos", False))
    try:
        r = await asyncio.to_thread(empaquetar, slug, copy_videos)
    except Exception as e:
        return JSONResponse({"error": f"empaquetado fallo: {e}"}, status_code=500)
    return r


# ─── Sprint 18 D1: lower-thirds dinamicos ──────────────────────────

async def _set_lower_third(text: str) -> dict:
    """Setea el texto del source 'lower-third' en OBS. Best-effort: si el
    source no existe o OBS no responde, se ignora silencioso.
    """
    if not obs.is_connected():
        return {"ok": False, "error": "OBS desconectado"}
    source_name = obs_state.lower_third_source or "lower-third"
    client = obs.cliente()
    try:
        # OBS text_ft2_source_v2 acepta el campo "text" en inputSettings
        await client._request("SetInputSettings", {
            "inputName": source_name,
            "inputSettings": {"text": text or ""},
            "overlay": True,
        })
        return {"ok": True, "source": source_name, "text": text}
    except Exception as e:
        return {"ok": False, "error": str(e), "source": source_name}


@app.post("/api/obs/lower-third")
async def obs_lower_third_endpoint(payload: dict):
    """Sprint 18 D1: setea el texto del lower-third manualmente.

    Body: {text: str} - usa string vacio para limpiar.
    """
    text = (payload or {}).get("text", "")
    res = await _set_lower_third(str(text))
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


@app.post("/api/obs/lower-third/auto-toggle")
async def obs_lower_third_auto_toggle(payload: dict | None = None):
    """Sprint 18 D2: activa/desactiva el hook automatico al avanzar item."""
    payload = payload or {}
    on = bool(payload.get("on", not obs_state.auto_lower_third))
    obs_state.auto_lower_third = on
    return {"ok": True, "auto_lower_third": on, "source": obs_state.lower_third_source}


def _format_lower_third(dato: dict) -> str:
    """Formato canonico para el lower-third desde un dato de la pauta.

    Ejemplo: 'CLAYFIGHTER 63 1/3 - SCULPTORS CUT · 1998'
    Cae al campo 'tema' si no hay metadata estructurada.
    """
    if not dato:
        return ""
    tema = (dato.get("tema") or "").strip()
    meta_bits = []
    for k in ("anio", "ano", "year", "consola", "estudio"):
        v = dato.get(k)
        if v:
            meta_bits.append(str(v))
    if meta_bits:
        return f"{tema} - {' · '.join(meta_bits)}"
    return tema


@app.get("/api/obs/recording/status")
async def obs_recording_status_endpoint():
    """Sprint 18 C1: estado de grabacion actual de OBS + flag auto-record."""
    from obs_recorder import status as recorder_status
    client = obs.cliente() if obs.is_connected() else None
    return await recorder_status(client)


@app.post("/api/obs/recording/start")
async def obs_recording_start_endpoint(payload: dict | None = None):
    """Sprint 18 C1: arranca grabacion OBS contra <repo>/recordings/<slug>/.

    Body: {slug?: str} - si no se pasa, usa el slug de la pauta cargada.
    """
    from obs_recorder import start_recording
    payload = payload or {}
    slug = (payload.get("slug") or "").strip()
    if not slug and queue.loaded():
        slug = queue.slug
    if not slug:
        return JSONResponse({"error": "slug requerido (carga una pauta o pasalo en el body)"}, status_code=400)
    if not obs.is_connected():
        return JSONResponse({"error": "OBS desconectado"}, status_code=400)
    res = await start_recording(obs.cliente(), slug)
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


@app.post("/api/obs/recording/stop")
async def obs_recording_stop_endpoint():
    """Sprint 18 C1: para la grabacion actual y captura el path generado."""
    from obs_recorder import stop_recording
    if not obs.is_connected():
        return JSONResponse({"error": "OBS desconectado"}, status_code=400)
    res = await stop_recording(obs.cliente())
    if not res.get("ok"):
        return JSONResponse(res, status_code=400)
    return res


@app.post("/api/obs/recording/auto-toggle")
async def obs_recording_auto_toggle(payload: dict | None = None):
    """Sprint 18 C1: activa/desactiva auto-record al cargar pauta.

    Body: {on: bool}
    """
    from obs_recorder import set_auto_record, is_auto_record
    payload = payload or {}
    on = bool(payload.get("on", not is_auto_record()))
    set_auto_record(on)
    return {"ok": True, "auto_record": is_auto_record()}


@app.get("/api/obs/recording/last")
async def obs_recording_last(slug: str | None = None):
    """Sprint 18 C2: devuelve el path del ultimo master grabado para un slug.

    Si slug no se pasa, usa el de la pauta cargada. Para integracion con
    TarroTeaser card (autorelleno del video_path).
    """
    from obs_recorder import last_recording_path
    if not slug and queue.loaded():
        slug = queue.slug
    if not slug:
        return {"ok": False, "error": "slug requerido"}
    path = last_recording_path(slug)
    return {"ok": True, "slug": slug, "path": path}


@app.post("/api/obs/setup-auto")
async def obs_setup_auto_endpoint(payload: dict | None = None):
    """
    Sprint 18 B2: Auto-setup escenas + sources del template Retrotarros Standard.

    Body opcional:
        dry_run (bool, default True): si True solo devuelve el plan sin
            tocar OBS. Si False ejecuta los CreateScene + CreateInput.

    Idempotente: nunca sobreescribe escenas o inputs ya existentes.

    Respuesta:
        - dry_run True: {dry_run: true, plan: {...}, would_create_scenes, would_create_inputs}
        - dry_run False: {dry_run: false, created, skipped, errors, plan}
    """
    from obs_setup import apply_template
    payload = payload or {}
    dry_run = bool(payload.get("dry_run", True))
    if not obs.is_connected():
        return JSONResponse({"error": "OBS desconectado"}, status_code=400)
    client = obs.cliente()
    try:
        result = await apply_template(client, dry_run=dry_run)
    except Exception as e:
        return JSONResponse({"error": f"fallo apply_template: {e}"}, status_code=500)
    return result


@app.post("/api/obs/escena")
async def obs_set_escena(payload: dict):
    """
    Cambia la escena en OBS. Acepta nombre real o alias por voz.
    Body: { "escena": "camara koko" } o { "escena": "cam-koko" }
    """
    if not obs.is_connected():
        return JSONResponse({"error": "OBS no conectado"}, status_code=400)
    nombre = (payload.get("escena") or "").strip()
    if not nombre:
        return JSONResponse({"error": "escena vacia"}, status_code=400)
    real = obs.resolver_escena(nombre)
    try:
        await obs.cliente().set_scene(real)
    except obs.OBSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    tracker.mark_input()
    stats.cambios_escena += 1
    return {"ok": True, "escena": real}


@app.post("/api/obs/fuente")
async def obs_set_fuente(payload: dict):
    """
    Muestra u oculta una fuente dentro de una escena.
    Body: { "escena": "cam-cenital", "fuente": "logo-retrotarros", "visible": true }
    O via alias: { "alias": "logo", "visible": true }  (busca en alias.fuentes)
    """
    if not obs.is_connected():
        return JSONResponse({"error": "OBS no conectado"}, status_code=400)

    alias = (payload.get("alias") or "").strip().lower()
    if alias:
        fuentes_map = obs.get_alias().get("fuentes", {})
        if alias not in fuentes_map:
            return JSONResponse({"error": f"alias '{alias}' no esta en obs-aliases.json"}, status_code=400)
        escena, fuente = fuentes_map[alias]
    else:
        escena = (payload.get("escena") or "").strip()
        fuente = (payload.get("fuente") or "").strip()
        if not escena or not fuente:
            return JSONResponse({"error": "falta escena o fuente"}, status_code=400)
        escena = obs.resolver_escena(escena)

    visible = bool(payload.get("visible", True))
    try:
        await obs.cliente().set_source_enabled(escena, fuente, visible)
    except obs.OBSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    tracker.mark_input()
    return {"ok": True, "escena": escena, "fuente": fuente, "visible": visible}


@app.post("/api/obs/auto-escena")
async def obs_auto_escena(payload: dict):
    """
    Activa o desactiva el hook auto-escena al hablar.
    Body: { "activo": true|false }
    """
    obs_state.auto_scene_on_speak = bool(payload.get("activo", False))
    return {"ok": True, "auto_scene_on_speak": obs_state.auto_scene_on_speak}


@app.post("/api/obs/close-up")
async def obs_close_up(payload: dict):
    """
    Reaccion "toma cercana a X": cambia escena de close-up, TarroBot dice
    frase WOW + cara excited y queda en close-up hasta que se diga
    "gracias TarroBot" o se llame /api/obs/gracias.

    Body: { "tema": "cartucho" | "caja" | "consola" | ... }
    """
    if not obs.is_connected():
        return JSONResponse({"error": "OBS no conectado"}, status_code=400)

    tema = (payload.get("tema") or "").strip()
    if not tema:
        return JSONResponse({"error": "tema vacio (ej: cartucho)"}, status_code=400)

    escena_target = obs.resolver_close_up(tema)
    if not escena_target:
        return JSONResponse({
            "error": f"no encontre close-up para '{tema}'. Edita "
                     f"studio/obs-aliases.json en close_ups."
        }, status_code=404)

    # Guardar escena previa para volver despues
    async with obs_state.lock:
        actual = await _obs_escena_actual_safe()
        # Solo guardar si NO estamos ya en close-up (evita perder la escena
        # real cuando se piden dos close-ups seguidos)
        if not obs_state.in_close_up and actual and actual != escena_target:
            obs_state.escena_previa = actual
        obs_state.in_close_up = True
        ok = await _obs_cambiar_escena_segura(escena_target)
        if not ok:
            obs_state.in_close_up = False
            return JSONResponse({"error": "fallo cambio de escena"}, status_code=500)

    # TarroBot dice WOW con cara excited
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    frase = pick_no_repeat(WOW_FRASES, "wow")
    audio_url = await _hablar_frase(
        frase, "excited", f"MIRA ESE {tema.upper()}", voz, pitch, rate
    )
    stats.close_ups += 1
    return {
        "ok": True,
        "tema": tema,
        "escena": escena_target,
        "frase": frase,
        "audio_url": audio_url,
    }


@app.post("/api/obs/gracias")
async def obs_gracias(payload: dict):
    """
    Cierra el close-up: TarroBot dice frase de agradecimiento y volvemos a
    la escena previa (la general).
    """
    if not obs_state.in_close_up:
        # Sprint 10 A3: si no estabamos en close-up, "gracias TarroBot"
        # significa cierre del programa → redirigir a despedir.
        return await despedir(payload)

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    frase = pick_no_repeat(GRACIAS_FRASES, "gracias")
    # Primero hablar (cara happy)
    audio_url = await _hablar_frase(
        frase, "happy", "VOLVEMOS", voz, pitch, rate
    )

    # Luego volver a la escena previa (con pequeño delay para que la frase
    # se escuche antes del corte)
    async def _volver_diferido():
        await asyncio.sleep(max(1.5, len(frase) * 0.06))
        async with obs_state.lock:
            target = obs_state.escena_previa or obs.get_alias().get("default_scene")
            if target:
                await _obs_cambiar_escena_segura(target)
            obs_state.in_close_up = False
            obs_state.escena_previa = None

    asyncio.create_task(_volver_diferido())
    return {"ok": True, "audio_url": audio_url, "frase": frase}


@app.post("/api/state")
async def set_state(payload: dict):
    """
    Cambia solo el estado visual de TarroBot.
    Body: { "estado": "idle|talking|excited|sleep|thinking|winking|confused|glitched|fact|happy|sad|angry|loading|bored|drowsy" }
    """
    estado = payload.get("estado", "idle")
    estados_validos = ESTADOS + ["bored", "drowsy"]
    if estado not in estados_validos:
        return JSONResponse({"error": f"Estado invalido. Validos: {estados_validos}"}, status_code=400)

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

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    generate_if_missing = bool(payload.get("generate_if_missing", False))

    db = cargar_db()
    matches = buscar(tema, db)
    dato = None

    if matches:
        # Si hay varios matches, elige aleatorio
        import random
        dato = random.choice(matches)
    elif generate_if_missing:
        # Sprint 10 A5: rate limit solo cuando va a llamar Claude
        espera = llm_cooldown_check("cuentame")
        if espera is not None:
            return JSONResponse(
                {"error": f"cooldown LLM: espera {espera:.1f}s antes de pedir otro dato a Claude"},
                status_code=429,
            )
        async with _procesando(f"buscando {tema} con Claude..."):
            result = await asyncio.to_thread(generar_con_llm, tema)
        if result:
            llm_resolver.track_llm_call("cuentame")
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
    mp3 = await asyncio.to_thread(generar_tts, dato, voz, pitch, rate)
    audio_url = f"/audio/{mp3.name}" if mp3 else None

    # Sprint 10 B1: contadores
    stats.datos_hablados += 1
    stats.ultimo_tema = dato.get("tema", "")
    stats.ultimo_dato_ts = time.time()

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


async def _hablar_frase(texto: str, estado: str, label: str, voz: str,
                        pitch: Optional[str] = None, rate: Optional[str] = None) -> Optional[str]:
    """
    Genera TTS de una frase suelta (sin tema asociado) y dispara WS.
    Usado por /api/saludar, /api/despedir, /api/catchphrase, /api/opinar, /api/precio.
    """
    import time
    if pitch is None or rate is None:
        _, p_default, r_default = resolver_preset(_voz_preset_actual)
        pitch = pitch or p_default
        rate = rate or r_default
    fake_dato = {
        "id": f"frase-{int(time.time() * 1000)}",
        "tema": "frase",
        "texto": texto,
        "estado": estado,
        "consola": "", "ano": 0, "editor": "",
    }
    mp3 = await asyncio.to_thread(generar_tts, fake_dato, voz, pitch, rate)
    audio_url = f"/audio/{mp3.name}" if mp3 else None

    # Sprint 9: hook pre-hablar para auto-escena OBS
    await _hook_pre_hablar()

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

    # Sprint 10 A1: hook post-hablar event-driven. Se dispara cuando el
    # cliente HTML reporta audio.onended via /api/audio-finished. Fallback:
    # timeout duro para evitar listener huerfano si el audio nunca termina.
    if obs_state.auto_scene_on_speak and not obs_state.in_close_up:
        async def _post():
            await _hook_post_hablar()
        tracker.add_finished_listener(_post)
        # fallback timeout (3x estimacion) por si el audio.onended nunca llega
        fallback = max(8.0, len(texto) * 0.12) + 2.0
        asyncio.create_task(_post_hablar_fallback(fallback))
    return audio_url


async def _post_hablar_fallback(delay: float) -> None:
    """Si el evento audio.onended nunca llega (cliente caido, mute, etc),
    dispara el hook post-hablar despues de un timeout generoso."""
    await asyncio.sleep(delay)
    if tracker.is_speaking:
        # forzar transicion para que dispare listeners pendientes
        tracker.mark_speaking(False)


def generar_respuesta_chat_llm(viewer_name: str, viewer_text: str,
                                platform: str = "chat",
                                context: Optional[str] = None) -> Optional[dict]:
    """
    Sprint 14: TarroBot responde a un mensaje del chat usando Claude.
    Devuelve {texto, estado} con la respuesta lista para TTS.
    """
    try:
        import anthropic
    except ImportError:
        return None
    import os, re as _re
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    client = anthropic.Anthropic(api_key=api_key)

    contexto_extra = (
        f"Contexto adicional (pauta del episodio actual): {context}\n"
        if context else ""
    )

    prompt = f"""Eres TarroBot, mascota del canal Retrotarros sobre videojuegos retro.
Un viewer te escribio en el chat de {platform}.

Viewer: "{viewer_name}"
Mensaje: "{viewer_text}"

{contexto_extra}
Devuelve una RESPUESTA corta y con personalidad (1-2 oraciones, max 220 caracteres).
Tambien decide el estado emocional que mejor calza.

Reglas (este texto se reproduce con TTS, por eso reglas estrictas):
- Saludale al viewer por su nombre si tiene sentido natural.
- Espanol ESTRICTAMENTE chileno neutro con TUTEO (tu/tienes/sabes/dime/puedes).
- NO voseo argentino: PROHIBIDO "tenes", "queres", "podes", "sabes (con tilde)",
  "decime", "decis", "vos", "sos", "vení", "andas (con tilde)", "che", "anda".
  USA: "eres", "tienes", "quieres", "puedes", "dices", "ven", "vas", "dime".
- NO palabras argentinas: evita "aca" (usa "aqui"), "andabamos" (usa "estabamos"),
  "me agarraste" (usa "me pillaste"), "pibe" (usa "chico").
- USA TILDES correctas del espanol ortografico (tambien, esta, mi, si, dia, ano).
  Critico para que el TTS pronuncie bien.
- NUMEROS EN PALABRAS para cifras grandes: "20 mil" en vez de "20,000".
- Tono curioso, cercano, vibe retrogaming.
- Si el viewer hace una pregunta tonta o trolea, responde con humor pero sin agresion.
- Estados validos: happy, excited, fact, winking, confused, sad, angry, thinking, talking.

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
        result = json.loads(raw)
        if "texto" in result:
            result["texto"] = chilenizar(result["texto"])
        return result
    except Exception as e:
        print(f"[respond_chat] error: {e}")
        return None


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
Tu humano te pregunta: "¿Qué opinas de {tema}?"

Devuelve una OPINIÓN corta y con personalidad (1-2 oraciones, max 200 caracteres total).
También decide el estado emocional que mejor calza.

Reglas (este texto se reproduce con TTS, por eso reglas estrictas):
- Español ESTRICTAMENTE chileno neutro con TUTEO (tú/tienes/sabes/dime/puedes).
- NO voseo argentino: PROHIBIDO "tenés", "querés", "podés", "sabés", "decime",
  "decís", "vos", "sos", "vení", "andás", "che", "andá". USA: "eres", "tienes",
  "quieres", "puedes", "dices", "ven", "vas", "dime".
- NO palabras argentinas: evita "acá" (usa "aquí"), "andábamos" (usa "estábamos"),
  "me agarraste" (usa "me pillaste"), "pibe" (usa "chico").
- USA TILDES correctas del español ortográfico (también, está, mí, sí, día, año).
  Crítico para que el TTS pronuncie bien.
- NÚMEROS EN PALABRAS para cifras grandes: "20 mil" en vez de "20,000".
  Años sí en cifras: 1996.
- Tono curioso, opinión clara, vibe retrogaming.
- Estados válidos: happy, excited, fact, winking, confused, sad, angry, thinking, talking.
  * Bueno → happy o excited
  * Malo → sad, angry o confused
  * Raro/curioso → confused o thinking
  * Icónico → fact o excited

Devuelve SOLO un JSON válido (sin markdown), formato:
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
        result = json.loads(raw)
        # Filtro anti-voseo (defensa ultima)
        if "texto" in result:
            result["texto"] = chilenizar(result["texto"])
        return result
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

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    # Sprint 15: capa 1 - pauta enriquecida (opinion pre-generada)
    pauta_actual = queue.pauta if queue.loaded() else None
    result = llm_resolver.resolver_opinion(pauta_actual, tema)
    if result:
        print(f"[opinar] cache pauta HIT para '{tema}'")
    else:
        # Sprint 15: capa 2 - cache JSON local
        result = llm_resolver.cache_get("opinar", tema)
        if result:
            print(f"[opinar] cache local HIT para '{tema}'")

    if not result:
        # Sprint 15: modo barato bloquea LLM real
        if llm_resolver.is_modo_barato():
            return JSONResponse({
                "error": "modo barato activo: sin opinion LLM. Cargar pauta con material "
                         "pre-generado o desactivar modo barato."
            }, status_code=503)

        # Sprint 10 A5: rate limit
        espera = llm_cooldown_check("opinar")
        if espera is not None:
            return JSONResponse(
                {"error": f"cooldown LLM: espera {espera:.1f}s antes de otra opinion"},
                status_code=429,
            )

        async with _procesando(f"opinando de {tema}..."):
            result = await asyncio.to_thread(generar_opinion_llm, tema)
        if result:
            llm_resolver.track_llm_call("opinar")
            llm_resolver.cache_save("opinar", tema, result)
    if not result:
        return JSONResponse({"error": "fallo Claude API. Verifica ANTHROPIC_API_KEY y creditos."}, status_code=500)

    texto = result.get("texto", f"No tengo opinion sobre {tema} todavia.")
    estado = result.get("estado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    audio_url = await _hablar_frase(texto, estado, f"¿QUE OPINO DE {tema.upper()}?", voz, pitch, rate)
    stats.opiniones_dadas += 1
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url, "tema": tema}


def generar_opinion_precio_llm(valor: int, juego: str) -> Optional[dict]:
    """Sprint 8.5: opinion extendida sobre un precio con LLM. Solo se llama
    si el usuario explicitamente pide opinion (con_opinion=True)."""
    try:
        import anthropic
    except ImportError:
        return None
    import os, re as _re
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    def _valor_a_palabras(v: int) -> str:
        if v >= 1_000_000:
            return f"{v/1_000_000:.1f} millones de dólares".replace(".0", "")
        if v >= 1000:
            miles = v // 1000
            resto = v % 1000
            return f"{miles} mil dólares" if resto == 0 else f"{miles} mil {resto} dólares"
        return f"{v} dólares"

    valor_str = _valor_a_palabras(valor)
    juego_part = f"para {juego}" if juego else "para este cartucho"

    prompt = f"""Eres TarroBot, mascota del canal Retrotarros sobre videojuegos retro.
Tu humano te pregunta explícitamente: "¿Qué opinas del precio de {valor_str} {juego_part}?"

Devuelve una opinión PERSONAL, 2-3 oraciones, sobre si vale la pena o no, qué pensás del mercado de coleccionismo retro a ese precio, contexto historico breve (si es razonable, escandaloso, ganga). Tono curioso y honesto.

Reglas (texto reproducido por TTS):
- Español ESTRICTAMENTE chileno neutro con TUTEO (tú/tienes/sabes).
- PROHIBIDO voseo argentino ("tenés", "querés", "podés", "sabés", "sos",
  "decime", "decís", "vos", "vení", "che", "andá"). USA: "eres", "tienes",
  "quieres", "puedes", "dices", "vas", "dime".
- Evita "acá" (usa "aquí"), "andábamos" (usa "estábamos"), "me agarraste"
  (usa "me pillaste"), "pibe" (usa "chico").
- USA TILDES correctas.
- NÚMEROS EN PALABRAS ("20 mil" en vez de "20,000").
- Estados válidos: confused, excited, fact, winking, thinking, sad, angry, happy.

Devuelve SOLO JSON: {{"texto": "...", "estado": "..."}}
"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        if "texto" in result:
            result["texto"] = chilenizar(result["texto"])
        return result
    except Exception as e:
        print(f"[precio-opinion] error: {e}")
        return None


@app.post("/api/precio")
async def precio(payload: dict):
    """
    Reacciona segun valor USD. Modos:
      con_opinion=False (default): frase pregenerada rapida segun el rango
      con_opinion=True: usa LLM (Claude) para opinion extendida con contexto

    Body: { "valor_usd": 4500, "juego": "DKC Competition Cart" (opcional),
            "con_opinion": false, "voz": ... }
    """
    try:
        valor = int(payload.get("valor_usd", 0))
    except (TypeError, ValueError):
        return JSONResponse({"error": "valor_usd invalido"}, status_code=400)

    juego = (payload.get("juego") or "").strip()
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    con_opinion = bool(payload.get("con_opinion", False))
    tracker.mark_input()

    # Modo OPINION explicita: LLM da una reaccion personal mas larga
    if con_opinion:
        # Sprint 10 A5: rate limit
        espera = llm_cooldown_check("precio_opinion")
        if espera is not None:
            return JSONResponse(
                {"error": f"cooldown LLM: espera {espera:.1f}s"},
                status_code=429,
            )
        async with _procesando(f"opinando sobre el precio..."):
            result = await asyncio.to_thread(generar_opinion_precio_llm, valor, juego)
        if result:
            llm_resolver.track_llm_call("precio_opinion")
            texto_opinion = result.get("texto", "")
            estado_opinion = result.get("estado", "thinking")
            if estado_opinion not in ESTADOS:
                estado_opinion = "thinking"
            audio_url = await _hablar_frase(
                texto_opinion, estado_opinion,
                f"OPINIÓN PRECIO",
                voz, pitch, rate,
            )
            stats.precios_reaccionados += 1
            stats.opiniones_dadas += 1
            return {"ok": True, "texto": texto_opinion, "estado": estado_opinion,
                    "audio_url": audio_url, "con_opinion": True}
        # Si fallo el LLM, cae al modo rapido

    # Formatear el valor en palabras para que TTS lo pronuncie bien
    # ("20 mil dólares" en vez de "20,000 dólares" que se lee "veinte coma cero cero cero")
    def _valor_a_palabras(v: int) -> str:
        if v >= 1_000_000:
            mill = v / 1_000_000
            return f"{mill:.1f} millones de dólares".replace(".0", "")
        if v >= 1000:
            miles = v // 1000
            resto = v % 1000
            if resto == 0:
                return f"{miles} mil dólares"
            return f"{miles} mil {resto} dólares"
        return f"{v} dólares"

    valor_str = _valor_a_palabras(valor)

    # Reacción según rango (con tildes y números en palabras para que TTS pronuncie bien)
    if valor >= 20000:
        estado = "confused"
        texto = f"¿{valor_str}? Eso ya no es coleccionismo, es un museo. Imposible de pagar."
    elif valor >= 10000:
        estado = "excited"
        texto = f"¡{valor_str}! Eso es plata para un auto. Locura total."
    elif valor >= 5000:
        estado = "excited"
        texto = f"{valor_str} es una locura. ¡Mind blown total!"
    elif valor >= 2000:
        estado = "fact"
        texto = f"{valor_str} ya es para coleccionistas serios. Cartucho serio."
    elif valor >= 500:
        estado = "thinking"
        texto = f"{valor_str} está caro pero no es escandaloso. Razonable para piezas raras."
    elif valor >= 100:
        estado = "talking"
        texto = f"{valor_str} es precio normal para retrogaming en buen estado."
    elif valor > 0:
        estado = "happy"
        texto = f"¿{valor_str}? Eso es chollo, ¡cómprate dos!"
    else:
        estado = "confused"
        texto = "Sin precio no puedo opinar. Dime cuánto sale."

    if juego:
        texto = f"¿{juego} a {valor_str}? " + texto

    audio_url = await _hablar_frase(texto, estado, "REACCION PRECIO", voz, pitch, rate)
    stats.precios_reaccionados += 1
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/random")
async def random_dato(payload: dict):
    """
    Elige un dato random de la base local, filtrado opcionalmente por categoria.
    Body: { "categoria": "all|consola|juego|musica|nfr", "voz": ... }
    """
    import random as _rnd
    categoria = (payload.get("categoria") or "all").lower()
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
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

    # Sprint 10 A2: anti-repeticion. Ventana mas grande para datos (15)
    dato = pick_no_repeat(candidatos, f"random_{categoria}", n_recent=15)

    mp3 = await asyncio.to_thread(generar_tts, dato, voz, pitch, rate)
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
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    stats.saludos += 1
    texto = pick_no_repeat(SALUDOS_GEEK, "saludos")
    audio_url = await _hablar_frase(texto, "excited", "HOLA HOLA", voz, pitch, rate)
    return {"ok": True, "texto": texto, "audio_url": audio_url}


async def _acelerar_dormir():
    """
    Sprint 8.5: despues de una despedida, TarroBot va a sleep en pocos segundos.
    Espera que termine la frase del chao (~5s), pasa a drowsy, espera otro
    poco y luego a sleep. Si el usuario interactua antes, cancela.
    """
    # Esperar a que termine la frase del chao (audio.onended marca is_speaking=False)
    await asyncio.sleep(6)
    if tracker.is_speaking:
        return  # algo nuevo paso, cancelar
    ts_referencia = tracker.last_input_ts
    # Bored
    await manager.broadcast_live({"tipo": "estado-idle", "estado": "bored"})
    tracker.current_idle_state = "bored"
    await asyncio.sleep(3)
    if tracker.last_input_ts != ts_referencia or tracker.is_speaking:
        return
    # Drowsy
    await manager.broadcast_live({"tipo": "estado-idle", "estado": "drowsy"})
    tracker.current_idle_state = "drowsy"
    await asyncio.sleep(3)
    if tracker.last_input_ts != ts_referencia or tracker.is_speaking:
        return
    # Sleep
    await manager.broadcast_live({"tipo": "estado-idle", "estado": "sleep"})
    tracker.current_idle_state = "sleep"
    # Forzar last_input_ts atras asi se queda dormido (no vuelve a idle solo)
    tracker.last_input_ts = time.time() - IDLE_SLEEP_AFTER - 10


@app.post("/api/despedir")
async def despedir(payload: dict):
    """Reproduce una despedida corta random con estado winking.
    Despues de despedirse, TarroBot acelera la somnolencia y se duerme."""
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    stats.despedidas += 1
    texto = pick_no_repeat(DESPEDIDAS_CORTAS, "despedidas")
    audio_url = await _hablar_frase(texto, "winking", "HASTA LUEGO", voz, pitch, rate)
    # Sprint 8.5: agendar transicion bored -> drowsy -> sleep
    asyncio.create_task(_acelerar_dormir())
    return {"ok": True, "texto": texto, "audio_url": audio_url}


@app.post("/api/escuchando")
async def escuchando(payload: dict):
    """Sprint 8.x: respuesta a '¿me estás escuchando?' o variantes."""
    import random as _rnd
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    texto = pick_no_repeat(ESCUCHANDO_FRASES, "escuchando")
    estado = _rnd.choice(["happy", "winking", "excited"])
    audio_url = await _hablar_frase(texto, estado, "TE ESCUCHO", voz, pitch, rate)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/personal")
async def personal(payload: dict):
    """
    Sprint 10 B4: respuesta a preguntas sobre TarroBot mismo.
    Body: { "categoria": "nombre"|"origen"|"edad"|"favorito"|... }
    Si no se pasa categoria, usa "generico".
    """
    import random as _rnd
    categoria = (payload.get("categoria") or "generico").strip().lower()
    if categoria not in PERSONALES_FRASES:
        categoria = "generico"
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    texto = pick_no_repeat(PERSONALES_FRASES[categoria], f"personal_{categoria}")
    # Estado segun categoria
    estado_map = {
        "nombre": "happy", "origen": "fact", "edad": "winking",
        "favorito": "excited", "consola_fav": "excited",
        "familia": "happy", "comida": "winking", "sueño": "thinking",
        "como_funciona": "fact", "generico": "thinking",
    }
    estado = estado_map.get(categoria, "happy")
    audio_url = await _hablar_frase(
        texto, estado, f"PERSONAL · {categoria.upper()}", voz, pitch, rate
    )
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url,
            "categoria": categoria}


@app.post("/api/como-estas")
async def como_estas(payload: dict):
    """Sprint 8.x: respuesta a '¿cómo estás?' con frase random."""
    import random as _rnd
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    texto = pick_no_repeat(COMO_ESTAS_FRASES, "como_estas")
    estado = _rnd.choice(["happy", "excited", "winking", "talking"])
    audio_url = await _hablar_frase(texto, estado, "¿CÓMO ESTÁS?", voz, pitch, rate)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/que-hacemos")
async def que_hacemos(payload: dict):
    """
    Sprint 8.x: respuesta a '¿qué hacemos hoy?'.
    Si hay pauta cargada -> respuesta contextual mencionando el episodio
    y cuantos datos/melodias hay preparados.
    Si NO hay pauta -> frase random generica de QUE_HACEMOS_FRASES.
    """
    import random
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    if queue.loaded():
        episodio = queue.pauta.get("episodio") or queue.slug.replace("-", " ").title()
        n_datos = len(queue.items_datos())
        n_melodias = len(queue.items_melodias())

        # Sprint 10 B1: si ya hablamos algunos datos, decir el progreso
        idx = queue.indice
        si_avanzados = idx >= 0
        restantes = max(0, n_datos - (idx + 1))

        if si_avanzados and restantes > 0:
            plantillas = [
                f"Vamos por el dato {idx + 1} de {n_datos} de {episodio}. Quedan {restantes}.",
                f"Estamos a la mitad de {episodio}, vamos por el {idx + 1} de {n_datos}.",
                f"Llevamos {idx + 1} datos del top, faltan {restantes} para cerrar.",
                f"Seguimos con {episodio}, próximo es el dato {idx + 2} de {n_datos}.",
            ]
        elif si_avanzados and restantes == 0:
            plantillas = [
                f"Ya cerramos {episodio} completo, ¡los {n_datos} datos sobre la mesa!",
                f"Llegamos al final del top de {episodio}. ¿Lo cerramos con catchphrase?",
                f"Top de {episodio} terminado. ¿Despedida o ronda libre?",
            ]
        else:
            plantillas = [
                f"Hoy vamos con {episodio}. Te traje {n_datos} datos curiosos para soltar.",
                f"Te propongo arrancar con {episodio}. Tengo {n_datos} datos esperando.",
                f"Tema del día: {episodio}. Ya cargué {n_datos} datos. ¿Empezamos?",
                f"Lista lista para grabar {episodio} con {n_datos} datos preparados.",
            ]
            if n_melodias > 0:
                plantillas += [
                    f"Hoy es {episodio}. Tengo {n_datos} datos y {n_melodias} melodías listas para acompañar.",
                    f"Hablemos de {episodio}. Cargué {n_datos} datos y {n_melodias} canciones retro.",
                    f"Vamos con {episodio}. {n_datos} datos y unas melodías para el ambiente.",
                ]

        # Sprint 10 B1: si la sesion lleva tiempo, agregar comentario
        mins = stats.mins_activos()
        if mins >= 30:
            plantillas.append(
                f"Llevamos {mins} minutos hablando de {episodio}. Esto se está poniendo épico."
            )

        texto = pick_no_repeat(plantillas, "que_hacemos_pauta")
        estado = "excited"
        label = f"PAUTA DEL DÍA · {queue.slug.upper()}"
    else:
        texto = pick_no_repeat(QUE_HACEMOS_FRASES, "que_hacemos")
        estado = random.choice(["excited", "thinking", "happy", "winking"])
        label = "¿QUÉ HACEMOS HOY?"

    audio_url = await _hablar_frase(texto, estado, label, voz, pitch, rate)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/despertar")
async def despertar(payload: dict):
    """
    Sprint 8.5: TarroBot 'despierta' cuando le hablamos estando dormido o aburrido.
    Reproduce una frase tipo 'sorry, aca estoy' y vuelve a idle.
    """
    import random as _rnd
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    # Forzar volver a idle desde el estado dormido
    tracker.current_idle_state = "idle"
    texto = pick_no_repeat(DESPERTAR_FRASES, "despertar")
    audio_url = await _hablar_frase(texto, "happy", "DESPERTANDO...", voz, pitch, rate)
    return {"ok": True, "texto": texto, "audio_url": audio_url}


@app.post("/api/catchphrase")
async def catchphrase(payload: dict):
    """Reproduce una catchphrase random del canal Retrotarros (Sprint 7.3)."""
    import random as _rnd
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    stats.catchphrases += 1
    texto = pick_no_repeat(CATCHPHRASES, "catchphrases")
    estado = _rnd.choice(CATCHPHRASE_ESTADOS)
    audio_url = await _hablar_frase(texto, estado, "RETROTARROS!", voz, pitch, rate)
    return {"ok": True, "texto": texto, "estado": estado, "audio_url": audio_url}


@app.post("/api/audio-finished")
async def audio_finished():
    """El cliente HTML llama esto cuando termina de reproducir un MP3."""
    tracker.mark_speaking(False)
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 10 C6: recetas (secuencias compuestas)
# ─────────────────────────────────────────────────────────────────────────

RECETAS_PATH = STUDIO / "tarrobot-recetas.json"


def _cargar_recetas() -> dict:
    if not RECETAS_PATH.exists():
        return {"recetas": {}}
    try:
        return json.loads(RECETAS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[recetas] error parseando {RECETAS_PATH}: {e}")
        return {"recetas": {}}


# Mapa accion → endpoint async para ejecutar pasos de recetas
_RECETA_DISPATCH = {
    # se llena lazy en _ejecutar_paso porque las funciones aun no estan
    # definidas en este punto del archivo (el endpoint se llama mas abajo).
}


async def _ejecutar_paso(paso: dict) -> dict:
    accion = (paso.get("accion") or "").strip().lower()
    params = paso.get("params") or {}
    if accion == "esperar":
        await asyncio.sleep(float(params.get("segundos", 1)))
        return {"ok": True, "esperado": params.get("segundos", 1)}
    # Despachar a endpoints existentes
    handlers = {
        "obs_escena": obs_set_escena,
        "obs_fuente": obs_set_fuente,
        "obs_close_up": obs_close_up,
        "obs_gracias": obs_gracias,
        "saludar": saludar,
        "despedir": despedir,
        "catchphrase": catchphrase,
        "como_estas": como_estas,
        "que_hacemos": que_hacemos,
        "escuchando": escuchando,
        "despertar": despertar,
        "personal": personal,
        "cuentame": cuentame,
        "opinar": opinar,
        "precio": precio,
        "queue_next": queue_next,
        "queue_melodia": queue_melodia,
    }
    handler = handlers.get(accion)
    if not handler:
        return {"ok": False, "error": f"accion desconocida en receta: '{accion}'"}
    try:
        result = await handler(params)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    if hasattr(result, "body"):
        try:
            result = json.loads(result.body.decode())
        except Exception:
            result = {"ok": False, "error": "respuesta interna invalida"}
    return result


@app.get("/api/recetas")
async def recetas_listar():
    """Lista las recetas configuradas en studio/tarrobot-recetas.json."""
    data = _cargar_recetas()
    return {
        "ok": True,
        "recetas": {
            nombre: {
                "titulo": r.get("titulo", nombre),
                "descripcion": r.get("descripcion", ""),
                "pasos": len(r.get("pasos", [])),
            }
            for nombre, r in data.get("recetas", {}).items()
        }
    }


@app.post("/api/receta/run")
async def receta_run(payload: dict):
    """
    Ejecuta una receta por nombre.
    Body: { "nombre": "intro_episodio" }
    Corre los pasos en orden, secuencial. Si un paso falla, sigue
    con el siguiente (best effort) y reporta cuales fallaron.
    """
    nombre = (payload.get("nombre") or "").strip()
    if not nombre:
        return JSONResponse({"error": "nombre vacio"}, status_code=400)
    data = _cargar_recetas()
    receta = data.get("recetas", {}).get(nombre)
    if not receta:
        return JSONResponse(
            {"error": f"receta '{nombre}' no existe",
             "disponibles": list(data.get("recetas", {}).keys())},
            status_code=404,
        )
    pasos = receta.get("pasos", [])
    if not pasos:
        return JSONResponse({"error": f"receta '{nombre}' no tiene pasos"}, status_code=400)

    tracker.mark_input()
    resultados = []
    for i, paso in enumerate(pasos):
        try:
            r = await _ejecutar_paso(paso)
            resultados.append({"paso": i + 1, "accion": paso.get("accion"), "ok": r.get("ok", True)})
        except Exception as e:
            resultados.append({"paso": i + 1, "accion": paso.get("accion"), "ok": False, "error": str(e)})
    return {
        "ok": True,
        "receta": nombre,
        "titulo": receta.get("titulo", nombre),
        "pasos_ejecutados": len(resultados),
        "resultados": resultados,
    }


# ─────────────────────────────────────────────────────────────────────────
# Sprint 12 C1: presentador asistente - sugerir y aplicar reorden
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/queue/sugerir-orden")
async def queue_sugerir_orden(payload: Optional[dict] = None):
    """
    Sprint 12 C1: con LLM analiza la pauta cargada y propone orden mas
    dinamico. NO aplica nada, solo devuelve sugerencia para que el
    operador acepte o rechace.
    """
    if not queue.loaded():
        return JSONResponse({"error": "no hay pauta cargada"}, status_code=400)
    datos_no_melodia = queue.items_datos()
    if len(datos_no_melodia) < 3:
        return JSONResponse({"error": "se necesitan al menos 3 datos para reordenar"}, status_code=400)

    espera = llm_cooldown_check("sugerir_orden")
    if espera is not None:
        return JSONResponse({"error": f"cooldown LLM: espera {espera:.1f}s"}, status_code=429)

    async with _procesando("analizando orden con Claude..."):
        result = await asyncio.to_thread(generar_reorden_pauta_con_llm, queue.pauta)
    if not result:
        return JSONResponse({"error": "fallo el LLM de reorden"}, status_code=500)
    llm_resolver.track_llm_call("sugerir_orden")

    # Mapear indices a previews para que el panel muestre nombres
    nuevo_orden = result.get("nuevo_orden", [])
    preview = []
    for nuevo_pos, idx_orig in enumerate(nuevo_orden):
        if 0 <= idx_orig < len(datos_no_melodia):
            d = datos_no_melodia[idx_orig]
            preview.append({
                "pos_nueva": nuevo_pos,
                "indice_original": idx_orig,
                "tema": d.get("tema", ""),
                "estado": d.get("estado", ""),
            })
    return {
        "ok": True,
        "nuevo_orden": nuevo_orden,
        "razon_global": result.get("razon_global", ""),
        "razones_por_dato": result.get("razones_por_dato", []),
        "preview": preview,
    }


@app.post("/api/queue/aplicar-orden")
async def queue_aplicar_orden(payload: dict):
    """
    Aplica un nuevo_orden devuelto por sugerir-orden. Reordena los datos
    NO melodia en la pauta cargada y la guarda en disco.
    Body: { "nuevo_orden": [3,1,5,0,7,2,6,4] }
    """
    if not queue.loaded():
        return JSONResponse({"error": "no hay pauta cargada"}, status_code=400)
    nuevo = payload.get("nuevo_orden")
    if not isinstance(nuevo, list) or not all(isinstance(x, int) for x in nuevo):
        return JSONResponse({"error": "nuevo_orden debe ser lista de enteros"}, status_code=400)

    datos = queue.pauta.get("datos", [])
    datos_no_melodia = [d for d in datos if d.get("tipo") != "melodia"]
    datos_melodia = [d for d in datos if d.get("tipo") == "melodia"]

    if sorted(nuevo) != list(range(len(datos_no_melodia))):
        return JSONResponse(
            {"error": f"nuevo_orden invalido (debe contener 0..{len(datos_no_melodia)-1} sin repetir)"},
            status_code=400,
        )

    async with queue.lock:
        reordenados = [datos_no_melodia[i] for i in nuevo]
        # Mantener melodias al final tal como estaban
        queue.pauta["datos"] = reordenados + datos_melodia
        # Reset indice porque las posiciones cambiaron
        queue.indice = -1
        # Persistir cambio en disco
        try:
            guardar_pauta(queue.pauta)
        except Exception as e:
            print(f"[reorden] no se pudo guardar pauta: {e}")
    tracker.mark_input()
    return {"ok": True, "indice": -1, "total": len(reordenados)}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 12 C2: descripcion + titulos + thumbnails del episodio
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/episodio/exportar-descripcion")
async def episodio_exportar_descripcion(payload: Optional[dict] = None):
    """
    Sprint 12 C2: genera material de publicacion para el episodio.
    Usa session_log si hay (timestamps reales) o estimacion si no.
    Guarda el resultado en studio/exports/<slug>-publicacion.txt.

    Body opcional: { "incluir_session_log": true }   (default true si hay)
    """
    payload = payload or {}
    if not queue.loaded():
        return JSONResponse({"error": "no hay pauta cargada"}, status_code=400)

    usar_session_log = bool(payload.get("incluir_session_log", True))
    session_log = queue.session_log if usar_session_log and queue.session_log else None

    # Sprint 15: usar publicacion pre-generada en la pauta si existe
    result = llm_resolver.resolver_publicacion(queue.pauta)
    if result:
        print("[export_desc] pauta HIT - usando publicacion pre-generada")
        # Si tenemos session_log con timestamps reales, sobreescribir los
        # timestamps tentativos de la pauta
        if session_log:
            # Generar lista de timestamps reales en el formato esperado
            from tarrobot import _ms_to_srt_timestamp
            result = dict(result)  # copy
            result["timestamps"] = [
                {
                    "ts": _ms_to_srt_timestamp(int(e.get("timestamp_session_ms", 0)))[:8],
                    "label": e.get("tema", ""),
                }
                for e in session_log
            ]
    else:
        if llm_resolver.is_modo_barato():
            return JSONResponse({
                "error": "modo barato: no hay publicacion pre-generada en esta pauta."
            }, status_code=503)
        espera = llm_cooldown_check("export_desc")
        if espera is not None:
            return JSONResponse({"error": f"cooldown LLM: espera {espera:.1f}s"}, status_code=429)
        async with _procesando("generando descripcion + titulos + thumbnails..."):
            result = await asyncio.to_thread(
                generar_descripcion_episodio_con_llm, queue.pauta, session_log
            )
        if result:
            llm_resolver.track_llm_call("exportar_descripcion")
    if not result:
        return JSONResponse({"error": "fallo el LLM de descripcion"}, status_code=500)

    # Guardar en disco para que Luis lo pueda copiar/pegar facil
    exports_dir = STUDIO / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    slug = queue.slug or "episodio"
    out_path = exports_dir / f"{slug}-publicacion.txt"

    lineas = []
    lineas.append("=" * 60)
    lineas.append(f"PUBLICACION: {queue.pauta.get('episodio', slug)}")
    lineas.append(f"Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lineas.append(f"Modo timestamps: {'GRABACION REAL' if session_log else 'ESTIMADO'}")
    lineas.append("=" * 60)
    lineas.append("")
    lineas.append("--- TITULOS SUGERIDOS ---")
    for i, t in enumerate(result.get("titulos", []), 1):
        lineas.append(f"  {i}. {t}")
    lineas.append("")
    lineas.append("--- DESCRIPCION ---")
    lineas.append(result.get("descripcion", ""))
    lineas.append("")
    lineas.append("--- TIMESTAMPS ---")
    for ts in result.get("timestamps", []):
        lineas.append(f"  {ts.get('ts', '')} - {ts.get('label', '')}")
    lineas.append("")
    lineas.append("--- HASHTAGS ---")
    lineas.append(" ".join(result.get("hashtags", [])))
    lineas.append("")
    lineas.append("--- PROMPTS PARA THUMBNAILS (texto en ingles) ---")
    for i, p in enumerate(result.get("thumbnail_prompts", []), 1):
        lineas.append(f"  {i}. {p}")
    lineas.append("")
    lineas.append("--- INSTAGRAM POST ---")
    lineas.append(result.get("ig_post", ""))
    lineas.append("")

    out_path.write_text("\n".join(lineas), encoding="utf-8")

    return {
        "ok": True,
        "path": str(out_path),
        "data": result,
    }


# ─────────────────────────────────────────────────────────────────────────
# Sprint 17: TarroTeaser - genera Short vertical 1080x1920 desde master
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/teaser/generar")
async def teaser_generar(payload: dict):
    """
    Encola un job de TarroTeaser.

    Body:
        video_path (str, requerido): ruta absoluta al MP4 master
        slug (str, requerido): kebab-case del episodio (ej. n64-top-precios)
        ep_type (str, opcional): forzar tipo (auto-detecta del slug si no)
        num_highlights (int, default 3): clips del centro
        clip_duration (float, default 3.0): duracion MIN del clip
        max_clip_duration (float, default 6.0): duracion MAX del clip
        model (str, default 'small'): modelo Whisper
        out_dir (str, opcional): override directorio salida

    Respuesta: {ok, job_id, queue_size}
    El progreso se publica via WS con tipos:
        teaser.queued / teaser.started / teaser.progress / teaser.done / teaser.error
    """
    payload = payload or {}
    video_path = (payload.get("video_path") or "").strip()
    slug = (payload.get("slug") or "").strip()
    if not video_path or not slug:
        return JSONResponse({"error": "video_path y slug son requeridos"}, status_code=400)

    video = Path(video_path)
    if not video.exists():
        return JSONResponse({"error": f"video no existe: {video_path}"}, status_code=404)

    # Validar slug kebab-case (defensa extra; tarroteaser tambien valida)
    import re as _re
    if not _re.match(r"^[a-z0-9-]+$", slug):
        return JSONResponse({"error": "slug invalido (kebab-case requerido)"}, status_code=400)

    params = {
        k: payload.get(k)
        for k in ("ep_type", "num_highlights", "clip_duration",
                  "max_clip_duration", "model", "out_dir")
        if payload.get(k) is not None
    }
    job_id = await teaser_jobs.submit(str(video.resolve()), slug, **params)
    return {
        "ok": True,
        "job_id": job_id,
        "queue_size": teaser_jobs._queue.qsize(),
    }


@app.get("/api/teaser/job/{job_id}")
async def teaser_get_job(job_id: str):
    """Devuelve el estado completo de un job de teaser."""
    job = teaser_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "job no existe"}, status_code=404)
    return {"ok": True, "job": job.to_dict()}


@app.get("/api/teaser/list")
async def teaser_list(limit: int = 20):
    """Devuelve los ultimos N jobs (default 20) ordenados por created_at desc."""
    return {
        "ok": True,
        "jobs": teaser_jobs.list_recent(limit=limit),
        "current_job_id": teaser_jobs.current_job_id(),
    }


@app.post("/api/teaser/cancel/{job_id}")
async def teaser_cancel(job_id: str):
    """Cancela un job. Si esta corriendo, solo marca el flag (no detiene ffmpeg)."""
    ok = await teaser_jobs.cancel(job_id)
    if not ok:
        return JSONResponse({"error": "no se pudo cancelar (no existe o ya termino)"}, status_code=400)
    return {"ok": True, "job_id": job_id}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 19: TarroShort (MP4 vertical para redes con TarroBot leyendo)
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/tarroshort/generar")
async def tarroshort_generar(payload: dict):
    """
    Encola un job de TarroShort.

    Body (una de dos formas):
      A) Desde pauta:  { "pauta_slug": "snes-top-precios" }
         -> arma el HTML del short desde la pauta JSON y luego renderiza.
      B) Desde HTML ya armado:  { "slug": "tarroshort-snes-top-precios" }
         -> renderiza un studio/<slug>.html existente.

    Opcionales: voice, pitch, rate, out_slug.
    Respuesta: {ok, job_id, queue_size}. Progreso por WS:
      tarroshort.queued / started / progress / done / error
    """
    payload = payload or {}
    import re as _re
    pauta_slug = (payload.get("pauta_slug") or "").strip()
    slug = (payload.get("slug") or "").strip()
    episodio_slug = (payload.get("episodio_slug") or "").strip()
    formato = (payload.get("formato") or "").strip()

    if episodio_slug:
        # highlights desde el HTML de un episodio (coleccion / entrevista)
        if not _re.match(r"^[a-z0-9-]+$", episodio_slug):
            return JSONResponse({"error": "episodio_slug invalido (kebab-case)"}, status_code=400)
        try:
            find_html(episodio_slug)
        except (FileNotFoundError, FileExistsError):
            return JSONResponse({"error": f"episodio no existe: {episodio_slug}"}, status_code=404)
        if formato not in ("coleccion", "entrevista"):
            formato = "entrevista" if "abriendo-el-tarro" in episodio_slug else "coleccion"
        job_id = await tarroshort_jobs.submit(
            episodio_slug, from_pauta=False, from_episodio=True, formato=formato)
        return {"ok": True, "job_id": job_id, "queue_size": tarroshort_jobs._queue.qsize()}

    if pauta_slug:
        if not _re.match(r"^[a-z0-9-]+$", pauta_slug):
            return JSONResponse({"error": "pauta_slug invalido (kebab-case)"}, status_code=400)
        pauta = PAUTAS_DIR / f"{pauta_slug}.tarrobot.json"
        if not pauta.exists():
            return JSONResponse({"error": f"pauta no existe: {pauta_slug}"}, status_code=404)
        target, from_pauta = pauta_slug, True
    elif slug:
        if not _re.match(r"^[a-z0-9-]+$", slug):
            return JSONResponse({"error": "slug invalido (kebab-case)"}, status_code=400)
        try:
            find_html(slug)
        except (FileNotFoundError, FileExistsError):
            return JSONResponse({"error": f"HTML no existe: {slug}"}, status_code=404)
        target, from_pauta = slug, False
    else:
        return JSONResponse({"error": "pauta_slug o slug requerido"}, status_code=400)

    params = {k: payload.get(k) for k in ("voice", "pitch", "rate", "out_slug")
              if payload.get(k) is not None}
    job_id = await tarroshort_jobs.submit(target, from_pauta=from_pauta, **params)
    return {"ok": True, "job_id": job_id, "queue_size": tarroshort_jobs._queue.qsize()}


@app.get("/api/tarroshort/job/{job_id}")
async def tarroshort_get_job(job_id: str):
    job = tarroshort_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "job no existe"}, status_code=404)
    return {"ok": True, "job": job.to_dict()}


@app.get("/api/tarroshort/list")
async def tarroshort_list(limit: int = 20):
    return {
        "ok": True,
        "jobs": tarroshort_jobs.list_recent(limit=limit),
        "current_job_id": tarroshort_jobs.current_job_id(),
    }


@app.get("/api/tarroshort/fuentes")
async def tarroshort_fuentes():
    """Lista las fuentes disponibles para armar un short:
       - pautas: rankings con pauta JSON (arman el HTML solos)
       - shorts: HTMLs tarroshort-* ya armados (listos para renderizar)."""
    pautas = []
    try:
        if PAUTAS_DIR.exists():
            pautas = sorted(p.name.replace(".tarrobot.json", "")
                            for p in PAUTAS_DIR.glob("*.tarrobot.json"))
    except Exception:
        pautas = []
    shorts = []
    try:
        shorts = sorted(h.stem for h in STUDIO.glob("**/tarroshort-*.html"))
    except Exception:
        shorts = []
    # Episodios para highlights: colecciones + entrevistas (Abriendo el Tarro)
    episodios = []
    try:
        for h in sorted(STUDIO.glob("**/*coleccion*.html")):
            if not h.name.startswith("_"):
                episodios.append({"slug": h.stem, "formato": "coleccion"})
        for h in sorted(STUDIO.glob("**/abriendo-el-tarro-*.html")):
            if not h.name.startswith("_"):
                episodios.append({"slug": h.stem, "formato": "entrevista"})
    except Exception:
        episodios = []
    return {"ok": True, "pautas": pautas, "shorts": shorts, "episodios": episodios}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 12 C4-lite: exportar dato suelto para Short (MP3 + SRT individual)
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/queue/short-export")
async def queue_short_export(payload: dict):
    """
    Exporta UN dato de la pauta cargada como archivo listo para Short:
      - studio/shorts/<slug>-<idx>.mp3
      - studio/shorts/<slug>-<idx>.srt

    Body: { "indice": 0 }  (indice basado en items_datos, no melodias)

    Pensado para alimentar CapCut/DaVinci con la pista de audio + subs
    sincronizados y agregar visual encima.
    """
    if not queue.loaded():
        return JSONResponse({"error": "no hay pauta cargada"}, status_code=400)
    try:
        idx = int(payload.get("indice", -1))
    except (TypeError, ValueError):
        return JSONResponse({"error": "indice invalido"}, status_code=400)
    datos = queue.items_datos()
    if not (0 <= idx < len(datos)):
        return JSONResponse({"error": f"indice fuera de rango (0..{len(datos)-1})"}, status_code=400)
    dato = datos[idx]

    # MP3 source: el precargado de pauta
    mp3_rel = dato.get("mp3")
    if not mp3_rel:
        return JSONResponse({"error": "el dato no tiene MP3 precargado. Corre --pauta-preload primero."}, status_code=400)
    mp3_src = PAUTAS_DIR / mp3_rel
    if not mp3_src.exists():
        return JSONResponse({"error": f"no existe el MP3 fuente: {mp3_src}"}, status_code=404)

    # Output paths
    shorts_dir = STUDIO / "shorts"
    shorts_dir.mkdir(parents=True, exist_ok=True)
    slug = queue.slug or "episodio"
    base_name = f"{slug}-{idx+1:02d}-{slugify(dato.get('tema', 'item'))[:30]}"
    mp3_dst = shorts_dir / f"{base_name}.mp3"
    srt_dst = shorts_dir / f"{base_name}.srt"

    import shutil
    shutil.copy2(str(mp3_src), str(mp3_dst))

    # SRT del dato suelto (un solo bloque)
    dur_ms = dato.get("duracion_ms") or max(3000, len(dato.get("texto", "")) * 60)
    # Reusamos helper de tarrobot.py
    from tarrobot import _ms_to_srt_timestamp
    srt = "1\n"
    srt += f"00:00:00,000 --> {_ms_to_srt_timestamp(dur_ms)}\n"
    srt += dato.get("texto", "") + "\n"
    srt_dst.write_text(srt, encoding="utf-8")

    return {
        "ok": True,
        "tema": dato.get("tema", ""),
        "mp3": str(mp3_dst),
        "srt": str(srt_dst),
        "duracion_ms": dur_ms,
    }


# ─────────────────────────────────────────────────────────────────────────
# Sprint 12 C5: quiz interactivo basico
# ─────────────────────────────────────────────────────────────────────────

def _generar_quiz_con_llm(tema_hint: Optional[str] = None) -> Optional[dict]:
    """LLM tira una pregunta retro con respuesta esperada."""
    try:
        import anthropic
    except ImportError:
        return None
    import os as _os, re as _re
    api_key = _os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    contexto_extra = f"Sesgalo al tema: {tema_hint}." if tema_hint else ""
    prompt = f"""Eres TarroBot, mascota del canal Retrotarros. Tirale a Luis o Koko UNA pregunta de trivia retrogaming.

{contexto_extra}

Requisitos:
- Pregunta corta (max 100 chars) y especifica (con respuesta unica clara).
- USA TILDES correctas, chileno neutro tuteo.
- Sin voseo argentino.
- Numeros en palabras si son grandes.
- Respuesta esperada debe ser una sola palabra/frase corta (max 30 chars).

Devuelve SOLO JSON sin markdown:
{{"pregunta": "...", "respuesta_esperada": "...", "pista_opcional": "...max 60 chars"}}
"""
    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        raw = _re.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        if "pregunta" in result:
            result["pregunta"] = chilenizar(result["pregunta"])
        return result
    except Exception as e:
        print(f"[quiz] error: {e}")
        return None


@app.post("/api/quiz/pregunta")
async def quiz_pregunta(payload: Optional[dict] = None):
    """Tira una pregunta de trivia. Deja modo quiz activo hasta /api/quiz/respuesta."""
    payload = payload or {}
    tema_hint = (payload.get("tema") or "").strip() or None
    if not tema_hint and queue.loaded():
        tema_hint = queue.pauta.get("episodio") or queue.slug

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    # Sprint 15: capa 1 - quiz pre-generado en la pauta
    pauta_actual = queue.pauta if queue.loaded() else None
    result = llm_resolver.resolver_quiz(pauta_actual, tema_hint)
    if result:
        print(f"[quiz] pauta HIT para '{tema_hint}'")

    if not result and llm_resolver.is_modo_barato():
        return JSONResponse({
            "error": "modo barato: sin quiz disponible (no hay pauta con quiz pregenerado)."
        }, status_code=503)

    if not result:
        # Capa 2: cache local
        result = llm_resolver.cache_get("quiz", tema_hint or "_no_hint_")
        if result:
            print(f"[quiz] cache local HIT para '{tema_hint}'")

    if not result:
        # Capa 3: llamar LLM
        espera = llm_cooldown_check("quiz")
        if espera is not None:
            return JSONResponse({"error": f"cooldown LLM: espera {espera:.1f}s"}, status_code=429)

        async with _procesando("preparando trivia..."):
            result = await asyncio.to_thread(_generar_quiz_con_llm, tema_hint)
        if result:
            llm_resolver.track_llm_call("quiz")
            llm_resolver.cache_save("quiz", tema_hint or "_no_hint_", result)

    if not result:
        return JSONResponse({"error": "fallo LLM quiz"}, status_code=500)

    pregunta = result.get("pregunta", "")
    respuesta = result.get("respuesta_esperada", "")

    async with quiz_state.lock:
        quiz_state.pregunta_activa = {
            "pregunta": pregunta,
            "respuesta": respuesta,
            "pista": result.get("pista_opcional", ""),
            "ts": time.time(),
        }

    audio_url = await _hablar_frase(
        pregunta, "thinking", "TRIVIA TARROBOT", voz, pitch, rate
    )
    return {
        "ok": True,
        "pregunta": pregunta,
        "respuesta_esperada": respuesta,
        "pista": result.get("pista_opcional", ""),
        "audio_url": audio_url,
    }


REACCION_ACERTO = [
    "¡Correcto! Tarro de oro para ti.",
    "¡Eso es! Mi RAM lo confirma.",
    "Bingo. Esa la sabias bien.",
    "¡Perfecto! Punto para el equipo.",
    "¡Acertaste! Eres una enciclopedia retro.",
]

REACCION_ERROR = [
    "Casi. La respuesta era: {resp}.",
    "Ufff, no. Iba por: {resp}.",
    "Cerca pero no. La correcta era {resp}.",
    "No esta vez. Te quedaste con la duda: {resp}.",
]


@app.post("/api/quiz/respuesta")
async def quiz_respuesta(payload: dict):
    """
    Confirma si acertaron o no la pregunta activa.
    Body: { "acerto": true|false }
    TarroBot reacciona con frase + estado.
    """
    if not quiz_state.hay_pregunta():
        return JSONResponse({"error": "no hay pregunta activa"}, status_code=400)
    acerto = bool(payload.get("acerto", False))
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    import random as _rnd
    async with quiz_state.lock:
        respuesta_correcta = quiz_state.pregunta_activa.get("respuesta", "")
        if acerto:
            quiz_state.aciertos += 1
            frase = pick_no_repeat(REACCION_ACERTO, "quiz_acerto")
            estado = "excited"
        else:
            quiz_state.errores += 1
            template = pick_no_repeat(REACCION_ERROR, "quiz_error")
            frase = template.format(resp=respuesta_correcta)
            estado = "winking"
        quiz_state.pregunta_activa = None

    audio_url = await _hablar_frase(
        frase, estado, "QUIZ RESULTADO", voz, pitch, rate
    )
    return {
        "ok": True,
        "acerto": acerto,
        "frase": frase,
        "aciertos": quiz_state.aciertos,
        "errores": quiz_state.errores,
        "audio_url": audio_url,
    }


@app.get("/api/quiz/status")
async def quiz_status():
    return {
        "ok": True,
        "pregunta_activa": quiz_state.pregunta_activa,
        "aciertos": quiz_state.aciertos,
        "errores": quiz_state.errores,
    }


# ─────────────────────────────────────────────────────────────────────────
# Sprint 12 C7: control de musica de fondo en OBS
# ─────────────────────────────────────────────────────────────────────────

def _input_name_musica() -> str:
    cfg = obs.get_alias().get("musica_fondo", {})
    return cfg.get("input_name") or "musica-fondo"


def _clamp_volumen_db(db: float) -> float:
    cfg = obs.get_alias().get("musica_fondo", {})
    lo = float(cfg.get("volumen_min_db", -45))
    hi = float(cfg.get("volumen_max_db", -6))
    return max(lo, min(db, hi))


@app.post("/api/obs/musica/volumen")
async def obs_musica_volumen(payload: dict):
    """
    Ajusta volumen del input de musica de fondo en OBS.
    Body: { "db": -20 }   o   { "delta": -3 }  (delta sumado al actual)
    """
    if not obs.is_connected():
        return JSONResponse({"error": "OBS no conectado"}, status_code=400)
    input_name = _input_name_musica()
    try:
        if "db" in payload:
            db = _clamp_volumen_db(float(payload["db"]))
        elif "delta" in payload:
            actual = await obs.cliente().get_input_volume_db(input_name)
            db = _clamp_volumen_db(actual + float(payload["delta"]))
        else:
            return JSONResponse({"error": "manda 'db' o 'delta'"}, status_code=400)
        await obs.cliente().set_input_volume_db(input_name, db)
    except obs.OBSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    tracker.mark_input()
    return {"ok": True, "input": input_name, "db": db}


@app.post("/api/obs/musica/mute")
async def obs_musica_mute(payload: dict):
    """
    Mute / unmute del input de musica.
    Body: { "muted": true|false }  o  { "toggle": true }
    """
    if not obs.is_connected():
        return JSONResponse({"error": "OBS no conectado"}, status_code=400)
    input_name = _input_name_musica()
    try:
        if payload.get("toggle"):
            actual = await obs.cliente().get_input_mute(input_name)
            target = not actual
        else:
            target = bool(payload.get("muted", False))
        await obs.cliente().set_input_mute(input_name, target)
    except obs.OBSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    tracker.mark_input()
    return {"ok": True, "input": input_name, "muted": target}


@app.get("/api/obs/musica/status")
async def obs_musica_status():
    if not obs.is_connected():
        return {"ok": False, "connected": False}
    input_name = _input_name_musica()
    try:
        db = await obs.cliente().get_input_volume_db(input_name)
        muted = await obs.cliente().get_input_mute(input_name)
        return {"ok": True, "connected": True, "input": input_name, "db": db, "muted": muted}
    except obs.OBSError as e:
        return {"ok": False, "connected": True, "error": str(e), "input": input_name}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 11 C3: auto-pauta desde tema libre (sin HTML, via LLM)
# ─────────────────────────────────────────────────────────────────────────

@app.post("/api/pauta/auto-tema")
async def pauta_auto_tema(payload: dict):
    """
    Genera una pauta completa desde un tema libre. Pasos:
      1. LLM genera N datos curados (Claude)
      2. Crea pauta JSON en studio/pautas/<slug>.tarrobot.json
      3. Precarga MP3s en paralelo (Edge TTS)
      4. Sincroniza al Drive si aplica

    Body:
      {
        "tema": "Mega Drive raros",           # obligatorio
        "n_datos": 10,                        # opcional, 3-20, default 10
        "slug": "mega-drive-raros",           # opcional, derivado del tema si falta
        "episodio": "Top 10 Mega Drive raros",# opcional
        "consola": "Genesis",                 # opcional, hint para el LLM
        "voz": "catalina",                    # opcional, default preset actual
        "preload": true,                      # default true: precarga MP3s
        "force": false                        # default false: no sobreescribe pauta existente
      }
    """
    tema = (payload.get("tema") or "").strip()
    if not tema:
        return JSONResponse({"error": "tema vacio"}, status_code=400)

    # Rate limit (es un LLM call caro)
    espera = llm_cooldown_check("pauta_auto_tema")
    if espera is not None:
        return JSONResponse(
            {"error": f"cooldown LLM: espera {espera:.1f}s antes de generar otra pauta"},
            status_code=429,
        )

    try:
        n_datos = int(payload.get("n_datos", 10))
    except (TypeError, ValueError):
        return JSONResponse({"error": "n_datos invalido"}, status_code=400)
    n_datos = max(3, min(n_datos, 20))

    slug_raw = (payload.get("slug") or "").strip()
    slug = slugify(slug_raw) if slug_raw else slugify(tema)

    consola = (payload.get("consola") or "").strip() or None
    voz_in = (payload.get("voz") or "").strip()
    voz = resolver_voz(voz_in) if voz_in else VOZ_DEFAULT
    force = bool(payload.get("force", False))
    preload = bool(payload.get("preload", True))

    # Validar que no se piserve una pauta existente sin force
    pauta_existente = cargar_pauta(slug)
    if pauta_existente and not force:
        return JSONResponse({
            "error": f"ya existe la pauta '{slug}' con {len(pauta_existente['datos'])} datos",
            "hint": "manda 'force': true para reemplazarla, o pasa un 'slug' distinto",
            "slug": slug,
        }, status_code=409)

    # 1) Generar via LLM en thread (el SDK es bloqueante)
    # Sprint 15: enriquecido=True por default para minimizar llamadas en vivo
    async with _procesando(f"generando pauta enriquecida '{tema}' con Claude..."):
        result = await asyncio.to_thread(
            generar_pauta_tema_con_llm, tema, n_datos, consola, None, True
        )

    if result is None:
        return JSONResponse(
            {"error": "fallo generacion LLM. Verifica ANTHROPIC_API_KEY y creditos."},
            status_code=500,
        )
    llm_resolver.track_llm_call("pauta_auto_tema_enriquecido")

    datos_llm = result.get("datos", [])
    if not datos_llm:
        return JSONResponse({"error": "el LLM no devolvio datos"}, status_code=500)

    # 2) Crear pauta en disco
    episodio = (payload.get("episodio") or "").strip() or result.get("episodio_titulo") or tema
    pauta = crear_pauta_vacia(slug, episodio, voz=voz, pitch=PITCH_DEFAULT, rate=RATE_DEFAULT)
    for d in datos_llm:
        d["fuente"] = "pauta-tema"
        pauta_agregar_dato(pauta, d)
    # Sprint 15: preservar contenido colateral a nivel episodio
    for key in ("catchphrases_episodio", "intros_cold_open",
                "outros_cliffhanger", "publicacion"):
        if key in result:
            pauta[key] = result[key]
    p = guardar_pauta(pauta)

    # 3) Preload MP3s (opcional, lento)
    preload_result = None
    if preload:
        async with _procesando(f"generando MP3s para {len(pauta['datos'])} datos..."):
            try:
                generados, skipped, errores = await _preload_pauta_async(
                    pauta, force=False, concurrency=3
                )
                guardar_pauta(pauta)  # persistir con mp3 y duracion_ms
                preload_result = {
                    "generados": generados, "skipped": skipped, "errores": errores
                }
            except Exception as e:
                preload_result = {"error": str(e)}

    return {
        "ok": True,
        "slug": slug,
        "episodio": episodio,
        "n_datos": len(pauta["datos"]),
        "path": str(p),
        "preload": preload_result,
        "datos_preview": [
            {"tema": d["tema"], "estado": d["estado"],
             "texto": d["texto"][:120]}
            for d in pauta["datos"]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────
# Sprint 10 B1: estadisticas de sesion
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/session/stats")
async def session_stats_endpoint():
    """Estadisticas en vivo de la sesion actual."""
    return {"ok": True, "stats": stats.resumen()}


@app.post("/api/session/reset")
async def session_stats_reset():
    """Resetea contadores de la sesion (no afecta DB ni pauta)."""
    stats.reset()
    return {"ok": True, "stats": stats.resumen()}


@app.get("/api/voz")
async def voz_get():
    """Devuelve el preset actual y la lista de presets disponibles."""
    voz, pitch, rate = resolver_preset(_voz_preset_actual)
    return {
        "preset": _voz_preset_actual,
        "voz": voz,
        "pitch": pitch,
        "rate": rate,
        "presets": {nombre: {"voz": v, "pitch": p, "rate": r}
                    for nombre, (v, p, r) in PRESETS_VOZ.items()},
    }


@app.post("/api/voz")
async def voz_set(payload: dict):
    """
    Cambia el preset de voz activo del server.
    Body: { "preset": "tarrobot-nino" }
    Tambien acepta voz/pitch/rate individuales como override del preset.
    """
    global _voz_preset_actual
    nuevo = payload.get("preset")
    if nuevo and nuevo not in PRESETS_VOZ:
        return JSONResponse({"error": f"preset '{nuevo}' no existe. Validos: {list(PRESETS_VOZ.keys())}"}, status_code=400)
    if nuevo:
        _voz_preset_actual = nuevo
    voz, pitch, rate = resolver_preset(_voz_preset_actual)
    return {"ok": True, "preset": _voz_preset_actual, "voz": voz, "pitch": pitch, "rate": rate}


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


def _whisper_prompt_dinamico() -> str:
    """
    Sprint 10 A4: arma el initial_prompt de Whisper sumando los temas de la
    pauta cargada (si la hay). Esto hace que Whisper transcriba mejor los
    juegos del episodio (ej: 'Conker', 'ClayFighter') porque los espera.
    """
    base = WHISPER_PROMPT
    if not queue.loaded():
        return base
    temas = [d.get("tema", "") for d in queue.pauta.get("datos", []) if d.get("tema")]
    if not temas:
        return base
    extras = ", ".join(temas[:25])  # tope para no inflar el prompt
    episodio = queue.pauta.get("episodio") or queue.slug
    return base + (
        f" El usuario tambien puede mencionar (estamos grabando '{episodio}'): "
        f"{extras}."
    )


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
            temperature=0.0,                       # mas determinista, menos alucina
            initial_prompt=_whisper_prompt_dinamico(),  # contexto + pauta cargada
            condition_on_previous_text=False,      # no se "atora" con audio anterior
            no_speech_threshold=0.4,               # mas tolerante a silencios al final
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

    # 1-OBS-A. "Gracias TarroBot" → cierre de close-up (Sprint 9)
    #          Va temprano porque "gracias" puede aparecer en frases largas.
    gracias_kws = ["gracias tarrobot", "gracias tarro", "gracias robot",
                   "muchas gracias tarrobot", "ya gracias",
                   "perfecto gracias", "listo gracias"]
    for kw in gracias_kws:
        if kw in t_clean:
            return {"accion": "obs_gracias", "params": {}}

    # 1-OBS-B. "Toma cercana / primer plano / acercate al X" (Sprint 9)
    close_up_triggers = [
        "toma cercana", "toma cercana a", "toma cerca de",
        "primer plano", "primer plano de", "primer plano al",
        "acercate al", "acercate a la", "acercate a",
        "acércate al", "acércate a la", "acércate a",
        "muestra de cerca", "muestrame de cerca", "muéstrame de cerca",
        "zoom al", "zoom a la", "zoom a",
        "close up al", "close up a la", "close up de",
        "closeup al", "closeup a la", "closeup de",
        "enfoca al", "enfoca la", "enfoca el",
    ]
    for kw in close_up_triggers:
        idx = t_clean.find(kw)
        if idx >= 0:
            tema = t_clean[idx + len(kw):].strip(" ,.;:!?¿¡")
            # quitar articulo inicial si quedo "al/a la/el"
            for art in ["al ", "a la ", "a las ", "a los ", "el ", "la ", "los ", "las "]:
                if tema.startswith(art):
                    tema = tema[len(art):]
                    break
            if tema:
                return {"accion": "obs_close_up", "params": {"tema": tema}}

    # 1-OBS-C. "Camara a X" / "cambia a X" → cambio simple de escena (Sprint 9)
    camara_triggers = ["camara a ", "cámara a ", "camara al ", "cámara al ",
                       "cambia a ", "cambia escena a ", "escena ",
                       "pasa a camara ", "pasa a cámara ", "vamos a camara ",
                       "vamos a cámara ", "ponte en camara ", "ponte en cámara "]
    for kw in camara_triggers:
        idx = t_clean.find(kw)
        if idx >= 0:
            escena = t_clean[idx + len(kw):].strip(" ,.;:!?¿¡")
            for art in ["el ", "la ", "los ", "las "]:
                if escena.startswith(art):
                    escena = escena[len(art):]
                    break
            if escena:
                return {"accion": "obs_escena", "params": {"escena": escena}}

    # 1-OBS-E. Musica de fondo (Sprint 12 C7)
    if any(kw in t_clean for kw in ["pon musica", "pon música", "musica de fondo", "música de fondo",
                                     "pone musica", "pone música", "arranca musica", "arranca música"]):
        return {"accion": "obs_musica_unmute", "params": {}}
    if any(kw in t_clean for kw in ["sube la musica", "sube la música", "mas volumen musica",
                                     "más volumen música", "sube el volumen"]):
        return {"accion": "obs_musica_subir", "params": {"delta": 3}}
    if any(kw in t_clean for kw in ["baja la musica", "baja la música", "menos volumen musica",
                                     "menos volumen música", "baja el volumen"]):
        return {"accion": "obs_musica_bajar", "params": {"delta": -3}}
    if any(kw in t_clean for kw in ["para la musica", "para la música", "detente musica", "detente música",
                                     "silencio musica", "silencio música", "mute musica", "mute música",
                                     "calla la musica", "calla la música"]):
        return {"accion": "obs_musica_mute", "params": {}}

    # 1-OBS-D. "Muestra el X" / "saca el X" → toggle de fuente via alias (Sprint 9)
    if t_clean.startswith("muestra ") or t_clean.startswith("muéstrame "):
        rest = t_clean.split(" ", 1)[1].strip(" ,.;:!?¿¡")
        for art in ["el ", "la ", "los ", "las "]:
            if rest.startswith(art):
                rest = rest[len(art):]
                break
        if rest:
            return {"accion": "obs_fuente", "params": {"alias": rest, "visible": True}}

    if t_clean.startswith("saca ") or t_clean.startswith("oculta "):
        rest = t_clean.split(" ", 1)[1].strip(" ,.;:!?¿¡")
        for art in ["el ", "la ", "los ", "las "]:
            if rest.startswith(art):
                rest = rest[len(art):]
                break
        if rest:
            return {"accion": "obs_fuente", "params": {"alias": rest, "visible": False}}

    # 1c0. "¿Me estás escuchando?" / "¿me oyes?" (Sprint 8.x)
    escuchando_kws = [
        "me estas escuchando", "me estás escuchando",
        "me escuchas", "me escuchás",
        "me oyes", "me oís", "me ois",
        "nos escuchas", "nos escuchás",
        "nos oyes", "nos oís", "nos ois",
        "estas escuchando", "estás escuchando",
        "estas oyendo", "estás oyendo",
        "escuchas bien", "se escucha bien",
        "audio ok", "audio okey", "audio limpio",
        "check de audio", "prueba de audio",
        "hay audio", "se oye", "se escucha",
    ]
    for kw in escuchando_kws:
        if kw in t_clean:
            return {"accion": "escuchando", "params": {}}

    # 1c-PERSONAL. Preguntas sobre TarroBot mismo (Sprint 10 B4)
    # Cada categoria tiene sus keywords. Devuelve accion="personal" con
    # params.categoria. El endpoint elige frase curada.
    personal_kws = {
        "nombre": ["como te llamas", "cómo te llamas", "tu nombre",
                   "quien eres", "quién eres", "te llamas"],
        "origen": ["de donde eres", "de dónde eres", "de donde vienes",
                   "de dónde vienes", "donde naciste", "dónde naciste",
                   "donde vives", "dónde vives", "como naciste", "cómo naciste"],
        "edad": ["cuantos años tienes", "cuántos años tienes", "tu edad",
                 "que edad tienes", "qué edad tienes", "eres viejo", "tu cumpleaños"],
        "favorito": ["tu juego favorito", "juego favorito", "que juego te gusta",
                     "qué juego te gusta", "cual es tu juego", "cuál es tu juego",
                     "mejor juego", "tu cartucho favorito"],
        "consola_fav": ["tu consola favorita", "consola favorita",
                        "que consola te gusta", "qué consola te gusta",
                        "mejor consola"],
        "familia": ["tienes familia", "tus padres", "tus hermanos",
                    "quien te creo", "quién te creó", "quien te hizo",
                    "quién te hizo"],
        "comida": ["que comes", "qué comes", "comes algo", "te alimentas"],
        "sueño": ["tu sueño", "que sueñas", "qué sueñas", "que te gustaría",
                  "qué te gustaría", "tu meta"],
        "como_funciona": ["como funcionas", "cómo funcionas", "como te hicieron",
                          "cómo te hicieron", "eres una ia", "eres robot",
                          "eres un robot", "que eres", "qué eres"],
    }
    for cat, kws in personal_kws.items():
        for kw in kws:
            if kw in t_clean:
                return {"accion": "personal", "params": {"categoria": cat}}

    # 1c. "¿Cómo estás?" (Sprint 8.x)
    como_estas_kws = [
        "como estas", "cómo estás", "como te sientes", "cómo te sientes",
        "que tal estas", "qué tal estás", "como andas", "cómo andas",
        "como te va", "cómo te va",
    ]
    for kw in como_estas_kws:
        if kw in t_clean:
            return {"accion": "como_estas", "params": {}}

    # 1d. "¿Qué hacemos hoy?" / "¿Qué te gustaría hacer?"
    que_hacemos_kws = [
        "que hacemos hoy", "qué hacemos hoy", "que hacemos", "qué hacemos",
        "que te gustaria hacer", "qué te gustaría hacer",
        "que haremos hoy", "qué haremos hoy",
        "que quieres hacer", "qué quieres hacer",
        "tienes ganas de", "tenés ganas de",
        "que proponemos", "qué proponemos",
        "que tienes pensado", "qué tienes pensado",
    ]
    for kw in que_hacemos_kws:
        if kw in t_clean:
            return {"accion": "que_hacemos", "params": {}}

    # 1b. Despertar (Sprint 8.5): si dicen "despierta", "estas ahi", "tarrobot?"
    despertar_kws = [
        "despierta", "despertate", "despertar",
        "estas ahi", "estas ahí", "estas con nosotros",
        "estás ahi", "estás ahí", "estás con nosotros",
        "tarrobot estas", "tarrobot estás",
        "sigues ahi", "sigues ahí", "sigues con nosotros",
        "estas dormido", "estás dormido", "te dormiste",
    ]
    for kw in despertar_kws:
        if kw in t_clean:
            return {"accion": "despertar", "params": {}}

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

    # 3b. Tocar/poner melodia (Sprint 8.x): detectar "tocá X", "ponme X",
    #     "ponete X", "suena X" -> accion melodia con tema fuzzy
    melodia_kws = ["toca ", "tocate ", "tocá ", "tócame ", "tocame ",
                   "pon ", "pone ", "ponete ", "ponme ", "ponéme ",
                   "ponete a tocar ", "tocate la ", "tocate el ",
                   "suena ", "sonar ", "reproduce ", "reproducí ", "reproducime ",
                   "te acordas de ", "te acuerdas de ", "te acordás de "]
    for kw in melodia_kws:
        idx = t_clean.find(kw)
        if idx >= 0:
            tema = t_clean[idx + len(kw):].strip(" ,.;:!?¿¡")
            if tema:
                return {"accion": "melodia", "params": {"tema": tema}}

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


def _aplicar_wake_word(texto: str, wake: str) -> tuple[bool, str]:
    """
    Verifica si la transcripcion contiene la wake-word y devuelve el texto
    limpio (sin la wake-word ni los caracteres antes de ella). Si no la
    contiene, devuelve (False, texto). Sprint 8.2.

    Variantes que Whisper suele transcribir mal (todas valen como wake):
      tarrobot, tarro bot, taro bot, taro vot, taro pot, tarrovot, tarobot,
      tarrobott, tarrobod, tarro pot, terrabot, tarrobo, tarro, ¡tarrobot!
    """
    import re as _re
    if not wake:
        return True, texto

    t_lower = texto.lower()

    # Lista exhaustiva de variantes (mejor coincidencia primero por longitud)
    variantes = [
        "tarrobot", "tarrobott", "tarrobod", "tarro bot", "tarro bott", "tarro bod",
        "tarobot", "taro bot", "taro pot", "taro vot",
        "tarrovot", "tarrov", "terrabot", "tarrabot",
        "tarro pot", "tarro vot",
        "tarro!", "tarro?",
    ]

    for v in variantes:
        idx = t_lower.find(v)
        if idx >= 0:
            resto = texto[idx + len(v):].strip(" ,.;:!?¿¡")
            return True, resto

    # Fallback regex mas amplio: 'tarro' seguido opcionalmente de 'bot/pot/vot/bott'
    m = _re.search(r"\btarr?o\s*(?:bot|pot|vot|bott|bod)?\w*\b", t_lower)
    if m:
        resto = texto[m.end():].strip(" ,.;:!?¿¡")
        return True, resto

    return False, texto


@app.post("/api/listen")
async def listen(request: Request, wake: str = ""):
    """
    Recibe audio del browser (mic del celu/PC), transcribe con Whisper local,
    parsea intent y dispara el endpoint correspondiente.

    Body: raw bytes (audio webm/opus).
    Query opcional:
      ?wake=tarrobot   modo continuo: solo procesa si la transcripcion
                       contiene la wake-word. El resto del texto despues
                       de la wake-word se usa como instruccion.
    """
    audio_bytes = await request.body()
    if not audio_bytes or len(audio_bytes) < 1000:
        return JSONResponse({"error": "audio vacio o muy corto"}, status_code=400)

    tracker.mark_input()

    # Transcribir
    try:
        async with _procesando("escuchando..."):
            texto = await asyncio.to_thread(transcribir_audio_sync, audio_bytes)
    except Exception as e:
        return JSONResponse({"error": f"transcripcion fallo: {e}"}, status_code=500)

    if not texto:
        return JSONResponse({"transcript": "", "error": "no se reconocio voz"}, status_code=400)

    # Sprint 8.2: filtrado por wake-word en modo continuo
    wake_detected, texto_limpio = _aplicar_wake_word(texto, wake)
    if wake and not wake_detected:
        return {"ok": True, "transcript": texto, "wake_detected": False, "ignored": True}
    if wake and wake_detected and not texto_limpio:
        # Detecto "tarrobot" solo, sin instruccion -> saludo default
        return {
            "ok": True,
            "transcript": texto,
            "wake_detected": True,
            "accion": "saludar",
            "params": {},
            "result": await saludar({}),
        }
    texto = texto_limpio if wake else texto

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
        elif accion == "despertar":
            result = await despertar({})
        elif accion == "como_estas":
            result = await como_estas({})
        elif accion == "que_hacemos":
            result = await que_hacemos({})
        elif accion == "escuchando":
            result = await escuchando({})
        elif accion == "opinar":
            result = await opinar(params)
        elif accion == "precio":
            result = await precio(params)
        elif accion == "random":
            result = await random_dato(params)
        elif accion == "melodia":
            result = await queue_melodia(params)
        elif accion == "obs_escena":
            result = await obs_set_escena(params)
        elif accion == "obs_fuente":
            result = await obs_set_fuente(params)
        elif accion == "obs_close_up":
            result = await obs_close_up(params)
        elif accion == "obs_gracias":
            result = await obs_gracias(params)
        elif accion == "personal":
            result = await personal(params)
        elif accion == "obs_musica_subir":
            result = await obs_musica_volumen({"delta": params.get("delta", 3)})
        elif accion == "obs_musica_bajar":
            result = await obs_musica_volumen({"delta": params.get("delta", -3)})
        elif accion == "obs_musica_mute":
            result = await obs_musica_mute({"muted": True})
        elif accion == "obs_musica_unmute":
            result = await obs_musica_mute({"muted": False})
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
        "wake_detected": True if wake else None,
        "accion": accion,
        "params": params,
        "result": result,
    }


# ─────────────────────────────────────────────────────────────────────────
# Queue (cola del episodio) — Sprint 6.3
# ─────────────────────────────────────────────────────────────────────────

async def _reproducir_dato_de_cola(dato: dict, voz_override: Optional[str] = None) -> Optional[str]:
    """
    Reproduce un dato de la cola: usa el MP3 precargado si existe, sino
    genera TTS al vuelo. Dispara el WS 'hablar' a las pantallas live.
    Devuelve la audio_url usada.
    """
    # Prioridad: voz_override del request > voz del JSON de pauta > preset actual
    preset_voz, preset_pitch, preset_rate = resolver_preset(_voz_preset_actual)
    if voz_override:
        voz = resolver_voz(voz_override)
    else:
        voz = queue.pauta.get("voz") or preset_voz
    pitch = queue.pauta.get("pitch") or preset_pitch
    rate = queue.pauta.get("rate") or preset_rate

    # 1. Intentar MP3 precargado
    audio_url = _audio_url_de_pauta(queue.slug, dato)

    # 2. Fallback a TTS al vuelo
    if not audio_url:
        print(f"[queue] dato {dato['id']} sin MP3 precargado, generando al vuelo...")
        async with _procesando(f"generando audio para {dato['tema'][:30]}..."):
            mp3 = await asyncio.to_thread(generar_tts, dato, voz, pitch, rate)
        audio_url = f"/audio/{mp3.name}" if mp3 else None

    # Sprint 9: hook pre-hablar para auto-escena OBS
    await _hook_pre_hablar()

    tracker.mark_speaking(True)
    # Sprint 7.5: registrar en session log para exportar SRT despues
    queue.log_play(dato)

    meta = " · ".join(
        s for s in [dato.get("consola", ""), str(dato.get("ano", "") or ""), dato.get("editor", "")]
        if s and s != "0"
    )
    await manager.broadcast_live({
        "tipo": "hablar",
        "estado": dato["estado"],
        "texto": dato["texto"],
        "label": LABEL_POR_ESTADO.get(dato["estado"], "DATO CURIOSO"),
        "meta": meta,
        "audio_url": audio_url,
        "tema": dato["tema"],
    })

    # Sprint 10 A1: post-hablar event-driven con fallback al duracion_ms
    if obs_state.auto_scene_on_speak and not obs_state.in_close_up:
        async def _post():
            await _hook_post_hablar()
        tracker.add_finished_listener(_post)
        dur_ms = dato.get("duracion_ms") or int(len(dato.get("texto", "")) * 60)
        # fallback 2x duracion + 2s
        asyncio.create_task(_post_hablar_fallback((dur_ms / 1000.0) * 2 + 2.0))
    return audio_url


@app.post("/api/queue/load")
async def queue_load(payload: dict):
    """
    Carga una pauta del disco a la cola activa.
    Body: { "slug": "snes-top-mundial" }
    """
    slug = (payload.get("slug") or "").strip()
    if not slug:
        return JSONResponse({"error": "slug vacio"}, status_code=400)
    pauta = cargar_pauta(slug)
    if not pauta:
        return JSONResponse({"error": f"no existe la pauta '{slug}' en studio/pautas/"}, status_code=404)
    if not pauta.get("datos"):
        return JSONResponse({"error": f"la pauta '{slug}' esta vacia"}, status_code=400)

    async with queue.lock:
        queue.pauta = pauta
        queue.slug = pauta["slug"]
        queue.indice = -1   # arranca en limbo, primer NEXT salta al 0
        queue.reset_session()

    tracker.mark_input()

    # Sprint 18 C1: si auto-record esta on y OBS conectado, arrancar grabacion
    auto_rec_started = None
    try:
        from obs_recorder import is_auto_record, start_recording
        if is_auto_record() and obs.is_connected():
            auto_rec_started = await start_recording(obs.cliente(), queue.slug)
            if auto_rec_started.get("ok"):
                print(f"[auto-record] grabacion iniciada en {auto_rec_started.get('dir')}")
                await manager.broadcast_live({
                    "tipo": "obs-recording-started",
                    "slug": queue.slug,
                    "dir": auto_rec_started.get("dir"),
                })
            else:
                print(f"[auto-record] no se pudo iniciar: {auto_rec_started.get('error')}")
    except Exception as e:
        print(f"[auto-record] hook fallo: {e}")

    return {"ok": True, "status": queue.status(), "auto_record_started": auto_rec_started}


@app.post("/api/queue/unload")
async def queue_unload():
    """Descarga la cola activa (vuelve al modo libre puro)."""
    async with queue.lock:
        queue.pauta = None
        queue.slug = None
        queue.indice = -1
    tracker.mark_input()
    return {"ok": True}


@app.get("/api/queue/status")
async def queue_status():
    """Devuelve el estado completo de la cola."""
    return queue.status()


@app.post("/api/queue/next")
async def queue_next(payload: Optional[dict] = None):
    """Avanza al siguiente item y lo reproduce. Body opcional: { voz: 'catalina' }"""
    payload = payload or {}
    async with queue.lock:
        if not queue.loaded():
            return JSONResponse({"error": "no hay cola cargada"}, status_code=400)
        next_idx = queue.indice + 1
        if next_idx >= queue.total():
            return JSONResponse({"error": "ya estas en el ultimo item", "indice": queue.indice}, status_code=400)
        queue.indice = next_idx
        dato = queue.current_dato()
    tracker.mark_input()
    audio_url = await _reproducir_dato_de_cola(dato, payload.get("voz"))
    # Sprint 18 D1: hook lower-third automatico (silent si falla)
    if obs_state.auto_lower_third and obs.is_connected():
        try:
            await _set_lower_third(_format_lower_third(dato))
        except Exception as e:
            print(f"[lower-third] hook fallo: {e}")
    return {"ok": True, "indice": queue.indice, "dato": dato, "audio_url": audio_url}


@app.post("/api/queue/prev")
async def queue_prev(payload: Optional[dict] = None):
    """Retrocede al item anterior y lo reproduce."""
    payload = payload or {}
    async with queue.lock:
        if not queue.loaded():
            return JSONResponse({"error": "no hay cola cargada"}, status_code=400)
        prev_idx = queue.indice - 1
        if prev_idx < 0:
            return JSONResponse({"error": "ya estas en el primer item", "indice": queue.indice}, status_code=400)
        queue.indice = prev_idx
        dato = queue.current_dato()
    tracker.mark_input()
    audio_url = await _reproducir_dato_de_cola(dato, payload.get("voz"))
    return {"ok": True, "indice": queue.indice, "dato": dato, "audio_url": audio_url}


@app.post("/api/queue/jump")
async def queue_jump(payload: dict):
    """Salta a un indice especifico. Body: { indice: N, voz?: 'catalina' }"""
    try:
        indice = int(payload.get("indice", -1))
    except (TypeError, ValueError):
        return JSONResponse({"error": "indice invalido"}, status_code=400)
    async with queue.lock:
        if not queue.loaded():
            return JSONResponse({"error": "no hay cola cargada"}, status_code=400)
        if indice < 0 or indice >= queue.total():
            return JSONResponse({"error": f"indice fuera de rango (0..{queue.total()-1})"}, status_code=400)
        queue.indice = indice
        dato = queue.current_dato()
    tracker.mark_input()
    audio_url = await _reproducir_dato_de_cola(dato, payload.get("voz"))
    return {"ok": True, "indice": queue.indice, "dato": dato, "audio_url": audio_url}


@app.post("/api/queue/reset")
async def queue_reset():
    """Vuelve al estado inicial (indice -1, sin reproducir)."""
    async with queue.lock:
        if not queue.loaded():
            return JSONResponse({"error": "no hay cola cargada"}, status_code=400)
        queue.indice = -1
        queue.reset_session()
    tracker.mark_input()
    return {"ok": True, "status": queue.status()}


def _buscar_melodia_por_tema(tema: str, melodias: list) -> Optional[dict]:
    """
    Busqueda fuzzy de melodia por tema. Devuelve la mejor coincidencia o None.
    Estrategia: match por palabras clave del tema en cualquier orden.
    Ejemplo: "aquatic ambience" -> match con "Donkey Kong Country Aquatic Ambience"
    """
    if not tema or not melodias:
        return None
    import re as _re

    # Normalizar tema buscado: lowercase, sin caracteres especiales
    def _norm(s: str) -> str:
        s = s.lower()
        s = _re.sub(r"[^\w\s]", " ", s)
        s = _re.sub(r"\s+", " ", s).strip()
        return s

    palabras_buscadas = set(_norm(tema).split())
    if not palabras_buscadas:
        return None

    mejor = None
    mejor_score = 0
    for m in melodias:
        tema_m = _norm(m.get("tema", ""))
        palabras_m = set(tema_m.split())
        # Contar palabras de la busqueda que aparecen en el tema
        coincidencias = sum(1 for p in palabras_buscadas if p in palabras_m)
        # Bonus si la busqueda completa esta como substring
        if _norm(tema) in tema_m:
            coincidencias += 2
        if coincidencias > mejor_score:
            mejor_score = coincidencias
            mejor = m

    return mejor if mejor_score >= 1 else None


@app.post("/api/queue/melodia")
async def queue_melodia(payload: dict):
    """
    Reproduce una melodia de la cola.
    Body opcional: { "indice": N, "id": "...", "tema": "...", "voz": "..." }
    Si no se especifica nada, elige una random.
    Si tema='aquatic' busca fuzzy entre las melodias cargadas.
    """
    melodias = queue.items_melodias()
    if not melodias:
        return JSONResponse({"error": "no hay melodias en la pauta cargada"}, status_code=400)

    dato = None
    if payload.get("id"):
        dato_id = payload["id"]
        for m in melodias:
            if m["id"] == dato_id:
                dato = m
                break
        if not dato:
            return JSONResponse({"error": f"melodia con id '{dato_id}' no encontrada"}, status_code=404)
    elif "indice" in payload and payload["indice"] is not None:
        try:
            idx = int(payload["indice"])
        except (TypeError, ValueError):
            return JSONResponse({"error": "indice invalido"}, status_code=400)
        if not (0 <= idx < len(melodias)):
            return JSONResponse({"error": f"indice fuera de rango (0..{len(melodias)-1})"}, status_code=400)
        dato = melodias[idx]
    elif payload.get("tema"):
        dato = _buscar_melodia_por_tema(payload["tema"], melodias)
        if not dato:
            return JSONResponse(
                {"error": f"no encontre una melodia que matchee '{payload['tema']}'",
                 "disponibles": [m["tema"] for m in melodias]},
                status_code=404
            )
    else:
        import random
        dato = random.choice(melodias)

    tracker.mark_input()
    stats.melodias_tocadas += 1
    audio_url = await _reproducir_dato_de_cola(dato, payload.get("voz"))
    return {"ok": True, "dato": dato, "audio_url": audio_url}


@app.get("/api/queue/srt")
async def queue_srt(modo: str = "auto", gap_ms: int = 500):
    """
    Exporta SRT de la cola actual.
    modo='auto'      usa session_log si hay items reproducidos, sino relative
    modo='relative'  fuerza modo relative (secuencial desde T=0)
    modo='recording' fuerza modo recording (timestamps reales)
    gap_ms           solo aplica en modo relative
    """
    if not queue.loaded():
        return JSONResponse({"error": "no hay cola cargada"}, status_code=400)

    use_log = None
    if modo == "recording":
        if not queue.session_log:
            return JSONResponse({"error": "no hay items reproducidos todavia"}, status_code=400)
        use_log = queue.session_log
    elif modo == "auto":
        use_log = queue.session_log if queue.session_log else None
    # modo='relative' -> use_log queda None

    srt = pauta_to_srt(queue.pauta, session_log=use_log, gap_ms=gap_ms)
    from fastapi.responses import Response
    filename = f"{queue.slug}.srt"
    return Response(
        content=srt,
        media_type="application/x-subrip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/queue/list")
async def queue_list():
    """Lista todas las pautas disponibles en disco (para selector del panel)."""
    if not PAUTAS_DIR.exists():
        return {"ok": True, "pautas": []}
    items = []
    for f in sorted(PAUTAS_DIR.glob("*.tarrobot.json")):
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
            audio_dir = pauta_audio_dir(p["slug"])
            mp3s = len(list(audio_dir.glob("*.mp3"))) if audio_dir.exists() else 0
            items.append({
                "slug": p["slug"],
                "episodio": p.get("episodio", ""),
                "total": len(p.get("datos", [])),
                "mp3_listos": mp3s,
                "actualizado": p.get("actualizado", ""),
            })
        except Exception:
            continue
    return {"ok": True, "pautas": items}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 13: Endpoints social (chat multi-plataforma)
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/social/status")
async def social_status():
    """Estado global del modulo social: conectores + sesion activa + counts."""
    return {"ok": True, "status": social_manager.manager.status()}


@app.post("/api/social/session/start")
async def social_session_start(payload: dict):
    """
    Inicia una sesion de stream. Cierra automaticamente la anterior si habia.
    Body: { "slug": "stream-2026-05-22", "title": "opcional" }
    """
    slug = (payload.get("slug") or "").strip()
    if not slug:
        return JSONResponse({"error": "slug obligatorio"}, status_code=400)
    title = (payload.get("title") or "").strip() or None
    sess = await asyncio.to_thread(message_store.start_stream_session, slug, title)
    # Notificar al panel
    try:
        await manager.broadcast_live({
            "tipo": "social-session-started",
            "session": sess,
        })
    except Exception:
        pass
    return {"ok": True, "session": sess}


@app.post("/api/social/session/end")
async def social_session_end(payload: Optional[dict] = None):
    """Cierra la sesion actual. Body opcional: { 'notes': '...' }"""
    payload = payload or {}
    sess = message_store.current_session()
    if not sess:
        return JSONResponse({"error": "no hay sesion activa"}, status_code=400)
    notes = (payload.get("notes") or "").strip() or None
    ok = await asyncio.to_thread(
        message_store.end_stream_session, sess["id"], notes
    )
    try:
        await manager.broadcast_live({
            "tipo": "social-session-ended",
            "session_id": sess["id"],
        })
    except Exception:
        pass
    return {"ok": ok, "session_id": sess["id"]}


@app.get("/api/social/session/current")
async def social_session_current():
    return {"ok": True, "session": message_store.current_session()}


@app.get("/api/social/messages")
async def social_messages(platform: Optional[str] = None,
                          session_id: Optional[str] = None,
                          limit: int = 100):
    """Lista de mensajes recientes con filtros opcionales."""
    try:
        limit = max(1, min(int(limit), 500))
    except (TypeError, ValueError):
        limit = 100
    msgs = await asyncio.to_thread(
        message_store.get_recent, limit, platform, session_id
    )
    return {"ok": True, "messages": msgs, "count": len(msgs)}


@app.get("/api/social/messages/pinned")
async def social_messages_pinned(session_id: Optional[str] = None):
    """Mensajes pinned, opcionalmente filtrados por sesion."""
    msgs = await asyncio.to_thread(message_store.get_pinned, session_id)
    return {"ok": True, "messages": msgs, "count": len(msgs)}


@app.post("/api/social/messages/{msg_id}/pin")
async def social_message_pin(msg_id: str, payload: Optional[dict] = None):
    """Toggle pin. Body: { 'pinned': true|false }. Default true."""
    payload = payload or {}
    pinned = bool(payload.get("pinned", True))
    ok = await asyncio.to_thread(message_store.set_pinned, msg_id, pinned)
    if not ok:
        return JSONResponse({"error": f"mensaje {msg_id} no encontrado"}, status_code=404)
    # Broadcast al panel para que actualice la UI
    try:
        await manager.broadcast_live({
            "tipo": "social-message-pinned",
            "message_id": msg_id, "pinned": pinned,
        })
    except Exception:
        pass
    return {"ok": True, "pinned": pinned}


@app.post("/api/social/messages/{msg_id}/replied")
async def social_message_replied(msg_id: str, payload: Optional[dict] = None):
    """Toggle replied. Body: { 'replied': true|false }. Default true."""
    payload = payload or {}
    replied = bool(payload.get("replied", True))
    ok = await asyncio.to_thread(message_store.set_replied, msg_id, replied)
    if not ok:
        return JSONResponse({"error": f"mensaje {msg_id} no encontrado"}, status_code=404)
    return {"ok": True, "replied": replied}


# ─── Conectores: control ON/OFF desde el panel ─────────────────────────

@app.post("/api/social/connectors/twitch/start")
async def social_twitch_start(payload: dict):
    """Arranca el conector Twitch con los canales especificados.
    Body: { 'channels': ['retrotarros', 'otro'] }"""
    channels = payload.get("channels") or []
    if not isinstance(channels, list) or not channels:
        return JSONResponse({"error": "channels obligatorio (lista no vacia)"}, status_code=400)
    # Si ya hay uno corriendo, detenerlo primero
    existing = social_manager.manager.find_connector("twitch")
    if existing:
        try:
            await existing.stop()
            social_manager.manager._connectors.remove(existing)
        except Exception:
            pass
    conn = TwitchConnector(channels=channels)
    await social_manager.manager.register(conn)
    return {"ok": True, "platform": "twitch", "status": conn.get_status(),
            "channels": conn.channels}


@app.post("/api/social/connectors/twitch/stop")
async def social_twitch_stop():
    conn = social_manager.manager.find_connector("twitch")
    if not conn:
        return JSONResponse({"error": "Twitch no esta activo"}, status_code=400)
    await conn.stop()
    try:
        social_manager.manager._connectors.remove(conn)
    except ValueError:
        pass
    return {"ok": True}


@app.post("/api/social/connectors/discord/start")
async def social_discord_start():
    """Arranca el conector Discord usando variables de entorno
    (DISCORD_BOT_TOKEN + DISCORD_GUILD_ID + DISCORD_CHANNEL_IDS)."""
    existing = social_manager.manager.find_connector("discord")
    if existing:
        try:
            await existing.stop()
            social_manager.manager._connectors.remove(existing)
        except Exception:
            pass
    conn = discord_connector_mod.from_env()
    if conn is None:
        return JSONResponse({
            "error": "No se pudo crear conector Discord. Verifica que esten "
                     "DISCORD_BOT_TOKEN, DISCORD_GUILD_ID y discord.py instalada."
        }, status_code=400)
    await social_manager.manager.register(conn)
    return {"ok": True, "platform": "discord", "status": conn.get_status()}


@app.post("/api/social/connectors/discord/stop")
async def social_discord_stop():
    conn = social_manager.manager.find_connector("discord")
    if not conn:
        return JSONResponse({"error": "Discord no esta activo"}, status_code=400)
    await conn.stop()
    try:
        social_manager.manager._connectors.remove(conn)
    except ValueError:
        pass
    return {"ok": True}


@app.post("/api/social/connectors/youtube/start")
async def social_youtube_start(payload: Optional[dict] = None):
    """
    Arranca el conector YouTube Live Chat. Lee YOUTUBE_API_KEY del env.
    Body opcional: { 'video_id': 'XXXXXXXXXXX' } para override del env var.
    """
    payload = payload or {}
    existing = social_manager.manager.find_connector("youtube")
    if existing:
        try:
            await existing.stop()
            social_manager.manager._connectors.remove(existing)
        except Exception:
            pass
    conn = youtube_connector_mod.from_env()
    if conn is None:
        return JSONResponse({
            "error": "No se pudo crear conector YouTube. "
                     "Verifica YOUTUBE_API_KEY en el .env."
        }, status_code=400)
    # Si el payload trae video_id, override
    override_vid = (payload.get("video_id") or "").strip()
    if override_vid:
        conn.set_video_id(override_vid)
    if not conn.video_id:
        return JSONResponse({
            "error": "YouTube necesita un video_id (del stream activo). "
                     "Mandalo en el body o seteatlo en YOUTUBE_VIDEO_ID env var."
        }, status_code=400)
    await social_manager.manager.register(conn)
    return {"ok": True, "platform": "youtube", "status": conn.get_status(),
            "video_id": conn.video_id}


@app.post("/api/social/connectors/youtube/stop")
async def social_youtube_stop():
    conn = social_manager.manager.find_connector("youtube")
    if not conn:
        return JSONResponse({"error": "YouTube no esta activo"}, status_code=400)
    await conn.stop()
    try:
        social_manager.manager._connectors.remove(conn)
    except ValueError:
        pass
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 14: TarroBot RESPONDE al chat (SAY / RESPOND / DICTATE)
# ─────────────────────────────────────────────────────────────────────────

def _get_message_or_404(message_id: str) -> Optional[dict]:
    """Helper: busca un mensaje por id en SQLite (Sprint 16 B16.3: lookup directo)."""
    return message_store.get_message_by_id(message_id)


@app.post("/api/social/say")
async def social_say(payload: dict):
    """
    TarroBot lee un mensaje del chat en voz alta (TTS literal).
    Body:
      { "message_id": "twitch-xxx" }  o
      { "text": "...", "user_name": "...", "platform": "..." }
      Opcional: { "with_intro": true|false } (default true)
                "voz", "pitch", "rate"
    """
    msg_id = (payload.get("message_id") or "").strip()
    if msg_id:
        msg = _get_message_or_404(msg_id)
        if not msg:
            return JSONResponse({"error": f"mensaje {msg_id} no encontrado"}, status_code=404)
        viewer = msg.get("user_name", "alguien")
        text = msg.get("text", "")
        platform = msg.get("platform", "chat")
    else:
        text = (payload.get("text") or "").strip()
        if not text:
            return JSONResponse({"error": "manda message_id o text"}, status_code=400)
        viewer = (payload.get("user_name") or "").strip()
        platform = (payload.get("platform") or "chat").strip()

    with_intro = payload.get("with_intro", True)
    if with_intro and viewer:
        frase = f"{viewer} dice: {text}"
    else:
        frase = text

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()
    audio_url = await _hablar_frase(
        frase, "talking", f"VIEWER · {platform.upper()}", voz, pitch, rate
    )

    # Marcar replied
    if msg_id:
        try:
            await asyncio.to_thread(message_store.set_replied, msg_id, True)
            await manager.broadcast_live({
                "tipo": "social-message-replied",
                "message_id": msg_id, "replied": True,
            })
        except Exception:
            pass

    return {"ok": True, "texto": frase, "audio_url": audio_url}


@app.post("/api/social/respond")
async def social_respond(payload: dict):
    """
    TarroBot responde a un mensaje del chat con LLM (Claude) + TTS.
    Body:
      { "message_id": "twitch-xxx" }
      Opcional: { "post_to_channel": true|false } - publicar respuesta en
                 el canal de origen (solo Discord soportado por ahora)
                "voz", "pitch", "rate"
    """
    msg_id = (payload.get("message_id") or "").strip()
    if not msg_id:
        return JSONResponse({"error": "message_id obligatorio"}, status_code=400)
    msg = _get_message_or_404(msg_id)
    if not msg:
        return JSONResponse({"error": f"mensaje {msg_id} no encontrado"}, status_code=404)

    # Rate limit (LLM call)
    espera = llm_cooldown_check("social_respond")
    if espera is not None:
        return JSONResponse(
            {"error": f"cooldown LLM: espera {espera:.1f}s antes de responder otro mensaje"},
            status_code=429,
        )

    # Contexto opcional: si hay pauta cargada, pasarlo al LLM
    context = None
    if queue.loaded():
        context = queue.pauta.get("episodio") or queue.slug

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    if llm_resolver.is_modo_barato():
        return JSONResponse({
            "error": "modo barato activo: TarroBot no responde a chat con LLM. "
                     "Usa /api/social/dictate o /api/social/say."
        }, status_code=503)

    async with _procesando(f"respondiendo a {msg.get('user_name', '?')}..."):
        result = await asyncio.to_thread(
            generar_respuesta_chat_llm,
            msg.get("user_name", "alguien"),
            msg.get("text", ""),
            msg.get("platform", "chat"),
            context,
        )
    if result:
        llm_resolver.track_llm_call("social_respond")
    if not result:
        return JSONResponse(
            {"error": "fallo LLM. Verifica ANTHROPIC_API_KEY y creditos."},
            status_code=500,
        )

    texto = result.get("texto", "")
    estado = result.get("estado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    audio_url = await _hablar_frase(
        texto, estado, f"RESPUESTA A {msg.get('user_name', '').upper()}",
        voz, pitch, rate,
    )

    # Marcar replied
    try:
        await asyncio.to_thread(message_store.set_replied, msg_id, True)
        await manager.broadcast_live({
            "tipo": "social-message-replied",
            "message_id": msg_id, "replied": True,
        })
    except Exception:
        pass

    # Opcional: publicar en el canal de origen (solo Discord)
    posted_to_channel = False
    post_error = None
    if payload.get("post_to_channel"):
        if msg.get("platform") == "discord":
            channel_id = (msg.get("meta") or {}).get("channel_id")
            if channel_id:
                discord_conn = social_manager.manager.find_connector("discord")
                if discord_conn and hasattr(discord_conn, "send_to_channel"):
                    try:
                        await discord_conn.send_to_channel(int(channel_id), texto)
                        posted_to_channel = True
                    except Exception as e:
                        post_error = str(e)
                else:
                    post_error = "Discord no conectado o sin metodo send_to_channel"
            else:
                post_error = "mensaje sin channel_id"
        else:
            post_error = f"plataforma '{msg.get('platform')}' no soporta write-back (solo Discord)"

    return {
        "ok": True, "texto": texto, "estado": estado, "audio_url": audio_url,
        "posted_to_channel": posted_to_channel,
        "post_error": post_error,
    }


@app.post("/api/social/dictate")
async def social_dictate(payload: dict):
    """
    El operador escribe una respuesta y TarroBot la lee literal con voz.
    Body:
      { "text": "...", "message_id": "opcional para marcar replied",
        "estado": "happy", "post_to_channel": true|false }
    """
    text = (payload.get("text") or "").strip()
    if not text:
        return JSONResponse({"error": "text obligatorio"}, status_code=400)
    estado = (payload.get("estado") or "talking").strip()
    if estado not in ESTADOS:
        estado = "talking"
    msg_id = (payload.get("message_id") or "").strip() or None

    voz, pitch, rate = _obtener_voz_pitch_rate(payload)
    tracker.mark_input()

    # chilenizar por si el operador escribio en argentino sin querer
    text = chilenizar(text)

    label = f"DICTADO · {estado.upper()}"
    if msg_id:
        msg = _get_message_or_404(msg_id)
        if msg:
            label = f"RESP A {msg.get('user_name', '').upper()}"

    audio_url = await _hablar_frase(text, estado, label, voz, pitch, rate)

    if msg_id:
        try:
            await asyncio.to_thread(message_store.set_replied, msg_id, True)
            await manager.broadcast_live({
                "tipo": "social-message-replied",
                "message_id": msg_id, "replied": True,
            })
        except Exception:
            pass

    # Post to channel (Discord) si pide
    posted_to_channel = False
    post_error = None
    if payload.get("post_to_channel") and msg_id:
        msg = _get_message_or_404(msg_id)
        if msg and msg.get("platform") == "discord":
            channel_id = (msg.get("meta") or {}).get("channel_id")
            if channel_id:
                discord_conn = social_manager.manager.find_connector("discord")
                if discord_conn and hasattr(discord_conn, "send_to_channel"):
                    try:
                        await discord_conn.send_to_channel(int(channel_id), text)
                        posted_to_channel = True
                    except Exception as e:
                        post_error = str(e)

    return {"ok": True, "texto": text, "audio_url": audio_url,
            "posted_to_channel": posted_to_channel, "post_error": post_error}


# ─── Cola: leer pinned secuencial ────────────────────────────────────

_pinned_queue_task: Optional[asyncio.Task] = None
_pinned_queue_stop = asyncio.Event()


@app.post("/api/social/read-pinned-queue")
async def social_read_pinned_queue(payload: Optional[dict] = None):
    """
    Lanza un task que lee TODOS los mensajes pinned en orden (oldest first).
    Espera entre cada uno a que el TTS termine (via tracker.is_speaking).
    Si ya hay una cola corriendo, la cancela y arranca de cero.

    Body opcional: { "stop": true } para solo detener la cola actual.
    """
    global _pinned_queue_task
    payload = payload or {}
    if payload.get("stop"):
        if _pinned_queue_task and not _pinned_queue_task.done():
            _pinned_queue_stop.set()
            _pinned_queue_task.cancel()
            try:
                await _pinned_queue_task
            except (asyncio.CancelledError, Exception):
                pass
        return {"ok": True, "stopped": True}

    # Cancelar cola previa si hay
    if _pinned_queue_task and not _pinned_queue_task.done():
        _pinned_queue_stop.set()
        _pinned_queue_task.cancel()
        try:
            await _pinned_queue_task
        except (asyncio.CancelledError, Exception):
            pass

    _pinned_queue_stop.clear()
    voz, pitch, rate = _obtener_voz_pitch_rate(payload)

    async def _read_loop():
        pinned = await asyncio.to_thread(message_store.get_pinned, None)
        if not pinned:
            return
        # Orden por timestamp ascendente (oldest primero, mas natural)
        pinned.sort(key=lambda m: m["timestamp_ms"])
        for i, m in enumerate(pinned):
            if _pinned_queue_stop.is_set():
                break
            viewer = m.get("user_name", "alguien")
            text = m.get("text", "")
            platform = m.get("platform", "chat")
            frase = f"{viewer} pregunta: {text}"
            await _hablar_frase(
                frase, "thinking",
                f"PINNED {i+1}/{len(pinned)} · {platform.upper()}",
                voz, pitch, rate,
            )
            # Esperar a que termine de hablar este mensaje antes de pasar al siguiente
            wait_start = time.time()
            while tracker.is_speaking and (time.time() - wait_start) < 30:
                if _pinned_queue_stop.is_set():
                    break
                await asyncio.sleep(0.3)
            if _pinned_queue_stop.is_set():
                break
            # Pequeno gap entre mensajes para que no sean rafaga
            await asyncio.sleep(0.8)

    _pinned_queue_task = asyncio.create_task(_read_loop(), name="pinned-queue")
    return {"ok": True, "started": True}


# ─── Discord post genérico (para casos no asociados a un message_id) ──

# ─────────────────────────────────────────────────────────────────────────
# Sprint 15: telemetria + modo barato
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/llm/stats")
async def llm_stats():
    """Estadisticas de uso de LLM: calls, costo estimado, cache."""
    return {"ok": True, **llm_resolver.telemetry_snapshot()}


@app.post("/api/llm/stats/reset")
async def llm_stats_reset():
    """Resetea contadores de la sesion (no toca el cache JSON)."""
    llm_resolver.reset_telemetry()
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────
# Sprint 16 B16.1: Auto-respond toggle
# ─────────────────────────────────────────────────────────────────────────

@app.get("/api/social/auto-respond")
async def social_auto_respond_get():
    """Estado actual del auto-respond: config + counters."""
    return {"ok": True, **auto_respond.status()}


@app.post("/api/social/auto-respond")
async def social_auto_respond_set(payload: dict):
    """
    Configura el auto-respond. Acepta cualquiera de los siguientes campos:
      activo (bool), mention_only (bool), cooldown_user_s (int),
      cooldown_global_s (int), skip_if_speaking (bool), platforms (list)
    Solo se actualizan los campos que vengan en el body.
    Body especial: { 'reset_counters': true } resetea contadores sin tocar config.
    """
    if payload.get("reset_counters"):
        auto_respond.reset_counters()
        return {"ok": True, "reset": True, **auto_respond.status()}

    # Sanitizar tipos
    kwargs = {}
    for key in ("activo", "mention_only", "skip_if_speaking"):
        if key in payload:
            kwargs[key] = bool(payload[key])
    for key in ("cooldown_user_s", "cooldown_global_s"):
        if key in payload:
            try:
                kwargs[key] = max(0, int(payload[key]))
            except (TypeError, ValueError):
                pass
    if "platforms" in payload and isinstance(payload["platforms"], list):
        kwargs["platforms"] = [str(p) for p in payload["platforms"]]

    auto_respond.update_config(**kwargs)
    return {"ok": True, **auto_respond.status()}


@app.post("/api/llm/modo-barato")
async def llm_modo_barato(payload: dict):
    """
    Toggle del modo barato. Cuando esta on, las llamadas LLM se rechazan
    con 503 y los endpoints intentan responder con material pre-generado
    (pauta enriquecida o cache local).
    Body: { "activo": true|false }
    """
    activo = bool(payload.get("activo", False))
    llm_resolver.set_modo_barato(activo)
    return {"ok": True, "modo_barato": llm_resolver.is_modo_barato()}


@app.post("/api/social/post-message")
async def social_post_message(payload: dict):
    """
    Publica un mensaje en un canal Discord arbitrario.
    Body: { "platform": "discord", "channel_id": "123", "text": "..." }
    Solo Discord soportado por ahora.
    """
    platform = (payload.get("platform") or "").strip()
    if platform != "discord":
        return JSONResponse(
            {"error": f"platform '{platform}' no soportada para post (solo Discord)"},
            status_code=400,
        )
    channel_id_raw = payload.get("channel_id")
    text = (payload.get("text") or "").strip()
    if not channel_id_raw or not text:
        return JSONResponse({"error": "channel_id y text obligatorios"}, status_code=400)
    try:
        channel_id = int(channel_id_raw)
    except (TypeError, ValueError):
        return JSONResponse({"error": "channel_id invalido"}, status_code=400)

    discord_conn = social_manager.manager.find_connector("discord")
    if not discord_conn:
        return JSONResponse({"error": "Discord no esta activo"}, status_code=400)
    if not hasattr(discord_conn, "send_to_channel"):
        return JSONResponse({"error": "conector Discord sin send_to_channel"}, status_code=500)
    try:
        await discord_conn.send_to_channel(channel_id, text)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return {"ok": True, "channel_id": channel_id}


@app.get("/api/ping")
async def ping():
    return {
        "ok": True,
        "live_clients": len(manager.live_clients),
        "idle_state": tracker.current_idle_state,
        "is_speaking": tracker.is_speaking,
        "queue": {
            "loaded": queue.loaded(),
            "slug": queue.slug,
            "indice": queue.indice,
            "total": queue.total(),
        },
    }


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
    print(f"  Hotkeys globales (cualquier app activa):")
    for key, (_, label) in HOTKEYS.items():
        print(f"    {label}")
    print(f"")
    print(f"  Ping de salud:")
    print(f"    http://localhost:{PORT}/api/ping")
    print(f"")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
