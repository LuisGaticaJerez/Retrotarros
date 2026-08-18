"""
retronota_deck.py - Retrotarros Studio Suite
Genera el deck del formato RETRONOTA: reportaje tematico de 15-20 min, Luis + Coco
investigando juntos en camara (a diferencia de Resena que los separa 1 y 1, y de
Specials/episodios largos que cierran con bateria). No gira en torno a UN juego ni es
un countdown de N items -- cubre un tema cultural/historico/tecnico del mundo retro,
casi siempre con angulo regional chileno/latam.

Diseño aprobado con Luis 2026-08-17 (ver
docs/superpowers/specs/2026-08-17-retronota-format-design.md). Estructura en 5
capitulos tematicos (gancho / origen-contexto / desarrollo / impacto-legado / cierre),
sin numeracion de ranking. NUNCA cierra con bateria.

Regla nueva especifica del formato: cada slide de contenido puede llevar un badge
HECHO VERIFICADO o MITO / LEYENDA URBANA -- obligatorio cuando el tema toca folclore,
para que la audiencia nunca confunda especulacion con dato duro (riesgo mas alto en
este formato que en cualquier otro del canal, porque un "reportaje" suena mas
autorizado por defecto).

Box art / fotos en studio/retronotas/img/<slug>/<key>.jpg. Salida en
studio/retronotas/<slug>.html (carpeta aparte, mismo patron que Resenas).
"""
from __future__ import annotations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
:root{--mg:#FF2E88;--cy:#00E5FF;--ye:#FFD23F;--dk:#06030f;--bo:#F5F0E8;--gr:#2ECC71;--rd:#FF4D4D}
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
.slide{position:absolute;inset:0;padding:28px 56px;overflow:hidden;opacity:0;pointer-events:none;transition:opacity .22s;display:flex;flex-direction:column}
.slide.active{opacity:1;pointer-events:auto}
.slide-num{position:absolute;top:16px;right:24px;font-family:'Press Start 2P';font-size:9px;color:rgba(255,255,255,.22);letter-spacing:2px}

.portada{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.portada .rn-tag{font-family:'Press Start 2P';font-size:13px;color:var(--cy);letter-spacing:6px;margin-bottom:22px}
.portada .rn-title{font-family:'Orbitron';font-weight:900;font-size:58px;line-height:1.1;color:#fff;margin-bottom:20px;max-width:1300px}
.portada .rn-sub{font-family:'Share Tech Mono';font-size:20px;color:var(--ye);letter-spacing:2px;max-width:1000px}

.capitulo{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:20px}
.capitulo .cap-num{font-family:'Orbitron';font-weight:900;font-size:26px;color:var(--mg);letter-spacing:4px}
.capitulo .cap-titulo{font-family:'Orbitron';font-weight:900;font-size:60px;color:#fff;line-height:1.05;max-width:1200px;text-shadow:0 0 22px rgba(255,46,136,.4)}
.capitulo .cap-texto{font-family:'Share Tech Mono';font-size:21px;color:rgba(255,255,255,.8);letter-spacing:1px;max-width:950px;line-height:1.6}

.badge{display:inline-flex;align-items:center;gap:8px;font-family:'Press Start 2P';font-size:11px;letter-spacing:2px;padding:8px 16px;border-radius:4px;margin-bottom:18px;align-self:flex-start}
.badge.verificado{color:#0a2e18;background:var(--gr);box-shadow:0 0 16px rgba(46,204,113,.5)}
.badge.mito{color:#3a0a0a;background:var(--rd);box-shadow:0 0 16px rgba(255,77,77,.5)}

.contenido{flex:1;display:flex;flex-direction:column;padding-top:6px;min-height:0}
.contenido-head{text-align:center;flex:none;margin-bottom:18px}
.contenido-cap{font-family:'Press Start 2P';font-size:10px;color:var(--cy);letter-spacing:3px;margin-bottom:8px}
.contenido-titulo{font-family:'Orbitron';font-weight:900;font-size:38px;color:#fff;line-height:1.1}
.contenido-body{flex:1;display:grid;grid-template-columns:1fr;gap:32px;align-items:center;min-height:0}
.contenido-body.con-img{grid-template-columns:1fr 46%}
.contenido-texto-wrap{display:flex;flex-direction:column;justify-content:center;min-height:0;height:100%;overflow-y:auto;max-width:1500px;margin:0 auto;width:100%}
.contenido-texto{font-family:'Share Tech Mono';font-size:22px;line-height:1.65;color:rgba(255,255,255,.9);background:rgba(255,255,255,.04);border-left:4px solid var(--cy);padding:26px 30px}
.contenido-img-wrap{display:flex;align-items:center;justify-content:center;height:100%;min-height:0}
.contenido-img-wrap img{max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;border-radius:10px;border:2px solid rgba(255,255,255,.18);box-shadow:0 18px 50px rgba(0,0,0,.6)}
.contenido-fuente{font-family:'Share Tech Mono';font-size:13px;color:rgba(255,255,255,.4);letter-spacing:1px;margin-top:14px;text-align:right}

.divider{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.divider .pre{font-family:'Press Start 2P';font-size:13px;color:var(--cy);letter-spacing:5px;margin-bottom:20px}
.divider .title{font-family:'Orbitron';font-weight:900;font-size:60px;color:#fff;line-height:1.05;margin-bottom:20px;text-shadow:0 0 22px rgba(0,229,255,.4)}
.divider .sub{font-family:'Share Tech Mono';font-size:20px;color:rgba(255,255,255,.75);letter-spacing:1px;max-width:950px;line-height:1.6}

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
document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();go(current+1)}
  if(e.key==='ArrowLeft'){e.preventDefault();go(current-1)}
  if(e.key==='Home'){go(0)}
  if(e.key==='End'){go(total-1)}
});
go(0);
"""


def _slide_portada(num: int, data: dict) -> str:
    return (
        f'<section class="slide active"><span class="slide-num">{num:02d}</span>'
        '<div class="portada">'
        '<div class="rn-tag">RETRONOTA</div>'
        f'<div class="rn-title">{_esc(data["titulo"]).upper()}</div>'
        f'<div class="rn-sub">{_esc(data["subtitulo"])}</div>'
        '</div></section>'
    )


def _slide_capitulo(num: int, bloque: dict) -> str:
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="capitulo">'
        f'<div class="cap-num">CAPITULO {bloque["cap_num"]}</div>'
        f'<div class="cap-titulo">{_esc(bloque["titulo"]).upper()}</div>'
        f'<div class="cap-texto">{_esc(bloque["texto"])}</div>'
        '</div></section>'
    )


def _slide_contenido(num: int, bloque: dict, out_slug: str) -> str:
    img_key = bloque.get("img_key")
    img_html = ""
    body_class = "contenido-body"
    if img_key:
        img_dir = REPO / "studio" / "retronotas" / "img" / out_slug
        ext = None
        for e in ("jpg", "png"):
            if (img_dir / f"{img_key}.{e}").exists():
                ext = e
                break
        if ext:
            img_html = (
                '<div class="contenido-img-wrap">'
                f'<img src="img/{out_slug}/{img_key}.{ext}" alt="">'
                '</div>'
            )
            body_class += " con-img"
    badge_html = ""
    if bloque.get("tag") == "verificado":
        badge_html = f'<div class="badge verificado">✔ {_esc(bloque.get("tag_texto") or "HECHO VERIFICADO")}</div>'
    elif bloque.get("tag") == "mito":
        badge_html = f'<div class="badge mito">⚠ {_esc(bloque.get("tag_texto") or "MITO / LEYENDA URBANA")}</div>'
    fuente_html = f'<div class="contenido-fuente">Fuente: {_esc(bloque["fuente"])}</div>' if bloque.get("fuente") else ""
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="contenido">'
        '<div class="contenido-head">'
        f'<div class="contenido-cap">CAPITULO {bloque["cap_num"]} · {_esc(bloque["cap_nombre"]).upper()}</div>'
        f'<div class="contenido-titulo">{_esc(bloque["titulo"]).upper()}</div>'
        '</div>'
        f'<div class="{body_class}">'
        '<div class="contenido-texto-wrap">'
        f'{badge_html}'
        f'<div class="contenido-texto">{_esc(bloque["texto"])}</div>'
        f'{fuente_html}'
        '</div>'
        f'{img_html}'
        '</div></div></section>'
    )


def _slide_divider(num: int, pre: str, titulo: str, texto: str) -> str:
    return (
        f'<section class="slide"><span class="slide-num">{num:02d}</span>'
        '<div class="divider">'
        f'<div class="pre">{_esc(pre).upper()}</div>'
        f'<div class="title">{_esc(titulo).upper()}</div>'
        f'<div class="sub">{_esc(texto)}</div>'
        '</div></section>'
    )


def generar_retronota(data: dict, out_slug: str) -> Path:
    num = 1
    slides = [_slide_portada(num, data)]
    num += 1
    for bloque in data["bloques"]:
        tipo = bloque["tipo"]
        if tipo == "capitulo":
            slides.append(_slide_capitulo(num, bloque))
        elif tipo == "contenido":
            slides.append(_slide_contenido(num, bloque, out_slug))
        num += 1
    ci = data["cierre"]
    slides.append(_slide_divider(num, ci.get("pre", "CIERRE"), ci["titulo"], ci["texto"]))

    html = (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>RETROTARROS · RETRONOTA · {_esc(data["titulo"]).upper()}</title>'
        f'<style>{CSS}</style></head><body>'
        '<header><div class="hdr-logo">RETROTARROS</div>'
        f'<div class="hdr-tag">RETRONOTA · {_esc(data.get("header_tag", data["titulo"])).upper()}</div>'
        '<div class="hdr-rec"><div class="dot"></div>EN VIVO</div></header>'
        '<div class="deck" id="deck">\n' + "\n".join(slides) + '\n</div>'
        '<nav class="footer"><button class="nav-btn" id="prevBtn">◀ ANTERIOR</button>'
        '<div class="nav-center"><div class="nav-counter" id="counter">01 / 01</div>'
        '<div class="nav-progress"><div class="bar" id="bar"></div></div></div>'
        '<div class="nav-hint">← → NAVEGAR</div>'
        '<button class="nav-btn" id="nextBtn">SIGUIENTE ▶</button></nav>'
        f'<script>{SCRIPT}</script></body></html>'
    )
    out_dir = REPO / "studio" / "retronotas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
    out.write_text(html, encoding="utf-8")
    return out
