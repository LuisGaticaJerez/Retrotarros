"""
tarroshort_render.py
=====================
Genera un MP4 vertical (1080x1920) de un TarroShort para redes: TarroBot presenta
y comenta cada item, con su cara MOVIENDOSE al hablar. Tu solo le pones musica y
ajustes finales en CapCut.

Pipeline (por escena del HTML):
  A. Playwright abre la escena con TarroBot "hablando" (clase tb-talking: boca +
     bob animados por CSS) y graba un clip corto de video (sin audio).
  B. edge-tts genera la voz de TarroBot (Catalina) desde el texto hablado de la
     escena (.saludo / .item-line / .sub). Si ya existe un MP3 propio, lo respeta.
  C. ffmpeg: recorta un loop limpio del clip, lo repite hasta la duracion de la
     voz, y mezcla video + voz -> escena MP4 (h264, yuv420p, 30fps).
  D. ffmpeg: concatena todas las escenas -> studio/shorts/<slug>.mp4

Uso CLI:
  python scripts/tarroshort_render.py tarroshort-snes-top-precios
  python scripts/tarroshort_render.py _template-tarroshort        (para probar)

Requisitos: playwright (+chromium), edge-tts, mutagen, ffmpeg.
La voz por escena queda en studio/shorts/audio/<slug>/scene-NN.mp3 (editable:
reemplaza el MP3 y vuelve a correr para usar tu propia narracion).
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Voz TarroBot (igual que tarrobot.py)
VOZ_DEFAULT = "es-CL-CatalinaNeural"
PITCH_DEFAULT = "+12Hz"
RATE_DEFAULT = "+0%"

# Parametros de video
W, H, FPS = 1080, 1920, 30
REC_SECONDS = 4.5      # cuanto grabamos del loop crudo (suficiente para 2-3 ciclos)
LOOP_TRIM_START = 1.0  # descartamos el arranque (navegacion + fuentes + settle)
LOOP_LEN = 3.0         # largo del loop limpio que se repite
TAIL_PAD = 0.6         # colita despues de la voz para que no quede seca


def _resolve_repo() -> Path:
    env = os.environ.get("RETROTARROS_REPO")
    if env and (Path(env) / "studio").exists():
        return Path(env)
    return Path(__file__).resolve().parent.parent


def _resolve_ffmpeg() -> str:
    env = os.environ.get("RETROTARROS_FFMPEG")
    if env and Path(env).exists():
        return env
    repo = _resolve_repo()
    local = repo / "installers" / "tarrobot-studio" / "bin" / "ffmpeg.exe"
    if local.exists():
        return str(local)
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError("ffmpeg no encontrado (ni en bin/, ni en PATH, ni RETROTARROS_FFMPEG).")


def _run(cmd):
    """Corre ffmpeg silencioso, lanza si falla."""
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError("ffmpeg fallo:\n" + res.stderr.decode("utf-8", "replace")[-1500:])


def _audio_dur(path: Path) -> float:
    from mutagen import File as MutaFile
    mf = MutaFile(str(path))
    if mf is not None and mf.info is not None:
        return float(mf.info.length)
    return 0.0


# ───────────────────────── FASE A · render de clips crudos ────────────────────
def _render_raw_clips(html_path: Path, work_dir: Path, progress=None):
    """Devuelve (lista_de_webm, lista_de_textos) por escena."""
    from playwright.sync_api import sync_playwright
    url = html_path.as_uri()
    clips, texts = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # contar escenas
        probe = browser.new_context(viewport={"width": W, "height": H})
        pp = probe.new_page()
        pp.goto(url, wait_until="networkidle")
        n = pp.evaluate("document.querySelectorAll('.slide').length")
        probe.close()

        for i in range(n):
            if progress:
                progress(f"grabando escena {i+1}/{n}")
            vdir = work_dir / f"raw{i:02d}"
            vdir.mkdir(parents=True, exist_ok=True)
            ctx = browser.new_context(
                viewport={"width": W, "height": H},
                device_scale_factor=1,
                record_video_dir=str(vdir),
                record_video_size={"width": W, "height": H},
            )
            page = ctx.new_page()
            page.goto(url, wait_until="networkidle")
            page.wait_for_function("document.fonts.ready")
            page.evaluate("(i) => go(i)", i)
            page.evaluate("const nv=document.querySelector('nav'); if(nv) nv.style.display='none';")
            page.evaluate("document.body.classList.add('tb-talking')")
            txt = page.evaluate(
                "(i) => { const s=document.querySelectorAll('.slide')[i];"
                " if(!s) return ''; const el=s.querySelector('.saludo, .item-line, .sub');"
                " return el ? el.textContent.trim() : ''; }",
                i,
            )
            texts.append(txt or "")
            page.wait_for_timeout(int(REC_SECONDS * 1000))
            vpath = page.video.path()
            ctx.close()  # finaliza el webm
            clips.append(Path(vpath))
        browser.close()
    return clips, texts


# ───────────────────────── FASE B · voz por escena (edge-tts) ─────────────────
async def _gen_voice(text: str, voice: str, pitch: str, rate: str, out: Path):
    import edge_tts
    com = edge_tts.Communicate(text, voice=voice, pitch=pitch, rate=rate)
    await com.save(str(out))


async def _gen_all_voices(jobs):
    # jobs: lista de (text, out_path); solo los que faltan
    await asyncio.gather(*[_gen_voice(t, v, p, r, o) for (t, v, p, r, o) in jobs])


# ───────────────────────── FASE C · escena MP4 (video+voz) ────────────────────
def _build_scene(ffmpeg: str, raw_webm: Path, voice_mp3, dur: float, out_mp4: Path, tmp: Path):
    loop_mp4 = tmp / (out_mp4.stem + "_loop.mp4")
    # 1) loop limpio: descartar arranque + tomar LOOP_LEN seg, sin audio
    _run([
        ffmpeg, "-y", "-ss", str(LOOP_TRIM_START), "-i", str(raw_webm),
        "-t", str(LOOP_LEN), "-an",
        "-vf", f"scale={W}:{H},setsar=1,fps={FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(loop_mp4),
    ])
    total = round(dur + TAIL_PAD, 2)
    if voice_mp3 is not None:
        # 2) repetir loop hasta total + pegar voz
        _run([
            ffmpeg, "-y", "-stream_loop", "-1", "-i", str(loop_mp4), "-i", str(voice_mp3),
            "-map", "0:v:0", "-map", "1:a:0", "-t", str(total),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            str(out_mp4),
        ])
    else:
        # escena sin texto: video + audio silencioso (para que el concat cuadre)
        _run([
            ffmpeg, "-y", "-stream_loop", "-1", "-i", str(loop_mp4),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-map", "0:v:0", "-map", "1:a:0", "-t", str(max(total, 2.5)),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k",
            str(out_mp4),
        ])


# ───────────────────────── orquestador ───────────────────────────────────────
def generar_tarroshort(slug: str, voice: str = VOZ_DEFAULT, pitch: str = PITCH_DEFAULT,
                       rate: str = RATE_DEFAULT, out_path=None, progress=None) -> Path:
    repo = _resolve_repo()
    html_path = repo / "studio" / f"{slug}.html"
    if not html_path.exists():
        raise FileNotFoundError(f"No existe el HTML del short: {html_path}")
    ffmpeg = _resolve_ffmpeg()

    shorts_dir = repo / "studio" / "shorts"
    audio_dir = shorts_dir / "audio" / slug
    audio_dir.mkdir(parents=True, exist_ok=True)
    shorts_dir.mkdir(parents=True, exist_ok=True)
    if out_path is None:
        out_path = shorts_dir / f"{slug}.mp4"
    out_path = Path(out_path)

    def _say(m):
        print(f"[tarroshort] {m}")
        if progress:
            progress(m)

    work = Path(tempfile.mkdtemp(prefix="tarroshort_"))
    try:
        # FASE A · clips crudos + textos
        _say("renderizando escenas (Playwright)...")
        raw_clips, texts = _render_raw_clips(html_path, work, progress)
        n = len(raw_clips)
        _say(f"{n} escenas detectadas")

        # FASE B · voces (solo las que faltan; respeta MP3 propios)
        voice_paths = []
        pending = []
        for i, txt in enumerate(texts):
            mp3 = audio_dir / f"scene-{i+1:02d}.mp3"
            if txt.strip() and not mp3.exists():
                pending.append((txt, voice, pitch, rate, mp3))
            voice_paths.append(mp3 if txt.strip() else None)
        if pending:
            _say(f"generando voz de {len(pending)} escenas (edge-tts)...")
            asyncio.run(_gen_all_voices(pending))

        # FASE C · escena MP4 por escena
        scene_mp4s = []
        for i in range(n):
            _say(f"armando clip {i+1}/{n}")
            vp = voice_paths[i]
            dur = _audio_dur(vp) if (vp and vp.exists()) else 0.0
            scene_out = work / f"scene-{i+1:02d}.mp4"
            _build_scene(ffmpeg, raw_clips[i], (vp if (vp and vp.exists()) else None),
                         dur, scene_out, work)
            scene_mp4s.append(scene_out)

        # FASE D · concat
        _say("concatenando escenas...")
        listfile = work / "concat.txt"
        listfile.write_text(
            "\n".join(f"file '{p.as_posix()}'" for p in scene_mp4s) + "\n",
            encoding="utf-8",
        )
        try:
            _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                  "-c", "copy", str(out_path)])
        except RuntimeError:
            # fallback: re-encode si el copy no cuadra
            _say("concat copy fallo, re-encodeando...")
            _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
                  "-c:a", "aac", "-b:a", "192k", str(out_path)])

        _say(f"LISTO -> {out_path}")
        return out_path
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ───────────────────────── builder desde pauta JSON ──────────────────────────
def _slugify(s: str) -> str:
    s = s.lower()
    repl = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n", "ü": "u"}
    for a, b in repl.items():
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _primera_frase(texto: str, max_len: int = 170) -> str:
    """Primera frase del texto (hook), para la linea breve del short."""
    t = (texto or "").strip()
    m = re.search(r"(.+?[.!?])(\s|$)", t)
    frase = m.group(1).strip() if m else t
    if len(frase) > max_len:
        frase = frase[:max_len].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return frase


def construir_desde_pauta(pauta_slug: str, out_slug=None, progress=None) -> Path:
    """Lee studio/pautas/<pauta_slug>.tarrobot.json y arma studio/tarroshort-<slug>.html
    clonando la estructura del template. Llena rank, nombre, meta y la linea breve.
    El precio (highlight) y las fotos los completa Luis."""
    repo = _resolve_repo()
    pauta_path = repo / "studio" / "pautas" / f"{pauta_slug}.tarrobot.json"
    if not pauta_path.exists():
        raise FileNotFoundError(f"No existe la pauta: {pauta_path}")
    template_path = repo / "studio" / "_template-tarroshort.html"
    if not template_path.exists():
        raise FileNotFoundError(f"No existe el template: {template_path}")

    data = json.loads(pauta_path.read_text(encoding="utf-8"))
    datos = data.get("datos", [])
    if not datos:
        raise ValueError("La pauta no tiene 'datos'.")
    out_slug = out_slug or pauta_slug
    episodio = data.get("episodio") or pauta_slug.replace("-", " ").title()
    img_dir = f"img/{out_slug}"

    template = template_path.read_text(encoding="utf-8")
    head, _, rest = template.partition('<div class="deck" id="deck">')
    nav_idx = rest.find('<nav class="footer">')
    foot = rest[nav_idx:]

    n = len(datos)
    slides = []

    # INTRO
    titulo = _esc(episodio.upper())
    saludo = ("Soy TarroBot. Trabajo con Koko y Luis en Retrotarros. "
              f"Hoy vamos a ver {_esc(episodio)}. Quedate hasta el final que el numero uno es una locura.")
    slides.append(
        '  <section class="slide active intro">\n'
        '    <span class="slide-num">01</span>\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        '    <div class="pre">RETROTARROS</div>\n'
        f'    <div class="titulo">{titulo}</div>\n'
        f'    <div class="saludo">{saludo}</div>\n'
        '  </section>'
    )

    # ITEMS (la pauta va del 10 al 1: datos[0] = puesto mas alto del numero)
    for i, d in enumerate(datos):
        rank = n - i
        num = i + 2
        name = _esc((d.get("tema") or "").upper())
        partes = [str(d.get("consola") or ""), str(d.get("ano") or ""), str(d.get("editor") or "")]
        meta = _esc(" · ".join([p for p in partes if p]))
        line = _esc(_primera_frase(d.get("texto", "")))
        photo = f"{img_dir}/{_slugify(d.get('tema', f'item-{rank}'))}.jpg"
        slides.append(
            '  <section class="slide item">\n'
            f'    <span class="slide-num">{num:02d}</span>\n'
            '    <div class="brand">RETROTARROS</div>\n'
            f'    <div class="rank-badge"><span class="hash">#</span>{rank}</div>\n'
            '    <div class="item-photo">\n'
            f'      <img src="{photo}" alt="" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">\n'
            f'      <div class="ph-fallback" style="display:none">{name}</div>\n'
            '    </div>\n'
            f'    <div class="item-name">{name}</div>\n'
            f'    <div class="item-meta">{meta}</div>\n'
            '    <div class="item-highlight">[precio / dato]</div>\n'
            f'    <div class="item-line">{line}</div>\n'
            '    <svg class="tb-corner"><use href="#tarrobot-mascot"/></svg>\n'
            '  </section>'
        )

    # CIERRE
    cierre_num = n + 2
    slides.append(
        '  <section class="slide cierre">\n'
        f'    <span class="slide-num">{cierre_num:02d}</span>\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        '    <div class="cta">SIGUE A <span class="mg">RETROTARROS</span></div>\n'
        '    <div class="sub">El ranking completo esta en el canal. Comenta cual te sorprendio y sigue para mas retro.</div>\n'
        '  </section>'
    )

    deck = '<div class="deck" id="deck">\n\n' + "\n\n".join(slides) + "\n\n</div>\n\n"
    html = head + deck + foot

    out_path = repo / "studio" / f"tarroshort-{out_slug}.html"
    out_path.write_text(html, encoding="utf-8")
    if progress:
        progress(f"HTML armado: {out_path} ({n} items)")
    print(f"[tarroshort] HTML armado desde pauta: {out_path}  ({n} items)")
    print(f"[tarroshort] Faltan: fotos en studio/{img_dir}/ y los precios ([precio / dato]).")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Genera un MP4 vertical de TarroShort (TarroBot leyendo).")
    ap.add_argument("slug", nargs="?", help="Slug del HTML en studio/ a renderizar (ej. tarroshort-snes-top-precios)")
    ap.add_argument("--from-pauta", metavar="PAUTA_SLUG", help="Arma el HTML del short desde studio/pautas/<PAUTA_SLUG>.tarrobot.json")
    ap.add_argument("--render", action="store_true", help="Tras --from-pauta, renderiza tambien el MP4")
    ap.add_argument("--voice", default=VOZ_DEFAULT)
    ap.add_argument("--pitch", default=PITCH_DEFAULT)
    ap.add_argument("--rate", default=RATE_DEFAULT)
    ap.add_argument("--out", default=None, help="Ruta de salida MP4 (default studio/shorts/<slug>.mp4)")
    args = ap.parse_args()
    try:
        if args.from_pauta:
            out_html = construir_desde_pauta(args.from_pauta)
            render_slug = out_html.stem  # tarroshort-<slug>
            if args.render:
                out = generar_tarroshort(render_slug, args.voice, args.pitch, args.rate, args.out)
                print(f"OK: {out}")
            else:
                print(f"OK: {out_html}")
                print("Agrega fotos + precios y luego corre:  "
                      f"python scripts/tarroshort_render.py {render_slug}")
            return
        if not args.slug:
            ap.error("falta el slug a renderizar, o usa --from-pauta")
        out = generar_tarroshort(args.slug, args.voice, args.pitch, args.rate, args.out)
        print(f"OK: {out}")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
