"""
tarroteaser.py — TarroTeaser

Activo oficial del proyecto Retrotarros. Genera un resumen CRUDO del episodio
para que Luis lo edite en DaVinci (agregar intro, outro, música, lower-thirds).

Selección automática:
  - 1 clip "inicio divertido" del primer tercio del video
  - N clips "centro" del medio del video (top score keywords)
  - 1 clip "clímax" según el TIPO de episodio (detectado del slug o forzado por --type)

Tipos soportados (auto-detectados del slug):
  ranking         → reveal del #1
  archivo         → valor total de la colección
  joyas           → joya principal
  top-precios     → el más caro
  hardware-raro   → hardware más raro
  no-latam        → exclusivo regional
  vs-mundo        → puntaje final
  generic         → despedida (Apóyenos, vemos, chao)

Output: MP4 vertical 1080x1920 con audio ORIGINAL del master.
SIN overlays, SIN intro/outro, SIN música agregada. Listo para edición manual.

Duración de clip: SE AJUSTA a la frase Whisper detectada (no es fija).
  - Lead-in 0.3s antes del segmento (no come la primera sílaba).
  - Tail-pad 0.7s después del segmento (cierra el número/palabra).
  - Si la frase Whisper queda mid-thought (sin '.', '!', '?'), encadena la
    siguiente frase contigua (hasta 2.5s extra · 3.5s en climax con precios).
  - Min 3s (--clip-duration), max 6s (--max-clip-duration).
  - Si excede max:
      · Centros/inicio: conserva el INICIO (donde está la keyword).
      · Climax: conserva el FINAL (donde está el reveal del #1).

Workflow esperado:
    1. python scripts/tarroteaser.py <master.mp4> --slug <slug>
    2. Importar el MP4 resultante en CapCut (o DaVinci)
    3. Aplicar "Voice Enhancement" / "Noise Reduction" sobre los clips para
       reducir la música de fondo del master (la app de edición lo hace mejor
       que separación AI standalone y sin dependencias extra).
    4. Agregar intro, outro, lower-thirds, etc.

Uso:
    python scripts/tarroteaser.py <video.mp4> --slug <slug>
    python scripts/tarroteaser.py <video.mp4> --slug n64-top-mundial --type ranking
    python scripts/tarroteaser.py <video.mp4> --slug psvita-archivo-koko

Defaults:
    --num-highlights 3
    --clip-duration 3.0
    --model small  (244MB, mejor accuracy chileno que base 74MB)
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

RECURSOS = Path("D:/Recursos Retrotarros")
REPO = RECURSOS / "repo"
DRIVE_STUDIO = RECURSOS / "Drive" / "Studio"
WHISPER_CACHE_DIR = REPO / ".cache" / "whisper"

# Output dimensions (TikTok / Reels / Shorts)
OUT_W = 1080
OUT_H = 1920

# Keywords para clasificar segmentos
KEYWORDS_FUNNY = [
    "jajaja", "ja ja", "no puede ser", "imposible",
    "no me digas", "wow", "increíble", "increible",
    "mira", "fíjate", "fijate", "qué loco", "que loco",
]
KEYWORDS_HIGHLIGHT = [
    # Precios y plata
    "dólares", "dolares", "dolar", "dólar", "mil", "lucas", "vale", "cuesta",
    "millón", "millon", "carísimo", "carisimo", "barato", "precio", "pagar",
    # Datos bomba
    "más caro", "mas caro", "más raro", "mas raro", "récord", "record",
    "increíble", "increible", "imposible", "primero", "último", "ultimo",
    "único", "unico", "spoiler",
    # Reacciones de cámara
    "qué", "que", "wow", "no puede", "no me", "mira",
    "atención", "atencion",
]
FAREWELL_KEYWORDS = [
    "esto fue retrotarros", "esto fue retro tarros", "fue retrotarros",
    "este fue el", "este fue",
    "apoyenos", "apóyenos",
    "suscribanse", "suscríbanse",
    "campanita",
    "chiquillos", "chiquíos", "chiquios",
    "nos vemos", " vemos", "vemos!",
    "hasta la proxima", "hasta la próxima",
    "chao", "chau",
]

# Keywords del clímax por TIPO de episodio.
# Cada tipo busca su frase canónica en el último tercio del video.
CLIMAX_KEYWORDS = {
    "ranking": [
        "número uno", "numero uno",
        "el primero", "primer puesto",
        "puesto número uno", "puesto numero uno", "puesto uno",
        "en el uno", "en el número uno",
        "número 1", "numero 1", "el número 1", "el numero 1",
    ],
    "archivo": [
        "valor total", "vale la colección", "vale la coleccion",
        "el total", "valor de la colección", "valor de la coleccion",
        "vale en total", "suma total", "todos juntos",
        "en plata", "en lucas", "en dólares", "en dolares",
    ],
    "joyas": [
        "la joya", "esta es la joya",
        "infravalorado", "infravalorada",
        "joya oculta", "joya escondida",
        "nadie conoce", "nadie habla",
        "el más subvalorado", "la más subvalorada",
    ],
    "top-precios": [
        "el más caro", "el mas caro", "la más cara", "la mas cara",
        "vale más", "vale mas",
        "valor récord", "valor record",
        "primer puesto en precio",
    ],
    "hardware-raro": [
        "más raro", "mas raro", "la más rara", "la mas rara",
        "única", "unica",
        "no se consigue", "imposible de conseguir",
    ],
    "no-latam": [
        "nunca llegó", "nunca llego", "nunca vino",
        "exclusivo", "solo en japón", "solo en japon",
        "no se vendió", "no se vendio",
    ],
    "vs-mundo": [
        "puntaje final", "ganó koko", "gano koko",
        "ganó el mundo", "gano el mundo",
        "scorecard", "puntos finales",
    ],
    "generic": [
        # Despedida típica (lo que antes era find_farewell)
        "esto fue retrotarros", "fue retrotarros",
        "este fue el", "apoyenos", "apóyenos",
        "suscribanse", "suscríbanse", "campanita",
        "chiquillos", "chiquíos", "nos vemos", " vemos",
        "hasta la proxima", "hasta la próxima", "chao", "chau",
    ],
}


def detect_episode_type(slug: str) -> str:
    """Mapea slug → tipo de episodio para elegir keywords del clímax."""
    s = slug.lower()
    # Orden importa: más específico primero
    if "vs-mundo" in s or "retrotarros-vs" in s:
        return "vs-mundo"
    if "top-precios" in s:
        return "top-precios"
    if "top-mundial" in s or "ranking" in s:
        return "ranking"
    if "archivo" in s:
        return "archivo"
    if "joyas" in s:
        return "joyas"
    if "hardware-raro" in s:
        return "hardware-raro"
    if "no-latam" in s:
        return "no-latam"
    return "generic"


# ============================================================================
# HELPERS (compartidos con generate-teaser.py)
# ============================================================================

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(str(c) for c in cmd[:4])}{'...' if len(cmd) > 4 else ''}")
    return subprocess.run(cmd, check=check, capture_output=False)


def ensure_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    winget_glob = list(Path(os.environ["LOCALAPPDATA"]).glob(
        "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_*/ffmpeg-*-full_build/bin/ffmpeg.exe"
    ))
    if winget_glob:
        return str(winget_glob[0])
    print("ERROR: ffmpeg no encontrado en PATH ni winget.")
    sys.exit(1)


def get_duration(video: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def _wav_hash(wav: Path) -> str:
    h = hashlib.md5()
    with open(wav, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def step_extract_audio(video: Path, out_wav: Path, ffmpeg: str) -> None:
    print("\n[1/5] Extrayendo audio para Whisper...")
    run([
        ffmpeg, "-y", "-i", str(video),
        "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        str(out_wav),
    ])


def step_whisper(wav: Path, model_name: str) -> list[dict]:
    """Whisper transcribe con cache (compatible con cache de generate-teaser.py)."""
    WHISPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n[2/5] Whisper transcribiendo (modelo={model_name})...")
    wav_h = _wav_hash(wav)
    cache_file = WHISPER_CACHE_DIR / f"{wav_h}_{model_name}.json"

    if cache_file.exists():
        with open(cache_file, encoding="utf-8") as f:
            segments = json.load(f)
        print(f"   [CACHE HIT] {cache_file.name} ({len(segments)} segmentos)")
        return segments

    print(f"   Cache miss, transcribiendo (5-10 min)...")
    import whisper  # type: ignore
    model = whisper.load_model(model_name)
    result = model.transcribe(str(wav), language="es", verbose=False)
    segments = result.get("segments", [])
    serializable = [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments]
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False)
    print(f"   {len(segments)} segmentos transcritos · cache guardado")
    return serializable


# ============================================================================
# DETECCIÓN DE MOMENTOS
# ============================================================================

def _score(text: str, keywords: list[str]) -> int:
    text_low = text.lower()
    return sum(1 for kw in keywords if kw in text_low)


def _extend_to_next_segment(seg: dict, all_segments: list[dict],
                             max_extra: float = 2.5) -> float:
    """Devuelve el end del segmento, extendido si la siguiente frase parece
    continuar el mismo pensamiento (p. ej. el numero esta partido entre 2 frases).

    Heuristica: si hay un segmento siguiente que arranca <= 0.5s despues del
    fin de este, y el texto actual termina mid-thought (sin punto/signo final),
    extender el clip hasta el end del siguiente. Cap a max_extra extra.
    """
    base_end = float(seg["end"])
    text = seg["text"].strip()
    # Si la frase ya cierra con punto/signo, no extender.
    if text and text[-1] in ".!?":
        return base_end
    # Buscar el siguiente segmento contiguo.
    seg_start = float(seg["start"])
    for s2 in all_segments:
        s2_start = float(s2["start"])
        if s2_start <= seg_start:
            continue
        if s2_start - base_end > 0.5:
            return base_end
        extra = min(max_extra, float(s2["end"]) - base_end)
        return base_end + max(0.0, extra)
    return base_end


def find_funny_start(segments: list[dict], video_duration: float) -> tuple[float, float, str]:
    """Mejor segmento del primer tercio del video. Mezcla keywords funny + highlight.

    Devuelve (start, end, text) — end ya viene extendido si la frase no cierra.
    """
    cutoff = video_duration / 3.0
    combined = KEYWORDS_FUNNY + KEYWORDS_HIGHLIGHT
    candidates = []
    for seg in segments:
        # Saltarse los primeros 15 seg (intro de cámara, presentación)
        if seg["start"] < 15 or seg["start"] >= cutoff:
            continue
        s = _score(seg["text"], combined)
        if s > 0:
            end_ext = _extend_to_next_segment(seg, segments)
            candidates.append((seg["start"], end_ext, s, seg["text"][:70]))
    if candidates:
        best = max(candidates, key=lambda x: (x[2], -x[0]))  # mejor score, después más temprano
        return best[0], best[1], best[3]
    # Fallback: segundo 60 (1 min) — sin segmento, devuelve start=end+3s para que cut use min duration
    return 60.0, 63.0, "(fallback, sin keywords detectadas)"


def find_center_highlights(segments: list[dict], video_duration: float,
                            n: int) -> list[tuple[float, float, str]]:
    """Top N segmentos por score entre 1/3 y 2/3 del video.

    Devuelve lista de (start, end, text). end viene extendido si la frase no cierra.
    """
    start_t = video_duration / 3.0
    end_t = video_duration * 2.0 / 3.0
    scored = []
    for seg in segments:
        if not (start_t <= seg["start"] < end_t):
            continue
        s = _score(seg["text"], KEYWORDS_HIGHLIGHT)
        if s > 0:
            end_ext = _extend_to_next_segment(seg, segments)
            scored.append((seg["start"], end_ext, s, seg["text"][:70]))
    scored.sort(key=lambda x: -x[2])

    # Tomar top N y ordenar cronológicamente
    top = sorted(scored[:n], key=lambda x: x[0])

    # Si no encontramos N, rellenar con puntos uniformes (start=fallback_t, end=fallback_t+3)
    while len(top) < n:
        step = (end_t - start_t) / (n + 1)
        fallback_t = start_t + step * (len(top) + 1)
        top.append((fallback_t, fallback_t + 3.0, 0, "(fallback)"))
        top.sort(key=lambda x: x[0])

    return [(t[0], t[1], t[3]) for t in top]


def find_farewell(segments: list[dict], video_duration: float) -> tuple[float, float, str]:
    """Detecta despedida ('vemos', 'apóyenos', 'chiquillos', etc) en últimos 90s."""
    cutoff = max(0.0, video_duration - 90.0)
    candidates = []
    for seg in segments:
        if seg["start"] < cutoff:
            continue
        text_low = seg["text"].lower()
        for kw in FAREWELL_KEYWORDS:
            if kw in text_low:
                end_ext = _extend_to_next_segment(seg, segments)
                candidates.append((seg["start"], end_ext, seg["text"][:70], kw))
                break
    if candidates:
        best = max(candidates, key=lambda x: x[0])
        return best[0], best[1], best[2]
    fallback_start = max(0.0, video_duration - 5.0)
    return fallback_start, min(video_duration, fallback_start + 3.0), "(fallback, sin keywords detectadas)"


def find_climax(segments: list[dict], video_duration: float,
                episode_type: str) -> tuple[float, float, str]:
    """Detecta el clímax del episodio según su tipo.

    Busca en el último tercio del video usando las keywords del tipo.
    Si no encuentra, fallback al tipo 'generic' (despedida).

    Devuelve (start, end, text). end viene extendido para no cortar reveals con numeros.
    """
    keywords = CLIMAX_KEYWORDS.get(episode_type, CLIMAX_KEYWORDS["generic"])

    # Para 'generic', buscar en los últimos 90 seg (es la despedida).
    # Para los demás tipos, buscar en el último tercio (es el reveal narrativo).
    if episode_type == "generic":
        cutoff_start = max(0.0, video_duration - 90.0)
        cutoff_end = video_duration
    else:
        cutoff_start = video_duration * 2.0 / 3.0
        cutoff_end = max(cutoff_start + 1, video_duration - 30.0)

    # Tipos con reveals numericos: dar mas margen de extension (precio o valor)
    PRICE_REVEAL_TYPES = {"top-precios", "archivo", "joyas", "ranking", "vs-mundo"}
    max_extra = 3.5 if episode_type in PRICE_REVEAL_TYPES else 2.5

    candidates = []
    for seg in segments:
        if not (cutoff_start <= seg["start"] < cutoff_end):
            continue
        text_low = seg["text"].lower()
        for kw in keywords:
            if kw in text_low:
                end_ext = _extend_to_next_segment(seg, segments, max_extra=max_extra)
                candidates.append((seg["start"], end_ext, seg["text"][:80], kw))
                break

    if candidates:
        if episode_type == "generic":
            # Despedida: el último match (más cerca del cierre)
            best = max(candidates, key=lambda x: x[0])
        else:
            # Reveal narrativo: el primer match en el último tercio
            best = min(candidates, key=lambda x: x[0])
        return best[0], best[1], best[2]

    # Sin match: intentar fallback al tipo 'generic' si no era genérico
    if episode_type != "generic":
        print(f"   No se detectó clímax tipo '{episode_type}', fallback a despedida")
        return find_climax(segments, video_duration, "generic")

    # Último fallback: últimos 5 seg del video
    fallback_start = max(0.0, video_duration - 5.0)
    return fallback_start, min(video_duration, fallback_start + 3.0), "(fallback final, sin keywords)"


# ============================================================================
# CUT + VERTICAL + CONCAT
# ============================================================================

def plan_clip_window(seg_start: float, seg_end: float, video_duration: float,
                      min_dur: float = 3.0, max_dur: float = 6.0,
                      lead_in: float = 0.3, tail_pad: float = 0.7,
                      prefer_end: bool = False) -> tuple[float, float]:
    """Calcula la ventana de corte para que NO se corte la frase.

    - Empieza un poco antes del segmento (lead_in) para no comer la primera silaba.
    - Termina despues del segmento (tail_pad) para que cierre el numero/palabra.
    - Si la duracion resultante es menor a min_dur, extiende por el final.
    - Si es mayor a max_dur:
        - prefer_end=True (climax): conserva el final (donde Koko revela el #1).
        - prefer_end=False (inicio/centros): conserva el inicio (donde Whisper detecto la keyword).
    """
    clip_start = max(0.0, seg_start - lead_in)
    clip_end = min(video_duration, seg_end + tail_pad)
    duration = clip_end - clip_start

    if duration < min_dur:
        clip_end = min(video_duration, clip_start + min_dur)
    elif duration > max_dur:
        if prefer_end:
            # Climax: preservar el final (reveal final)
            clip_start = max(0.0, clip_end - max_dur)
        else:
            # Inicio/centros: preservar el inicio (donde estaba la keyword)
            clip_end = min(video_duration, clip_start + max_dur)

    return clip_start, clip_end


def cut_and_verticalize(video: Path, start: float, end: float,
                         out: Path, ffmpeg: str) -> None:
    """Recorta y convierte directo a vertical 1080x1920 con blur background.
    Mantiene el audio original del master tal cual.

    start, end: tiempos absolutos en el video master (en segundos).
    """
    duration = end - start
    vertical_filter = (
        "[0:v]split=2[bg][fg];"
        f"[bg]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},boxblur=20:5[bgblur];"
        f"[fg]scale={OUT_W}:-1[fgscaled];"
        "[bgblur][fgscaled]overlay=(W-w)/2:(H-h)/2[vout]"
    )
    run([
        ffmpeg, "-y", "-ss", f"{start:.2f}", "-i", str(video),
        "-t", f"{duration:.2f}",
        "-filter_complex", vertical_filter,
        "-map", "[vout]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(out),
    ])


def concat_clips(clip_paths: list[Path], output: Path, tmp_dir: Path, ffmpeg: str) -> None:
    """Concatena los clips. Como todos son mismo codec/res, usamos concat demuxer (rápido)."""
    list_file = tmp_dir / "concat.txt"
    list_file.write_text(
        "\n".join(f"file '{p.as_posix()}'" for p in clip_paths),
        encoding="utf-8",
    )
    run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy",
        str(output),
    ])


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="TarroTeaser - genera teaser crudo para edición manual.")
    parser.add_argument("video", help="Ruta al video master (MP4)")
    parser.add_argument("--slug", required=True, help="Slug del episodio (ej. n64-top-mundial)")
    parser.add_argument("--type", dest="ep_type", default=None,
                        choices=list(CLIMAX_KEYWORDS.keys()),
                        help="Tipo de episodio (auto-detectado del slug si se omite)")
    parser.add_argument("--num-highlights", type=int, default=3,
                        help="Cantidad de clips del centro (default 3)")
    parser.add_argument("--clip-duration", type=float, default=3.0,
                        help="Duración MINIMA de cada clip en segundos (default 3.0). El "
                             "clip se extiende si la frase Whisper dura más, hasta el max.")
    parser.add_argument("--max-clip-duration", type=float, default=6.0,
                        help="Duración MAXIMA de cada clip en segundos (default 6.0). Evita "
                             "clips eternos si Whisper detecta segmentos largos.")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Modelo Whisper (default small - mejor accuracy chileno que base)")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    # Para limpiar la música del master: usar CapCut "Voice Enhance" /
    # "Noise Reduction" o DaVinci "Voice Isolation" sobre el MP4 importado.
    # Lo hacemos fuera del script (mejor calidad + menos infra).

    video = Path(args.video).resolve()
    if not video.exists():
        print(f"ERROR: no existe {video}")
        sys.exit(1)
    if not re.match(r"^[a-z0-9-]+$", args.slug):
        print("ERROR: --slug inválido (kebab-case)")
        sys.exit(1)

    ffmpeg = ensure_ffmpeg()
    duration = get_duration(video)

    # Detectar tipo de episodio (o usar el forzado por CLI)
    ep_type = args.ep_type if args.ep_type else detect_episode_type(args.slug)

    out_dir = Path(args.out_dir) if args.out_dir else (DRIVE_STUDIO / args.slug / "teasers")
    out_dir.mkdir(parents=True, exist_ok=True)
    date_tag = date.today().strftime("%Y%m%d")
    output = out_dir / f"{args.slug}-tarroteaser-{date_tag}.mp4"

    total_clips = 1 + args.num_highlights + 1

    print(f"=== TARROTEASER ===")
    print(f"   video    : {video}")
    print(f"   slug     : {args.slug}")
    print(f"   tipo     : {ep_type}{' (auto-detectado)' if not args.ep_type else ' (forzado)'}")
    print(f"   duración : {duration:.1f}s ({duration/60:.1f} min)")
    print(f"   clips    : 1 inicio + {args.num_highlights} centro + 1 clímax = {total_clips} clips")
    print(f"   por clip : min {args.clip_duration:.1f}s · max {args.max_clip_duration:.1f}s (se ajusta a frase Whisper)")
    print(f"   modelo   : whisper-{args.model}")
    print(f"   output   : {output}")

    with tempfile.TemporaryDirectory(prefix="highlights_") as tmp:
        tmp_dir = Path(tmp)

        # 1. Audio
        wav = tmp_dir / "audio.wav"
        step_extract_audio(video, wav, ffmpeg)

        # 2. Whisper (con cache)
        segments = step_whisper(wav, args.model)

        # 3. Detectar momentos
        print(f"\n[3/5] Detectando momentos...")
        funny_start, funny_end, funny_txt = find_funny_start(segments, duration)
        print(f"   INICIO @ {funny_start:.1f}-{funny_end:.1f}s ({funny_end-funny_start:.1f}s): \"{funny_txt}\"")

        centers = find_center_highlights(segments, duration, args.num_highlights)
        for i, (s_t, e_t, txt) in enumerate(centers):
            print(f"   CENTRO {i+1} @ {s_t:.1f}-{e_t:.1f}s ({e_t-s_t:.1f}s): \"{txt}\"")

        climax_start, climax_end, climax_txt = find_climax(segments, duration, ep_type)
        print(f"   CLIMAX ({ep_type}) @ {climax_start:.1f}-{climax_end:.1f}s ({climax_end-climax_start:.1f}s): \"{climax_txt}\"")

        # 4. Recortar + verticalizar
        # ranges con flag prefer_end: solo el climax preserva final (resto preserva inicio)
        all_ranges = (
            [(funny_start, funny_end, False)]
            + [(s, e, False) for s, e, _ in centers]
            + [(climax_start, climax_end, True)]
        )
        print(f"\n[4/5] Recortando y verticalizando {len(all_ranges)} clips...")
        clip_paths = []
        total_out_dur = 0.0
        for i, (seg_s, seg_e, prefer_end) in enumerate(all_ranges):
            # Planificar ventana: lead-in 0.3s + tail-pad 0.7s, ajustada a min/max
            clip_s, clip_e = plan_clip_window(
                seg_s, seg_e, duration,
                min_dur=args.clip_duration,
                max_dur=args.max_clip_duration,
                prefer_end=prefer_end,
            )
            print(f"   clip {i:02d}: {clip_s:.2f} -> {clip_e:.2f}s ({clip_e-clip_s:.2f}s)")
            out = tmp_dir / f"clip_{i:02d}.mp4"
            cut_and_verticalize(video, clip_s, clip_e, out, ffmpeg)
            clip_paths.append(out)
            total_out_dur += (clip_e - clip_s)

        # 5. Concat
        print(f"\n[5/5] Concatenando...")
        concat_clips(clip_paths, output, tmp_dir, ffmpeg)

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"\n=== LISTO ===")
    print(f"   Highlights crudos: {output}")
    print(f"   Tamaño: {size_mb:.1f} MB · {total_out_dur:.1f}s")
    print(f"   Audio: original del master · sin overlays · sin música agregada")
    print(f"   Importalo en DaVinci y agregale intro + outro + lower-thirds a tu gusto.")


if __name__ == "__main__":
    main()
