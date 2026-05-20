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

# REPO puede venir de env var (modo Drive, estudio compartido) o del path del script.
# Esto permite que el PC del estudio lea el repo desde el Drive sincronizado y
# vea automaticamente todas las pautas/datos que generas en tu PC.
_REPO_FROM_ENV = os.environ.get("RETROTARROS_REPO")
if _REPO_FROM_ENV and Path(_REPO_FROM_ENV).exists():
    REPO = Path(_REPO_FROM_ENV).resolve()
else:
    REPO = Path(__file__).parent.parent

DB_PATH = REPO / "data" / "tarrobot-database.json"
TEMPLATE = REPO / "studio" / "_template-tarrobot-slide.html"
OUT_DIR = REPO / "studio" / "tarrobot-out"
PAUTAS_DIR = REPO / "studio" / "pautas"
PAUTAS_AUDIO_DIR = PAUTAS_DIR / "audio"

ESTADOS = [
    "idle", "talking", "excited", "sleep", "thinking", "winking",
    "confused", "glitched", "fact", "happy", "sad", "angry", "loading"
]

LABEL_POR_ESTADO = {
    "idle":     "DATO CURIOSO",
    "talking":  "DATO CURIOSO",
    "excited":  "DATO BOMBA · MIND BLOWN",
    "fact":     "FACT TIME · DATO ESTRELLA",
    "thinking": "PROCESANDO DATO...",
    "winking":  "ENTRE NOSOTROS...",
    "confused": "EN SERIO?",
    "happy":    "BUENA NOTICIA",
    "sad":      "QUE PENA",
    "angry":    "ESTO NO ME GUSTA",
    "loading":  "BUSCANDO INFO...",
    "glitched": "SEÑAL CORRUPTA",
    "sleep":    "DESCANSANDO",
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

Requisitos OBLIGATORIOS:
- Español chileno neutro con tuteo (NO voseo argentino: nada de "tenes", "queres", "decime", "vos").
- SIN tildes (a/e/i/o/u sin acento).
- Maximo 3 oraciones por dato, alrededor de 220 caracteres.
- Verificable y especifico: fechas, numeros, nombres reales.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabias".
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


def resolver_voz(voz_arg: str) -> str:
    """Acepta alias corto ('catalina') o nombre completo Edge ('es-CL-...')."""
    if not voz_arg:
        return VOZ_DEFAULT
    if voz_arg in VOCES_SUGERIDAS:
        return VOCES_SUGERIDAS[voz_arg]
    return voz_arg


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

Requisitos OBLIGATORIOS para CADA dato:
- Español chileno neutro con tuteo (NO voseo argentino: nada de "tenes", "queres", "decime", "vos", "che").
- SIN tildes (a/e/i/o/u sin acento). ESTO ES CRITICO, revisa antes de devolver.
- Maximo 3 oraciones por dato, alrededor de 200-260 caracteres.
- Verificable y especifico: fechas, numeros, nombres reales.
- Tono curioso y entusiasta tipo "te voy a contar algo que no sabias".
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

    return result


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
    return 0


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
    parser.add_argument("--pauta-preload", metavar="SLUG", help="Precarga (genera) todos los MP3 de una pauta en paralelo. Acepta --force, --concurrency.")
    parser.add_argument("--concurrency", type=int, help="Cantidad de TTS concurrentes para --pauta-preload (default 3, max razonable 6).")
    parser.add_argument("--pauta-srt", metavar="SLUG", help="Exporta SRT desde una pauta (modo relative, util para preview offline).")
    parser.add_argument("--gap-ms", type=int, help="Milisegundos de pausa entre items en SRT modo relative (default 500).")
    parser.add_argument("--pauta-list", action="store_true", help="Lista todas las pautas creadas en studio/pautas/")
    parser.add_argument("--pauta-show", metavar="SLUG", help="Muestra el contenido de una pauta")
    parser.add_argument("--episodio", help="Titulo del episodio (para --pauta-init y --pauta-auto)")
    parser.add_argument("--n-datos", type=int, help="Cantidad de datos a generar con --pauta-auto (default 10, max 20)")
    parser.add_argument("--force", action="store_true", help="Sobrescribe la pauta si ya existe")

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
    if args.pauta_preload:
        return cmd_pauta_preload(args)
    if args.pauta_srt:
        return cmd_pauta_srt(args)

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
