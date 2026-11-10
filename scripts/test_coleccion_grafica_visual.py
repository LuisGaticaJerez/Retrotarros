"""Pruebas visuales de la grafica nueva de las colecciones (Chromium via Playwright, 1920 x 1080).

Sin pytest: `python scripts/test_coleccion_grafica_visual.py`. Genera en carpetas temporales los 4 decks
versionados en data/colecciones/ (NES con cajas de prueba, los otros sin cajas, para probar el respaldo)
y mide cada slide:
  - la slide no desborda su alto y nada queda cortado dentro de una tarjeta;
  - ningun texto visible baja de 20 px (fuera de la TarroVision y del numero de slide);
  - ningun texto queda cortado en horizontal;
  - la pantalla de la TarroVision del paneo mide 16:9 exacto y la del triple 4:3 exacto (o 16:9 con "ancha").
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coleccion_deck as D  # noqa: E402
import test_coleccion_grafica as TG  # noqa: E402

MIN_FUENTE_PX = 20
JS_SLIDE = """
() => {
  const out = [];
  const slide = document.querySelector('.slide.active');
  if (slide.scrollHeight > slide.clientHeight + 2) out.push('slide desborda: ' + slide.scrollHeight + ' > ' + slide.clientHeight);
  const saltar = (e) => e.closest('.tarrovision, .slide-num, .notas');
  slide.querySelectorAll('*').forEach(e => {
    if (saltar(e)) return;
    const cs = getComputedStyle(e);
    const texto = [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (texto && parseFloat(cs.fontSize) < %(min)d) out.push('fuente chica ' + cs.fontSize + ': ' + e.textContent.trim().slice(0, 30));
    if (texto && e.scrollWidth > e.clientWidth + 2 && cs.display !== 'inline') out.push('texto cortado: ' + e.className + ' ' + e.textContent.trim().slice(0, 30));
    const recortado = (cs.overflow === 'hidden' || cs.overflowY === 'hidden') && !e.matches('.g-mos,.g-mosw,.g-cell');
    if (recortado && e.scrollHeight > e.clientHeight + 2) out.push('contenido cortado: ' + e.className + ' ' + e.scrollHeight + ' > ' + e.clientHeight);
    if (e.matches('.g-cell,.g-hcard,.g-icard,.g-pcard,.g-bchart')) {
      const pr = e.getBoundingClientRect();
      [...e.children].forEach(ch => {
        const cr = ch.getBoundingClientRect();
        if (cr.bottom > pr.bottom + 2 || cr.right > pr.right + 2) out.push('hijo fuera de su tarjeta: ' + e.className + ' > ' + ch.className);
      });
    }
  });
  return out;
}
""" % {"min": MIN_FUENTE_PX}

JS_TV = """
() => [...document.querySelectorAll('.slide.active .tarrovision .tv-screen-inner')].map(e => {
  const r = e.getBoundingClientRect(); return r.width / r.height; })
"""


def _cajas_de_prueba(data: dict, carpeta: Path, slug: str) -> None:
    from PIL import Image
    (carpeta / "img" / slug).mkdir(parents=True, exist_ok=True)
    colores = [(220, 40, 90), (30, 160, 200), (230, 190, 40)]
    for i, c in enumerate(data["categorias"]):
        for k, j in enumerate(c["joyas"]):
            Image.new("RGB", (260, 375), colores[(i + k) % 3]).save(carpeta / "img" / slug / f"{D_slug(j['title'])}.jpg")


def D_slug(s: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _medir(ruta: Path, esperado_triple: float = 4 / 3) -> list[str]:
    from playwright.sync_api import sync_playwright
    fallas: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_context(viewport={"width": 1920, "height": 1080}).new_page()
            page.goto(ruta.as_uri(), wait_until="networkidle")
            page.wait_for_function("document.fonts.ready")
            n = page.evaluate("document.querySelectorAll('.slide').length")
            for i in range(n):
                page.evaluate("(i)=>{document.querySelectorAll('.slide').forEach((s,j)=>s.classList.toggle('active',j===i));"
                              "document.body.classList.remove('read-mode')}", i)
                page.wait_for_timeout(100)
                for m in sorted(set(page.evaluate(JS_SLIDE))):
                    fallas.append(f"{ruta.stem} slide {i + 1}: {m}")
                clase = page.evaluate("document.querySelector('.slide.active .g-paneo') ? 'paneo' : "
                                      "(document.querySelector('.slide.active .g-triple') ? 'triple' : '')")
                if clase:
                    esperado = 16 / 9 if clase == "paneo" else esperado_triple
                    for prop in page.evaluate(JS_TV):
                        if abs(prop - esperado) > 0.02:
                            fallas.append(f"{ruta.stem} slide {i + 1}: pantalla de la TarroVision {prop:.3f}, esperaba {esperado:.3f}")
        finally:
            browser.close()
    return fallas


def test_las_colecciones_versionadas_se_ven_bien():
    fallas: list[str] = []
    for ruta in sorted(TG.DATOS.glob("*-coleccion.json")):
        data = json.loads(ruta.read_text(encoding="utf-8"))
        slug = ruta.stem
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            if slug.startswith("nes"):
                _cajas_de_prueba(data, tmp, slug)
            data["grafica"] = "nueva"
            if slug.startswith("nes"):
                data["proximo"] = {"titulo": "NES TOP MUNDIAL", "consola": "NES", "tag": "RANKING"}
            salida = D.generar_deck(data, slug, out_dir=tmp, lista=False)
            fallas += _medir(salida)
    assert not fallas, "\n".join(fallas[:20])


def test_triple_en_16_9_con_tarrovision_ancha():
    data = json.loads((TG.DATOS / "nes-coleccion.json").read_text(encoding="utf-8"))
    data.update({"grafica": "nueva", "tarrovision": "ancha"})
    with tempfile.TemporaryDirectory() as tmp:
        salida = D.generar_deck(data, "nes-coleccion", out_dir=Path(tmp), lista=False)
        fallas = _medir(salida, esperado_triple=16 / 9)
    assert not fallas, "\n".join(fallas[:20])


def main() -> int:
    pruebas = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    fallas = 0
    for nombre, fn in pruebas:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            fallas += 1
            print(f"FALLA {nombre}: {type(exc).__name__}: {exc}")
    if fallas:
        print(f"{fallas} de {len(pruebas)} pruebas fallaron")
        return 1
    print(f"OK {len(pruebas)} pruebas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
