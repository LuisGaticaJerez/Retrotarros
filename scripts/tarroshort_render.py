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
TAIL_PAD = 0.3         # colita despues de la voz para que no quede seca
MIN_SCENE = 3.8        # piso por escena: ritmo parejo, ningun item pasa volando


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
    total = round(max(dur + TAIL_PAD, MIN_SCENE), 2)
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
    studio = repo / "studio"
    # Blindaje anti-footgun: el slug de un short SIEMPRE es 'tarroshort-<nombre>'.
    # Si llega el slug pelado (ej. 'n64-top-mundial') y existe el short
    # correspondiente, auto-corregimos para no renderizar el deck del episodio
    # (16:9 horizontal) por error.
    if not slug.startswith("tarroshort-") and (studio / f"tarroshort-{slug}.html").exists():
        slug = f"tarroshort-{slug}"
    html_path = studio / f"{slug}.html"
    if not html_path.exists():
        raise FileNotFoundError(f"No existe el HTML del short: {html_path}")
    # Verificar que el HTML sea efectivamente un short vertical (template TarroShort),
    # no el deck horizontal del episodio. 'item-photo' es exclusivo del short.
    if "item-photo" not in html_path.read_text(encoding="utf-8", errors="ignore"):
        raise ValueError(
            f"'{html_path.name}' no parece un short vertical TarroShort. "
            f"Usa el slug con prefijo (tarroshort-<nombre>) o arma el short primero "
            f"con construir_desde_pauta / construir_short_highlights.")
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

        # FASE B · voces. El nombre incluye un HASH del texto+voz, asi que si el
        # texto de la escena cambia se regenera la voz (no reusa audio viejo de
        # otra version del short). Si el texto es identico, reusa (rapido).
        import hashlib
        voice_paths = []
        pending = []
        for i, txt in enumerate(texts):
            if not txt.strip():
                voice_paths.append(None)
                continue
            h = hashlib.md5(f"{txt}|{voice}|{pitch}|{rate}".encode("utf-8")).hexdigest()[:10]
            mp3 = audio_dir / f"scene-{i+1:02d}-{h}.mp3"
            if not mp3.exists():
                pending.append((txt, voice, pitch, rate, mp3))
            voice_paths.append(mp3)
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


def _detectar_formato(slug: str, titulo: str = "") -> str:
    """Infiere el formato del short. La convencion de nombres del canal manda:
    el SLUG es la senal autoritativa (no el titulo, que a veces queda mal copiado).
      - '...-precios'   -> precios
      - '...-coleccion' -> coleccion
      - '...-mundial'   -> calidad (los mejores juegos; convencion del canal)
    El titulo solo se usa de respaldo cuando el slug no trae ninguna senal
    explicita, para atrapar pautas con slugs poco convencionales."""
    s = slug.lower()
    # 1) Senales EXPLICITAS del slug (convencion del canal, no se sobrescriben)
    if "precio" in s:
        return "precios"
    if "coleccion" in s:
        return "coleccion"
    if "mundial" in s:
        return "calidad"  # 'mundial' = los mejores, NUNCA precios aunque el titulo confunda
    # 2) Slug sin senal -> usar el titulo como respaldo
    t = (titulo or "").lower()
    precio_signals = ("precio", "caro", "caros", "valioso", "valiosos",
                      "cotiza", "usd", "dolar", "subasta")
    if any(sig in t for sig in precio_signals):
        return "precios"
    if "coleccion" in t:
        return "coleccion"
    return "calidad"  # default: rankings de calidad (los mejores)


def _reaccion_llm(dato: dict, formato: str):
    """Genera una reaccion hablada (neutra, con tildes y comas) via Claude haiku.
    Para precios devuelve tambien el precio en formato 'USD N'. Devuelve dict o None."""
    import os as _os
    key = _os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
    except ImportError:
        return None
    tema = dato.get("tema", "")
    texto = dato.get("texto", "")
    campo_precio = ""
    if formato == "precios":
        campo_precio = ' "precio": "el precio en formato USD N (ej. USD 400), tomado del dato",'
    prompt = f"""Eres TarroBot, la mascota del canal de retrogaming Retrotarros.
Vas a comentar este item de un ranking para un short vertical de redes sociales.

ITEM: {tema}
DATO: {texto}

Escribe UNA reaccion hablada para que TarroBot la lea en voz alta.

Reglas ESTRICTAS:
- Espanol NEUTRO. Nada de jergas, chilenismos, voseo ni acento de ningun pais.
- USA tildes correctas y comas, para marcar las pausas naturales al hablar.
- Entre 8 y 14 palabras. Una o dos frases cortas, con ritmo agil.
- Reacciona o interpreta el dato (sorpresa, gancho, dato curioso), NO lo leas literal.
- Sin emojis, sin hashtags, sin comillas dentro del texto.

Devuelve SOLO un JSON sin markdown:
{{"reaccion": "...",{campo_precio} }}"""
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=220,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        return json.loads(m.group(0))
    except Exception as e:
        print(f"[tarroshort] LLM reaccion fallo para '{tema}': {e}")
        return None


def _asegurar_reacciones(pauta_path: Path, data: dict, indices: list, formato: str, progress=None) -> bool:
    """Para cada indice, asegura dato['reaccion_short'] (y 'precio_short' si precios).
    Genera lo que falte via LLM y GUARDA la pauta (respeta lo ya editado a mano).
    Devuelve True si guardo cambios."""
    datos = data["datos"]
    cambios = False
    for idx in indices:
        d = datos[idx]
        falta_reaccion = not (d.get("reaccion_short") or "").strip()
        falta_precio = formato == "precios" and not (d.get("precio_short") or "").strip()
        if not (falta_reaccion or falta_precio):
            continue
        if progress:
            progress(f"reaccion LLM: {d.get('tema','item')}")
        res = _reaccion_llm(d, formato)
        if not res:
            # fallback: primera frase recortada (sin LLM)
            if falta_reaccion:
                d["reaccion_short"] = _primera_frase(d.get("texto", ""), max_len=120)
                cambios = True
            continue
        if falta_reaccion and res.get("reaccion"):
            d["reaccion_short"] = str(res["reaccion"]).strip()
            cambios = True
        if falta_precio and res.get("precio"):
            d["precio_short"] = str(res["precio"]).strip()
            cambios = True
    if cambios:
        data["actualizado"] = data.get("actualizado", "")
        pauta_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if progress:
            progress("reacciones guardadas en la pauta")
    return cambios


def construir_desde_pauta(pauta_slug: str, out_slug=None, formato=None,
                          mostrar: int = 5, progress=None) -> Path:
    """Arma studio/tarroshort-<slug>.html desde la pauta JSON.
    - formato: 'calidad' / 'precios' / 'coleccion' (auto-detecta del slug si None).
    - mostrar: cuantos items muestra (default 5: del #10 al #6). El resto se teasea
      al final ('los primeros estan en el canal') para empujar trafico a YouTube.
    Genera/usa reacciones LLM (neutras, con tildes) guardadas en la pauta."""
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
    formato = formato or _detectar_formato(pauta_slug, episodio)
    img_dir = f"img/{out_slug}"

    # Los rankings del canal SIEMPRE empiezan en el #10 (regla fija), sin importar
    # cuantos 'datos' tenga la pauta (a veces trae melodias extra al final). El tope
    # se puede sobrescribir por pauta con el campo 'top'.
    rank_top = int(data.get("top") or 10)
    # datos[0] = #rank_top, datos[1] = #(rank_top-1), ... Mostramos los primeros
    # 'mostrar' (los puestos mas altos en numero: #10, #9, ...) y dejamos el resto
    # como gancho para el canal.
    mostrar = max(1, min(mostrar, rank_top, len(datos)))
    indices = list(range(mostrar))
    teaser_n = rank_top - mostrar  # cuantos puestos quedan para el canal (#5..#1)

    # Reacciones LLM (neutras, con tildes) + precio si aplica, guardadas en la pauta
    _asegurar_reacciones(pauta_path, data, indices, formato, progress=progress)
    datos = data["datos"]  # refrescar por si se enriquecio

    template = template_path.read_text(encoding="utf-8")
    head, _, rest = template.partition('<div class="deck" id="deck">')
    nav_idx = rest.find('<nav class="footer">')
    foot = rest[nav_idx:]

    slides = []

    # INTRO (saludo neutro, con tildes/comas para que TarroBot pause bien)
    titulo = _esc(episodio.upper())
    saludo = (f"Soy TarroBot, de Retrotarros. Hoy vemos {_esc(episodio)}, "
              f"desde el número {rank_top}.")
    slides.append(
        '  <section class="slide active intro">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        '    <div class="pre">RETROTARROS</div>\n'
        f'    <div class="titulo">{titulo}</div>\n'
        f'    <div class="saludo">{saludo}</div>\n'
        '  </section>'
    )

    # ITEMS mostrados (del #10 hacia abajo en numero, segun 'mostrar')
    for i in indices:
        d = datos[i]
        rank = rank_top - i
        name = _esc((d.get("tema") or "").upper())
        partes = [str(d.get("consola") or ""), str(d.get("ano") or ""), str(d.get("editor") or "")]
        meta = _esc(" · ".join([p for p in partes if p]))
        reaccion = _esc((d.get("reaccion_short") or _primera_frase(d.get("texto", ""), 120)))
        photo = f"{img_dir}/{_slugify(d.get('tema', f'item-{rank}'))}.jpg"
        price_html = ""
        if formato == "precios":
            precio = _esc((d.get("precio_short") or "").strip()) or "[precio]"
            price_html = f'    <div class="item-price">{precio}</div>\n'
        slides.append(
            '  <section class="slide item">\n'
            '    <div class="item-top">\n'
            '      <div class="tb-mini"><svg class="tb-mascot"><use href="#tarrobot-mascot"/></svg></div>\n'
            f'      <div class="rank-badge"><span class="hash">#</span>{rank}</div>\n'
            '    </div>\n'
            '    <div class="item-photo">\n'
            f'      <img src="{photo}" alt="" onerror="this.style.display=\'none\'">\n'
            '    </div>\n'
            f'    <div class="item-name">{name}</div>\n'
            f'    <div class="item-meta">{meta}</div>\n'
            f'{price_html}'
            f'    <div class="item-line">{reaccion}</div>\n'
            '  </section>'
        )

    # CIERRE / CLIFFHANGER: si quedaron puestos sin mostrar, los teaseamos al canal
    if teaser_n > 0:
        cta_sub = (f"¿Quieres conocer el top {teaser_n}? Descúbrelo completo en el canal.")
        cta_titulo = f'EL TOP {teaser_n},<br><span class="mg">EN EL CANAL</span>'
    else:
        cta_sub = "El ranking completo esta en el canal. Comenta cual te sorprendio y sigue para mas retro."
        cta_titulo = 'SIGUE A <span class="mg">RETROTARROS</span>'
    slides.append(
        '  <section class="slide cierre">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        f'    <div class="cta">{cta_titulo}</div>\n'
        f'    <div class="sub">{cta_sub}</div>\n'
        '  </section>'
    )

    deck = '<div class="deck" id="deck">\n\n' + "\n\n".join(slides) + "\n\n</div>\n\n"
    html = head + deck + foot

    out_path = repo / "studio" / f"tarroshort-{out_slug}.html"
    out_path.write_text(html, encoding="utf-8")
    msg = f"HTML armado ({formato}): {mostrar} items mostrados, {teaser_n} al canal"
    if progress:
        progress(msg)
    print(f"[tarroshort] {msg} -> {out_path}")
    if formato == "precios":
        print(f"[tarroshort] Revisa precios/fotos: precio_short en la pauta + fotos en studio/{img_dir}/")
    else:
        print(f"[tarroshort] Agrega fotos en studio/{img_dir}/ si quieres (sino, fallback al nombre).")
    return out_path


# ───────────── formato HIGHLIGHTS (coleccion / entrevista) ───────────────────
def _extraer_highlights(html_path: Path, formato: str, max_items: int):
    """Saca los destacados/joyas del HTML del episodio via Playwright.
    coleccion -> .tv-namebox .tv-title ; entrevista -> .joya-name.
    Devuelve (portada, [nombres], tag)."""
    from playwright.sync_api import sync_playwright
    sel = ".joya-name" if formato == "entrevista" else ".tv-namebox .tv-title"
    tag = "JOYA" if formato == "entrevista" else "DESTACADO"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.as_uri(), wait_until="domcontentloaded")
        names = pg.evaluate(f"Array.from(document.querySelectorAll('{sel}')).map(e=>e.textContent.trim())")
        portada = pg.evaluate("((document.querySelector('.ep-title')||{}).textContent||'').trim() "
                              "|| ((document.querySelector('.nombre')||{}).textContent||'').trim()")
        b.close()
    seen, out = set(), []
    for nm in names:
        if not nm or nm.startswith("[") or nm in seen:
            continue
        seen.add(nm)
        out.append(nm)
    return (portada or "").strip(), out[:max_items], tag


def _asegurar_reacciones_highlights(out_slug: str, names: list, formato: str, portada: str, progress=None) -> dict:
    """Reacciones LLM por pieza, cacheadas en studio/shorts/highlights/<slug>.json
    (editables; no se regeneran). Devuelve dict {nombre: reaccion}."""
    repo = _resolve_repo()
    side_dir = repo / "studio" / "shorts" / "highlights"
    side_dir.mkdir(parents=True, exist_ok=True)
    sidecar = side_dir / f"{out_slug}.json"
    cache = {}
    if sidecar.exists():
        try:
            cache = json.loads(sidecar.read_text(encoding="utf-8"))
        except Exception:
            cache = {}
    changed = False
    for nm in names:
        if (cache.get(nm) or "").strip():
            continue
        if formato == "entrevista":
            ctx = f"{nm}, una joya de la coleccion del invitado, con valor sentimental y nostalgia."
        else:
            ctx = f"{nm}, una pieza destacada de la coleccion {portada}."
        if progress:
            progress(f"reaccion LLM: {nm}")
        res = _reaccion_llm({"tema": nm, "texto": ctx}, "calidad")
        cache[nm] = ((res or {}).get("reaccion") or "").strip() or nm.title()
        changed = True
    if changed:
        sidecar.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        if progress:
            progress("reacciones guardadas")
    return cache


def construir_short_highlights(source_slug: str, formato: str, out_slug=None,
                               max_items: int = 6, progress=None) -> Path:
    """Arma un short de highlights (coleccion/entrevista) leyendo los destacados/joyas
    del HTML del episodio studio/<source_slug>.html. Reusa las imagenes del episodio."""
    repo = _resolve_repo()
    html_src = repo / "studio" / f"{source_slug}.html"
    if not html_src.exists():
        raise FileNotFoundError(f"No existe el episodio: {html_src}")
    template_path = repo / "studio" / "_template-tarroshort.html"
    if not template_path.exists():
        raise FileNotFoundError(f"No existe el template: {template_path}")
    out_slug = out_slug or source_slug

    portada, names, tag = _extraer_highlights(html_src, formato, max_items)
    if not names:
        raise ValueError(f"No encontre destacados/joyas en {source_slug} (formato {formato}).")
    cache = _asegurar_reacciones_highlights(out_slug, names, formato, portada, progress=progress)
    img_dir = f"img/{source_slug}"  # reusa el arte del episodio

    template = template_path.read_text(encoding="utf-8")
    head, _, rest = template.partition('<div class="deck" id="deck">')
    foot = rest[rest.find('<nav class="footer">'):]

    titulo = _esc((portada or source_slug.replace("-", " ")).upper())
    if formato == "entrevista":
        saludo = f"Soy TarroBot, de Retrotarros. Estas son las joyas de {_esc(portada)}."
        cta_sub = "La entrevista completa esta en el canal. Busca Retrotarros en YouTube."
        cta_titulo = 'LA ENTREVISTA COMPLETA,<br><span class="mg">EN EL CANAL</span>'
    else:
        saludo = f"Soy TarroBot, de Retrotarros. Estos son los destacados de {_esc(portada)}."
        cta_sub = "La coleccion completa esta en el canal. Busca Retrotarros en YouTube."
        cta_titulo = 'LA COLECCION COMPLETA,<br><span class="mg">EN EL CANAL</span>'

    slides = [
        '  <section class="slide active intro">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        '    <div class="pre">RETROTARROS</div>\n'
        f'    <div class="titulo">{titulo}</div>\n'
        f'    <div class="saludo">{saludo}</div>\n'
        '  </section>'
    ]
    for nm in names:
        reaccion = _esc((cache.get(nm) or nm))
        name_up = _esc(nm.upper())
        photo = f"{img_dir}/{_slugify(nm)}.jpg"
        slides.append(
            '  <section class="slide item">\n'
            '    <div class="item-top">\n'
            '      <div class="tb-mini"><svg class="tb-mascot"><use href="#tarrobot-mascot"/></svg></div>\n'
            f'      <div class="item-tag">{tag}</div>\n'
            '    </div>\n'
            '    <div class="item-photo">\n'
            f'      <img src="{photo}" alt="" onerror="this.style.display=\'none\'">\n'
            '    </div>\n'
            f'    <div class="item-name">{name_up}</div>\n'
            f'    <div class="item-line">{reaccion}</div>\n'
            '  </section>'
        )
    slides.append(
        '  <section class="slide cierre">\n'
        '    <svg class="tb-big"><use href="#tarrobot-mascot"/></svg>\n'
        f'    <div class="cta">{cta_titulo}</div>\n'
        f'    <div class="sub">{cta_sub}</div>\n'
        '  </section>'
    )

    deck = '<div class="deck" id="deck">\n\n' + "\n\n".join(slides) + "\n\n</div>\n\n"
    out_path = repo / "studio" / f"tarroshort-{out_slug}.html"
    out_path.write_text(head + deck + foot, encoding="utf-8")
    msg = f"HTML highlights ({formato}): {len(names)} piezas de {source_slug}"
    if progress:
        progress(msg)
    print(f"[tarroshort] {msg} -> {out_path}")
    print(f"[tarroshort] Reacciones editables en studio/shorts/highlights/{out_slug}.json · fotos en studio/{img_dir}/")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Genera un MP4 vertical de TarroShort (TarroBot leyendo).")
    ap.add_argument("slug", nargs="?", help="Slug del HTML en studio/ a renderizar (ej. tarroshort-snes-top-precios)")
    ap.add_argument("--from-pauta", metavar="PAUTA_SLUG", help="Arma el HTML del short desde studio/pautas/<PAUTA_SLUG>.tarrobot.json (rankings)")
    ap.add_argument("--from-episodio", metavar="SLUG", help="Arma un short de highlights desde studio/<SLUG>.html (coleccion/entrevista)")
    ap.add_argument("--formato", choices=["calidad", "precios", "coleccion", "entrevista"], help="Forzar formato (auto-detecta del slug si no)")
    ap.add_argument("--render", action="store_true", help="Tras armar, renderiza tambien el MP4")
    ap.add_argument("--voice", default=VOZ_DEFAULT)
    ap.add_argument("--pitch", default=PITCH_DEFAULT)
    ap.add_argument("--rate", default=RATE_DEFAULT)
    ap.add_argument("--out", default=None, help="Ruta de salida MP4 (default studio/shorts/<slug>.mp4)")
    args = ap.parse_args()
    try:
        if args.from_episodio:
            formato = args.formato or _detectar_formato(args.from_episodio)
            if formato not in ("coleccion", "entrevista"):
                # heuristica: si el slug arranca con 'abriendo-el-tarro' es entrevista
                formato = "entrevista" if "abriendo-el-tarro" in args.from_episodio else "coleccion"
            out_html = construir_short_highlights(args.from_episodio, formato)
            render_slug = out_html.stem
            if args.render:
                out = generar_tarroshort(render_slug, args.voice, args.pitch, args.rate, args.out)
                print(f"OK: {out}")
            else:
                print(f"OK: {out_html}")
                print(f"Revisa reacciones/fotos y luego: python scripts/tarroshort_render.py {render_slug}")
            return
        if args.from_pauta:
            out_html = construir_desde_pauta(args.from_pauta, formato=args.formato)
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
