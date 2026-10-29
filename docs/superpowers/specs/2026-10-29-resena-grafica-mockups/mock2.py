"""Mockups grafica de reseñas, pantalla 2: contexto, jugabilidad, audiovisual, cierre."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(r"D:\Recursos Retrotarros\repo\.claude\worktrees\silly-cray-d933c3")
OUT = Path(sys.argv[1])
SIMS = REPO / "studio" / "resenas" / "resena-the-sims.html"
CMD = REPO / "studio" / "resenas" / "resena-commandos-behind-enemy-lines.html"

CTX_IMG = """
const c = document.querySelectorAll('.slide')[2].querySelector('.contexto');
const img = document.createElement('img');
img.src = 'img/resenas/commandos-behind-enemy-lines.jpg';
img.style.cssText = 'height:70%;border-radius:6px;box-shadow:0 0 40px rgba(0,229,255,.4);border:2px solid rgba(255,255,255,.25)';
const wrap = document.createElement('div');
wrap.style.cssText = 'display:flex;flex-direction:column;gap:26px;align-items:flex-start;text-align:left;max-width:1000px';
while (c.firstChild) wrap.appendChild(c.firstChild);
c.style.cssText += ';flex-direction:row;gap:80px;padding:0 90px;align-items:center;justify-content:center';
c.appendChild(img); c.appendChild(wrap);
"""

CTX_CIFRA = """
const c = document.querySelectorAll('.slide')[2].querySelector('.contexto');
const body = c.querySelector('.ctx-body');
const f = document.createElement('div');
f.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:10px';
f.innerHTML = '<div style="font-family:Orbitron;font-weight:900;font-size:104px;line-height:1;color:#FFD23F;text-shadow:0 0 30px rgba(255,210,63,.45)"><span style="color:#00E5FF">15.000</span><span style="color:#FF2E88;margin:0 34px">&#9656;</span>700.000+</div>'
  + '<div style="font-family:Press Start 2P;font-size:15px;letter-spacing:4px;color:rgba(255,255,255,.7)">COPIAS ESPERADAS &nbsp;&#9656;&nbsp; COPIAS VENDIDAS</div>';
body.before(f);
body.style.fontSize = '30px';
"""

JUGAB = """
const side = document.querySelectorAll('.slide')[4].querySelector('.gp-side');
const items = [['01','CONTROLAS CON EL MOUSE','Clic en un objeto y eliges la accion'],
               ['02','OCHO NECESIDADES','Hambre, baño, energia, diversion y mas'],
               ['03','CONSTRUYE TU CASA','20.000 simoleones para empezar']];
side.innerHTML = items.map(i => `<div style="display:flex;gap:22px;align-items:center;margin-bottom:26px"><div style="font-family:'Press Start 2P';font-size:20px;color:#06030f;background:#FFD23F;padding:16px 14px;border-radius:6px;min-width:72px;text-align:center">${i[0]}</div><div><div style="font-family:Orbitron;font-weight:900;font-size:26px;color:#fff;letter-spacing:1px">${i[1]}</div><div style="font-family:'Share Tech Mono';font-size:21px;color:rgba(255,255,255,.78);margin-top:4px">${i[2]}</div></div></div>`).join('');
"""

AUDIO = """
const side = document.querySelectorAll('.slide')[5].querySelector('.gp-side');
const c = document.createElement('div');
c.style.cssText = 'margin-top:26px;border:2px solid #00E5FF;border-radius:8px;padding:16px 22px;display:flex;flex-direction:column;gap:6px';
c.innerHTML = "<div style=\\"font-family:'Press Start 2P';font-size:12px;letter-spacing:3px;color:#00E5FF\\">BANDA SONORA</div><div style=\\"font-family:Orbitron;font-weight:700;font-size:28px;color:#fff\\">Jerry Martin &middot; Marc Russo</div>";
side.appendChild(c);
"""

CIERRE = """
const d = document.querySelectorAll('.slide')[7].querySelector('.divider');
const card = document.createElement('div');
card.style.cssText = 'margin-top:38px;display:flex;align-items:center;gap:30px;border:2px solid #FF2E88;border-radius:10px;padding:18px 34px;background:rgba(255,46,136,.08)';
card.innerHTML = "<img src='img/resenas/god-of-war.jpg' style='height:170px;border-radius:5px;box-shadow:0 0 24px rgba(255,46,136,.5)'><div style='text-align:left'><div style=\\"font-family:'Press Start 2P';font-size:14px;letter-spacing:4px;color:#FFD23F\\">PROXIMA RESEÑA</div><div style='font-family:Orbitron;font-weight:900;font-size:50px;color:#fff;margin-top:10px'>GOD OF WAR</div><div style=\\"font-family:'Share Tech Mono';font-size:22px;color:rgba(255,255,255,.75);margin-top:8px\\">PlayStation 2 &middot; 2005</div></div>";
d.appendChild(card);
"""


def shot(page, html, idx, name, js=None):
    page.goto(html.as_uri(), wait_until="networkidle")
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
    shot(page, CMD, 2, "m2-contexto-antes.png")
    shot(page, CMD, 2, "m2-contexto-imagen.png", CTX_IMG)
    shot(page, CMD, 2, "m2-contexto-cifra.png", CTX_CIFRA)
    shot(page, SIMS, 4, "m2-jugab-antes.png")
    shot(page, SIMS, 4, "m2-jugab-despues.png", JUGAB)
    shot(page, SIMS, 5, "m2-audio-antes.png")
    shot(page, SIMS, 5, "m2-audio-despues.png", AUDIO)
    shot(page, SIMS, 7, "m2-cierre-antes.png")
    shot(page, SIMS, 7, "m2-cierre-despues.png", CIERRE)
    b.close()
