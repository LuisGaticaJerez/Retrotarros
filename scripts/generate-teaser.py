"""
generate-teaser.py

Genera un teaser vertical 1080x1920 (~18 seg) para TikTok / Reels / Shorts
desde el video master de un episodio de Retrotarros.

Pipeline:
  1. Extrae audio del video.
  2. Whisper transcribe (modelo "base", español, local sin internet).
  3. Detecta highlights por keywords (precios, datos bomba, reacciones).
  4. Selecciona 6 clips: cold open + 4 highlights + cierre (3 seg c/u).
  5. Recorta los clips.
  6. Crop/blur a vertical 1080x1920 (estilo TikTok con background blureado).
  7. Concatena con fade transitions.
  8. Overlay de texto ("NUEVO CAPÍTULO" arriba al inicio, CTA al cierre).
  9. Mezcla audio: música 70% + voz original 30%.
 10. Render H.264 + AAC, 5 Mbps.

Uso:
    python scripts/generate-teaser.py <video.mp4> --slug n64-top-mundial
    python scripts/generate-teaser.py <video.mp4> --slug n64-top-mundial --music "Carcasa de Neón.wav" --model small

Requisitos:
    - ffmpeg en PATH (winget install Gyan.FFmpeg)
    - pip install openai-whisper
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Rutas base
RECURSOS = Path("D:/Recursos Retrotarros")
REPO = RECURSOS / "repo"
DRIVE_STUDIO = RECURSOS / "Drive" / "Studio"
MUSIC_DIR = RECURSOS / "Drive" / "Musica Retrotarros"
FONTS_DIR = REPO / "assets" / "fonts"

# Música default (track fijo brand Retrotarros)
DEFAULT_MUSIC = "8 Bits Rock.wav"

# Fuente para overlays
FONT_FILE = FONTS_DIR / "PressStart2P-Regular.ttf"

# Intro de marca (cold open viene de acá, NO del master)
# Segs 2-5: tilt sobre estantería N64 + batería. Cubre los 3 conceptos del canal.
INTRO_VIDEO = RECURSOS / "INTRO - CAP-0-N64" / "INTRO RETROTARROS def.mp4"
INTRO_START_TIME = 2.0  # segundo desde el cual empezamos el cold open

# Logo para la outro card (el banner del canal, ya con tagline actualizado)
LOGO_FILE = REPO / "assets" / "Retrotarros_Logo_v2_1920x1080.png"

# Cache de transcripciones Whisper. Hash del audio extraído + modelo = clave única.
# Si existe cache válido, skip Whisper (3-5 min). Útil para iterar diseño rápido.
WHISPER_CACHE_DIR = REPO / ".cache" / "whisper"

# End card oficial - VHS estilo Tarrovision (fija para todos los episodios)
# Vive en Drive (sincronizada por Drive Desktop). Si querés cambiar a Cartucho
# o GameBoy, apuntá esta constante a ese archivo.
END_CARD = (RECURSOS / "Drive" / "Imagenes retrotarros" /
            "Templates Tiktok_Shorts" / "Retrotarros_EndCard_VHS_Siguenos.png")

# Template para la trivia card del medio del teaser (estilo TarroVision TV CRT)
TRIVIA_TEMPLATE = (RECURSOS / "Drive" / "Imagenes retrotarros" /
                   "Templates Tiktok_Shorts" / "Retrotarros_Template_4_TarroVision.png")
# Rectángulo amarillo del template TarroVision donde va la pregunta (1080x1920)
TRIVIA_TEXT_BBOX = (155, 870, 925, 1030)  # x1, y1, x2, y2

# Colores brand
MAGENTA = (255, 46, 136)   # #FF2E88
CYAN = (0, 229, 255)        # #00E5FF
YELLOW = (255, 210, 63)     # #FFD23F
DARK = (6, 3, 15)           # #06030F

# Duración del teaser (30 seg: intro + 4H + trivia + 3H + outro = 10 clips × 3s)
CLIP_DURATION = 3.0
NUM_HIGHLIGHTS_PRE_TRIVIA = 4   # highlights antes de la trivia card
NUM_HIGHLIGHTS_POST_TRIVIA = 3  # highlights después de la trivia card
TOTAL_HIGHLIGHTS = NUM_HIGHLIGHTS_PRE_TRIVIA + NUM_HIGHLIGHTS_POST_TRIVIA  # 7
TOTAL_CLIPS = 1 + TOTAL_HIGHLIGHTS + 2  # intro + 7H + trivia + outro = 10
TEASER_DURATION = CLIP_DURATION * TOTAL_CLIPS  # 30 seg

# Output dimensions (TikTok / Reels / Shorts)
OUT_W = 1080
OUT_H = 1920

# Audio mix levels (decisión Luis 2026-05-17: voz domina, música muy baja)
MUSIC_VOL = 0.15
VOICE_VOL = 0.85

# Keywords para detectar highlights (mayor score = más interesante)
KEYWORDS_BOMBA = [
    # Precios y plata
    "dólares", "dolares", "dolar", "dólar", "mil", "lucas", "vale", "cuesta",
    "millón", "millon", "carísimo", "carisimo", "barato", "precio", "pagar",
    # Datos bomba
    "más caro", "mas caro", "más raro", "mas raro", "récord", "record",
    "increíble", "increible", "imposible", "primero", "último", "ultimo",
    "único", "unico", "spoiler",
    # Reacciones de cámara
    "qué", "que", "wow", "no puede", "no me", "mira", "fíjate", "fijate",
    "atención", "atencion",
]


# ============================================================================
# HELPERS
# ============================================================================

def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Ejecuta ffmpeg / comando, log limpio, retorna CompletedProcess."""
    print(f"  $ {' '.join(str(c) for c in cmd[:4])}{'...' if len(cmd) > 4 else ''}")
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def ensure_ffmpeg() -> str:
    """Busca ffmpeg en PATH o ubicaciones conocidas. Retorna ruta o exit."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    # Fallback: winget Gyan.FFmpeg
    winget_glob = list(Path(os.environ["LOCALAPPDATA"]).glob(
        "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_*/ffmpeg-*-full_build/bin/ffmpeg.exe"
    ))
    if winget_glob:
        return str(winget_glob[0])
    print("ERROR: ffmpeg no encontrado en PATH ni winget. Instalá con `winget install Gyan.FFmpeg`.")
    sys.exit(1)


def get_duration(video: Path) -> float:
    """Devuelve la duración del video en segundos."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


# ============================================================================
# INFERENCIA DE TITLE + TRIVIA desde slug y pauta MD
# ============================================================================

# Trivia question por tipo de episodio. Si el slug matchea, se usa esto.
TRIVIA_BY_TYPE = {
    "top-mundial": "¿SABES CUAL ES EL #1 DEL MUNDO?",
    "top-precios": "¿CUAL ES EL JUEGO MAS CARO?",
    "archivo-koko": "¿CUANTO VALE LA COLECCION?",
    "joyas-ocultas": "¿CUAL ES LA JOYA OCULTA?",
    "retrotarros-vs-mundo": "¿KOKO LE GANA A LA CRITICA?",
    "hardware-raro": "¿CUAL ES EL HARDWARE MAS RARO?",
    "no-latam": "¿QUE JUEGOS NUNCA LLEGARON?",
    "kirkhope-rare": "¿QUE HIZO RARE EN LOS 90?",
    "nintendo-vs-playstation": "¿COMO PERDIO NINTENDO LA GEN 5?",
}


def infer_title_and_trivia(slug: str, pauta_md: Path | None = None) -> tuple[str, str]:
    """Devuelve (title, trivia) inferidos del slug + pauta MD si existe.

    Title: lee la primera línea **negrita** después de "*Nostalgia + Juegos + Música*"
           en la pauta MD del episodio. Fallback: slug formateado.
    Trivia: matchea el slug contra TRIVIA_BY_TYPE. Fallback: pregunta genérica.
    """
    # Title default = slug en mayúsculas con espacios
    title = slug.replace("-", " ").upper()

    # Intentar leer del MD
    if pauta_md is None:
        pauta_md = REPO / "docs" / f"pauta-{slug}.md"
    if pauta_md.exists():
        text = pauta_md.read_text(encoding="utf-8")
        for line in text.split("\n")[:20]:
            line = line.strip()
            # Buscar línea **negrita** que sea el título del episodio
            if line.startswith("**") and line.endswith("**") and len(line) > 8:
                candidate = line.replace("**", "").strip()
                # Skip headers de plantilla
                if "Pauta de episodio" in candidate or "Nostalgia" in candidate:
                    continue
                # Tomar solo la primera parte si tiene " — "
                if " — " in candidate:
                    candidate = candidate.split(" — ")[0]
                title = candidate.upper()
                break

    # Trivia: matchear tipo de slug
    trivia = "¿QUE TIENE ESTE EPISODIO?"
    for kw, q in TRIVIA_BY_TYPE.items():
        if kw in slug:
            trivia = q
            break

    return title, trivia


# ============================================================================
# OUTRO CARD (PNG + video) - generada dinámicamente
# ============================================================================

def generate_outro_card(logo_path: Path, output_png: Path) -> None:
    """Genera PNG 1080x1920 outro: logo + CTA YouTube + flecha."""
    from PIL import Image, ImageDraw, ImageFont  # type: ignore

    canvas = Image.new("RGB", (OUT_W, OUT_H), color=DARK)

    # Cargar logo y escalar a 90% del ancho del canvas
    logo = Image.open(logo_path).convert("RGBA")
    target_w = int(OUT_W * 0.92)
    ratio = target_w / logo.size[0]
    target_h = int(logo.size[1] * ratio)
    logo = logo.resize((target_w, target_h), Image.LANCZOS)

    # Centrar el logo en el tercio superior
    pos_x = (OUT_W - target_w) // 2
    pos_y = int(OUT_H * 0.22)
    canvas.paste(logo, (pos_x, pos_y), logo)

    # Textos CTA debajo del logo
    draw = ImageDraw.Draw(canvas)
    font_big = ImageFont.truetype(str(FONT_FILE), 72)
    font_med = ImageFont.truetype(str(FONT_FILE), 56)
    font_small = ImageFont.truetype(str(FONT_FILE), 30)

    cta_y = pos_y + target_h + 140

    # "NUEVO CAPITULO" en magenta arcade
    cta1 = "NUEVO CAPITULO"
    bbox = draw.textbbox((0, 0), cta1, font=font_big)
    w = bbox[2] - bbox[0]
    draw.text(((OUT_W - w) // 2, cta_y), cta1, font=font_big, fill=MAGENTA,
              stroke_width=2, stroke_fill=DARK)

    # "EN YOUTUBE" en cyan eléctrico
    cta2 = "EN YOUTUBE"
    bbox = draw.textbbox((0, 0), cta2, font=font_med)
    w = bbox[2] - bbox[0]
    draw.text(((OUT_W - w) // 2, cta_y + 130), cta2, font=font_med, fill=CYAN,
              stroke_width=2, stroke_fill=DARK)

    # "↑ link en bio" abajo en amarillo arcade
    cta3 = "LINK EN BIO"
    bbox = draw.textbbox((0, 0), cta3, font=font_small)
    w = bbox[2] - bbox[0]
    draw.text(((OUT_W - w) // 2, OUT_H - 220), cta3, font=font_small, fill=YELLOW)

    canvas.save(output_png, "PNG", optimize=True)


def image_to_video(png_path: Path, duration: float, output_mp4: Path, ffmpeg: str) -> None:
    """Convierte un PNG estático en un MP4 de N segundos (30fps, mismo codec que el resto)."""
    run([
        ffmpeg, "-y",
        "-loop", "1",
        "-framerate", "30",
        "-i", str(png_path),
        "-t", f"{duration}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        str(output_mp4),
    ], check=True)


def generate_trivia_card(template_path: Path, question: str, output_png: Path) -> None:
    """Toma el template TarroVision y mete la pregunta dentro del rectángulo amarillo."""
    from PIL import Image, ImageDraw, ImageFont  # type: ignore

    img = Image.open(template_path).convert("RGB")
    # Asegurar 1080x1920
    if img.size != (OUT_W, OUT_H):
        img = img.resize((OUT_W, OUT_H), Image.LANCZOS)

    draw = ImageDraw.Draw(img)
    x1, y1, x2, y2 = TRIVIA_TEXT_BBOX
    box_w = x2 - x1
    box_h = y2 - y1

    # Wrap text en líneas que quepan en el box
    import textwrap
    # Probamos tamaños decrecientes hasta que quepa en 3 líneas máx
    for font_size in (44, 40, 36, 32, 28):
        font = ImageFont.truetype(str(FONT_FILE), font_size)
        # Avg char width aprox = font_size * 1.1 para Press Start 2P (monospace)
        chars_per_line = max(10, int(box_w / (font_size * 1.0)))
        lines = textwrap.wrap(question, width=chars_per_line)
        if len(lines) <= 3:
            break

    line_height = int(font_size * 1.3)
    total_h = len(lines) * line_height

    # Centrar verticalmente dentro del box
    start_y = y1 + (box_h - total_h) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = x1 + (box_w - w) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font, fill=YELLOW,
                  stroke_width=2, stroke_fill=DARK)

    img.save(output_png, "PNG", optimize=True)


# ============================================================================
# PASOS DEL PIPELINE
# ============================================================================

def step_extract_audio(video: Path, out_wav: Path, ffmpeg: str) -> None:
    """1. Extrae audio del video como WAV 16kHz mono (formato Whisper)."""
    print("\n[1/10] Extrayendo audio para Whisper...")
    run([
        ffmpeg, "-y", "-i", str(video),
        "-vn", "-ar", "16000", "-ac", "1",
        "-c:a", "pcm_s16le",
        str(out_wav),
    ], check=True)


def _wav_hash(wav: Path) -> str:
    """Hash MD5 del archivo WAV (rápido sobre wav de 60MB ~1s)."""
    h = hashlib.md5()
    with open(wav, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def step_whisper_transcribe(wav: Path, model_name: str) -> list[dict]:
    """2. Whisper transcribe en español con cache. Retorna lista de segmentos.

    Cache key = hash(wav) + model_name. Si existe → skip Whisper (3-5 min).
    Cache en D:\\Recursos Retrotarros\\repo\\.cache\\whisper\\<hash>.json
    """
    WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[2/10] Whisper transcribiendo (modelo={model_name})...")
    wav_hash = _wav_hash(wav)
    cache_file = WHISPER_CACHE_DIR / f"{wav_hash}_{model_name}.json"

    if cache_file.exists():
        with open(cache_file, encoding="utf-8") as f:
            segments = json.load(f)
        print(f"   [CACHE HIT] {cache_file.name} ({len(segments)} segmentos, skip Whisper)")
        return segments

    print(f"   Cache miss, transcribiendo (5-10 min)...")
    import whisper  # type: ignore
    model = whisper.load_model(model_name)
    result = model.transcribe(str(wav), language="es", verbose=False)
    segments = result.get("segments", [])
    # Solo guardar campos esenciales para reducir tamaño cache
    serializable = [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments]
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False)
    print(f"   {len(segments)} segmentos transcritos · cache guardado en {cache_file.name}")
    return serializable


def find_farewell_segment(segments: list[dict], video_duration: float) -> float | None:
    """Busca el momento de despedida en los últimos 90 seg del transcript.

    Heurística: keywords típicas de cierre de Luis en Retrotarros (CTA YouTube
    + cierre informal). Whisper "base" transcribe imperfecto en chileno, por
    eso incluímos variaciones ("vemos" sin "nos", "chiquíos" sin doble-LL, etc).
    """
    farewell_keywords = [
        # Frase canónica
        "esto fue retrotarros", "esto fue retro tarros", "esto fue retrotaros",
        "fue retrotarros", "fue retrotaros",
        "este fue", "este fue el",  # "Este fue el ranking..."
        # CTA YouTube clásico
        "apoyenos", "apóyenos", "apoyennos",
        "suscribanse", "suscríbanse", "suscribite",
        "campanita",
        # Cierre informal Luis/Koko
        "chiquillos", "chiquíos", "chiquios", "chiquillo",
        "nos vemos", " vemos", "vemos!",
        "hasta la proxima", "hasta la próxima",
        "chao", "chau",
        # Mando comentario
        "mandanos un comentario", "mándanos un comentario",
        "fin del episodio", "fin de episodio",
    ]
    cutoff = max(0.0, video_duration - 90.0)
    candidates = []
    for seg in segments:
        if seg["start"] < cutoff:
            continue
        text_low = seg["text"].lower()
        for kw in farewell_keywords:
            if kw in text_low:
                candidates.append((seg["start"], seg["text"][:80], kw))
                break

    if candidates:
        # Tomar el más cercano al final (último cierre antes del end)
        best = max(candidates, key=lambda x: x[0])
        print(f"   Despedida detectada @ {best[0]:.1f}s (keyword='{best[2]}'):")
        print(f"     \"{best[1]}\"")
        return best[0]
    print(f"   No se detectó despedida específica en los últimos 90s")
    return None


def step_detect_highlights(segments: list[dict], video_duration: float,
                            num_highlights: int = 4) -> list[float]:
    """3-4. Score por keywords + selección de N highlights espaciados.

    Divide el video en N cuantiles y elige el mejor segmento de cada uno.
    """
    print("\n[3/10] Detectando keywords y scoring segmentos...")

    def score(text: str) -> int:
        text_low = text.lower()
        return sum(1 for kw in KEYWORDS_BOMBA if kw in text_low)

    scored = []
    for seg in segments:
        s = score(seg["text"])
        if s > 0:
            scored.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"][:60],
                "score": s,
            })

    scored.sort(key=lambda x: -x["score"])
    print(f"   {len(scored)} segmentos con keywords. Top 5:")
    for s in scored[:5]:
        print(f"     [{s['start']:.0f}s] score={s['score']} · {s['text']}")

    print(f"\n[4/10] Seleccionando {num_highlights} highlights espaciados...")
    selected = []
    for i in range(num_highlights):
        q_start = video_duration * i / num_highlights
        q_end = video_duration * (i + 1) / num_highlights
        candidates = [s for s in scored
                      if q_start <= s["start"] < q_end
                      and s["start"] > 10
                      and s["start"] < video_duration - 10]
        if candidates:
            best = max(candidates, key=lambda x: x["score"])
            selected.append(best["start"])
            print(f"   Q{i+1} ({q_start:.0f}-{q_end:.0f}s): elegido seg {best['start']:.1f}s")
        else:
            mid = (q_start + q_end) / 2
            selected.append(mid)
            print(f"   Q{i+1} ({q_start:.0f}-{q_end:.0f}s): fallback {mid:.1f}s (sin keywords)")

    return selected


def step_cut_clips(video: Path, highlight_times: list[float],
                   video_duration: float, trivia_question: str,
                   tmp_dir: Path, ffmpeg: str) -> tuple[list[Path], list[tuple[Path, float]]]:
    """5. Recorta los clips del teaser. Estructura:

    intro (1) + highlights_pre_trivia (N) + trivia (1) + highlights_post_trivia (M) + outro (1)

    Por default: 1 + 4 + 1 + 3 + 1 = 10 clips × 3s = 30s
    """
    print(f"\n[5/10] Recortando {TOTAL_CLIPS} clips de {CLIP_DURATION}s...")

    clip_plan: list[tuple[Path, float]] = []

    # ── Cold open desde el intro de marca ──
    if INTRO_VIDEO.exists():
        clip_plan.append((INTRO_VIDEO, INTRO_START_TIME))
        print(f"   clip 1 (cold open): INTRO de marca @ {INTRO_START_TIME:.1f}s")
    else:
        print(f"   WARN: no existe {INTRO_VIDEO}, usando master para cold open")
        clip_plan.append((video, 0.0))

    # ── Primeros N highlights del master ──
    for t in highlight_times[:NUM_HIGHLIGHTS_PRE_TRIVIA]:
        clip_plan.append((video, max(0.0, t - CLIP_DURATION / 2)))

    # ── Trivia card (estática, generada del template TarroVision) ──
    trivia_png = tmp_dir / "trivia.png"
    trivia_mp4 = tmp_dir / "trivia.mp4"
    if TRIVIA_TEMPLATE.exists():
        generate_trivia_card(TRIVIA_TEMPLATE, trivia_question, trivia_png)
        image_to_video(trivia_png, CLIP_DURATION, trivia_mp4, ffmpeg)
        clip_plan.append((trivia_mp4, 0.0))
        print(f"   clip {NUM_HIGHLIGHTS_PRE_TRIVIA + 2} (trivia): \"{trivia_question}\"")
    else:
        print(f"   WARN: no existe {TRIVIA_TEMPLATE.name}, saltando trivia")

    # ── Highlights post-trivia ──
    for t in highlight_times[NUM_HIGHLIGHTS_PRE_TRIVIA:NUM_HIGHLIGHTS_PRE_TRIVIA + NUM_HIGHLIGHTS_POST_TRIVIA]:
        clip_plan.append((video, max(0.0, t - CLIP_DURATION / 2)))

    # ── Cierre = END_CARD oficial ──
    outro_png = tmp_dir / "outro.png"
    outro_mp4 = tmp_dir / "outro.mp4"
    if END_CARD.exists():
        shutil.copy2(END_CARD, outro_png)
        image_to_video(outro_png, CLIP_DURATION, outro_mp4, ffmpeg)
        clip_plan.append((outro_mp4, 0.0))
        print(f"   clip {len(clip_plan)} (outro): END CARD oficial = {END_CARD.name}")
    elif LOGO_FILE.exists():
        print(f"   WARN: no existe {END_CARD.name}, fallback a outro PIL")
        generate_outro_card(LOGO_FILE, outro_png)
        image_to_video(outro_png, CLIP_DURATION, outro_mp4, ffmpeg)
        clip_plan.append((outro_mp4, 0.0))
    else:
        clip_plan.append((video, max(0.0, video_duration - CLIP_DURATION)))

    clip_paths = []
    for i, (src, start) in enumerate(clip_plan):
        out = tmp_dir / f"clip_{i:02d}.mp4"
        run([
            ffmpeg, "-y", "-ss", f"{start:.2f}", "-i", str(src),
            "-t", f"{CLIP_DURATION}",
            "-an",  # sin audio (lo mezclamos al final)
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(out),
        ], check=True)
        clip_paths.append(out)

    return clip_paths, clip_plan


def get_video_size(video: Path) -> tuple[int, int]:
    """Devuelve (width, height) del video con ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=s=x:p=0", str(video)],
        capture_output=True, text=True, check=True,
    )
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def step_to_vertical(clip_paths: list[Path], tmp_dir: Path, ffmpeg: str) -> list[Path]:
    """6. Cada clip horizontal -> vertical 1080x1920 con blur background.

    Si el clip ya es 1080x1920 (ej. outro card), se normaliza a 30fps sin blur.
    """
    print(f"\n[6/10] Convirtiendo a vertical {OUT_W}x{OUT_H} con blur background...")
    vertical_paths = []
    for i, clip in enumerate(clip_paths):
        out = tmp_dir / f"vert_{i:02d}.mp4"
        w, h = get_video_size(clip)

        if w == OUT_W and h == OUT_H:
            # Ya es vertical 1080x1920 (outro card) - solo normalizar fps
            print(f"   clip {i+1}/{len(clip_paths)}: ya es {OUT_W}x{OUT_H}, sin blur")
            run([
                ffmpeg, "-y", "-i", str(clip),
                "-vf", "fps=30",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                str(out),
            ], check=True)
        else:
            # Horizontal -> vertical con blur background + foreground centrado
            filter_complex = (
                "[0:v]split=2[bg][fg];"
                f"[bg]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
                f"crop={OUT_W}:{OUT_H},boxblur=20:5[bgblur];"
                f"[fg]scale={OUT_W}:-1[fgscaled];"
                "[bgblur][fgscaled]overlay=(W-w)/2:(H-h)/2"
            )
            run([
                ffmpeg, "-y", "-i", str(clip),
                "-filter_complex", filter_complex,
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                "-pix_fmt", "yuv420p",
                str(out),
            ], check=True)
        vertical_paths.append(out)

    return vertical_paths


def step_concat(vertical_paths: list[Path], tmp_dir: Path, ffmpeg: str) -> Path:
    """7. Concatena los 6 clips verticales (concat demuxer)."""
    print("\n[7/10] Concatenando clips...")
    list_file = tmp_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in vertical_paths),
        encoding="utf-8",
    )
    out = tmp_dir / "concat.mp4"
    run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out),
    ], check=True)
    return out


def step_overlay_text(video: Path, tmp_dir: Path, ffmpeg: str,
                      title: str = "",
                      trivia_start_sec: float | None = None,
                      include_outro_text: bool = False) -> Path:
    """8. Overlay persistente: 'NUEVO CAPITULO' arriba + título abajo.

    Ambos overlays se muestran de 0 a (TEASER_DURATION - 3) seg, excepto
    durante los 3 seg de la trivia card (donde tapan el diseño del template).

    Si include_outro_text=True agrega 'RETROTARROS · YOUTUBE' al pie en el cierre
    (solo cuando NO se usa END_CARD oficial).
    """
    print("\n[8/10] Agregando overlays de texto...")
    out = tmp_dir / "with_text.mp4"
    font_path = str(FONT_FILE).replace("\\", "/").replace(":", "\\:")

    overlay_end = TEASER_DURATION - CLIP_DURATION  # hasta antes del outro

    # Cuándo mostrar/ocultar overlays (visibles todo el teaser excepto outro y trivia)
    intro_text = "NUEVO CAPITULO DE RETROTARROS"
    if trivia_start_sec is not None:
        trivia_end = trivia_start_sec + CLIP_DURATION
        nuevocap_enable = (
            f"'(between(t,0.3,{trivia_start_sec})+between(t,{trivia_end},{overlay_end}))'"
        )
    else:
        nuevocap_enable = f"'between(t,0.3,{overlay_end})'"

    # "NUEVO CAPITULO DE RETROTARROS" abajo (encima del título del video)
    # Font más chico porque el texto es más largo. Posición y = h-360.
    filter_chain = (
        f"drawtext=fontfile='{font_path}':text='{intro_text}':"
        f"fontsize=36:fontcolor=#FFD23F:"
        f"x=(w-text_w)/2:y=h-360:"
        f"box=1:boxcolor=black@0.65:boxborderw=18:"
        f"enable={nuevocap_enable}"
    )

    # Título del video abajo — debajo del "NUEVO CAPITULO DE RETROTARROS"
    if title:
        safe_title = (title.replace("Á", "A").replace("É", "E").replace("Í", "I")
                            .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N")
                            .replace("á", "a").replace("é", "e").replace("í", "i")
                            .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
                            .replace("¿", "").replace("?", "").upper())
        safe_title = safe_title.replace(":", "\\:").replace("'", "\\'")
        filter_chain += (
            f",drawtext=fontfile='{font_path}':text='{safe_title}':"
            f"fontsize=44:fontcolor=#00E5FF:"
            f"x=(w-text_w)/2:y=h-240:"
            f"box=1:boxcolor=black@0.65:boxborderw=18:"
            f"enable={nuevocap_enable}"
        )

    if include_outro_text:
        outro_start = TEASER_DURATION - CLIP_DURATION
        outro_text = "RETROTARROS - YOUTUBE"
        filter_chain += (
            f",drawtext=fontfile='{font_path}':text='{outro_text}':"
            f"fontsize=48:fontcolor=#FFD23F:"
            f"x=(w-text_w)/2:y=h-280:"
            f"box=1:boxcolor=black@0.6:boxborderw=20:"
            f"enable='between(t,{outro_start},{TEASER_DURATION})'"
        )

    run([
        ffmpeg, "-y", "-i", str(video),
        "-vf", filter_chain,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out),
    ], check=True)
    return out


def step_mix_audio(video_with_text: Path, clip_plan: list[tuple[Path, float]],
                   music: Path, tmp_dir: Path, ffmpeg: str) -> tuple[Path, Path]:
    """9. Extrae voz de cada source clip (intro o master) y arma una pista única."""
    print("\n[9/10] Extrayendo audio sincronizado con cada clip + mezclando con música...")

    voice_track = tmp_dir / "voice.wav"
    voice_clips = []
    last_idx = len(clip_plan) - 1
    for i, (src, start) in enumerate(clip_plan):
        out = tmp_dir / f"voice_{i:02d}.wav"
        # Silenciar:
        #  - clip 0 (cold open de intro): el intro tiene su propia música que
        #    se solaparía con 8 Bits Rock, así que silenciamos.
        #  - trivia card (PNG estático): no tiene audio relevante.
        #  - outro card (PNG estático): solo música.
        is_intro = i == 0 and src == INTRO_VIDEO
        is_static_card = src.name in ("trivia.mp4", "outro.mp4")
        if is_intro or is_static_card:
            run([
                ffmpeg, "-y", "-f", "lavfi",
                "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", f"{CLIP_DURATION}",
                "-c:a", "pcm_s16le",
                str(out),
            ], check=True)
        else:
            run([
                ffmpeg, "-y", "-ss", f"{start:.2f}", "-i", str(src),
                "-t", f"{CLIP_DURATION}",
                "-vn", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le",
                str(out),
            ], check=True)
        voice_clips.append(out)

    voice_list = tmp_dir / "voice_concat.txt"
    voice_list.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in voice_clips),
        encoding="utf-8",
    )
    run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", str(voice_list),
        "-c:a", "pcm_s16le",
        str(voice_track),
    ], check=True)

    print("   mezclando música + voz...")
    return video_with_text, voice_track


def step_render_final(video_with_text: Path, voice_track: Path, music: Path,
                      output: Path, ffmpeg: str) -> None:
    """10. Render final con audio mezclado."""
    print(f"\n[10/10] Render final -> {output.name}")
    output.parent.mkdir(parents=True, exist_ok=True)

    # ffmpeg complex filter: mezcla música (loop si necesario) + voz + boost final
    # amix divide entre inputs por default → contraresta con volume boost al final.
    filter_complex = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{TEASER_DURATION},"
        f"volume={MUSIC_VOL}[mus];"
        f"[2:a]volume={VOICE_VOL}[voc];"
        f"[mus][voc]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
        f"volume=2.2[aout]"
    )
    run([
        ffmpeg, "-y",
        "-i", str(video_with_text),
        "-i", str(music),
        "-i", str(voice_track),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output),
    ], check=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Genera teaser vertical desde video master.")
    parser.add_argument("video", help="Ruta al video master del episodio (MP4)")
    parser.add_argument("--slug", required=True, help="Slug del episodio (ej. n64-top-mundial)")
    parser.add_argument("--music", default=DEFAULT_MUSIC, help=f"Nombre del archivo de música (default: {DEFAULT_MUSIC})")
    parser.add_argument("--model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo Whisper (default base, ~74MB)")
    parser.add_argument("--out-dir", default=None,
                        help="Carpeta output (default: D:/Recursos Retrotarros/Drive/Studio/<slug>/teasers)")
    parser.add_argument("--title", default=None,
                        help="Título del episodio para overlay inferior (default: inferido de pauta MD)")
    parser.add_argument("--trivia", default=None,
                        help="Pregunta para la trivia card (default: inferida del slug)")
    args = parser.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        print(f"ERROR: no existe {video}")
        sys.exit(1)
    if not args.slug or not re.match(r"^[a-z0-9-]+$", args.slug):
        print("ERROR: --slug invalido (usá kebab-case: n64-top-mundial)")
        sys.exit(1)

    music = MUSIC_DIR / args.music
    if not music.exists():
        print(f"ERROR: no existe música {music}")
        print(f"   tracks disponibles en {MUSIC_DIR}:")
        for m in sorted(MUSIC_DIR.glob("*.wav"))[:10]:
            print(f"     - {m.name}")
        sys.exit(1)

    if not FONT_FILE.exists():
        print(f"ERROR: no existe la font {FONT_FILE}")
        sys.exit(1)

    ffmpeg = ensure_ffmpeg()

    out_dir = Path(args.out_dir) if args.out_dir else (DRIVE_STUDIO / args.slug / "teasers")
    out_dir.mkdir(parents=True, exist_ok=True)
    date_tag = date.today().strftime("%Y%m%d")
    output = out_dir / f"{args.slug}-teaser-{date_tag}.mp4"

    # Inferir title + trivia desde slug + pauta MD (a menos que se pasen por CLI)
    inferred_title, inferred_trivia = infer_title_and_trivia(args.slug)
    title = args.title if args.title else inferred_title
    trivia = args.trivia if args.trivia else inferred_trivia

    print(f"=== GENERATE TEASER ===")
    print(f"   video    : {video}")
    print(f"   slug     : {args.slug}")
    print(f"   título   : {title}")
    print(f"   trivia   : {trivia}")
    print(f"   música   : {music.name}")
    print(f"   modelo   : whisper-{args.model}")
    print(f"   output   : {output}")

    video_duration = get_duration(video)
    print(f"   duración : {video_duration:.1f}s ({video_duration/60:.1f} min)")

    with tempfile.TemporaryDirectory(prefix="teaser_") as tmp:
        tmp_dir = Path(tmp)

        # 1. Extract audio
        wav = tmp_dir / "audio.wav"
        step_extract_audio(video, wav, ffmpeg)

        # 2. Whisper
        segments = step_whisper_transcribe(wav, args.model)

        # 3-4. Highlights (necesitamos TOTAL_HIGHLIGHTS = 7 para 4 pre-trivia + 3 post-trivia)
        highlight_times = step_detect_highlights(segments, video_duration,
                                                  num_highlights=TOTAL_HIGHLIGHTS)

        # Si encontramos despedida ("esto fue retrotarros") la usamos como último
        # highlight, antes del outro card. Crea un cierre narrativo natural.
        print("\n[4b/10] Buscando despedida en el master...")
        farewell = find_farewell_segment(segments, video_duration)
        if farewell is not None:
            highlight_times[-1] = farewell
            print(f"   Reemplazo: highlight #{TOTAL_HIGHLIGHTS} ahora es la despedida @ {farewell:.1f}s")

        # 5. Cut clips (intro + 4H + trivia + 3H + outro = 10 clips)
        clip_paths, clip_plan = step_cut_clips(video, highlight_times, video_duration,
                                               trivia, tmp_dir, ffmpeg)

        # 6. Vertical
        vertical_paths = step_to_vertical(clip_paths, tmp_dir, ffmpeg)

        # 7. Concat
        concatenated = step_concat(vertical_paths, tmp_dir, ffmpeg)

        # 8. Overlays persistentes + título abajo. Calcular segundo donde
        # arranca la trivia card para ocultar overlays durante esos 3 seg.
        trivia_clip_idx = 1 + NUM_HIGHLIGHTS_PRE_TRIVIA  # 0=intro, 1..4=highlights, 5=trivia
        trivia_start_sec = trivia_clip_idx * CLIP_DURATION

        last_clip_source = clip_plan[-1][0]
        using_end_card = last_clip_source.name.endswith("outro.mp4")
        with_text = step_overlay_text(concatenated, tmp_dir, ffmpeg,
                                      title=title,
                                      trivia_start_sec=trivia_start_sec,
                                      include_outro_text=not using_end_card)

        # 9. Voice track (sincronizado con cada source clip del plan)
        with_text, voice = step_mix_audio(with_text, clip_plan, music, tmp_dir, ffmpeg)

        # 10. Render
        step_render_final(with_text, voice, music, output, ffmpeg)

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"\n=== LISTO ===")
    print(f"   Teaser: {output}")
    print(f"   Tamaño: {size_mb:.1f} MB")
    print(f"   Duración: {TEASER_DURATION:.0f}s")
    print(f"\n   Subí a TikTok / Reels / Shorts desde el celular.")


if __name__ == "__main__":
    main()
