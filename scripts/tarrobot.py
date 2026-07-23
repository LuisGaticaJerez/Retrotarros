"""
tarrobot.py
Asistente de datos curiosos retro Retrotarros · TarroBot.

Uso:
    python scripts/tarrobot.py "Super Mario 64"           # busca en DB local
    python scripts/tarrobot.py "Super Mario 64" --slide   # + genera HTML
    python scripts/tarrobot.py "X" --generate             # genera con Claude API
    python scripts/tarrobot.py --add "tema" "texto" --state talking
    python scripts/tarrobot.py --list                      # lista todos los datos

Requisitos:
    pip install anthropic    (solo para --generate)

Para --generate, setear variable de entorno:
    PowerShell:  $env:ANTHROPIC_API_KEY = "sk-ant-..."
    cmd:         setx ANTHROPIC_API_KEY "sk-ant-..."   (persistente, reabrir terminal)
"""

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path
from datetime import date
from typing import Optional

# REPO puede venir de env var (modo Drive, estudio compartido) o del path del script.
# Esto permite que el PC del estudio lea el repo desde el Drive sincronizado y
# vea automaticamente todas las pautas/datos que generas en tu PC.
_REPO_FROM_ENV = os.environ.get("RETROTARROS_REPO")
if _REPO_FROM_ENV and Path(_REPO_FROM_ENV).exists():
    REPO = Path(_REPO_FROM_ENV).resolve()
else:
    REPO = Path(__file__).parent.parent

DB_PATH = REPO / "data" / "tarrobot-database.json"
TEMPLATE = REPO / "studio" / "templates" / "_template-tarrobot-slide.html"
OUT_DIR = REPO / "studio" / "tarrobot-out"
PAUTAS_DIR = REPO / "studio" / "pautas"
PAUTAS_AUDIO_DIR = PAUTAS_DIR / "audio"

# Sprint 8.1: melodias (MIDI fans -> MP3 con FluidSynth + soundfont SNES)
MELODIAS_DIR = REPO / "studio" / "melodias"
SOUNDFONT_PATH = MELODIAS_DIR / "soundfont.sf2"
FFMPEG_BIN = REPO / "installers" / "tarrobot-studio" / "bin" / "ffmpeg.exe"  # del instalador

ESTADOS = [
    "idle", "talking", "excited", "sleep", "thinking", "winking",
    "confused", "glitched", "fact", "happy", "sad", "angry", "loading",
    "whistling",  # Sprint 8.1: tocando melodia (notas saliendo de la boca)
]

LABEL_POR_ESTADO = {
    "idle":      "DATO CURIOSO",
    "talking":   "DATO CURIOSO",
    "excited":   "DATO BOMBA · MIND BLOWN",
    "fact":      "FACT TIME · DATO ESTRELLA",
    "thinking":  "PROCESANDO DATO...",
    "winking":   "ENTRE NOSOTROS...",
    "confused":  "EN SERIO?",
    "happy":     "BUENA NOTICIA",
    "sad":       "QUE PENA",
    "angry":     "ESTO NO ME GUSTA",
    "loading":   "BUSCANDO INFO...",
    "glitched":  "SEÑAL CORRUPTA",
    "sleep":     "DESCANSANDO",
    "whistling": "MUSICA DE FONDO ♪",
}


# ─────────────────────────────────────────────────────────────────────────
# Util
# ─────────────────────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-")


def cargar_db() -> dict:
    if not DB_PATH.exists():
        return {"version": 1, "actualizado": str(date.today()), "datos": []}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def guardar_db(data: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["actualizado"] = str(date.today())
    DB_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def buscar(tema: str, db: dict) -> list:
    """Substring match case-insensitive contra el campo 'tema'."""
    t = tema.lower()
    return [d for d in db["datos"] if t in d.get("tema", "").lower()]


def agregar_dato(
    tema: str,
    texto: str,
    estado: str,
    db: dict,
    consola: str = "",
    ano: int = 0,
    editor: str = "",
    fuente: str = "manual",
) -> dict:
    base_slug = slugify(tema)
    # Evitar colision de IDs
    existing_ids = {d["id"] for d in db["datos"]}
    n = 1
    new_id = f"{base_slug}-{n}"
    while new_id in existing_ids:
        n += 1
        new_id = f"{base_slug}-{n}"

    dato = {
        "id": new_id,
        "tema": tema,
        "texto": texto,
        "estado": estado,
        "consola": consola or "",
        "ano": ano or 0,
        "editor": editor or "",
        "creado": str(date.today()),
        "fuente": fuente,
    }
    db["datos"].append(dato)
    guardar_db(db)
    return dato


# ─────────────────────────────────────────────────────────────────────────
# LLM (Claude API)
# ─────────────────────────────────────────────────────────────────────────

def call_claude(
    prompt: str,
    max_tokens: int = 300,
    model: str = "claude-haiku-4-5",
    parse_json: bool = True,
    system: str | None = None,
) -> dict | str | None:
    """
    Sprint 16 B16.2: helper unificado para llamar Claude.

    Centraliza:
      - Init del cliente Anthropic con check de API key
      - Llamada messages.create con manejo de errores
      - Strip de markdown fences (```)
      - Parseo JSON opcional
      - System prompt opcional (preparado para prompt caching futuro)

    Devuelve dict (si parse_json=True) o str (si parse_json=False) o None
    si fallo. Las funciones LLM existentes siguen funcionando como estan;
    este helper se usa para llamadas NUEVAS que no quieran duplicar codigo.

    NOTA: no se refactorizaron las 8 funciones LLM existentes a este helper
    para evitar riesgo de romper lo que ya anda. Si en sprint futuro se
    quiere unificar, este es el target.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    try:
        response = client.messages.create(**kwargs)
    except Exception as e:
        print(f"ERROR call_claude: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    if not parse_json:
        return raw

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR call_claude: JSON invalido: {e}\n{raw[:300]}", file=sys.stderr)
        return None

    # Aplicar chilenizar a textos comunes si el dict tiene esos keys
    if isinstance(result, dict) and "texto" in result and isinstance(result["texto"], str):
        result["texto"] = chilenizar(result["texto"])

    return result


def generar_con_llm(tema: str) -> dict | None:
    """
    Llama a Claude API para generar 3 propuestas de datos curiosos.
    Requiere variable de entorno ANTHROPIC_API_KEY.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        print("Instalala con: pip install anthropic", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: variable de entorno ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        print("", file=sys.stderr)
        print("PowerShell (sesion actual):", file=sys.stderr)
        print('  $env:ANTHROPIC_API_KEY = "sk-ant-..."', file=sys.stderr)
        print("", file=sys.stderr)
        print("PowerShell (persistente):", file=sys.stderr)
        print('  [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY","sk-ant-...","User")', file=sys.stderr)
        print("  (despues reabrir la terminal)", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Eres TarroBot, mascota del canal de YouTube Retrotarros sobre videojuegos retro.
Genera 3 datos curiosos cortos sobre: "{tema}".

Requisitos OBLIGATORIOS (este texto se reproduce con TTS, por eso reglas estrictas):
- Español ESTRICTAMENTE chileno neutro con TUTEO (tú/tienes/sabes/dime/puedes/mira).
- NO usar voseo argentino: PROHIBIDO "tenés", "querés", "decime", "vení", "vos",
  "sos", "podés", "sabés", "decís", "andás", "vas vos", "che", "andá", "haceme",
  "fijate" (con voseo). USA: "eres", "tienes", "quieres", "puedes", "dime", "vas".
- NO usar palabras o entonaciones que suenen argentino-uruguayas, evitar:
  * "acá" -> usa "aquí"
  * "andábamos" -> usa "estábamos"
  * "me agarraste" -> usa "me pillaste"
  * "pasa" (como saludo) -> usa "permite" o "disculpa"
  * "bajando el telón" -> usa "cerrando"
  * "pibe/piba" -> usa "chico/chica" o "amigo"
  * "guita" -> usa "plata" o "dinero"
- USA TILDES correctas del español ortográfico estándar (también, está, mí, sí, etc.).
  Esto es importante para que el TTS pronuncie correctamente.
- NÚMEROS EN PALABRAS, no en cifras. Ejemplos:
  * "20 mil dólares" en vez de "20,000 dólares" (el TTS lee "veinte mil")
  * "5 mil" en vez de "5,000"
  * Años SÍ van en cifras: 1996, 1985
- Máximo 3 oraciones por dato, alrededor de 220 caracteres.
- Verificable y específico: fechas, números, nombres reales.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabías".
- Cada dato distinto del otro (no parafrasear el mismo hecho).

Devuelve SOLO un JSON valido con esta estructura exacta, SIN texto extra ni codigo markdown:

{{
  "consola": "...",
  "ano": 0,
  "editor": "...",
  "datos": [
    {{"texto": "...", "estado_recomendado": "talking"}},
    {{"texto": "...", "estado_recomendado": "excited"}},
    {{"texto": "...", "estado_recomendado": "fact"}}
  ]
}}

Estados validos para "estado_recomendado": talking, excited, fact, winking, confused, happy, sad, angry, thinking.
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR: llamada a Claude API fallo: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    # Limpiar codeblocks si los devolvio
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: el LLM devolvio JSON invalido: {e}", file=sys.stderr)
        print(raw, file=sys.stderr)
        return None

    # Filtro anti-voseo en los textos generados (defensa ultima)
    if "datos" in result and isinstance(result["datos"], list):
        for d in result["datos"]:
            if "texto" in d:
                d["texto"] = chilenizar(d["texto"])

    return result


# ─────────────────────────────────────────────────────────────────────────
# TTS (Edge TTS)
# ─────────────────────────────────────────────────────────────────────────

# Voces sugeridas para TarroBot (es- latino)
VOCES_SUGERIDAS = {
    "catalina":  "es-CL-CatalinaNeural",   # chilena default, calza con el canal
    "yolanda":   "es-NI-YolandaNeural",    # juvenil nicaraguense
    "karina":    "es-PR-KarinaNeural",     # juvenil puertorriquena
    "salome":    "es-CO-SalomeNeural",     # colombiana neutra
    "dalia":     "es-MX-DaliaNeural",      # mexicana adulta clara
    "lorenzo":   "es-CL-LorenzoNeural",    # chileno masculino
    "tomas":     "es-AR-TomasNeural",      # NO usar (argentino - rompe regla canal)
}
VOZ_DEFAULT = "es-CL-CatalinaNeural"
PITCH_DEFAULT = "+12Hz"   # un poco mas joven/curioso
RATE_DEFAULT = "+0%"

# Presets de voz: cada uno combina (voz Edge TTS, pitch, rate) para un
# estilo distinto. Los presets "-nino" suben el pitch para sonar mas
# infantil. El default es "tarrobot" (catalina +12Hz).
PRESETS_VOZ = {
    # Default actual: joven curioso femenino chileno
    "tarrobot":        ("es-CL-CatalinaNeural", "+12Hz", "+0%"),
    # Mas infantil: pitch elevado, mas energico
    "tarrobot-nino":   ("es-CL-CatalinaNeural", "+24Hz", "+5%"),
    "tarrobot-bebe":   ("es-CL-CatalinaNeural", "+35Hz", "+8%"),
    # Niño masculino chileno
    "tarrobot-pibe":   ("es-CL-LorenzoNeural",  "+18Hz", "+5%"),
    # Otras voces femeninas latinas con pitch infantil
    "renata-nina":     ("es-NI-YolandaNeural",  "+18Hz", "+3%"),
    "karina-nina":     ("es-PR-KarinaNeural",   "+18Hz", "+3%"),
    "camila-nina":     ("es-PE-CamilaNeural",   "+18Hz", "+3%"),
    "paola-nina":      ("es-VE-PaolaNeural",    "+18Hz", "+3%"),
    "valentina-nina":  ("es-UY-ValentinaNeural","+18Hz", "+3%"),
    "sofia-nina":      ("es-BO-SofiaNeural",    "+18Hz", "+3%"),
    # Mexicanas
    "dalia":           ("es-MX-DaliaNeural",    "+14Hz", "+0%"),
    "jorge-pibe":      ("es-MX-JorgeNeural",    "+18Hz", "+5%"),
    # Tonos especiales
    "narrador":        ("es-MX-DaliaNeural",    "+0Hz",  "-5%"),  # serio
    "energico":        ("es-CL-CatalinaNeural", "+15Hz", "+10%"), # rapido entusiasta
}


def resolver_voz(voz_arg: str) -> str:
    """Acepta alias corto ('catalina') o nombre completo Edge ('es-CL-...')."""
    if not voz_arg:
        return VOZ_DEFAULT
    if voz_arg in VOCES_SUGERIDAS:
        return VOCES_SUGERIDAS[voz_arg]
    # Si es un preset, devolver solo la voz (el pitch/rate los maneja resolver_preset)
    if voz_arg in PRESETS_VOZ:
        return PRESETS_VOZ[voz_arg][0]
    return voz_arg


def resolver_preset(nombre: Optional[str]) -> tuple[str, str, str]:
    """
    Devuelve (voz, pitch, rate) para un preset nombrado.
    Si no existe, devuelve los defaults.
    """
    if nombre and nombre in PRESETS_VOZ:
        return PRESETS_VOZ[nombre]
    return (VOZ_DEFAULT, PITCH_DEFAULT, RATE_DEFAULT)


def generar_tts(dato: dict, voz: str = VOZ_DEFAULT, pitch: str = PITCH_DEFAULT, rate: str = RATE_DEFAULT) -> Path | None:
    """
    Genera MP3 con voz TarroBot usando Edge TTS.
    Output: studio/tarrobot-out/<id>.mp3
    """
    try:
        import edge_tts
    except ImportError:
        print("ERROR: libreria 'edge-tts' no instalada.", file=sys.stderr)
        print("Instalala con: pip install edge-tts", file=sys.stderr)
        return None

    import asyncio

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{dato['id']}.mp3"

    texto = dato["texto"]

    async def _generar():
        communicate = edge_tts.Communicate(
            texto,
            voice=voz,
            pitch=pitch,
            rate=rate,
        )
        await communicate.save(str(out_path))

    try:
        asyncio.run(_generar())
    except Exception as e:
        print(f"ERROR: TTS fallo: {e}", file=sys.stderr)
        return None

    return out_path


# ─────────────────────────────────────────────────────────────────────────
# Pauta (cola del episodio)
# ─────────────────────────────────────────────────────────────────────────
#
# Una pauta es un JSON paralelo a un episodio HTML que contiene la cola de
# datos pre-armada para que TarroBot los reproduzca en orden durante la
# grabacion. Vive en studio/pautas/<slug>.tarrobot.json al lado del HTML.
#
# Schema:
#   {
#     "version": 1, "slug": "...", "episodio": "...", "creado": "...",
#     "actualizado": "...", "voz": "...", "pitch": "...", "rate": "...",
#     "datos": [
#       {
#         "id": "<slug>-N", "tema": "...", "texto": "...", "estado": "talking",
#         "consola": "...", "ano": 0, "editor": "...",
#         "mp3": "audio/<slug>/<id>.mp3"  (relativo a PAUTAS_DIR, null si no precargado),
#         "duracion_ms": null,
#         "fuente": "pauta-manual"|"pauta-auto"
#       }
#     ]
#   }
#
# Los MP3 viven en studio/pautas/audio/<slug>/ y NO se versionan (regenerables).
# El JSON SI se versiona — es el guion del episodio.


def _ejecutar_sync_drive(verbose: bool = True) -> bool:
    """
    Corre el script sync-tarrobot-to-drive.ps1 en background.
    Devuelve True si el sync arranco OK (no espera el resultado completo).
    """
    import subprocess
    sync_script = REPO / "scripts" / "sync-tarrobot-to-drive.ps1"
    if not sync_script.exists():
        if verbose:
            print(f"[SYNC] skip: {sync_script.name} no existe en este repo")
        return False
    try:
        if verbose:
            print()
            print("[SYNC] Sincronizando con Drive...")
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(sync_script)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            if verbose:
                # Mostrar solo la linea de SYNC COMPLETO + contadores
                for line in result.stdout.splitlines():
                    if "sincronizados" in line.lower() or "skipped" in line.lower():
                        print(f"[SYNC] {line.strip()}")
                print("[SYNC] Drive Desktop sincronizara al cloud en 1-3 min.")
            return True
        else:
            if verbose:
                print(f"[SYNC] error (exit {result.returncode}):")
                print(result.stderr[-500:])
            return False
    except subprocess.TimeoutExpired:
        if verbose:
            print("[SYNC] timeout (120s). El sync sigue en background, no es critico.")
        return False
    except Exception as e:
        if verbose:
            print(f"[SYNC] error: {e}")
        return False


def _path_dentro_repo(p: Path) -> bool:
    """Valida que un path resuelto este dentro del repo (defensa path traversal)."""
    try:
        p.resolve().relative_to(REPO.resolve())
        return True
    except (ValueError, OSError):
        return False


def pauta_path(slug: str) -> Path:
    """Devuelve el path del JSON de pauta para un slug dado."""
    safe = slugify(slug)
    return PAUTAS_DIR / f"{safe}.tarrobot.json"


def pauta_audio_dir(slug: str) -> Path:
    """Carpeta donde viven los MP3 precargados de una pauta."""
    safe = slugify(slug)
    return PAUTAS_AUDIO_DIR / safe


def cargar_pauta(slug: str) -> dict | None:
    p = pauta_path(slug)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def guardar_pauta(pauta: dict) -> Path:
    PAUTAS_DIR.mkdir(parents=True, exist_ok=True)
    pauta["actualizado"] = str(date.today())
    p = pauta_path(pauta["slug"])
    p.write_text(
        json.dumps(pauta, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return p


def crear_pauta_vacia(slug: str, episodio: str, voz: str = VOZ_DEFAULT,
                      pitch: str = PITCH_DEFAULT, rate: str = RATE_DEFAULT) -> dict:
    """Crea una pauta vacia con metadata pero sin datos."""
    return {
        "version": 1,
        "slug": slugify(slug),
        "episodio": episodio,
        "creado": str(date.today()),
        "actualizado": str(date.today()),
        "voz": voz,
        "pitch": pitch,
        "rate": rate,
        "datos": [],
    }


def extraer_contexto_html(html_path: Path, max_chars: int = 6000) -> str:
    """
    Lee un HTML de episodio y extrae texto plano relevante (titulo + secciones)
    para mandar a Claude como contexto. Heuristica simple: saca tags y comprime.
    """
    raw = html_path.read_text(encoding="utf-8", errors="ignore")

    # Sacar <script>, <style>, comentarios
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.IGNORECASE | re.DOTALL)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.DOTALL)

    # Reemplazar tags por espacio
    texto = re.sub(r"<[^>]+>", " ", raw)
    # Decodificar entities basicas
    texto = (texto.replace("&nbsp;", " ").replace("&amp;", "&")
                  .replace("&lt;", "<").replace("&gt;", ">")
                  .replace("&quot;", '"').replace("&#39;", "'"))
    # Comprimir whitespace
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:max_chars]


def generar_pauta_con_llm(html_path: Path, n_datos: int = 10) -> dict | None:
    """
    Lee el HTML del episodio y le pide a Claude que genere n_datos datos
    curiosos sincronizados con el contenido del episodio.
    Devuelve dict con keys: episodio, datos[].
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        print("Instalala con: pip install anthropic", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: variable de entorno ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        return None

    contexto = extraer_contexto_html(html_path)
    if not contexto:
        print(f"ERROR: no se pudo extraer texto del HTML {html_path}", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Eres TarroBot, mascota del canal de YouTube Retrotarros sobre videojuegos retro.
Te paso el contenido de un episodio del canal. Tu tarea: generar exactamente {n_datos} datos curiosos cortos para que TarroBot los lance durante la grabacion del programa, en orden, sincronizados con lo que se va presentando en el episodio.

CONTENIDO DEL EPISODIO:
\"\"\"
{contexto}
\"\"\"

Requisitos OBLIGATORIOS para CADA dato (este texto se reproduce con TTS):
- Español ESTRICTAMENTE chileno neutro con TUTEO (tú/tienes/sabes/dime/puedes/mira).
- NO voseo argentino: PROHIBIDO "tenés", "querés", "decime", "vení", "vos",
  "che", "andá", "haceme", "fijate" (con voseo).
- NO palabras que suenen argentinas/uruguayas: evita "acá" (usa "aquí"),
  "andábamos" (usa "estábamos"), "me agarraste" (usa "me pillaste"),
  "pibe/piba" (usa "chico/amigo"), "guita" (usa "plata").
- USA TILDES correctas del español ortográfico (también, está, día, año, mí, sí).
  Es crítico para que el TTS pronuncie correctamente.
- NÚMEROS EN PALABRAS para cifras grandes:
  * "20 mil dólares" en vez de "20,000 dólares"
  * "5 mil copias" en vez de "5,000"
  * Años SÍ van en cifras: 1996, 1985
  Los pronuncia bien así.
- Máximo 3 oraciones por dato, alrededor de 200-260 caracteres.
- Verificable y específico: fechas, números, nombres reales.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabías".
- Cada dato distinto del otro.
- Los datos deben seguir el ORDEN del episodio (si el episodio lista Top 10, dato 1 = item 10, dato 2 = item 9, etc.).
- Distribuye los estados emocionales para que no sean todos iguales.

Devuelve SOLO un JSON valido con esta estructura exacta, SIN texto extra ni markdown:

{{
  "episodio_titulo": "...",
  "datos": [
    {{
      "tema": "Nombre del juego o tema puntual",
      "texto": "El dato curioso completo, max 260 chars.",
      "estado": "talking",
      "consola": "SNES",
      "ano": 1994,
      "editor": "Nintendo"
    }}
    // ... {n_datos} en total
  ]
}}

Estados validos: talking, excited, fact, winking, confused, happy, sad, angry, thinking.
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR: llamada a Claude API fallo: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: el LLM devolvio JSON invalido: {e}", file=sys.stderr)
        print(raw[:800], file=sys.stderr)
        return None

    # Filtro anti-voseo en los textos generados (defensa ultima)
    if "datos" in result and isinstance(result["datos"], list):
        for d in result["datos"]:
            if "texto" in d:
                d["texto"] = chilenizar(d["texto"])

    return result


def generar_pauta_tema_con_llm(
    tema: str,
    n_datos: int = 10,
    consola_hint: str | None = None,
    enfoque: str | None = None,
    enriquecido: bool = True,
) -> dict | None:
    """
    Sprint 11 + Sprint 15: genera una pauta completa a partir de un tema libre.

    Si enriquecido=True (Sprint 15 default), ademas de los datos basicos
    genera CONTENIDO COLATERAL pre-horneado para minimizar llamadas LLM
    durante grabacion:
      - Por cada dato: opiniones_alternativas (3), comentarios_cortos (5),
        quiz_pregenerado (2 preguntas con respuesta).
      - A nivel episodio: catchphrases_episodio (8), intros_cold_open (3),
        outros_cliffhanger (3), publicacion {titulos, descripcion,
        hashtags, thumbnail_prompts, ig_post}.

    Resultado: durante grabacion, ~80% de las llamadas Claude se evitan
    porque ya esta todo cacheado en el JSON.

    Devuelve dict con la estructura completa.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        print("Instalala con: pip install anthropic", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: variable de entorno ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        return None

    client = anthropic.Anthropic(api_key=api_key)

    consola_linea = (
        f"- CONSOLA O AMBITO: limita los datos a {consola_hint}." if consola_hint else
        "- CONSOLA O AMBITO: elige la que mejor calce con el tema; si el tema cubre varias, mezcla."
    )
    enfoque_linea = (
        f"- ENFOQUE ESPECIFICO: {enfoque}." if enfoque else
        "- ENFOQUE: datos curiosos, anecdotas, rarezas, hechos verificables que enganchen a un retrogamer."
    )

    # Sprint 15 B15.1: bloque "enriquecido" pide TODO el contenido colateral
    # en una sola llamada para evitar 30+ llamadas LLM durante grabacion.
    bloque_enriquecido = ""
    if enriquecido:
        bloque_enriquecido = f"""

CONTENIDO COLATERAL (CRITICO - Sprint 15 ahorro de gasto):

Ademas de los {n_datos} datos basicos, genera el siguiente material extra
para que durante la grabacion NO se necesiten mas llamadas LLM:

Por CADA DATO ademas de tema/texto/estado/consola/ano/editor, agrega:
  - "opiniones_alternativas": array de 3 strings, cada una es una opinion
    distinta de TarroBot sobre ese tema (1-2 oraciones, max 200 chars).
  - "comentarios_cortos": array de 5 strings cortos (max 80 chars) que
    TarroBot puede soltar entre datos para colorear ("te lo digo yo",
    "esa es de las buenas", etc, contextualizadas al item).
  - "quiz_pregenerado": array de 2 objetos {{"pregunta":"...", "respuesta":"...",
    "pista":"..."}} - trivia sobre ese item.

A NIVEL EPISODIO, agrega:
  - "catchphrases_episodio": array de 8 strings, frases especificas
    contextuales al episodio (no genericas), max 80 chars cada una.
  - "intros_cold_open": array de 3 strings - aperturas posibles del
    video (max 220 chars cada una, energicas).
  - "outros_cliffhanger": array de 3 strings - cierres con gancho al
    proximo episodio (max 220 chars).
  - "publicacion": objeto con todo el material para YouTube:
      {{
        "titulos": [3 titulos optimizados CTR, max 70 chars],
        "descripcion": "Descripcion completa del video, 2-3 parrafos
                        + lista de items con timestamps tentativos,
                        SIN tildes y SIN emojis (regla del canal)",
        "hashtags": [15-20 hashtags retro/tema, sin espacios],
        "thumbnail_prompts": [5 prompts en INGLES para generar
                              thumbnails con IA, descriptivos],
        "ig_post": "Post para Instagram/Reels max 280 chars, tono
                    casual chileno, emojis OK"
      }}

REGLA CRITICA PARA TODO EL CONTENIDO COLATERAL:
- TODO va con las MISMAS reglas de chileno neutro tuteo + sin voseo.
- Las opiniones tienen variedad: no todas felices, mezcla winking,
  thinking, confused, etc.
- Los comentarios cortos son tipo "interjecciones" para soltar entre datos.
- El quiz_pregenerado: pregunta corta, respuesta corta (max 30 chars),
  pista opcional para si el operador quiere darla.
"""

    estructura_basica = f"""
{{
  "episodio_titulo": "Titulo corto del episodio (max 60 chars)",
  "datos": [
    {{
      "tema": "Nombre del juego o item puntual (max 40 chars)",
      "texto": "El dato curioso completo, max 260 chars.",
      "estado": "talking",
      "consola": "SNES",
      "ano": 1994,
      "editor": "Nintendo"
    }}
  ]
}}"""

    estructura_enriquecida = f"""
{{
  "episodio_titulo": "...",
  "catchphrases_episodio": ["...", "...", ...],
  "intros_cold_open": ["...", "...", "..."],
  "outros_cliffhanger": ["...", "...", "..."],
  "publicacion": {{
    "titulos": ["...", "...", "..."],
    "descripcion": "...",
    "hashtags": ["#Retrotarros", "...", ...],
    "thumbnail_prompts": ["...", "...", ...],
    "ig_post": "..."
  }},
  "datos": [
    {{
      "tema": "...", "texto": "...", "estado": "...",
      "consola": "...", "ano": 0, "editor": "...",
      "opiniones_alternativas": ["...", "...", "..."],
      "comentarios_cortos": ["...", "...", ...],
      "quiz_pregenerado": [
        {{"pregunta": "...", "respuesta": "...", "pista": "..."}},
        {{"pregunta": "...", "respuesta": "...", "pista": "..."}}
      ]
    }}
  ]
}}"""

    estructura = estructura_enriquecida if enriquecido else estructura_basica

    prompt = f"""Eres TarroBot, mascota del canal de YouTube Retrotarros sobre videojuegos retro.

Necesito que prepares UNA PAUTA COMPLETA de un episodio nuevo para el canal. El tema del episodio es:

  "{tema}"

{consola_linea}
{enfoque_linea}

Genera EXACTAMENTE {n_datos} datos curiosos. Pueden formar un top countdown (de menor a mayor impacto), un recorrido cronologico, o variantes alrededor del tema. Lo que mejor narrativamente funcione para grabar un episodio del canal.

Requisitos OBLIGATORIOS para CADA dato (este texto se reproduce con TTS, por eso reglas estrictas):
- Español ESTRICTAMENTE chileno neutro con TUTEO (tú/tienes/sabes/dime/puedes/mira).
- NO voseo argentino: PROHIBIDO "tenés", "querés", "decime", "vení", "vos", "sos",
  "podés", "sabés", "decís", "andás", "che", "andá", "haceme", "fijate" (con voseo).
  USA: "eres", "tienes", "quieres", "puedes", "dices", "ven", "vas", "dime".
- NO palabras que suenen argentinas/uruguayas: evita "acá" (usa "aquí"),
  "andábamos" (usa "estábamos"), "me agarraste" (usa "me pillaste"),
  "pibe/piba" (usa "chico/amigo"), "guita" (usa "plata").
- USA TILDES correctas del español ortográfico (también, está, día, año, mí, sí).
  Crítico para que el TTS pronuncie bien.
- NÚMEROS EN PALABRAS para cifras grandes:
  * "20 mil dólares" en vez de "20,000 dólares"
  * "5 mil copias" en vez de "5,000"
  * Años SÍ van en cifras: 1996, 1985
- Máximo 3 oraciones por dato, alrededor de 200-260 caracteres.
- Verificable y específico: fechas, números, nombres reales. Nada inventado.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabías".
- Cada dato distinto del otro. NO repetir hechos parafraseados.
- Distribuye los estados emocionales: que NO sean todos talking. Mezcla excited,
  fact, winking, confused, happy, sad, angry, thinking según el tono de cada dato.
{bloque_enriquecido}
Devuelve SOLO un JSON valido con esta estructura exacta, SIN texto extra ni markdown:
{estructura}

Estados validos: talking, excited, fact, winking, confused, happy, sad, angry, thinking.
"""

    try:
        # Sprint 15 B15.4: prompt caching para reducir costos en llamadas repetidas
        max_tokens = 8192 if enriquecido else 4096
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR: llamada a Claude API fallo: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: el LLM devolvio JSON invalido: {e}", file=sys.stderr)
        print(raw[:800], file=sys.stderr)
        return None

    # Validar shape
    if "datos" not in result or not isinstance(result["datos"], list):
        print("ERROR: respuesta sin 'datos'.", file=sys.stderr)
        return None

    # Filtro anti-voseo en los textos generados (defensa ultima)
    # Sprint 15: aplica tambien al contenido colateral enriquecido
    def _chilenizar_lista(items):
        if not isinstance(items, list):
            return items
        return [chilenizar(x) if isinstance(x, str) else x for x in items]

    for d in result["datos"]:
        if "texto" in d:
            d["texto"] = chilenizar(d["texto"])
        # Material colateral (Sprint 15)
        if "opiniones_alternativas" in d:
            d["opiniones_alternativas"] = _chilenizar_lista(d["opiniones_alternativas"])
        if "comentarios_cortos" in d:
            d["comentarios_cortos"] = _chilenizar_lista(d["comentarios_cortos"])
        if "quiz_pregenerado" in d and isinstance(d["quiz_pregenerado"], list):
            for q in d["quiz_pregenerado"]:
                if isinstance(q, dict):
                    if "pregunta" in q:
                        q["pregunta"] = chilenizar(q["pregunta"])
                    if "respuesta" in q:
                        q["respuesta"] = chilenizar(q["respuesta"])
                    if "pista" in q and q["pista"]:
                        q["pista"] = chilenizar(q["pista"])

    # Nivel episodio (Sprint 15)
    if "catchphrases_episodio" in result:
        result["catchphrases_episodio"] = _chilenizar_lista(result["catchphrases_episodio"])
    if "intros_cold_open" in result:
        result["intros_cold_open"] = _chilenizar_lista(result["intros_cold_open"])
    if "outros_cliffhanger" in result:
        result["outros_cliffhanger"] = _chilenizar_lista(result["outros_cliffhanger"])
    # Nota: publicacion va SIN tildes (regla del canal), no aplica chilenizar
    # porque chilenizar mantiene tildes ortograficas. Solo el ig_post podria
    # tener voseo si Claude se equivoco - aplicar selectivo.
    pub = result.get("publicacion") or {}
    if "ig_post" in pub and pub["ig_post"]:
        pub["ig_post"] = chilenizar(pub["ig_post"])

    return result


def generar_reorden_pauta_con_llm(pauta: dict) -> dict | None:
    """
    Sprint 12 C1: presentador asistente. Toma una pauta cargada y le pide
    a Claude que sugiera un orden mas dinamico de los datos (gancho al
    principio, climax al final, transiciones suaves). NO genera datos
    nuevos: solo reordena los existentes.

    Devuelve {nuevo_orden: [indices], razon_global: str, razones_por_dato: [str]}
    donde indices son enteros 0-based referenciando datos NO-melodia de la
    pauta original.
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        return None

    datos = [d for d in pauta.get("datos", []) if d.get("tipo") != "melodia"]
    if len(datos) < 3:
        print("ERROR: pauta con menos de 3 datos no necesita reorden.", file=sys.stderr)
        return None

    # Lista enumerada para que Claude pueda referenciar por indice
    lista = "\n".join(
        f"  [{i}] {d.get('tema', 'sin tema')} ({d.get('estado', 'talking')}) - "
        f"{d.get('texto', '')[:140]}"
        for i, d in enumerate(datos)
    )

    episodio = pauta.get("episodio") or pauta.get("slug", "episodio")

    prompt = f"""Eres director de contenido del canal Retrotarros. Te paso la pauta de un episodio: "{episodio}".

Tu tarea: sugerir un ORDEN DE PRESENTACION mas dinamico de estos {len(datos)} datos. Pensa como un editor de YouTube buscando RETENCION:
- Item 1: gancho fuerte (que prenda al espectador en los primeros 30s).
- Items 2 a {len(datos)-1}: ritmo variado, contraste de tonos emocionales, mantener interes.
- Item ultimo: climax, el dato que mejor cierra el episodio (mas potente, mas memorable).

DATOS DISPONIBLES (con indices 0 a {len(datos)-1}):
{lista}

Reglas:
- Usa TODOS los indices, sin repetir ninguno.
- Maxima variedad emocional entre items consecutivos (no poner dos 'talking' seguidos si se puede evitar).
- Si hay un dato claramente epico o caro, dejalo cerca del final.
- Si hay un dato sorprendente o curioso, ponlo al principio.

Devuelve SOLO un JSON valido sin markdown:

{{
  "nuevo_orden": [3, 1, 5, 0, 7, 2, 6, 4],
  "razon_global": "1-2 oraciones explicando la logica del orden",
  "razones_por_dato": [
    "Item 1 (orden 3): por que abre el episodio",
    "Item ultimo (orden 4): por que cierra"
  ]
}}
"""

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR: llamada Claude fallo: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR JSON LLM: {e}\n{raw[:500]}", file=sys.stderr)
        return None

    # Validar shape: nuevo_orden debe tener TODOS los indices 0..N-1 una vez
    nuevo = result.get("nuevo_orden", [])
    if sorted(nuevo) != list(range(len(datos))):
        print(f"ERROR: nuevo_orden invalido (debe contener 0..{len(datos)-1} sin repetir). Recibido: {nuevo}", file=sys.stderr)
        return None
    return result


def generar_descripcion_episodio_con_llm(
    pauta: dict,
    session_log: list | None = None,
) -> dict | None:
    """
    Sprint 12 C2: genera titulo + descripcion + hashtags + prompts de thumbnail
    para el episodio, basado en la pauta + session_log (si se grabo).

    session_log es la lista de entries que QueueManager rellena cada vez
    que se reproduce un dato durante la grabacion. Cada entry tiene
    timestamp_session_ms, dato_id, tema, duracion_ms. Si esta presente,
    los timestamps de la descripcion son REALES (no estimados).

    Devuelve {
      "titulos": [3 opciones de titulo],
      "descripcion": "...",
      "timestamps": [{"ts": "HH:MM:SS", "label": "...", "tema": "..."}],
      "hashtags": ["#...", ...],
      "thumbnail_prompts": [5 prompts texto para generar thumbnails],
      "ig_post": "Texto corto para Instagram/Reels",
    }
    """
    try:
        import anthropic
    except ImportError:
        print("ERROR: libreria 'anthropic' no instalada.", file=sys.stderr)
        return None
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no definida.", file=sys.stderr)
        return None

    episodio = pauta.get("episodio") or pauta.get("slug", "Episodio Retrotarros")
    datos = [d for d in pauta.get("datos", []) if d.get("tipo") != "melodia"]

    # Construir timestamps. Si hay session_log usamos timestamps REALES;
    # sino estimamos por duracion_ms acumulada con gap de 500ms entre items.
    timestamps_raw = []
    if session_log:
        for entry in session_log:
            ts_ms = int(entry.get("timestamp_session_ms", 0))
            timestamps_raw.append({
                "ts_ms": ts_ms,
                "tema": entry.get("tema", ""),
                "texto": entry.get("texto", "")[:120],
            })
    else:
        acum = 30_000  # 30s de intro estimada
        for d in datos:
            timestamps_raw.append({
                "ts_ms": acum,
                "tema": d.get("tema", ""),
                "texto": d.get("texto", "")[:120],
            })
            acum += (d.get("duracion_ms") or 12_000) + 500

    timestamps_list = "\n".join(
        f"  {_ms_to_srt_timestamp(t['ts_ms'])[:8]} - {t['tema']}: {t['texto']}"
        for t in timestamps_raw
    )

    lista_temas = ", ".join(d.get("tema", "") for d in datos if d.get("tema"))

    prompt = f"""Eres community manager del canal de YouTube Retrotarros (retrogaming).

EPISODIO: "{episodio}"
ITEMS COMENTADOS ({len(datos)}): {lista_temas}

TIMESTAMPS Y CONTEXTO DE CADA ITEM:
{timestamps_list}

Genera material de publicacion completo. Reglas:
- TITULOS: 3 opciones distintas, max 70 chars cada uno, optimizados para CTR
  YouTube. Mezcla tipos: numero+gancho, pregunta intrigante, declaracion potente.
- DESCRIPCION: 2 parrafos cortos (max 600 chars total) + lista de timestamps.
- TIMESTAMPS: usar EXACTAMENTE los timestamps que te paso arriba (no inventar).
  Formato HH:MM:SS - texto corto.
- HASHTAGS: 15-20 hashtags retrogaming/canal/items mencionados.
- THUMBNAIL_PROMPTS: 5 prompts de texto en INGLES para generar thumbnails con IA.
  Cada uno descriptivo, mencionando: cartucho retro relevante, color vibrante,
  texto grande tipo "TOP 10" o el numero clave del episodio, estilo retro 80s.
- IG_POST: texto corto (max 280 chars) para Instagram con tono casual chileno.

REGLAS DE ESCRITURA (descripcion, titulos, IG):
- SIN TILDES en TODOS los textos (regla del canal Retrotarros).
- SIN EMOJIS en titulos y descripcion (regla del canal).
- Chileno neutro con tuteo, sin voseo argentino.
- En IG_POST emojis OK ya que es plataforma mas casual, pero discretos.

Devuelve SOLO un JSON valido sin markdown:

{{
  "titulos": ["...", "...", "..."],
  "descripcion": "Texto completo de la descripcion del video (multilinea con \\n).",
  "timestamps": [
    {{"ts": "00:00:30", "label": "Intro"}},
    {{"ts": "00:01:45", "label": "Item 1 - ..."}}
  ],
  "hashtags": ["#Retrotarros", "#N64", "..."],
  "thumbnail_prompts": ["...", "...", "...", "...", "..."],
  "ig_post": "..."
}}
"""

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        print(f"ERROR Claude: {e}", file=sys.stderr)
        return None

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR JSON LLM: {e}\n{raw[:500]}", file=sys.stderr)
        return None


def _mp3_duracion_ms(mp3_path: Path) -> int | None:
    """Lee la duracion de un MP3 en ms. Usa mutagen si esta, sino None."""
    try:
        from mutagen.mp3 import MP3
    except ImportError:
        return None
    try:
        audio = MP3(str(mp3_path))
        if audio.info and audio.info.length:
            return int(audio.info.length * 1000)
    except Exception:
        return None
    return None


async def _tts_one_async(texto: str, voz: str, pitch: str, rate: str, out_path: Path) -> bool:
    """Genera UN mp3 con edge-tts (version async, para usar dentro de gather)."""
    try:
        import edge_tts
    except ImportError:
        return False
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(texto, voice=voz, pitch=pitch, rate=rate)
        await communicate.save(str(out_path))
        return True
    except Exception as e:
        print(f"    [ERROR] {out_path.name}: {e}", file=sys.stderr)
        return False


async def _preload_pauta_async(pauta: dict, force: bool = False, concurrency: int = 3) -> tuple[int, int, int]:
    """
    Genera en paralelo todos los MP3s faltantes (o todos si force=True).
    Devuelve (generados, skipped, errores).
    """
    slug = pauta["slug"]
    audio_dir = pauta_audio_dir(slug)
    audio_dir.mkdir(parents=True, exist_ok=True)

    voz = pauta.get("voz", VOZ_DEFAULT)
    pitch = pauta.get("pitch", PITCH_DEFAULT)
    rate = pauta.get("rate", RATE_DEFAULT)

    # Path relativo a PAUTAS_DIR que se guarda en el JSON (portable)
    def rel_path_for(dato_id: str) -> str:
        return f"audio/{slug}/{dato_id}.mp3"

    import asyncio
    sem = asyncio.Semaphore(concurrency)
    generados = 0
    skipped = 0
    errores = 0
    lock = asyncio.Lock()

    async def worker(idx: int, dato: dict):
        nonlocal generados, skipped, errores
        out_path = audio_dir / f"{dato['id']}.mp3"
        rel = rel_path_for(dato["id"])

        if out_path.exists() and not force:
            # Skip pero asegurar que el JSON refleje el path real
            async with lock:
                dato["mp3"] = rel
                if dato.get("duracion_ms") is None:
                    dato["duracion_ms"] = _mp3_duracion_ms(out_path)
                skipped += 1
            print(f"  [{idx:2}/?] SKIP  {dato['id']:35} (ya existe)")
            return

        async with sem:
            print(f"  [{idx:2}/?] TTS   {dato['id']:35} ({len(dato['texto'])} chars)")
            ok = await _tts_one_async(dato["texto"], voz, pitch, rate, out_path)

        async with lock:
            if ok and out_path.exists():
                dato["mp3"] = rel
                dato["duracion_ms"] = _mp3_duracion_ms(out_path)
                generados += 1
            else:
                errores += 1
                dato["mp3"] = None

    tareas = [worker(i, d) for i, d in enumerate(pauta["datos"], 1)]
    await asyncio.gather(*tareas)
    return generados, skipped, errores


# Sprint 8.x: filtro postproceso anti-voseo. Si Claude se salio del prompt
# y devolvio voseo argentino, este filtro lo reemplaza por las formas
# chilenas neutras equivalentes. Es la ultima defensa antes de pasar al TTS.

# Mapeo voseo -> tuteo chileno. Las claves son lowercase; el filtro
# preserva la capitalizacion del match original.
VOSEO_MAPA = {
    # Verbos
    "sos": "eres",
    "tenés": "tienes", "tenes": "tienes",
    "querés": "quieres", "queres": "quieres",
    "podés": "puedes", "podes": "puedes",
    "sabés": "sabes", "sabes vos": "sabes",
    "decís": "dices",
    "decime": "dime",
    "vení": "ven",
    "andás": "andas",
    "hacé": "haz",
    "haceme": "hazme",
    "contame": "cuéntame",
    "mandame": "mándame",
    # Pronombre
    "vos": "tú",
    # Argentinismos camuflados
    "acá": "aquí",
    "andábamos": "estábamos",
    "me agarraste": "me pillaste",
}


def chilenizar(texto: str) -> str:
    """Aplica reemplazos anti-voseo preservando capitalizacion del original.
    Si encuentra matches, imprime warning al stderr."""
    import re as _re

    def _preservar_caps(orig: str, reemplazo: str) -> str:
        """Si el original arranca con mayuscula, capitaliza el reemplazo."""
        if orig and orig[0].isupper():
            return reemplazo[0].upper() + reemplazo[1:]
        return reemplazo

    cambios = 0
    nuevo = texto

    # Aplicar voseo: matchear con \b<palabra>\b case-insensitive,
    # preservar caps del match original
    for clave, reemplazo in VOSEO_MAPA.items():
        # escapar caracteres especiales del regex en la clave
        patron = r"\b" + _re.escape(clave) + r"\b"

        def _sub(m):
            return _preservar_caps(m.group(0), reemplazo)

        nuevo, n = _re.subn(patron, _sub, nuevo, flags=_re.IGNORECASE)
        cambios += n

    # Caso especial "che" -> remover (con comas y espacios)
    nuevo, n = _re.subn(r"\b[Cc]he\b,?\s*", "", nuevo)
    cambios += n

    if cambios > 0:
        print(f"[chilenizar] {cambios} reemplazo(s) aplicado(s) a texto LLM", file=sys.stderr)
    return nuevo


def _ms_to_srt_timestamp(ms: int) -> str:
    """Convierte ms a 'HH:MM:SS,mmm' formato SRT."""
    if ms < 0:
        ms = 0
    horas, ms = divmod(ms, 3600_000)
    minutos, ms = divmod(ms, 60_000)
    segundos, ms = divmod(ms, 1000)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d},{ms:03d}"


def pauta_to_srt(pauta: dict, session_log: list | None = None, gap_ms: int = 500) -> str:
    """
    Genera SRT desde una pauta. Dos modos:

    Modo 'relative' (default, sin session_log): asume que cada dato se
    reproduce inmediatamente despues del anterior + gap_ms de pausa.
    Util para preview offline o cuando el video se monta dato-tras-dato.

    Modo 'recording' (con session_log): usa timestamps reales de cuando
    se apreto NEXT durante la grabacion. Cada entry del session_log es
    {timestamp_session_ms, dato_id, texto, duracion_ms}. La sincronizacion
    queda exacta para importar en CapCut/DaVinci sobre la grabacion real.
    """
    bloques = []

    if session_log:
        # Modo recording: timestamps reales
        for i, entry in enumerate(session_log, 1):
            start_ms = int(entry.get("timestamp_session_ms", 0))
            dur_ms = int(entry.get("duracion_ms") or 0)
            end_ms = start_ms + (dur_ms if dur_ms > 0 else 4000)  # fallback 4s si no hay duracion
            texto = entry.get("texto", "").strip()
            bloques.append(f"{i}\n{_ms_to_srt_timestamp(start_ms)} --> {_ms_to_srt_timestamp(end_ms)}\n{texto}\n")
    else:
        # Modo relative: secuencial desde T=0
        cursor_ms = 0
        for i, dato in enumerate(pauta.get("datos", []), 1):
            dur_ms = int(dato.get("duracion_ms") or 0) or 4000  # 4s fallback si no hay mp3
            start_ms = cursor_ms
            end_ms = cursor_ms + dur_ms
            texto = dato.get("texto", "").strip()
            bloques.append(f"{i}\n{_ms_to_srt_timestamp(start_ms)} --> {_ms_to_srt_timestamp(end_ms)}\n{texto}\n")
            cursor_ms = end_ms + gap_ms

    return "\n".join(bloques)


# ─────────────────────────────────────────────────────────────────────────
# Melodias MIDI -> MP3 (Sprint 8.1)
# ─────────────────────────────────────────────────────────────────────────
#
# Flujo:
#   1. Luis baja un MIDI de Ichigos / Ninsheetmusic en studio/melodias/
#   2. CLI --melodia-add le pasa el MIDI + recorte (desde + segundos)
#   3. FluidSynth renderiza con soundfont SNES a WAV temporal
#   4. ffmpeg recorta a [desde, desde+segundos] y convierte a MP3
#   5. Se agrega el item a la pauta con tipo="melodia"
#
# Para uso "te acuerdas de esa cancion?" → 5-10 segundos por melodia,
# nunca canciones completas (fair use razonable como referencia).


def _which(name: str) -> Optional[str] | None:
    """Encuentra el binario en PATH o en el bin/ del instalador."""
    import shutil
    found = shutil.which(name)
    if found:
        return found
    # Fallback: revisar bin/ del instalador
    local = REPO / "installers" / "tarrobot-studio" / "bin" / f"{name}.exe"
    if local.exists():
        return str(local)
    return None


def _parse_tiempo(s: str) -> float:
    """Convierte '14', '14.5', '0:14', '1:23' a segundos float."""
    s = str(s).strip()
    if ":" in s:
        partes = s.split(":")
        if len(partes) == 2:
            return int(partes[0]) * 60 + float(partes[1])
        if len(partes) == 3:
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + float(partes[2])
    return float(s)


def render_midi_a_mp3(midi_path: Path, out_mp3: Path,
                       desde_s: float = 0.0, segundos: Optional[float] = None,
                       soundfont: Optional[Path] = None) -> Optional[Path]:
    """
    Renderiza un MIDI a MP3 usando FluidSynth + soundfont SNES + ffmpeg.
    Recorta a [desde_s, desde_s + segundos] si se especifica.
    Devuelve el path del MP3 o None si fallo.
    """
    import subprocess
    import tempfile

    if not midi_path.exists():
        print(f"ERROR: MIDI no existe: {midi_path}", file=sys.stderr)
        return None

    sf = soundfont or SOUNDFONT_PATH
    if not sf.exists():
        print(f"ERROR: soundfont SNES no encontrado en {sf}", file=sys.stderr)
        print(f"       Bajalo con install.bat o pon un .sf2 ahi manualmente.", file=sys.stderr)
        return None

    fluidsynth = _which("fluidsynth")
    if not fluidsynth:
        print("ERROR: fluidsynth no esta instalado.", file=sys.stderr)
        print("       En Windows: install.bat lo descarga. Manual: https://www.fluidsynth.org/", file=sys.stderr)
        return None

    ffmpeg = _which("ffmpeg")
    if not ffmpeg:
        print("ERROR: ffmpeg no encontrado.", file=sys.stderr)
        return None

    out_mp3.parent.mkdir(parents=True, exist_ok=True)

    # 1. FluidSynth: MIDI -> WAV completo en tmp
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_wav = Path(f.name)
    try:
        cmd_fluid = [
            fluidsynth, "-ni",
            "-F", str(tmp_wav),
            "-r", "44100",
            "-g", "0.8",   # gain (volumen master, 0.8 evita clipping)
            str(sf), str(midi_path),
        ]
        proc = subprocess.run(cmd_fluid, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0 or not tmp_wav.exists():
            print(f"ERROR: fluidsynth fallo: {proc.stderr[:300]}", file=sys.stderr)
            return None

        # 2. ffmpeg: WAV -> MP3 con recorte opcional + fade-in/out
        cmd_ff = [ffmpeg, "-y", "-i", str(tmp_wav)]
        if desde_s > 0:
            cmd_ff += ["-ss", f"{desde_s:.3f}"]
        if segundos is not None:
            cmd_ff += ["-t", f"{segundos:.3f}"]
            # Fade-out de 0.5s al final para que no corte abrupto
            fade_start = max(0, segundos - 0.5)
            cmd_ff += ["-af", f"afade=in:st=0:d=0.3,afade=out:st={fade_start:.3f}:d=0.5"]
        cmd_ff += ["-b:a", "128k", "-ac", "2", str(out_mp3)]

        proc = subprocess.run(cmd_ff, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0 or not out_mp3.exists():
            print(f"ERROR: ffmpeg fallo: {proc.stderr[:300]}", file=sys.stderr)
            return None
    finally:
        try:
            tmp_wav.unlink(missing_ok=True)
        except Exception:
            pass

    return out_mp3


def pauta_agregar_melodia(pauta: dict, midi_path: Path, desde_s: float = 0.0,
                           segundos: float = 12.0, titulo: str = "",
                           consola: str = "", ano: int = 0, editor: str = "") -> dict:
    """
    Renderiza un MIDI a MP3 y lo agrega como item tipo=melodia a la pauta.
    El path del MP3 queda relativo a PAUTAS_DIR para que el server lo sirva.
    """
    slug = pauta["slug"]
    existing = {d["id"] for d in pauta["datos"]}
    n = len(pauta["datos"]) + 1
    new_id = f"{slug}-melodia-{n}"
    while new_id in existing:
        n += 1
        new_id = f"{slug}-melodia-{n}"

    out_mp3 = PAUTAS_DIR / "audio" / slug / f"{new_id}.mp3"
    rendered = render_midi_a_mp3(midi_path, out_mp3, desde_s=desde_s, segundos=segundos)
    if not rendered:
        raise RuntimeError(f"No se pudo renderizar {midi_path.name}")

    # Leer duracion real
    dur_ms = _mp3_duracion_ms(out_mp3) or int(segundos * 1000)

    titulo = titulo or midi_path.stem.replace("-", " ").replace("_", " ").title()
    rel_mp3 = f"audio/{slug}/{new_id}.mp3"
    try:
        midi_rel = str(midi_path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except (ValueError, OSError):
        midi_rel = str(midi_path)

    dato = {
        "id": new_id,
        "tipo": "melodia",  # Sprint 8.1: marca que es musica, no TTS
        "tema": titulo,
        "texto": f"[Tocando: {titulo} ({segundos:.0f}s)]",
        "estado": "whistling",  # Estado visual nuevo en la TV
        "consola": consola or "",
        "ano": int(ano or 0),
        "editor": editor or "",
        "mp3": rel_mp3,
        "duracion_ms": dur_ms,
        "fuente": "midi-render",
        "midi_source": {
            "midi": midi_rel,
            "desde_s": desde_s,
            "segundos": segundos,
        },
    }
    pauta["datos"].append(dato)
    return dato


def pauta_agregar_dato(pauta: dict, dato_in: dict) -> dict:
    """Agrega un dato a la pauta con id unico y campos por defecto. Mutates pauta."""
    base = pauta["slug"]
    existing = {d["id"] for d in pauta["datos"]}
    n = len(pauta["datos"]) + 1
    new_id = f"{base}-{n}"
    while new_id in existing:
        n += 1
        new_id = f"{base}-{n}"

    estado = dato_in.get("estado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    dato = {
        "id": new_id,
        "tema": dato_in.get("tema", "Sin tema"),
        "texto": dato_in.get("texto", ""),
        "estado": estado,
        "consola": dato_in.get("consola", ""),
        "ano": int(dato_in.get("ano", 0) or 0),
        "editor": dato_in.get("editor", ""),
        "mp3": None,
        "duracion_ms": None,
        "fuente": dato_in.get("fuente", "pauta-manual"),
    }
    # Sprint 15: preservar contenido colateral pre-generado si vino
    for key in ("opiniones_alternativas", "comentarios_cortos", "quiz_pregenerado"):
        if key in dato_in:
            dato[key] = dato_in[key]
    pauta["datos"].append(dato)
    return dato


# ─────────────────────────────────────────────────────────────────────────
# Slide HTML
# ─────────────────────────────────────────────────────────────────────────

def resaltar_quotes(texto: str) -> str:
    """
    Resalta automaticamente algunas palabras clave envolviendolas en <span class='quote'>.
    Heuristica: cantidades en USD, anios, "primer/primera", numeros grandes.
    """
    # USD X.XXX  o  USD XX
    texto = re.sub(r"(USD\s+[\d\.\,]+\+?)", r'<span class="quote">\1</span>', texto)
    # "primer/primera/unico/unica"
    texto = re.sub(r"\b(primer[oa]?|unic[oa])\b", r'<span class="quote">\1</span>', texto, flags=re.IGNORECASE)
    return texto


def generar_slide(dato: dict) -> Path | None:
    if not TEMPLATE.exists():
        print(f"ERROR: no existe el template {TEMPLATE}", file=sys.stderr)
        return None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    template = TEMPLATE.read_text(encoding="utf-8")

    channel = random.randint(1, 99)
    label = LABEL_POR_ESTADO.get(dato["estado"], "DATO CURIOSO")
    meta_partes = [
        dato.get("consola", ""),
        str(dato.get("ano", "")) if dato.get("ano") else "",
        dato.get("editor", ""),
    ]
    meta = " · ".join(s for s in meta_partes if s and s != "0")

    texto_html = resaltar_quotes(dato["texto"])

    html = (
        template
        .replace("{{ESTADO}}", dato["estado"])
        .replace("{{TEMA}}", dato["tema"])
        .replace("{{TEXTO_HTML}}", texto_html)
        .replace("{{LABEL}}", label)
        .replace("{{META}}", meta or "RETROTARROS · TARROBOT")
        .replace("{{CHANNEL}}", f"CH {channel:02d}")
    )

    out_path = OUT_DIR / f"{dato['id']}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────

def cmd_list(db: dict) -> int:
    if not db["datos"]:
        print("(base vacia)")
        return 0
    print(f"=== TarroBot DB · {len(db['datos'])} datos ===")
    print()
    for d in db["datos"]:
        meta = " · ".join(s for s in [d.get("consola", ""), str(d.get("ano", "") or "")] if s and s != "0")
        meta_str = f" [{meta}]" if meta else ""
        print(f"  · [{d['estado']:8}] {d['tema']:35}{meta_str}")
        print(f"             {d['texto'][:90]}{'...' if len(d['texto']) > 90 else ''}")
    return 0


def cmd_add(args, db: dict) -> int:
    tema, texto = args.add
    if args.state not in ESTADOS:
        print(f"ERROR: estado invalido. Validos: {', '.join(ESTADOS)}", file=sys.stderr)
        return 1
    dato = agregar_dato(
        tema, texto, args.state, db,
        consola=args.consola or "",
        ano=args.ano or 0,
        editor=args.editor or "",
        fuente="manual",
    )
    print(f"[OK] dato agregado: {dato['id']}")
    print(f"     tema: {dato['tema']}")
    print(f"     estado: {dato['estado']}")
    print(f"     texto: {dato['texto']}")
    if args.slide:
        out = generar_slide(dato)
        if out:
            print(f"[OK] slide HTML: {out}")
    if args.tts:
        voz = resolver_voz(args.voice)
        print(f"[TTS] generando audio con {voz}...")
        out = generar_tts(dato, voz=voz, pitch=args.pitch, rate=args.rate)
        if out:
            print(f"[OK] audio MP3: {out}")
    return 0


def cmd_buscar(args, db: dict) -> int:
    matches = buscar(args.tema, db)

    if matches:
        print(f"\n=== {len(matches)} dato(s) sobre '{args.tema}' ===\n")
        for i, d in enumerate(matches, 1):
            print(f"[{i}] {d['tema']} · {d['estado']}")
            print(f"    {d['texto']}")
            meta = " · ".join(s for s in [d.get("consola", ""), str(d.get("ano", "") or ""), d.get("editor", "")] if s and s != "0")
            if meta:
                print(f"    {meta}")
            print()

        if args.slide:
            out = generar_slide(matches[0])
            if out:
                print(f"[OK] slide generado: {out}")
        if args.tts:
            voz = resolver_voz(args.voice)
            print(f"[TTS] generando audio con {voz}...")
            out = generar_tts(matches[0], voz=voz, pitch=args.pitch, rate=args.rate)
            if out:
                print(f"[OK] audio MP3: {out}")
        return 0

    # Sin matches
    print(f"(no hay datos sobre '{args.tema}' en la base local)")

    if not args.generate:
        print("Tip: usa --generate para que Claude proponga 3 opciones.")
        return 0

    # --generate
    print("\n[Claude API] Generando 3 propuestas con Haiku...")
    result = generar_con_llm(args.tema)
    if result is None:
        return 1

    datos_llm = result.get("datos", [])
    if not datos_llm:
        print("ERROR: el LLM no devolvio datos.", file=sys.stderr)
        return 1

    print(f"\n=== Propuestas para '{args.tema}' ===\n")
    for i, d in enumerate(datos_llm, 1):
        estado_rec = d.get("estado_recomendado", "talking")
        print(f"[{i}] ({estado_rec})")
        print(f"    {d['texto']}\n")

    # Aprobar interactivo
    try:
        respuesta = input("Cual aprobas? (1/2/3, 'no' para descartar todas): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nCancelado.")
        return 0

    if respuesta not in ("1", "2", "3"):
        print("Descartado. No se guardo nada.")
        return 0

    idx = int(respuesta) - 1
    elegida = datos_llm[idx]
    estado = elegida.get("estado_recomendado", "talking")
    if estado not in ESTADOS:
        estado = "talking"

    dato = agregar_dato(
        args.tema,
        elegida["texto"],
        estado,
        db,
        consola=result.get("consola", ""),
        ano=int(result.get("ano", 0) or 0),
        editor=result.get("editor", ""),
        fuente="LLM",
    )
    print(f"\n[OK] aprobado y guardado: {dato['id']}")
    if args.slide:
        out = generar_slide(dato)
        if out:
            print(f"[OK] slide: {out}")
    if args.tts:
        voz = resolver_voz(args.voice)
        print(f"[TTS] generando audio con {voz}...")
        out = generar_tts(dato, voz=voz, pitch=args.pitch, rate=args.rate)
        if out:
            print(f"[OK] audio MP3: {out}")
    return 0


def cmd_pauta_list(args) -> int:
    if not PAUTAS_DIR.exists():
        print("(no hay pautas creadas)")
        return 0
    archivos = sorted(PAUTAS_DIR.glob("*.tarrobot.json"))
    if not archivos:
        print("(no hay pautas creadas)")
        return 0
    print(f"=== Pautas en {PAUTAS_DIR} ===")
    print()
    for f in archivos:
        try:
            p = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            print(f"  · [BROKEN] {f.name}")
            continue
        n = len(p.get("datos", []))
        audio_dir = pauta_audio_dir(p["slug"])
        mp3s = len(list(audio_dir.glob("*.mp3"))) if audio_dir.exists() else 0
        print(f"  · {p['slug']:30}  {n:3} datos  {mp3s:3} mp3s  ·  {p.get('episodio', '')}")
    return 0


def cmd_pauta_show(args) -> int:
    pauta = cargar_pauta(args.pauta_show)
    if not pauta:
        print(f"ERROR: no existe la pauta '{args.pauta_show}'", file=sys.stderr)
        print(f"       (buscada en {pauta_path(args.pauta_show)})", file=sys.stderr)
        return 1
    print(f"=== Pauta: {pauta['slug']} ===")
    print(f"Episodio:   {pauta.get('episodio', '')}")
    print(f"Creada:     {pauta.get('creado', '')}")
    print(f"Actualizada:{pauta.get('actualizado', '')}")
    print(f"Voz:        {pauta.get('voz', '')}  pitch={pauta.get('pitch', '')}  rate={pauta.get('rate', '')}")
    print(f"Datos:      {len(pauta['datos'])}")
    print()
    for i, d in enumerate(pauta["datos"], 1):
        mp3_mark = "[MP3]" if d.get("mp3") and (PAUTAS_DIR / d["mp3"]).exists() else "[   ]"
        print(f"  {i:2}. {mp3_mark} [{d['estado']:8}] {d['tema'][:40]}")
        print(f"           {d['texto'][:90]}{'...' if len(d['texto']) > 90 else ''}")
    return 0


def cmd_pauta_init(args) -> int:
    slug = slugify(args.pauta_init)
    if not slug:
        print("ERROR: slug invalido", file=sys.stderr)
        return 1
    existing = cargar_pauta(slug)
    if existing and not args.force:
        print(f"ERROR: ya existe la pauta '{slug}'. Usa --force para sobrescribir.", file=sys.stderr)
        return 1
    episodio = args.episodio or slug.replace("-", " ").title()
    voz = resolver_voz(args.voice)
    pauta = crear_pauta_vacia(slug, episodio, voz=voz, pitch=args.pitch, rate=args.rate)
    p = guardar_pauta(pauta)
    print(f"[OK] pauta creada: {p}")
    print(f"     slug:      {pauta['slug']}")
    print(f"     episodio:  {pauta['episodio']}")
    print(f"     voz:       {pauta['voz']}")
    print()
    print("Proximo paso:")
    print(f"  python scripts/tarrobot.py --pauta-auto <ruta-html>  (autogenerar datos desde el HTML)")
    print(f"  python scripts/tarrobot.py --pauta-show {slug}        (verla)")
    if not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0


def cmd_melodia_add(args) -> int:
    """Agrega un item de melodia a una pauta. Renderiza el MIDI a MP3 con FluidSynth."""
    slug = slugify(args.melodia_add)
    pauta = cargar_pauta(slug)
    if not pauta:
        print(f"ERROR: no existe la pauta '{slug}'. Crea una primero con --pauta-init.", file=sys.stderr)
        return 1

    if not args.midi:
        print("ERROR: falta --midi <ruta>", file=sys.stderr)
        return 1

    midi_path = Path(args.midi)
    if not midi_path.is_absolute():
        midi_path = (REPO / midi_path).resolve()
    if not midi_path.exists():
        print(f"ERROR: MIDI no existe: {midi_path}", file=sys.stderr)
        return 1
    if midi_path.suffix.lower() not in (".mid", ".midi"):
        print(f"ERROR: el archivo debe ser .mid o .midi (recibido: {midi_path.suffix})", file=sys.stderr)
        return 1

    desde_s = _parse_tiempo(args.desde) if args.desde else 0.0
    segundos = float(args.segundos) if args.segundos else 12.0
    if segundos > 30:
        print(f"[WARN] {segundos}s es bastante para una referencia. Recomendado max 20s.", file=sys.stderr)

    titulo = args.titulo or midi_path.stem.replace("-", " ").replace("_", " ").title()

    print(f"[INFO] Renderizando MIDI...")
    print(f"       Archivo: {midi_path.name}")
    print(f"       Recorte: desde {desde_s:.1f}s, duracion {segundos:.1f}s")
    print(f"       Titulo:  {titulo}")
    print()

    try:
        dato = pauta_agregar_melodia(
            pauta, midi_path,
            desde_s=desde_s, segundos=segundos,
            titulo=titulo,
            consola=args.consola or "",
            ano=args.ano or 0,
            editor=args.editor or "",
        )
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    guardar_pauta(pauta)
    print(f"[OK] melodia agregada como item {dato['id']}")
    print(f"     MP3: {PAUTAS_DIR / dato['mp3']}")
    print(f"     duracion real: {dato['duracion_ms']/1000:.1f}s")
    print()
    print(f"En la cola va a aparecer como:")
    print(f"  [whistling] {dato['tema']}")
    print(f"  {dato['texto']}")
    if not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0


def cmd_melodia_clean(args) -> int:
    """Borra todas las melodias (items tipo='melodia') de una pauta."""
    slug = slugify(args.melodia_clean)
    pauta = cargar_pauta(slug)
    if not pauta:
        print(f"ERROR: no existe la pauta '{slug}'", file=sys.stderr)
        return 1

    antes = len(pauta["datos"])
    pauta["datos"] = [d for d in pauta["datos"] if d.get("tipo") != "melodia"]
    despues = len(pauta["datos"])
    borradas = antes - despues

    if borradas == 0:
        print(f"(pauta '{slug}' no tenia melodias)")
        return 0

    # Tambien borrar los MP3 fisicos de melodias huerfanos
    audio_dir = pauta_audio_dir(slug)
    if audio_dir.exists():
        for mp3 in audio_dir.glob(f"{slug}-melodia-*.mp3"):
            try:
                mp3.unlink()
            except Exception:
                pass

    guardar_pauta(pauta)
    print(f"[OK] {borradas} melodia(s) borradas de '{slug}'. Quedan {despues} datos normales.")
    if not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0


def cmd_melodia_bulk(args) -> int:
    """
    Agrega los MIDIs de studio/melodias/ (o de una subcarpeta) a una pauta.
    Ignora los que ya estan agregados (compara por nombre de archivo).
    """
    slug = slugify(args.melodia_bulk)
    pauta = cargar_pauta(slug)
    if not pauta:
        print(f"ERROR: no existe la pauta '{slug}'. Crea una con --pauta-init primero.", file=sys.stderr)
        return 1

    # Folder opcional dentro de MELODIAS_DIR
    if args.folder:
        folder = MELODIAS_DIR / args.folder
        if not folder.exists():
            print(f"ERROR: no existe la subcarpeta {folder}", file=sys.stderr)
            print(f"       Carpetas disponibles en {MELODIAS_DIR}:", file=sys.stderr)
            for sub in MELODIAS_DIR.iterdir():
                if sub.is_dir():
                    print(f"         {sub.name}/", file=sys.stderr)
            return 1
        scan_dir = folder
    else:
        scan_dir = MELODIAS_DIR

    if not scan_dir.exists():
        print(f"ERROR: no existe la carpeta {scan_dir}", file=sys.stderr)
        return 1

    # MIDIs disponibles
    midis = sorted(list(scan_dir.glob("*.mid")) + list(scan_dir.glob("*.midi")))
    if not midis:
        print(f"(no hay MIDIs en {MELODIAS_DIR})")
        print(f"Pon archivos .mid o .midi en esa carpeta y volve a correr.")
        return 0

    # MIDIs ya agregados (revisamos midi_source.midi de cada item melodia)
    ya_agregados = set()
    for d in pauta["datos"]:
        if d.get("tipo") == "melodia":
            src = d.get("midi_source", {}).get("midi", "")
            if src:
                ya_agregados.add(Path(src).name.lower())

    desde_s = _parse_tiempo(args.desde) if args.desde else 0.0
    segundos = float(args.segundos) if args.segundos else 12.0

    print(f"=== Bulk melodia add a pauta '{slug}' ===")
    print(f"Scan dir:         {scan_dir}")
    print(f"MIDIs en carpeta: {len(midis)}")
    print(f"Ya agregados:     {len(ya_agregados)}")
    print()

    nuevos = 0
    errores = 0
    for midi_path in midis:
        if midi_path.name.lower() in ya_agregados:
            print(f"  [SKIP] {midi_path.name} (ya en la pauta)")
            continue
        titulo = midi_path.stem.replace("-", " ").replace("_", " ").title()
        print(f"  [TTS ] {midi_path.name} -> {titulo}")
        try:
            pauta_agregar_melodia(
                pauta, midi_path,
                desde_s=desde_s, segundos=segundos,
                titulo=titulo,
            )
            nuevos += 1
        except RuntimeError as e:
            print(f"  [ERR ] {midi_path.name}: {e}", file=sys.stderr)
            errores += 1

    if nuevos > 0:
        guardar_pauta(pauta)
    print()
    print(f"[OK] {nuevos} melodia(s) agregadas a {slug}")
    if errores:
        print(f"[WARN] {errores} fallaron (ver mensajes arriba)")
    if nuevos > 0 and not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0 if errores == 0 else 1


def cmd_pauta_srt(args) -> int:
    slug = slugify(args.pauta_srt)
    pauta = cargar_pauta(slug)
    if not pauta:
        print(f"ERROR: no existe la pauta '{slug}'", file=sys.stderr)
        return 1
    if not pauta["datos"]:
        print(f"ERROR: la pauta '{slug}' esta vacia", file=sys.stderr)
        return 1

    srt = pauta_to_srt(pauta, session_log=None, gap_ms=args.gap_ms or 500)
    out_path = PAUTAS_DIR / f"{slug}.srt"
    out_path.write_text(srt, encoding="utf-8")
    print(f"[OK] SRT generado: {out_path}")
    print(f"     modo: relative (asume reproduccion secuencial con {args.gap_ms or 500}ms entre items)")
    print(f"     items: {len(pauta['datos'])}")
    # Mostrar primeras 2 entradas como preview
    preview = "\n".join(srt.split("\n\n")[:2])
    print()
    print("Preview:")
    print(preview)
    return 0


def cmd_pauta_preload(args) -> int:
    slug = slugify(args.pauta_preload)
    pauta = cargar_pauta(slug)
    if not pauta:
        print(f"ERROR: no existe la pauta '{slug}'", file=sys.stderr)
        print(f"       (buscada en {pauta_path(slug)})", file=sys.stderr)
        return 1
    if not pauta["datos"]:
        print(f"ERROR: la pauta '{slug}' esta vacia. Usa --pauta-auto o --add primero.", file=sys.stderr)
        return 1

    # Avisar si falta mutagen (no es bloqueante)
    try:
        import mutagen  # noqa: F401
    except ImportError:
        print("[WARN] libreria 'mutagen' no instalada -> duracion_ms quedara en null.")
        print("       Instalala con: pip install mutagen  (recomendado para Sprint 6.3+)")
        print()

    try:
        import edge_tts  # noqa: F401
    except ImportError:
        print("ERROR: libreria 'edge-tts' no instalada.", file=sys.stderr)
        print("Instalala con: pip install edge-tts", file=sys.stderr)
        return 1

    audio_dir = pauta_audio_dir(slug)
    print(f"=== Precargando MP3s de la pauta '{slug}' ===")
    print(f"Total datos:   {len(pauta['datos'])}")
    print(f"Carpeta audio: {audio_dir}")
    print(f"Voz:           {pauta.get('voz', VOZ_DEFAULT)}  pitch={pauta.get('pitch', PITCH_DEFAULT)}  rate={pauta.get('rate', RATE_DEFAULT)}")
    print(f"Concurrencia:  {args.concurrency or 3}")
    print(f"Force:         {args.force}")
    print()

    import asyncio
    import time
    inicio = time.time()
    try:
        generados, skipped, errores = asyncio.run(
            _preload_pauta_async(pauta, force=args.force, concurrency=args.concurrency or 3)
        )
    except KeyboardInterrupt:
        print("\n[CANCEL] interrumpido por el usuario. Guardando lo que alcance...")
        guardar_pauta(pauta)
        return 130

    guardar_pauta(pauta)
    elapsed = time.time() - inicio

    total_ms = sum(d["duracion_ms"] or 0 for d in pauta["datos"])
    print()
    print(f"=== Precarga completa en {elapsed:.1f}s ===")
    print(f"  generados: {generados}")
    print(f"  skipped:   {skipped}")
    print(f"  errores:   {errores}")
    print(f"  duracion total estimada: {total_ms/1000:.1f}s ({total_ms/1000/60:.1f} min)")
    if generados > 0 and not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    if errores:
        return 1
    return 0


def cmd_pauta_auto(args) -> int:
    html_arg = Path(args.pauta_auto)
    if not html_arg.is_absolute():
        html_path = (REPO / html_arg).resolve()
    else:
        html_path = html_arg.resolve()

    if not _path_dentro_repo(html_path):
        print(f"ERROR: el HTML debe estar dentro del repo ({REPO})", file=sys.stderr)
        return 1
    if not html_path.exists():
        print(f"ERROR: no existe el archivo {html_path}", file=sys.stderr)
        return 1
    if html_path.suffix.lower() != ".html":
        print(f"ERROR: se esperaba un .html, recibi {html_path.suffix}", file=sys.stderr)
        return 1

    # Derivar slug del filename (sin extension)
    slug = slugify(html_path.stem)
    n_datos = max(3, min(args.n_datos or 10, 20))

    print(f"[INFO] Leyendo {html_path.name}...")
    print(f"[INFO] Pidiendo {n_datos} datos a Claude (haiku-4-5)...")

    result = generar_pauta_con_llm(html_path, n_datos=n_datos)
    if result is None:
        return 1

    datos_llm = result.get("datos", [])
    if not datos_llm:
        print("ERROR: el LLM no devolvio datos.", file=sys.stderr)
        return 1

    # Crear o cargar pauta
    pauta = cargar_pauta(slug)
    if pauta and not args.force:
        print(f"ERROR: ya existe la pauta '{slug}' con {len(pauta['datos'])} datos.", file=sys.stderr)
        print(f"       Usa --force para reemplazar, o --pauta-init <slug> --force primero.", file=sys.stderr)
        return 1

    episodio = args.episodio or result.get("episodio_titulo") or slug.replace("-", " ").title()
    voz = resolver_voz(args.voice)
    pauta = crear_pauta_vacia(slug, episodio, voz=voz, pitch=args.pitch, rate=args.rate)

    for d in datos_llm:
        d["fuente"] = "pauta-auto"
        pauta_agregar_dato(pauta, d)

    p = guardar_pauta(pauta)
    print()
    print(f"[OK] pauta generada con {len(pauta['datos'])} datos: {p}")
    print()
    for i, d in enumerate(pauta["datos"], 1):
        print(f"  {i:2}. [{d['estado']:8}] {d['tema'][:50]}")
        print(f"            {d['texto'][:100]}{'...' if len(d['texto']) > 100 else ''}")
    print()
    print("Proximo paso (Sprint 6.2):")
    print(f"  python scripts/tarrobot.py --pauta-preload {slug}     (precargar todos los MP3)")
    if not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0


def cmd_pauta_tema(args) -> int:
    """
    Sprint 11: genera una pauta completa desde un tema libre.
    No requiere HTML previo. Llama LLM, crea pauta, opcionalmente precarga MP3s.
    """
    tema = (args.pauta_tema or "").strip()
    if not tema:
        print("ERROR: tema vacio. Ejemplo: --pauta-tema 'Mega Drive raros'", file=sys.stderr)
        return 1

    n_datos = max(3, min(args.n_datos or 10, 20))

    # Derivar slug: si lo pasaron, usar; sino slugify del tema
    if args.slug:
        slug = slugify(args.slug)
    else:
        slug = slugify(tema)

    pauta_existente = cargar_pauta(slug)
    if pauta_existente and not args.force:
        print(f"ERROR: ya existe la pauta '{slug}' con {len(pauta_existente['datos'])} datos.", file=sys.stderr)
        print(f"       Usa --force para reemplazar, o --slug otro-nombre.", file=sys.stderr)
        return 1

    print(f"[INFO] Tema: '{tema}'")
    print(f"[INFO] Slug: {slug}")
    if args.consola:
        print(f"[INFO] Consola: {args.consola}")
    print(f"[INFO] Pidiendo {n_datos} datos a Claude (haiku-4-5)...")

    result = generar_pauta_tema_con_llm(
        tema=tema,
        n_datos=n_datos,
        consola_hint=args.consola,
    )
    if result is None:
        return 1

    datos_llm = result.get("datos", [])
    if not datos_llm:
        print("ERROR: el LLM no devolvio datos.", file=sys.stderr)
        return 1

    episodio = args.episodio or result.get("episodio_titulo") or tema
    voz = resolver_voz(args.voice) if args.voice else VOZ_DEFAULT
    pauta = crear_pauta_vacia(slug, episodio, voz=voz, pitch=args.pitch, rate=args.rate)

    for d in datos_llm:
        d["fuente"] = "pauta-tema"
        pauta_agregar_dato(pauta, d)

    # Sprint 15: preservar contenido colateral a nivel episodio
    for key in ("catchphrases_episodio", "intros_cold_open",
                "outros_cliffhanger", "publicacion"):
        if key in result:
            pauta[key] = result[key]

    p = guardar_pauta(pauta)
    print()
    print(f"[OK] pauta '{slug}' generada con {len(pauta['datos'])} datos:")
    print(f"     {p}")
    print()
    for i, d in enumerate(pauta["datos"], 1):
        print(f"  {i:2}. [{d['estado']:8}] {d['tema'][:50]}")
        print(f"            {d['texto'][:100]}{'...' if len(d['texto']) > 100 else ''}")
    print()

    # Precargar MP3s salvo --no-preload
    if not getattr(args, "no_preload", False):
        print("[INFO] Precargando MP3s en paralelo (esto puede tardar 1-3 min)...")
        import asyncio as _asyncio
        concurrency = max(1, args.concurrency or 3)
        try:
            generados, skipped, errores = _asyncio.run(
                _preload_pauta_async(pauta, force=False, concurrency=concurrency)
            )
            guardar_pauta(pauta)  # guardar con mp3 + duracion_ms ya seteados
            print(f"[OK] MP3s: {generados} generados, {skipped} skipped, {errores} errores")
        except Exception as e:
            print(f"[WARN] fallo el preload: {e}", file=sys.stderr)
            print("        Puedes correrlo manualmente con:", file=sys.stderr)
            print(f"        python scripts/tarrobot.py --pauta-preload {slug}", file=sys.stderr)
    else:
        print(f"[INFO] Saltando preload (--no-preload). Para hacerlo manual:")
        print(f"       python scripts/tarrobot.py --pauta-preload {slug}")

    print()
    print(f"Listo. Para usar la pauta desde el panel TarroBot, carga el slug: {slug}")

    if not getattr(args, "no_sync", False):
        _ejecutar_sync_drive()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="TarroBot - asistente de datos curiosos retro Retrotarros",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tema", nargs="?", help="Tema/juego/consola a buscar")
    parser.add_argument("--list", action="store_true", help="Lista todos los datos en la base")
    parser.add_argument("--generate", action="store_true", help="Si no hay match local, llama Claude API para generar 3 propuestas")
    parser.add_argument("--add", nargs=2, metavar=("TEMA", "TEXTO"), help="Agrega un dato manualmente")
    parser.add_argument("--state", default="talking", help=f"Estado de TarroBot (default: talking). Validos: {', '.join(ESTADOS)}")
    parser.add_argument("--consola", help="Consola del dato (NES, SNES, N64, etc.)")
    parser.add_argument("--ano", type=int, help="Anio del dato")
    parser.add_argument("--editor", help="Editor/estudio")
    parser.add_argument("--slide", action="store_true", help="Genera HTML slide standalone listo para CapCut/DaVinci")
    parser.add_argument("--tts", action="store_true", help="Genera audio MP3 con voz TarroBot (Edge TTS)")
    parser.add_argument("--voice", help=f"Voz Edge TTS. Alias cortos: {', '.join(VOCES_SUGERIDAS.keys())}. O nombre completo es-XX-NombreNeural. Default: catalina (es-CL).")
    parser.add_argument("--pitch", default=PITCH_DEFAULT, help=f"Pitch del TTS (default: {PITCH_DEFAULT}). Ej: '+8Hz', '+20Hz'.")
    parser.add_argument("--rate", default=RATE_DEFAULT, help="Rate del TTS. Default 0 porciento. Acepta +N o -N seguido de porciento.")
    parser.add_argument("--list-voices", action="store_true", help="Lista voces sugeridas y termina")

    # Pauta / cola del episodio (Sprint 6)
    parser.add_argument("--pauta-init", metavar="SLUG", help="Crea una pauta vacia con ese slug. Acepta --episodio, --voice, --pitch, --rate.")
    parser.add_argument("--pauta-auto", metavar="HTML", help="Autogenera la pauta desde un HTML de episodio (usa Claude). Acepta --n-datos, --force.")
    parser.add_argument("--pauta-tema", metavar="TEMA", help="Sprint 11: genera pauta desde un tema libre sin HTML (Claude). Ej: --pauta-tema 'Mega Drive raros'. Acepta --n-datos, --slug, --consola, --episodio, --voice, --no-preload, --force.")
    parser.add_argument("--slug", help="Slug explicito para --pauta-tema (por default se deriva del tema).")
    parser.add_argument("--no-preload", action="store_true", help="No precargar MP3s al generar pauta (--pauta-tema).")
    parser.add_argument("--pauta-preload", metavar="SLUG", help="Precarga (genera) todos los MP3 de una pauta en paralelo. Acepta --force, --concurrency.")
    parser.add_argument("--concurrency", type=int, help="Cantidad de TTS concurrentes para --pauta-preload (default 3, max razonable 6).")
    parser.add_argument("--pauta-srt", metavar="SLUG", help="Exporta SRT desde una pauta (modo relative, util para preview offline).")
    parser.add_argument("--gap-ms", type=int, help="Milisegundos de pausa entre items en SRT modo relative (default 500).")
    parser.add_argument("--melodia-add", metavar="SLUG", help="Agrega un item de melodia a la pauta (Sprint 8.1, MIDI->MP3 SNES).")
    parser.add_argument("--melodia-bulk", metavar="SLUG", help="Agrega los MIDIs de studio/melodias/ a la pauta. Usa --folder para limitar a una subcarpeta especifica.")
    parser.add_argument("--melodia-clean", metavar="SLUG", help="Borra TODAS las melodias de una pauta (los MP3 tambien). Util para reorganizar.")
    parser.add_argument("--folder", help="Subcarpeta dentro de studio/melodias/ para --melodia-bulk (ej: 'n64', 'snes', 'mario').")
    parser.add_argument("--midi", metavar="PATH", help="Ruta al MIDI para --melodia-add.")
    parser.add_argument("--desde", help="Donde empieza el snippet en el MIDI. Formato: '14', '0:14', '1:23'.")
    parser.add_argument("--segundos", type=float, help="Duracion del snippet en segundos (default 8, max recomendado 15).")
    parser.add_argument("--titulo", help="Titulo de la melodia (ej: 'DKC Aquatic Ambience').")
    parser.add_argument("--pauta-list", action="store_true", help="Lista todas las pautas creadas en studio/pautas/")
    parser.add_argument("--pauta-show", metavar="SLUG", help="Muestra el contenido de una pauta")
    parser.add_argument("--episodio", help="Titulo del episodio (para --pauta-init y --pauta-auto)")
    parser.add_argument("--n-datos", type=int, help="Cantidad de datos a generar con --pauta-auto (default 10, max 20)")
    parser.add_argument("--force", action="store_true", help="Sobrescribe la pauta si ya existe")
    parser.add_argument("--no-sync", action="store_true", help="No sincronizar con Drive al terminar (los comandos que modifican pautas hacen sync automatico por default)")

    args = parser.parse_args()

    # --list-voices
    if args.list_voices:
        print("=== Voces sugeridas TarroBot (alias -> Edge TTS) ===")
        for alias, full in VOCES_SUGERIDAS.items():
            nota = ""
            if "AR" in full:
                nota = "  (NO usar: argentino, rompe regla del canal)"
            if alias == "catalina":
                nota = "  (DEFAULT, chilena)"
            print(f"  {alias:12} -> {full}{nota}")
        return 0

    # Pauta commands (no requieren DB global)
    if args.pauta_list:
        return cmd_pauta_list(args)
    if args.pauta_show:
        return cmd_pauta_show(args)
    if args.pauta_init:
        return cmd_pauta_init(args)
    if args.pauta_auto:
        return cmd_pauta_auto(args)
    if args.pauta_tema:
        return cmd_pauta_tema(args)
    if args.pauta_preload:
        return cmd_pauta_preload(args)
    if args.pauta_srt:
        return cmd_pauta_srt(args)
    if args.melodia_add:
        return cmd_melodia_add(args)
    if args.melodia_bulk:
        return cmd_melodia_bulk(args)
    if args.melodia_clean:
        return cmd_melodia_clean(args)

    db = cargar_db()

    if args.list:
        return cmd_list(db)

    if args.add:
        return cmd_add(args, db)

    if not args.tema:
        parser.print_help()
        return 0

    return cmd_buscar(args, db)


if __name__ == "__main__":
    sys.exit(main() or 0)
