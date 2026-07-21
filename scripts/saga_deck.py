"""
saga_deck.py - Retrotarros Studio Suite
Genera el deck del formato SAGA: una LINEA DE TIEMPO extensa de una franquicia,
y por cada juego un slide que hace ZOOM al punto de la linea donde aparece
("llegamos a 1987, a la NES... aparece The Legend of Zelda").

Estructura:
  01 PORTADA
  02 LINEA DE TIEMPO COMPLETA (overview, todos los juegos)
  03..N por juego: cinta de tiempo centrada en el juego + ficha (box, año, consola, por que, EN COLECCION)
  BONUS ediciones especiales/hardware (opcional)
  BALANCE + CIERRE

Box art en studio/img/<slug>/<key>.jpg (key = slug del titulo). Sin tildes (HTML).
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAL = {"mg": "#FF2E88", "cy": "#00E5FF", "ye": "#FFD23F", "dk": "#06030f"}
NODE_W = 168          # ancho de cada nodo de la cinta
ACTIVE_SCALE = 1.85


def _slug(s: str) -> str:
    s = s.lower()
    for a, b in {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n","ü":"u"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def _node(g: dict, slug: str, active: bool) -> str:
    cls = "snode active" if active else "snode"
    key = g.get("key") or _slug(g["title"])
    owned = '<div class="sowned">EN COLECCION</div>' if g.get("owned") else '<div class="sowned faltan">FALTA</div>'
    return (
        f'<div class="{cls}">'
        f'<div class="sbox"><img src="img/{slug}/{key}.jpg" onerror="this.style.opacity=0"></div>'
        f'<div class="sline-dot"></div>'
        f'<div class="syear">{g["year"]}</div>'
        f'<div class="scons">{g["console"]}</div>'
        f'{owned}'
        '</div>'
    )


def _ribbon(games: list, slug: str, active_idx) -> str:
    nodes = "".join(_node(g, slug, i == active_idx) for i, g in enumerate(games))
    n = len(games)
    if active_idx is None:
        # overview: escalar para que entren todos en 1920 y centrar el track
        scale = min(1.0, 1820 / (n * NODE_W))
        tx = (1920 - n * NODE_W * scale) / 2
        track = (f'<div class="ribbon-track" style="transform:translateX({tx:.0f}px) scale({scale:.3f});'
                 f'transform-origin:left center">{nodes}</div>')
        here = ""
    else:
        center = active_idx * NODE_W + NODE_W / 2
        tx = 960 - center
        track = f'<div class="ribbon-track" style="transform:translateX({tx:.0f}px)">{nodes}</div>'
        here = '<div class="here-marker"></div>'
    return f'<div class="ribbon">{here}<div class="ribbon-line"></div>{track}</div>'


def _slide_portada(num, data):
    p = data["portada"]
    return (f'<section class="slide active"><span class="slide-num">{num:02d}</span>'
            f'<div class="portada"><div class="ep-tag">{p["tag"]}</div>'
            f'<div class="ep-title">{p["title"]}</div><div class="ep-sub">{p["sub"]}</div></div></section>')


def _slide_timeline(num, data, games, slug):
    return (f'<section class="slide"><span class="slide-num">{num:02d}</span>'
            f'<div class="tl-full"><div class="tl-title">{data["timeline_title"]}</div>'
            f'{_ribbon(games, slug, None)}'
            f'<div class="tl-sub">{data["timeline_sub"]}</div></div></section>')


def _slide_game(num, g, idx, games, slug):
    key = g.get("key") or _slug(g["title"])
    owned = ('<div class="saga-owned">EN COLECCION</div>' if g.get("owned")
             else '<div class="saga-owned faltan">NO LA TENEMOS</div>')
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        f'{_ribbon(games, slug, idx)}'
        '<div class="saga-detail">'
        f'  <div class="saga-cart"><img src="img/{slug}/{key}.jpg" alt="" onerror="this.style.display=\'none\'"></div>'
        '  <div class="saga-info">'
        f'    <div class="saga-arrive">LLEGAMOS A <b>{g["year"]}</b> · {g["console"]}</div>'
        f'    <div class="saga-title">{g["title"]}</div>'
        f'    <div class="saga-why"><span class="lbl">▶ EN LA HISTORIA</span>{g["why"]}</div>'
        f'    {owned}'
        '  </div>'
        '</div></section>')


def _tv(ch: int) -> str:
    return (
        '<div class="tarrovision">'
        f'<div class="tv-controls-top"><span class="tv-led"></span><span class="tv-brand">TARROVISION</span><span class="tv-channel">CH {ch:02d}</span></div>'
        '<div class="tv-screen"><div class="tv-screen-inner"><div class="tv-noscreen">'
        '<div class="tv-noscreen-big">NO SIGNAL</div><div class="tv-noscreen-sub">Inserta gameplay aqui</div></div></div></div>'
        '<div class="tv-controls-bottom"><div class="tv-knob"></div><div class="tv-knob cy"></div><div class="tv-speaker"></div></div>'
        '</div>'
    )


def _slide_gameplay(num, g, idx):
    owned = ('<div class="gp-owned-mini">★ EN LA COLECCION</div>' if g.get("owned") else '')
    dato = g.get("dato", "")
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        f'<div class="gp-head"><div class="gp-title">{g["title"]}</div>'
        f'<div class="gp-meta">{g["console"]} · {g["year"]} · GAMEPLAY</div></div>'
        '<div class="gp-body">'
        f'  <div class="gp-tv">{_tv((idx % 12) + 1)}</div>'
        '  <div class="gp-side">'
        f'    <div class="gp-dato"><span class="lbl">EL DATO</span>{dato}</div>'
        f'    {owned}'
        '  </div>'
        '</div></section>')


def _slide_bonus(num, data):
    cards = "".join(
        f'<div class="bonus-card {c.get("color","cy")}"><h3>{c["name"]}</h3>'
        f'<span class="tag">{c["tag"]}</span><p>{c["desc"]}</p></div>'
        for c in data.get("bonus", []))
    return (f'<section class="slide"><span class="slide-num">{num:02d}</span>'
            f'<h1>{data["bonus_title"]}</h1><h2 class="mg">{data["bonus_sub"]}</h2>'
            f'<div class="bonus-grid">{cards}</div></section>')


def _slide_divider(num, d):
    color = d.get("color", "cy")
    style = f' style="font-size:{d["title_size"]}px;"' if d.get("title_size") else ""
    return (f'<section class="slide"><span class="slide-num">{num:02d}</span><div class="divider">'
            f'<div class="pre {color}">{d["pre"]}</div><div class="title {color}"{style}>{d["title"]}</div>'
            f'<div class="sub">{d["sub"]}</div></div></section>')


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
:root{--mg:#FF2E88;--cy:#00E5FF;--ye:#FFD23F;--dk:#06030f;--bo:#F5F0E8;--card-bg:rgba(12,6,32,.92)}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:var(--dk);font-family:'Share Tech Mono',monospace;color:var(--bo)}
body{background-image:radial-gradient(ellipse 100% 50% at 50% -5%,rgba(255,46,136,.12) 0,transparent 65%),repeating-linear-gradient(0deg,transparent 0 39px,rgba(255,255,255,.014) 39px 40px),repeating-linear-gradient(90deg,transparent 0 39px,rgba(255,255,255,.014) 39px 40px)}
header{position:fixed;top:0;left:0;right:0;height:56px;z-index:200;background:rgba(6,3,15,.97);border-bottom:2px solid var(--mg);display:flex;align-items:center;justify-content:space-between;padding:0 28px}
.hdr-logo{font-family:'Orbitron';font-weight:900;font-size:20px;color:var(--mg);text-shadow:0 0 14px rgba(255,46,136,.6);letter-spacing:3px}
.hdr-tag{font-family:'Share Tech Mono';font-size:12px;color:var(--ye);letter-spacing:3px}
.hdr-rec{display:flex;align-items:center;gap:8px;font-family:'Press Start 2P';font-size:8px;color:var(--mg)}
.dot{width:10px;height:10px;background:var(--mg);border-radius:50%;animation:blink 1.2s ease-in-out infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.15}}
.deck{position:fixed;top:56px;left:0;right:0;bottom:64px;overflow:hidden}
.slide{position:absolute;inset:0;padding:24px 40px;opacity:0;pointer-events:none;transition:opacity .22s;display:flex;flex-direction:column}
.slide.active{opacity:1;pointer-events:auto}
.slide-num{position:absolute;top:14px;right:22px;font-family:'Press Start 2P';font-size:9px;color:rgba(255,255,255,.22);letter-spacing:2px}
.portada{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.portada .ep-tag{font-family:'Press Start 2P';font-size:11px;color:var(--cy);letter-spacing:5px;margin-bottom:22px}
.portada .ep-title{font-family:'Orbitron';font-weight:900;font-size:76px;line-height:1;color:#fff;margin-bottom:18px}
.portada .ep-title .vs{color:var(--mg);text-shadow:0 0 26px rgba(255,46,136,.55)}
.portada .ep-sub{font-family:'Share Tech Mono';font-size:18px;color:var(--ye);letter-spacing:3px}
/* RIBBON */
.ribbon{position:relative;height:300px;overflow:hidden;flex:none;margin-bottom:8px}
.ribbon-line{position:absolute;top:208px;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,rgba(0,229,255,.5) 8%,rgba(0,229,255,.5) 92%,transparent);z-index:1}
.here-marker{position:absolute;top:120px;left:960px;width:0;height:150px;border-left:2px dashed var(--ye);z-index:5;transform:translateX(-1px)}
.here-marker::before{content:"";position:absolute;top:-12px;left:-9px;border-left:9px solid transparent;border-right:9px solid transparent;border-top:13px solid var(--ye)}
.ribbon-track{position:absolute;top:0;left:0;height:100%;display:flex;align-items:flex-start;will-change:transform;transition:transform .35s ease}
.snode{width:168px;flex:none;display:flex;flex-direction:column;align-items:center;gap:5px;padding-top:18px;opacity:.45;transition:all .3s}
.snode .sbox{width:96px;height:128px;border:2px solid rgba(255,255,255,.4);border-radius:4px;overflow:hidden;background:#0e0a20;box-shadow:0 6px 16px rgba(0,0,0,.5)}
.snode .sbox img{width:100%;height:100%;object-fit:cover}
.snode .sline-dot{width:14px;height:14px;border-radius:50%;background:#2a2a3a;border:2px solid var(--cy);position:relative;z-index:2;margin-top:2px}
.snode .syear{font-family:'Orbitron';font-weight:900;font-size:20px;color:#fff;line-height:1}
.snode .scons{font-family:'Share Tech Mono';font-size:10px;color:rgba(255,255,255,.6);letter-spacing:1px;text-align:center}
.snode .sowned{font-family:'Press Start 2P';font-size:6px;color:var(--cy);letter-spacing:1px}
.snode .sowned.faltan{color:rgba(255,255,255,.3)}
.snode.active{opacity:1;transform:scale(1.85);z-index:4}
.snode.active .sbox{border-color:var(--mg);box-shadow:0 0 24px rgba(255,46,136,.7)}
.snode.active .sline-dot{background:var(--mg);border-color:var(--mg);box-shadow:0 0 12px var(--mg)}
.snode.active .syear{color:var(--mg);text-shadow:0 0 10px rgba(255,46,136,.6)}
.snode.active .sowned{color:var(--ye)}
/* TIMELINE FULL */
.tl-full{flex:1;display:flex;flex-direction:column;justify-content:center;gap:14px}
.tl-title{font-family:'Orbitron';font-weight:900;font-size:46px;color:#fff;text-align:center;letter-spacing:1px}
.tl-sub{font-family:'Share Tech Mono';font-size:16px;color:rgba(255,255,255,.65);text-align:center;letter-spacing:2px;max-width:1200px;margin:0 auto;line-height:1.5}
.tl-full .ribbon{height:340px}
.tl-full .snode{opacity:.92}
/* DETALLE JUEGO */
.saga-detail{flex:1;display:grid;grid-template-columns:380px 1fr;gap:40px;align-items:center;padding:0 30px;min-height:0}
.saga-cart{display:flex;align-items:center;justify-content:center;height:100%}
.saga-cart img{max-height:420px;max-width:100%;border:3px solid rgba(255,255,255,.85);border-radius:8px;box-shadow:0 18px 50px rgba(0,0,0,.7)}
.saga-info{display:flex;flex-direction:column;gap:14px}
.saga-arrive{font-family:'Press Start 2P';font-size:13px;color:var(--cy);letter-spacing:2px}
.saga-arrive b{color:var(--ye);font-size:18px}
.saga-title{font-family:'Orbitron';font-weight:900;font-size:46px;color:#fff;line-height:1.05}
.saga-why{background:rgba(255,255,255,.04);border-left:4px solid var(--ye);padding:14px 22px;font-family:'Share Tech Mono';font-size:16px;line-height:1.55;color:rgba(255,255,255,.88);max-width:1000px}
.saga-why .lbl{display:block;font-family:'Press Start 2P';font-size:8px;color:var(--ye);letter-spacing:2px;margin-bottom:8px}
.saga-owned{align-self:flex-start;font-family:'Orbitron';font-weight:900;font-size:30px;color:var(--dk);background:var(--ye);padding:8px 22px;border-radius:5px;letter-spacing:1px;box-shadow:0 0 22px rgba(255,210,63,.6)}
.saga-owned.faltan{color:var(--bo);background:transparent;border:2px solid rgba(255,255,255,.3);box-shadow:none;font-size:22px}
/* GAMEPLAY (TarroVision grande) */
.gp-head{text-align:center;flex:none;padding-top:6px;margin-bottom:8px}
.gp-title{font-family:'Orbitron';font-weight:900;font-size:40px;color:#fff;line-height:1}
.gp-meta{font-family:'Share Tech Mono';font-size:13px;color:var(--ye);letter-spacing:3px;margin-top:4px}
.gp-body{flex:1;display:grid;grid-template-columns:1fr 440px;gap:40px;align-items:center;min-height:0;padding:0 16px 8px}
.gp-tv{height:100%;display:flex;align-items:center;justify-content:center;min-height:0}
.gp-tv .tarrovision{height:min(100%,640px);aspect-ratio:4/3;max-width:100%}
.gp-side{display:flex;flex-direction:column;gap:18px}
.gp-dato{background:rgba(255,255,255,.04);border-left:4px solid var(--cy);padding:18px 22px;font-family:'Share Tech Mono';font-size:18px;line-height:1.6;color:rgba(255,255,255,.9)}
.gp-dato .lbl{display:block;font-family:'Press Start 2P';font-size:8px;color:var(--cy);letter-spacing:2px;margin-bottom:10px}
.gp-owned-mini{font-family:'Press Start 2P';font-size:11px;color:var(--ye);letter-spacing:2px}
.tarrovision{position:relative;background:linear-gradient(180deg,#1a1a1f,#0d0d12);border-radius:22px;padding:20px 24px;box-shadow:0 0 0 2px rgba(255,255,255,.04),0 22px 60px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.08),inset 0 -2px 0 rgba(0,0,0,.4);display:grid;grid-template-rows:auto 1fr auto;gap:12px}
.tv-controls-top{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:0 6px}
.tv-led{width:10px;height:10px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#ff8fb8,var(--mg) 60%,#7a0030);box-shadow:0 0 10px rgba(255,46,136,.8)}
.tv-brand{flex:1;text-align:center;font-family:'Press Start 2P';font-size:12px;color:var(--ye);letter-spacing:4px}
.tv-channel{font-family:'Share Tech Mono';font-size:12px;color:var(--cy);padding:4px 10px;border:1px solid rgba(0,229,255,.4);background:rgba(0,229,255,.06)}
.tv-screen{position:relative;background:#2a2a2f;border-radius:14px;padding:16px;box-shadow:inset 0 0 0 2px #3a3a3f,inset 0 0 14px rgba(0,0,0,.6);min-height:0}
.tv-screen-inner{position:relative;width:100%;height:100%;background:#000;border-radius:18px/8px;overflow:hidden;box-shadow:inset 0 0 0 1px rgba(255,255,255,.05),inset 0 0 40px rgba(0,0,0,.95)}
.tv-screen-inner img,.tv-screen-inner video{display:block;width:100%;height:100%;object-fit:cover}
.tv-screen-inner::before{content:"";position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,0) 0 2px,rgba(0,0,0,.18) 2px 3px);z-index:3;mix-blend-mode:multiply}
.tv-noscreen{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 50% 50%,rgba(45,27,105,.6),#000 80%);color:rgba(255,255,255,.35);text-align:center;padding:30px;z-index:2}
.tv-noscreen-big{font-family:'Press Start 2P';font-size:18px;color:var(--mg);letter-spacing:4px;margin-bottom:12px;text-shadow:0 0 12px rgba(255,46,136,.5)}
.tv-noscreen-sub{font-family:'Share Tech Mono';font-size:12px;color:rgba(0,229,255,.55)}
.tv-controls-bottom{display:grid;grid-template-columns:auto auto 1fr;align-items:center;gap:14px;padding:4px 6px 0}
.tv-knob{width:32px;height:32px;border-radius:50%;background:radial-gradient(circle at 30% 30%,#5a5a60,#2a2a30 60%,#0a0a0e);box-shadow:inset 0 1px 0 rgba(255,255,255,.15),inset 0 -2px 0 rgba(0,0,0,.4),0 2px 4px rgba(0,0,0,.6);position:relative}
.tv-knob::after{content:"";position:absolute;top:6px;left:50%;width:2px;height:10px;background:var(--ye);transform:translateX(-50%) rotate(45deg)}
.tv-knob.cy::after{background:var(--cy);transform:translateX(-50%) rotate(-30deg)}
.tv-speaker{height:26px;background:repeating-linear-gradient(90deg,#0a0a0e 0 3px,#1a1a1f 3px 6px);border-radius:4px}
/* BONUS + DIVIDER + NUMBERS */
.slide h1{font-family:'Orbitron';font-weight:900;font-size:60px;color:#fff;text-align:center;margin-bottom:6px}
.slide h2{font-family:'Share Tech Mono';font-size:18px;letter-spacing:4px;text-align:center;margin-bottom:24px;color:rgba(255,255,255,.7)}
.slide h2.mg{color:var(--mg)}
.bonus-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;max-width:1340px;margin:0 auto;padding:0 30px}
.bonus-card{background:var(--card-bg);border:1px solid rgba(255,255,255,.08);border-top:3px solid var(--cy);padding:18px 16px;text-align:center}
.bonus-card.mg{border-top-color:var(--mg)}.bonus-card.ye{border-top-color:var(--ye)}.bonus-card.cy{border-top-color:var(--cy)}
.bonus-card h3{font-family:'Press Start 2P';font-size:10px;color:var(--ye);letter-spacing:2px;margin-bottom:10px;min-height:30px;display:flex;align-items:center;justify-content:center}
.bonus-card .tag{display:inline-block;font-family:'Press Start 2P';font-size:8px;padding:4px 8px;border:1px solid var(--cy);color:var(--cy);margin-bottom:10px;letter-spacing:2px}
.bonus-card p{font-family:'Share Tech Mono';font-size:12px;color:rgba(255,255,255,.7);line-height:1.5}
.divider{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.divider .pre{font-family:'Press Start 2P';font-size:11px;letter-spacing:6px;margin-bottom:22px}
.divider .pre.cy{color:var(--cy)}.divider .pre.mg{color:var(--mg)}
.divider .title{font-family:'Orbitron';font-weight:900;font-size:72px;line-height:1;color:#fff;margin-bottom:20px}
.divider .title.cy{color:var(--cy);text-shadow:0 0 22px rgba(0,229,255,.5)}.divider .title.mg{color:var(--mg);text-shadow:0 0 22px rgba(255,46,136,.55)}
.divider .sub{font-family:'Share Tech Mono';font-size:18px;color:rgba(255,255,255,.7);letter-spacing:2px;max-width:900px;line-height:1.6}
nav.footer{position:fixed;bottom:0;left:0;right:0;height:64px;background:rgba(6,3,15,.97);border-top:2px solid var(--cy);display:flex;align-items:center;justify-content:space-between;padding:0 28px;z-index:200}
.nav-btn{background:transparent;border:2px solid var(--cy);color:var(--cy);font-family:'Press Start 2P';font-size:9px;padding:10px 18px;letter-spacing:2px;cursor:pointer;border-radius:2px}
.nav-btn:disabled{opacity:.25}
.nav-center{display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;margin:0 24px}
.nav-counter{font-family:'Press Start 2P';font-size:10px;color:var(--mg);letter-spacing:3px}
.nav-progress{width:100%;max-width:480px;height:4px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden}
.nav-progress .bar{height:100%;background:linear-gradient(90deg,var(--mg),var(--cy));width:0;transition:width .25s}
.nav-hint{font-family:'Share Tech Mono';font-size:11px;color:rgba(255,255,255,.4);letter-spacing:2px}
"""

SCRIPT = """
const slides=document.querySelectorAll('.slide');const prevBtn=document.getElementById('prevBtn');
const nextBtn=document.getElementById('nextBtn');const counter=document.getElementById('counter');const bar=document.getElementById('bar');
let current=0;const total=slides.length;function pad(n){return String(n).padStart(2,'0')}
function go(i){if(i<0||i>=total)return;slides[current].classList.remove('active');current=i;slides[current].classList.add('active');
prevBtn.disabled=current===0;nextBtn.disabled=current===total-1;counter.textContent=pad(current+1)+' / '+pad(total);bar.style.width=((current+1)/total*100)+'%'}
prevBtn.addEventListener('click',()=>go(current-1));nextBtn.addEventListener('click',()=>go(current+1));
document.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();go(current+1)}if(e.key==='ArrowLeft'){e.preventDefault();go(current-1)}if(e.key==='Home')go(0);if(e.key==='End')go(total-1)});go(0);
"""


def generar_saga(data: dict, out_slug: str) -> Path:
    games = data["games"]
    slides = []
    n = 1
    slides.append(_slide_portada(n, data)); n += 1
    slides.append(_slide_timeline(n, data, games, out_slug)); n += 1
    for i, g in enumerate(games):
        slides.append(_slide_game(n, g, i, games, out_slug)); n += 1
        slides.append(_slide_gameplay(n, g, i)); n += 1   # TarroVision para gameplay
    if data.get("bonus"):
        slides.append(_slide_bonus(n, data)); n += 1
    if data.get("balance"):
        slides.append(_slide_divider(n, data["balance"])); n += 1
    slides.append(_slide_divider(n, data["cierre"])); n += 1

    html = (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>RETROTARROS · {data["doc_title"]}</title><style>{CSS}</style></head><body>'
        '<header><div class="hdr-logo">RETROTARROS</div>'
        f'<div class="hdr-tag">{data["header_tag"]}</div>'
        '<div class="hdr-rec"><div class="dot"></div>EN VIVO</div></header>'
        '<div class="deck" id="deck">\n' + "\n".join(slides) + '\n</div>'
        '<nav class="footer"><button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>'
        '<div class="nav-center"><div class="nav-counter" id="counter">01 / 01</div>'
        '<div class="nav-progress"><div class="bar" id="bar"></div></div></div>'
        '<div class="nav-hint">← → NAVEGAR</div>'
        '<button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button></nav>'
        f'<script>{SCRIPT}</script></body></html>'
    )
    out_dir = REPO / "studio" / "sagas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
    out.write_text(html, encoding="utf-8")
    return out
