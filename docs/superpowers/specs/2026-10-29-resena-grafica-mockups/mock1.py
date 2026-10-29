"""Mockups grafica de reseñas, pantalla 1: portada, ficha, veredicto (antes y despues).
Usa el HTML real de The Sims y le inyecta cambios solo para la captura."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(r"D:\Recursos Retrotarros\repo\.claude\worktrees\silly-cray-d933c3")
OUT = Path(sys.argv[1])
HTML = REPO / "studio" / "resenas" / "resena-the-sims.html"

PORTADA = """
const s = document.querySelectorAll('.slide')[0];
s.style.overflow = 'hidden';
const bg = document.createElement('div');
bg.style.cssText = "position:absolute;inset:-40px;background:url('img/resenas/the-sims.jpg') center/cover;filter:blur(18px) brightness(.38) saturate(1.2);z-index:0";
s.prepend(bg);
const box = document.createElement('img');
box.src = 'img/resenas/the-sims.jpg';
box.style.cssText = "position:absolute;right:120px;top:50%;transform:translateY(-50%) rotate(3deg);height:78%;border-radius:6px;box-shadow:0 0 60px rgba(255,46,136,.55),0 18px 50px rgba(0,0,0,.8);z-index:1";
s.appendChild(box);
const p = s.querySelector('.portada');
p.style.position = 'relative'; p.style.zIndex = 2; p.style.alignItems = 'flex-start'; p.style.textAlign = 'left'; p.style.paddingLeft = '90px'; p.style.maxWidth = '62%';
"""

FICHA = """
const s = document.querySelectorAll('.slide')[1];
const st = s.querySelectorAll('.ficha-stat')[0];
const val = st.querySelector('.val');
const plats = [['PC','2000'],['MAC','2000'],['PS2','2003'],['XBOX','2003'],['GAMECUBE','2003']];
val.innerHTML = plats.map((p,i)=>`<span class="chip${i===0?' first':''}"><b>${p[0]}</b><i>${p[1]}</i></span>`).join('<span class="arr">▸</span>');
val.style.cssText = 'display:flex;flex-wrap:wrap;align-items:center;gap:8px';
const css = document.createElement('style');
css.textContent = `.chip{display:inline-flex;flex-direction:column;align-items:center;padding:6px 14px;border:2px solid rgba(0,229,255,.55);border-radius:6px;color:#00E5FF;font-family:Orbitron;font-size:20px;line-height:1.1}
.chip i{font-style:normal;font-family:'Share Tech Mono';font-size:14px;color:rgba(255,255,255,.65)}
.chip.first{background:#FFD23F;color:#06030f;border-color:#FFD23F;box-shadow:0 0 18px rgba(255,210,63,.55)}.chip.first i{color:#06030f}
.arr{color:#FF2E88;font-size:20px}`;
document.head.appendChild(css);
"""

VEREDICTO = """
const s = document.querySelectorAll('.slide')[6];
const v = s.querySelector('.veredicto');
const tag = v.querySelector('.ver-tag');
const wrap = document.createElement('div');
wrap.style.cssText = 'display:flex;gap:14px;margin-top:6px';
['IMPRESCINDIBLE','JUEGAZO','MEMORABLE','COLECCIONABLE'].forEach((t,i)=>{
  const d = document.createElement('div');
  const on = i===0;
  d.textContent = t;
  d.style.cssText = `font-family:Orbitron;font-weight:700;font-size:20px;letter-spacing:1px;padding:10px 20px;border-radius:6px;border:2px solid ${on?'#FFD23F':'rgba(255,255,255,.25)'};color:${on?'#FFD23F':'rgba(255,255,255,.4)'};${on?'box-shadow:0 0 20px rgba(255,210,63,.5)':''}`;
  wrap.appendChild(d);
});
tag.after(wrap);
"""


def shot(page, idx, name, js=None):
    page.goto(HTML.as_uri(), wait_until="networkidle")
    page.wait_for_function("document.fonts.ready")
    page.evaluate("document.body.classList.remove('read-mode')")
    page.evaluate(f"go({idx})")
    if js:
        page.evaluate(js)
    page.wait_for_timeout(500)
    page.evaluate("document.querySelector('nav').style.display='none';document.querySelectorAll('.no-capture').forEach(e=>e.style.display='none')")
    page.screenshot(path=str(OUT / name))
    print("ok", name)


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1).new_page()
    shot(page, 0, "m1-portada-antes.png")
    shot(page, 0, "m1-portada-despues.png", PORTADA)
    shot(page, 1, "m1-ficha-antes.png")
    shot(page, 1, "m1-ficha-despues.png", FICHA)
    shot(page, 6, "m1-veredicto-antes.png")
    shot(page, 6, "m1-veredicto-despues.png", VEREDICTO)
    b.close()
