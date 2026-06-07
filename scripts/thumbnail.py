"""
thumbnail.py - Retrotarros Studio Suite
Genera una miniatura YouTube 1280x720 estilo canal (synthwave), alto CTR:
numero gigante + 2-3 palabras + collage de box art + mascota TarroBot.

Sigue docs/guia-youtube-viral.md: <=3 palabras de texto grande, alto contraste,
legible en movil. Sin tildes (asset publico).

Uso (modulo):
  from thumbnail import generar
  generar(out_path, titulo_top="MI COLECCION", titulo_big="N64",
          numero="58", sub="JUEGOS", boxes=[rutas...])
"""
from __future__ import annotations
import base64
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
W, H = 1280, 720

MASCOT = '''<svg viewBox="0 0 64 64" class="masc">
<rect x="10" y="18" width="44" height="34" rx="6" fill="#00E5FF"/>
<rect x="15" y="23" width="34" height="24" rx="3" fill="#0e0a20" stroke="#FF2E88" stroke-width="2"/>
<circle cx="24" cy="33" r="3.2" fill="#FFD23F"/><circle cx="40" cy="33" r="3.2" fill="#FFD23F"/>
<rect x="24" y="40" width="16" height="3" rx="1.5" fill="#FFD23F"/>
<line x1="32" y1="18" x2="32" y2="10" stroke="#00E5FF" stroke-width="2"/><circle cx="32" cy="9" r="2.5" fill="#FF2E88"/>
<rect x="18" y="52" width="5" height="7" fill="#00E5FF"/><rect x="41" y="52" width="5" height="7" fill="#00E5FF"/>
</svg>'''


def _b64(p: Path) -> str:
    ext = p.suffix.lower().lstrip(".").replace("jpg", "jpeg")
    return f"data:image/{ext};base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def _html(titulo_top, titulo_big, numero, sub, boxes):
    tilts = [-8, 6, -5, 7, -6]
    cards = ""
    for i, b in enumerate(boxes[:5]):
        try:
            uri = _b64(Path(b))
        except Exception:
            continue
        z = 10 + i
        cards += f'<img class="box" style="--t:{tilts[i%5]}deg;z-index:{z}" src="{uri}">'
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Press+Start+2P&display=swap');
*{{margin:0;box-sizing:border-box}}
.thumb{{width:{W}px;height:{H}px;position:relative;overflow:hidden;
  background:
   radial-gradient(ellipse 70% 80% at 78% 50%, rgba(255,46,136,.30) 0%, transparent 60%),
   radial-gradient(ellipse 60% 70% at 15% 90%, rgba(0,229,255,.18) 0%, transparent 60%),
   repeating-linear-gradient(0deg, transparent 0 47px, rgba(255,255,255,.04) 47px 48px),
   repeating-linear-gradient(90deg, transparent 0 47px, rgba(255,255,255,.04) 47px 48px),
   linear-gradient(160deg,#0e0a20 0%, #06030f 100%);
  font-family:'Orbitron';}}
.left{{position:absolute;left:54px;top:0;height:100%;width:660px;display:flex;flex-direction:column;justify-content:center;gap:6px;z-index:30}}
.pill{{font-family:'Press Start 2P';font-size:18px;color:#FFD23F;letter-spacing:3px;
  border:2px solid #FFD23F;padding:8px 14px;align-self:flex-start;border-radius:3px;margin-bottom:14px;
  text-shadow:0 0 8px rgba(255,210,63,.6)}}
.top{{font-family:'Orbitron';font-weight:900;font-size:74px;color:#fff;line-height:.95;letter-spacing:1px;
  text-shadow:3px 3px 0 #000, 0 0 22px rgba(255,255,255,.25)}}
.big{{font-family:'Orbitron';font-weight:900;font-size:210px;color:#FF2E88;line-height:.8;letter-spacing:-2px;
  text-shadow:5px 5px 0 #000, 0 0 38px rgba(255,46,136,.75)}}
.numwrap{{display:flex;align-items:flex-end;gap:18px;margin-top:8px}}
.num{{font-family:'Orbitron';font-weight:900;font-size:150px;color:#00E5FF;line-height:.8;
  text-shadow:4px 4px 0 #000, 0 0 30px rgba(0,229,255,.8)}}
.sub{{font-family:'Press Start 2P';font-size:30px;color:#fff;letter-spacing:2px;margin-bottom:16px;
  text-shadow:2px 2px 0 #000}}
.right{{position:absolute;right:-30px;top:0;height:100%;width:520px;display:flex;align-items:center;justify-content:center}}
.box{{position:absolute;width:240px;border-radius:8px;border:3px solid rgba(255,255,255,.85);
  box-shadow:0 16px 40px rgba(0,0,0,.7);transform:rotate(var(--t));object-fit:cover;height:320px}}
.box:nth-child(1){{right:230px;top:120px}}
.box:nth-child(2){{right:60px;top:70px}}
.box:nth-child(3){{right:300px;top:340px}}
.box:nth-child(4){{right:110px;top:360px}}
.box:nth-child(5){{right:340px;top:60px;width:210px;height:280px}}
.masc{{position:absolute;left:30px;bottom:18px;width:130px;height:130px;z-index:40;filter:drop-shadow(0 0 14px rgba(0,229,255,.6))}}
.scan{{position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,0) 0 3px,rgba(0,0,0,.10) 3px 4px);z-index:50}}
.vig{{position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 160px rgba(0,0,0,.7);z-index:49}}
</style></head><body>
<div class="thumb">
  <div class="right">{cards}</div>
  <div class="left">
    <div class="pill">RETROTARROS</div>
    <div class="top">{titulo_top}</div>
    <div class="big">{titulo_big}</div>
    <div class="numwrap"><div class="num">{numero}</div><div class="sub">{sub}</div></div>
  </div>
  {MASCOT}
  <div class="vig"></div><div class="scan"></div>
</div></body></html>'''


def generar(out_path, titulo_top="MI COLECCION", titulo_big="N64",
            numero="58", sub="JUEGOS", boxes=None) -> Path:
    from playwright.sync_api import sync_playwright
    boxes = boxes or []
    out_path = Path(out_path); out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = REPO / "studio" / ".thumb-tmp.html"
    tmp.write_text(_html(titulo_top, titulo_big, numero, sub, boxes), encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(tmp.resolve().as_uri()); pg.wait_for_function("document.fonts.ready"); pg.wait_for_timeout(400)
        pg.locator(".thumb").screenshot(path=str(out_path))
        b.close()
    try: tmp.unlink()
    except Exception: pass
    return out_path


if __name__ == "__main__":
    print("Modulo. Importar generar() desde un driver.")
