"""
capture-slides.py
Captura cada slide de un HTML del estudio Retrotarros como PNG 1920x1080 limpio.

Uso:
    python scripts/capture-slides.py <slug>
    python scripts/capture-slides.py n64-top-mundial
    python scripts/capture-slides.py psvita-top-precios --width 1080 --height 1920  (vertical/shorts)

Resultado:
    studio/captures/<slug>/<slug>-slide-01.png
    studio/captures/<slug>/<slug>-slide-02.png
    ...

Requisitos (una sola vez por máquina):
    pip install playwright
    python -m playwright install chromium

Convención Retrotarros:
- Render a 2x DPI para que el texto quede crisp aún cuando DaVinci lo escala.
- Viewport exacto 1920x1080 (16:9) por defecto — cubre el frame completo sin rebordes.
- Sin browser chrome, sin scrollbar (chromium headless ya lo hace).
- Salida lista para meter en edición como overlay full-screen o cortina entre tomas.
"""

import argparse
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def capture(slug: str, width: int = 1920, height: int = 1080, scale: int = 2, wait_ms: int = 400) -> int:
    repo_root = Path(__file__).parent.parent
    html_path = repo_root / "studio" / f"{slug}.html"
    out_dir = repo_root / "studio" / "captures" / slug

    if not html_path.exists():
        print(f"ERROR: no existe {html_path}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== Retrotarros · capture-slides ===")
    print(f"Slug    : {slug}")
    print(f"HTML    : {html_path}")
    print(f"Out     : {out_dir}")
    print(f"Tamaño  : {width}x{height} @ {scale}x DPI")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        page = ctx.new_page()

        # file:// URL con ruta absoluta (Windows-safe)
        url = html_path.as_uri()
        page.goto(url, wait_until="networkidle")

        # Esperar fuentes web (Orbitron, Share Tech Mono, etc.)
        page.wait_for_function("document.fonts.ready")

        # Seguridad: forzar modo limpio (sin la capa de notas de lectura/teleprompter)
        # para que las capturas nunca incluyan las notas de los hosts.
        page.evaluate("document.body.classList.remove('read-mode')")

        total = page.evaluate("document.querySelectorAll('.slide').length")
        print(f"Slides detectados: {total}")
        print()

        captured = 0
        for i in range(total):
            page.evaluate(f"go({i})")
            # Pequeña espera para imágenes lazy / transiciones / re-layout
            page.wait_for_timeout(wait_ms)

            # Ocultar la barra de navegación inferior para que la captura sea solo el contenido del slide
            page.evaluate("""
                const nav = document.querySelector('nav');
                if (nav) nav.style.display = 'none';
            """)
            page.wait_for_timeout(50)

            num = str(i + 1).zfill(2)
            out_file = out_dir / f"{slug}-slide-{num}.png"
            page.screenshot(path=str(out_file), full_page=False, omit_background=False)
            print(f"  [{num}/{str(total).zfill(2)}]  {out_file.name}")
            captured += 1

            # Restaurar nav por si el script lee algo del DOM en próxima iteración
            page.evaluate("""
                const nav = document.querySelector('nav');
                if (nav) nav.style.display = '';
            """)

        browser.close()

    print()
    print(f"=== LISTO ===")
    print(f"Capturados: {captured} PNGs en {out_dir}")
    print()
    print("Próximo paso: abrir 2-3 PNGs para revisar legibilidad.")
    print("Si el texto se ve chico → re-render con --scale 3.")
    print("Si querés versión vertical (shorts) → --width 1080 --height 1920.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Captura slides de un HTML del estudio Retrotarros.")
    parser.add_argument("slug", help="Slug del HTML (ej. n64-top-mundial)")
    parser.add_argument("--width", type=int, default=1920, help="Ancho del viewport (default 1920)")
    parser.add_argument("--height", type=int, default=1080, help="Alto del viewport (default 1080)")
    parser.add_argument("--scale", type=int, default=2, help="Device scale factor para texto crisp (default 2)")
    parser.add_argument("--wait-ms", type=int, default=400, help="Espera por slide en ms (default 400)")
    args = parser.parse_args()

    sys.exit(capture(args.slug, args.width, args.height, args.scale, args.wait_ms))


if __name__ == "__main__":
    main()
