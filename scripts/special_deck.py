"""
special_deck.py - Retrotarros Studio Suite
Genera el deck de episodios ESPECIALES de fecha conmemorativa (formato piloto:
Top 10 Glorias Navales Retro, 21 de mayo 2026). Top 10 personajes/items con un
documento falso-oficial recurrente como gancho de humor (HOJA DE SERVICIOS en
el naval, FICHA CLINICA en el de gatos, etc -- parametrizable por episodio).

Clonado 1:1 del CSS/JS de studio/specials/retro-glorias-navales.html (hecho a
mano, sin generador, en la sesion original del 21 de mayo). Este generador
existe para que el SEGUNDO special (y los que vengan) no repitan HTML a mano
-- la nota final de esa pauta decia explicitamente "si funciona, se replica
con otras fechas".

Estructura fija:
  01 PORTADA     - tag fecha + titulo (con palabra destacada en magenta) + sub.
  02 INTRO       - divider: presenta el concepto del especial.
  03-12 ITEMS    - #10 -> #1, cada uno con box art + TarroVision vacio +
                   titulo/meta + bloque de "documento oficial" con humor.
                   Label del documento cambia por rango: doc_label (4-10),
                   doc_label_podio (2-3), doc_label_top (1).
  13 ANALISIS    - divider: cierre tematico del top.
  14 CIERRE      - divider: CTA suscripcion + adelanto del proximo episodio.

Box art en studio/specials/img/<slug>/<key>.jpg (mismo patron que glorias
navales). Salida en studio/specials/<slug>.html.
"""
from __future__ import annotations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
:root {
  --mg: #FF2E88; --cy: #00E5FF; --ye: #FFD23F; --pu: #2D1B69;
  --bo: #F5F0E8; --dk: #06030f; --card-bg: rgba(12, 6, 32, 0.92);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; overflow: hidden; background: var(--dk); font-family: 'Share Tech Mono', monospace; color: var(--bo); }
body {
  background-image:
    radial-gradient(ellipse 100% 50% at 50% -5%, rgba(255,46,136,.12) 0%, transparent 65%),
    repeating-linear-gradient(0deg, transparent 0px, transparent 39px, rgba(255,255,255,.014) 39px, rgba(255,255,255,.014) 40px),
    repeating-linear-gradient(90deg, transparent 0px, transparent 39px, rgba(255,255,255,.014) 39px, rgba(255,255,255,.014) 40px);
}
header { position: fixed; top: 0; left: 0; right: 0; height: 56px; z-index: 200; background: rgba(6, 3, 15, 0.97); border-bottom: 2px solid var(--mg); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; }
.hdr-logo { font-family: 'Orbitron'; font-weight: 900; font-size: 20px; color: var(--mg); text-shadow: 0 0 14px rgba(255,46,136,.6); letter-spacing: 3px; }
.hdr-tag { font-family: 'Share Tech Mono'; font-size: 12px; color: var(--ye); letter-spacing: 3px; }
.hdr-rec { display: flex; align-items: center; gap: 8px; font-family: 'Press Start 2P'; font-size: 8px; color: var(--mg); }
.dot { width: 10px; height: 10px; background: var(--mg); border-radius: 50%; animation: blink 1.2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.15} }
.deck { position: fixed; top: 56px; left: 0; right: 0; bottom: 64px; overflow: hidden; }
.slide { position: absolute; inset: 0; padding: 28px 44px; overflow: hidden; opacity: 0; pointer-events: none; transition: opacity .22s; }
.slide.active { opacity: 1; pointer-events: auto; }
.slide-num { position: absolute; top: 16px; right: 24px; font-family: 'Press Start 2P'; font-size: 9px; color: rgba(255,255,255,.22); letter-spacing: 2px; }
.portada { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; }
.portada .ep-tag { font-family: 'Press Start 2P'; font-size: 11px; color: var(--cy); letter-spacing: 5px; margin-bottom: 22px; }
.portada .ep-title { font-family: 'Orbitron'; font-weight: 900; font-size: 62px; letter-spacing: 1.5px; line-height: 1.05; color: #fff; margin-bottom: 18px; max-width: 1100px; }
.portada .ep-title .vs { color: var(--mg); text-shadow: 0 0 22px rgba(255,46,136,.55); }
.portada .ep-sub { font-family: 'Share Tech Mono'; font-size: 18px; color: var(--ye); letter-spacing: 4px; }
.divider { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%; }
.divider .pre { font-family: 'Press Start 2P'; font-size: 11px; letter-spacing: 6px; margin-bottom: 24px; }
.divider .pre.cy { color: var(--cy); } .divider .pre.mg { color: var(--mg); }
.divider .title { font-family: 'Orbitron'; font-weight: 900; font-size: 78px; letter-spacing: 2px; line-height: 1; color: #fff; margin-bottom: 22px; }
.divider .title.cy { color: var(--cy); text-shadow: 0 0 22px rgba(0,229,255,.5); }
.divider .title.mg { color: var(--mg); text-shadow: 0 0 22px rgba(255,46,136,.55); }
.divider .sub { font-family: 'Share Tech Mono'; font-size: 18px; color: rgba(255,255,255,.7); letter-spacing: 2px; max-width: 800px; line-height: 1.6; }

/* HIBRIDO */
.slide-hybrid { display: grid; grid-template-rows: auto 1fr auto auto; height: 100%; gap: 14px; max-width: 1400px; margin: 0 auto; }
.hybrid-head { display: flex; align-items: center; justify-content: space-between; }
.game-pos { font-family: 'Orbitron'; font-weight: 900; font-size: 64px; line-height: 1; letter-spacing: 1px; }
.game-pos.cy { color: var(--cy); text-shadow: 0 0 20px rgba(0,229,255,.55); }
.game-pos.mg { color: var(--mg); text-shadow: 0 0 20px rgba(255,46,136,.6); }
.game-pos .hash { font-size: 28px; color: rgba(255,255,255,.35); margin-right: 4px; }
.game-block-label { font-family: 'Press Start 2P'; font-size: 9px; letter-spacing: 3px; padding: 6px 12px; border: 1px solid; }
.game-block-label.cy { color: var(--cy); border-color: var(--cy); }
.game-block-label.mg { color: var(--mg); border-color: var(--mg); }
.hybrid-body { display: grid; grid-template-columns: 38% 1fr; gap: 32px; align-items: center; justify-items: center; min-height: 0; }
.cart-wrap { display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; min-height: 0; }
.cart { position: relative; width: min(100%, 380px); aspect-ratio: 5/4; max-height: 100%; background: linear-gradient(180deg, #1f1f24 0%, #0d0d12 100%); border-radius: 12px 12px 6px 6px; box-shadow: 0 0 0 2px rgba(255,255,255,.04), 0 18px 50px rgba(0,0,0,.6), inset 0 1px 0 rgba(255,255,255,.08); }
.cart::before { content: ""; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 78%; height: 14%; background: linear-gradient(180deg, #2a2a2f 0%, #1a1a1f 100%); border-radius: 0 0 6px 6px; box-shadow: inset 0 -1px 0 rgba(0,0,0,.6); z-index: 3; }
.cart-img-wrap { position: absolute; inset: 14% 10% 10%; border-radius: 4px; overflow: hidden; background: var(--label-1, #2D1B69); box-shadow: inset 0 0 0 3px rgba(255,255,255,.07), inset 0 0 0 6px rgba(0,0,0,.25), 0 4px 14px rgba(0,0,0,.4); }
.cart-img-wrap img { display: block; width: 100%; height: 100%; object-fit: contain; position: relative; z-index: 2; }
.cart-img-wrap img.cart-img-bg { object-fit: cover; filter: blur(22px) brightness(0.55) saturate(1.2); transform: scale(1.1); z-index: 1; position: absolute; inset: 0; }
.cart-fallback { position: absolute; inset: 0; z-index: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 18px; background: linear-gradient(135deg, var(--label-1, #2D1B69) 0%, var(--label-2, #4a2a99) 100%); text-align: center; }
.cart-fallback::after { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 22%; background: linear-gradient(180deg, rgba(255,255,255,.16) 0%, transparent 100%); pointer-events: none; }
.cart-fallback .title { font-family: 'Orbitron'; font-weight: 900; font-size: clamp(14px, 1.8vw, 22px); line-height: 1.05; color: #fff; letter-spacing: .5px; text-shadow: 0 2px 4px rgba(0,0,0,.5); z-index: 2; }
.cart-fallback .sub { font-family: 'Press Start 2P'; font-size: 8px; letter-spacing: 2px; color: rgba(255,255,255,.7); margin-top: 8px; z-index: 2; }
.cart-console { position: absolute; bottom: 6px; left: 50%; transform: translateX(-50%); font-family: 'Press Start 2P'; font-size: 7px; letter-spacing: 3px; color: rgba(255,255,255,.22); z-index: 4; }
.lb-default { --label-1:#2D1B69; --label-2:#4a2a99; }
{PALETA}

.tv-wrap { display: flex; align-items: center; justify-content: center; height: 100%; width: 100%; min-height: 0; container-type: size; }
.tarrovision { width: min(100cqh, 100cqw); height: min(100cqh, 100cqw); max-width: 100%; max-height: 100%; background: linear-gradient(180deg, #1a1a1f 0%, #0d0d12 100%); border-radius: 22px; padding: 18px 22px; box-shadow: 0 0 0 2px rgba(255,255,255,.04), 0 18px 50px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.08), inset 0 -2px 0 rgba(0,0,0,.4); display: grid; grid-template-rows: auto 1fr auto; gap: 10px; }
.tv-controls-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 0 4px; }
.tv-led { width: 9px; height: 9px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ff8fb8 0%, var(--mg) 60%, #7a0030 100%); box-shadow: 0 0 10px rgba(255,46,136,.8), inset 0 0 2px rgba(0,0,0,.5); }
.tv-brand { flex: 1; text-align: center; font-family: 'Press Start 2P'; font-size: 10px; color: var(--ye); letter-spacing: 3px; text-shadow: 0 0 8px rgba(255,210,63,.4); }
.tv-channel { font-family: 'Share Tech Mono'; font-size: 11px; color: var(--cy); letter-spacing: 2px; padding: 3px 9px; border: 1px solid rgba(0,229,255,.4); background: rgba(0,229,255,.06); }
.tv-screen { position: relative; background: #2a2a2f; border-radius: 12px; padding: 14px; box-shadow: inset 0 0 0 2px #3a3a3f, inset 0 0 14px rgba(0,0,0,.6); min-height: 0; }
.tv-screen-inner { position: relative; width: 100%; height: 100%; background: #000; border-radius: 16px / 8px; overflow: hidden; box-shadow: inset 0 0 0 1px rgba(255,255,255,.05), inset 0 0 40px rgba(0,0,0,.95); }
.tv-screen-inner img, .tv-screen-inner video { display: block; width: 100%; height: 100%; object-fit: cover; }
.tv-screen-inner::before { content: ""; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(0,0,0,0) 0px, rgba(0,0,0,0) 2px, rgba(0,0,0,.18) 2px, rgba(0,0,0,.18) 3px); z-index: 3; mix-blend-mode: multiply; }
.tv-screen-inner::after { content: ""; position: absolute; inset: 0; pointer-events: none; background: radial-gradient(ellipse 110% 70% at 50% 0%, rgba(255,255,255,.08) 0%, transparent 55%), radial-gradient(ellipse 90% 50% at 50% 100%, rgba(0,229,255,.06) 0%, transparent 60%); z-index: 4; }
.tv-noscreen { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(circle at 50% 50%, rgba(45,27,105,.6) 0%, #000 80%), repeating-linear-gradient(0deg, #0a0a14 0px, #0a0a14 1px, #14142a 1px, #14142a 2px); color: rgba(255,255,255,.35); text-align: center; padding: 24px; z-index: 2; }
.tv-noscreen .tv-noscreen-big { font-family: 'Press Start 2P'; font-size: 14px; color: var(--mg); letter-spacing: 3px; margin-bottom: 10px; text-shadow: 0 0 12px rgba(255,46,136,.5); }
.tv-noscreen .tv-noscreen-sub { font-family: 'Share Tech Mono'; font-size: 11px; letter-spacing: 2px; color: rgba(0,229,255,.55); }
.tv-controls-bottom { display: grid; grid-template-columns: auto auto 1fr; align-items: center; gap: 12px; padding: 2px 4px 0; }
.tv-knob { width: 28px; height: 28px; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #5a5a60 0%, #2a2a30 60%, #0a0a0e 100%); box-shadow: inset 0 1px 0 rgba(255,255,255,.15), inset 0 -2px 0 rgba(0,0,0,.4), 0 2px 4px rgba(0,0,0,.6); position: relative; }
.tv-knob::after { content: ""; position: absolute; top: 5px; left: 50%; width: 2px; height: 9px; background: var(--ye); transform-origin: bottom center; transform: translateX(-50%) rotate(45deg); box-shadow: 0 0 4px rgba(255,210,63,.6); }
.tv-knob.cy::after { background: var(--cy); box-shadow: 0 0 4px rgba(0,229,255,.6); transform: translateX(-50%) rotate(-30deg); }
.tv-speaker { height: 22px; background: repeating-linear-gradient(90deg, #0a0a0e 0px, #0a0a0e 3px, #1a1a1f 3px, #1a1a1f 6px); border-radius: 4px; box-shadow: inset 0 1px 0 rgba(255,255,255,.05), inset 0 -1px 0 rgba(0,0,0,.6); }

.hybrid-title { text-align: center; display: flex; flex-direction: column; gap: 4px; }
.game-title { font-family: 'Orbitron'; font-weight: 900; font-size: 26px; color: #fff; letter-spacing: 1px; line-height: 1.1; }
.game-meta { font-family: 'Share Tech Mono'; font-size: 12px; color: rgba(255,255,255,.5); letter-spacing: 2px; }
.game-why { max-width: 1200px; margin: 0 auto; padding: 12px 22px; background: rgba(255,255,255,.04); border-left: 4px solid var(--ye); font-family: 'Share Tech Mono'; font-size: 14.5px; line-height: 1.55; color: rgba(255,255,255,.86); text-align: left; }
.game-why .lbl { display: block; font-family: 'Press Start 2P'; font-size: 8px; color: var(--ye); letter-spacing: 2px; margin-bottom: 6px; }

nav.footer { position: fixed; bottom: 0; left: 0; right: 0; height: 64px; background: rgba(6, 3, 15, 0.97); border-top: 2px solid var(--cy); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; z-index: 200; }
.nav-btn { background: transparent; border: 2px solid var(--cy); color: var(--cy); font-family: 'Press Start 2P'; font-size: 9px; padding: 10px 18px; letter-spacing: 2px; cursor: pointer; transition: all .15s; border-radius: 2px; }
.nav-btn:hover:not(:disabled) { background: var(--cy); color: #000; }
.nav-btn:disabled { opacity: .25; cursor: not-allowed; }
.nav-center { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; margin: 0 24px; }
.nav-counter { font-family: 'Press Start 2P'; font-size: 10px; color: var(--mg); letter-spacing: 3px; }
.nav-progress { width: 100%; max-width: 480px; height: 4px; background: rgba(255,255,255,.08); border-radius: 2px; overflow: hidden; }
.nav-progress .bar { height: 100%; background: linear-gradient(90deg, var(--mg), var(--cy)); width: 0; transition: width .25s; box-shadow: 0 0 8px rgba(255,46,136,.5); }
.nav-hint { font-family: 'Share Tech Mono'; font-size: 11px; color: rgba(255,255,255,.4); letter-spacing: 2px; }
.nav-hint kbd { display: inline-block; padding: 2px 8px; background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18); border-radius: 3px; font-family: 'Share Tech Mono'; font-size: 11px; color: var(--ye); margin: 0 2px; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--dk); }
::-webkit-scrollbar-thumb { background: var(--mg); border-radius: 3px; }
"""

SCRIPT = """
const slides = document.querySelectorAll('.slide');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const counter = document.getElementById('counter');
const bar = document.getElementById('bar');
let current = 0;
const total = slides.length;
function pad(n) { return String(n).padStart(2, '0'); }
function go(i) {
  if (i < 0 || i >= total) return;
  slides[current].classList.remove('active');
  current = i;
  slides[current].classList.add('active');
  prevBtn.disabled = current === 0;
  nextBtn.disabled = current === total - 1;
  counter.textContent = pad(current + 1) + ' / ' + pad(total);
  bar.style.width = ((current + 1) / total * 100) + '%';
}
prevBtn.addEventListener('click', () => go(current - 1));
nextBtn.addEventListener('click', () => go(current + 1));
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); go(current + 1); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); go(current - 1); }
  if (e.key === 'Home') { go(0); }
  if (e.key === 'End') { go(total - 1); }
});
go(0);
"""


def _slide_portada(num: int, data: dict) -> str:
    titulo = _esc(data["titulo"]).upper()
    if data.get("titulo_vs_word"):
        w = _esc(data["titulo_vs_word"]).upper()
        titulo = titulo.replace(w, f'<span class="vs">{w}</span>')
    return (
        f'<section class="slide active"><span class="slide-num">{num:02d}</span>'
        '<div class="portada">'
        f'<div class="ep-tag">{_esc(data["titulo_pre"]).upper()}</div>'
        f'<div class="ep-title">{titulo}</div>'
        f'<div class="ep-sub">{_esc(data["subtitulo"]).upper()}</div>'
        '</div></section>'
    )


def _slide_divider(num: int, pre: str, titulo: str, texto: str, color: str, font_size: str | None = None) -> str:
    style = f' style="font-size:{font_size}px;"' if font_size else ""
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="divider">'
        f'<div class="pre {color}">{_esc(pre).upper()}</div>'
        f'<div class="title {color}"{style}>{_esc(titulo).upper()}</div>'
        f'<div class="sub">{_esc(texto)}</div>'
        '</div></section>'
    )


def _slide_item(num: int, item: dict, data: dict, out_slug: str) -> str:
    pos = item["pos"]
    color = "mg" if pos <= 3 else "cy"
    if pos == 1:
        doc_label = data.get("doc_label_top", data["doc_label"])
    elif pos <= 3:
        doc_label = data.get("doc_label_podio", data["doc_label"])
    else:
        doc_label = data["doc_label"]
    key = item["img_key"]
    label_class = item.get("label_class", "lb-default")
    img_dir = REPO / "studio" / "specials" / "img" / out_slug
    img_ext = None
    for ext in ("jpg", "png"):
        if (img_dir / f"{key}.{ext}").exists():
            img_ext = ext
            break
    if img_ext:
        img_html = (
            f'<div class="cart-img-wrap {label_class}">'
            f'<img class="cart-img-bg" src="img/{out_slug}/{key}.{img_ext}" alt="" aria-hidden="true">'
            f'<img src="img/{out_slug}/{key}.{img_ext}" alt="{_esc(item["nombre"])}">'
            '</div>'
        )
    else:
        img_html = (
            f'<div class="cart-fallback {label_class}">'
            f'<div class="title">{_esc(item["nombre"]).upper()}</div>'
            f'<div class="sub">{_esc(item.get("consola", ""))}</div>'
            '</div>'
        )
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="slide-hybrid">'
        '<div class="hybrid-head">'
        f'<div class="game-pos {color}"><span class="hash">#</span>{pos}</div>'
        f'<div class="game-block-label {color}">{_esc(doc_label).upper()}</div>'
        '</div>'
        '<div class="hybrid-body">'
        f'<div class="cart-wrap"><div class="cart">{img_html}'
        f'<div class="cart-console">{_esc(item.get("consola", "")).upper()}</div>'
        '</div></div>'
        '<div class="tv-wrap"><div class="tarrovision">'
        f'<div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {pos:02d}</span></div>'
        '<div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen">'
        '<div class="tv-noscreen-big">NO SIGNAL</div><div class="tv-noscreen-sub">Inserta gameplay aqui</div></div></div></div>'
        '<div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>'
        '</div></div>'
        '</div>'
        '<div class="hybrid-title">'
        f'<div class="game-title">{_esc(item["nombre"]).upper()} — {_esc(item["rol"]).upper()}</div>'
        f'<div class="game-meta">{_esc(item.get("consola", "")).upper()} · {_esc(item.get("anio", ""))} · {_esc(item.get("editor", "")).upper()} · {_esc(item.get("meta_extra", "")).upper()}</div>'
        '</div>'
        f'<div class="game-why"><span class="lbl">▶ {_esc(doc_label).upper()}</span>{_esc(item["ficha"])}</div>'
        '</div></section>'
    )


def generar_special(data: dict, out_slug: str) -> Path:
    num = 1
    slides = [_slide_portada(num, data)]
    num += 1
    slides.append(_slide_divider(num, data["intro_pre"], data["intro_titulo"], data["intro_texto"], "cy"))
    num += 1
    for item in sorted(data["items"], key=lambda x: -x["pos"]):
        slides.append(_slide_item(num, item, data, out_slug))
        num += 1
    an = data["analisis"]
    slides.append(_slide_divider(num, an["pre"], an["titulo"], an["texto"], "mg", font_size=an.get("font_size", 56)))
    num += 1
    ci = data["cierre"]
    slides.append(_slide_divider(num, ci["pre"], ci["titulo"], ci["texto"], "cy", font_size=ci.get("font_size", 54)))

    paleta = "\n".join(
        f'.{it.get("label_class", "lb-default")}   {{ --label-1:{it["color_1"]}; --label-2:{it["color_2"]}; }}'
        for it in data["items"] if it.get("label_class") and it.get("color_1")
    )
    css = CSS.replace("{PALETA}", paleta)

    html = (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>RETROTARROS · {_esc(data["titulo"]).upper()}</title>'
        f'<style>{css}</style></head><body>'
        '<header><div class="hdr-logo">RETROTARROS</div>'
        f'<div class="hdr-tag">ESTUDIO · {_esc(data["header_tag"]).upper()}</div>'
        '<div class="hdr-rec"><div class="dot"></div>EN VIVO</div></header>'
        '<div class="deck" id="deck">\n' + "\n".join(slides) + '\n</div>'
        '<nav class="footer"><button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>'
        '<div class="nav-center"><div class="nav-counter" id="counter">01 / 01</div>'
        '<div class="nav-progress"><div class="bar" id="bar"></div></div></div>'
        '<div class="nav-hint"><kbd>←</kbd> <kbd>→</kbd> NAVEGAR</div>'
        '<button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button></nav>'
        f'<script>{SCRIPT}</script></body></html>'
    )
    out_dir = REPO / "studio" / "specials"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
    out.write_text(html, encoding="utf-8")
    return out
