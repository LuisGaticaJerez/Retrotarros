# Reorganización de studio/ en carpetas unificadas — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mover los 47 episodios largos + 32 TarroShorts de `studio/*.html` (plano) a
carpetas por tipo (`studio/rankings/top-precios/`, `studio/colecciones/`, etc.), en el
repo y en el Drive, sin romper ni una sola imagen ni un solo script.

**Architecture:** Un script de migración one-shot (`git mv` para preservar historial)
mueve HTML + su `img/<slug>/` + `captures/<slug>/` como unidad a la carpeta nueva
(cero cambios de string dentro de cada HTML). Los generadores y scripts de sync se
actualizan para conocer la carpeta destino de cada categoría. Verificación automática
con Playwright sobre las 79 páginas movidas antes de tocar Drive o hacer push.

**Tech Stack:** Python (migración + generadores + verificación con Playwright), 
PowerShell (sync a Drive), Git (`git mv`).

## Global Constraints

- Ningún `<img src="...">` dentro de los HTML movidos cambia de string — solo se
  mueve la carpeta que contiene la imagen. (Spec § "Cómo se mueven los assets".)
- `studio/resenas/`, `studio/shorts/` (MP4s), `studio/pautas/`, `studio/melodias/`,
  `studio/branding/`, y todo `studio/_template-*.html` quedan SIN TOCAR.
- Los comandos CLI que Luis y Claude ya usan (`python scripts/tarroshort_render.py
  <slug>`, `python scripts/capture-slides.py <slug>`) siguen aceptando solo el slug
  pelado (sin ruta) — el script lo busca recursivo. No se rompe la muscle-memory.
- Verificación automática cubre el 100% de los archivos movidos, no una muestra
  (lección de la sesión de Reseñas: un solo `../` mal puesto rompió la caja).
- Un solo commit grande para el movimiento de archivos (más fácil de revisar/revertir
  que varios commits parciales a medio migrar).

---

### Task 1: Módulo compartido de rutas/categorías (`scripts/_studio_layout.py`)

**Files:**
- Create: `scripts/_studio_layout.py`
- Test: `.cache/test_studio_layout.py` (gitignored, script de verificación manual — no hay framework pytest en este repo)

**Interfaces:**
- Produces: `REPO: Path`, `find_html(slug: str) -> Path`,
  `episode_category(slug: str) -> str`, `short_category(slug: str) -> str`
  — usados por todas las tareas siguientes.

- [ ] **Step 1: Escribir el módulo completo**

```python
"""
scripts/_studio_layout.py - Retrotarros Studio Suite
Mapeo compartido slug -> carpeta de categoria dentro de studio/, y helper para
encontrar un HTML por slug sin importar en que subcarpeta quedo despues de la
reorganizacion de 2026-07-21. Importado por los generadores de deck, el render
de TarroShorts, y capture-slides.py -- no se repite esta logica en cada script.
"""
from __future__ import annotations
import re
from pathlib import Path


def _repo() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent.parent] + list(here.parents):
        if (p / "studio").is_dir() and (p / "scripts").is_dir():
            return p
    return here.parent.parent


REPO = _repo()
STUDIO = REPO / "studio"

# Orden importa: se evalua de arriba a abajo, la primera regla que matchea gana.
EPISODE_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"-top-mundial$", "rankings/top-mundial"),
    (r"-top-precios$", "rankings/top-precios"),
    (r"-retrotarros-vs-mundo$", "rankings/retrotarros-vs-mundo"),
    (r"-coleccion$", "colecciones"),
    (r"^saga-", "sagas"),
    (r"^retro-", "specials"),
    (r"^n64-(hardware-raro|joyas-ocultas|kirkhope-rare|nintendo-vs-playstation|no-latam)$", "curaduria-n64"),
    (r"-archivo-koko$", "archivo-koko"),
    (r"^teaser-", "teasers"),
]

SHORT_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"^tarroshort-datos-", "datos"),
    (r"^tarroshort-(mas-caros-historia|mejor-consola-retro)$", "cross-console"),
    (r"^tarroshort-.*-top-mundial$", "rankings/top-mundial"),
    (r"^tarroshort-.*-top-precios$", "rankings/top-precios"),
    (r"^tarroshort-.*-coleccion$", "colecciones"),
    (r"^tarroshort-retro-", "specials"),
]


def episode_category(slug: str) -> str:
    """Devuelve la carpeta relativa a studio/ para un episodio largo (ej. 'rankings/top-precios').
    Lanza ValueError si el slug no matchea ninguna regla conocida -- mejor fallar
    ruidoso que adivinar mal y dejar un archivo perdido."""
    for pattern, folder in EPISODE_CATEGORY_RULES:
        if re.search(pattern, slug):
            return folder
    raise ValueError(f"episode_category: '{slug}' no matchea ninguna regla conocida")


def short_category(slug: str) -> str:
    """Igual que episode_category pero para tarroshort-*.html (studio/shorts-html/)."""
    for pattern, folder in SHORT_CATEGORY_RULES:
        if re.search(pattern, slug):
            return folder
    raise ValueError(f"short_category: '{slug}' no matchea ninguna regla conocida")


def find_html(slug: str) -> Path:
    """Busca <slug>.html en todo studio/ (recursivo). Slug pelado, sin ruta --
    asi los comandos CLI existentes (python scripts/tarroshort_render.py <slug>)
    siguen funcionando igual que antes de la reorganizacion."""
    matches = list(STUDIO.glob(f"**/{slug}.html"))
    if not matches:
        raise FileNotFoundError(f"No existe {slug}.html en ninguna subcarpeta de studio/")
    if len(matches) > 1:
        raise FileExistsError(f"'{slug}.html' matcheo mas de un archivo: {matches}")
    return matches[0]
```

- [ ] **Step 2: Escribir el script de verificación manual**

```python
# .cache/test_studio_layout.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _studio_layout import episode_category, short_category

CASOS_EPISODIO = {
    "n64-top-mundial": "rankings/top-mundial",
    "n64-top-precios": "rankings/top-precios",
    "n64-retrotarros-vs-mundo": "rankings/retrotarros-vs-mundo",
    "n64-coleccion": "colecciones",
    "saga-zelda": "sagas",
    "retro-padres-gamer": "specials",
    "n64-hardware-raro": "curaduria-n64",
    "n64-archivo-koko": "archivo-koko",
    "teaser-n64-top-precios": "teasers",
}
CASOS_SHORT = {
    "tarroshort-datos-sonic": "datos",
    "tarroshort-mas-caros-historia": "cross-console",
    "tarroshort-n64-top-mundial": "rankings/top-mundial",
    "tarroshort-dreamcast-top-precios": "rankings/top-precios",
    "tarroshort-n64-coleccion": "colecciones",
    "tarroshort-retro-padres-gamer": "specials",
}

fallos = []
for slug, esperado in CASOS_EPISODIO.items():
    real = episode_category(slug)
    if real != esperado:
        fallos.append(f"episode_category({slug!r}) = {real!r}, esperaba {esperado!r}")
for slug, esperado in CASOS_SHORT.items():
    real = short_category(slug)
    if real != esperado:
        fallos.append(f"short_category({slug!r}) = {real!r}, esperaba {esperado!r}")

if fallos:
    print("FALLOS:")
    for f in fallos:
        print(" -", f)
    sys.exit(1)
print(f"OK: {len(CASOS_EPISODIO)} episodios + {len(CASOS_SHORT)} shorts clasificados correcto.")
```

- [ ] **Step 3: Correr la verificación**

Run: `python .cache/test_studio_layout.py`
Expected: `OK: 9 episodios + 6 shorts clasificados correcto.`

- [ ] **Step 4: Confirmar que TODOS los 79 slugs reales matchean (no solo los casos de prueba)**

```python
# .cache/test_studio_layout_full.py -- corre contra los nombres de archivo reales
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _studio_layout import episode_category, short_category, STUDIO

episodios = sorted(p.stem for p in STUDIO.glob("*.html") if not p.stem.startswith("_"))
shorts = sorted(p.stem for p in STUDIO.glob("tarroshort-*.html"))
episodios = [s for s in episodios if not s.startswith("tarroshort-")]

fallos = []
for slug in episodios:
    try:
        episode_category(slug)
    except ValueError as e:
        fallos.append(str(e))
for slug in shorts:
    try:
        short_category(slug)
    except ValueError as e:
        fallos.append(str(e))

print(f"{len(episodios)} episodios, {len(shorts)} shorts revisados.")
if fallos:
    print("SIN CATEGORIA:")
    for f in fallos:
        print(" -", f)
    sys.exit(1)
print("OK: todos matchean.")
```

Run: `python .cache/test_studio_layout_full.py`
Expected: `47 episodios, 32 shorts revisados.` seguido de `OK: todos matchean.` Si
aparece algo en "SIN CATEGORIA", agregar la regla que falta a `_studio_layout.py`
antes de seguir — no continuar con archivos sin categoría conocida.

- [ ] **Step 5: Commit**

```bash
git add scripts/_studio_layout.py
git commit -m "feat(studio-layout): mapeo slug->categoria + busqueda recursiva de HTML"
```

---

### Task 2: Script de migración física (mueve HTML + img + captures)

**Files:**
- Create: `.cache/migrate_studio_folders.py` (gitignored, one-shot)

**Interfaces:**
- Consumes: `episode_category`, `short_category`, `STUDIO`, `REPO` de Task 1.
- Produces: archivos físicamente movidos vía `git mv` (no hay interfaz de código,
  el resultado es el estado del filesystem + índice de git).

- [ ] **Step 1: Escribir el script de migración**

```python
"""
.cache/migrate_studio_folders.py
Mueve cada episodio/short + su img/<slug>/ + captures/<slug>/ a su carpeta de
categoria. Usa git mv (preserva historial). Caso especial: TarroShorts que
referencian el img/ de su episodio padre (no tienen carpeta propia) -- para esos
se COPIAN las imagenes referenciadas dentro de la nueva carpeta del short (no se
puede symlink de forma confiable en Drive).
Uso: python .cache/migrate_studio_folders.py [--dry-run]
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _studio_layout import REPO, STUDIO, episode_category, short_category

DRY_RUN = "--dry-run" in sys.argv


def git_mv(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"  git mv {src.relative_to(REPO)}  ->  {dst.relative_to(REPO)}")
    if not DRY_RUN:
        subprocess.run(["git", "mv", str(src), str(dst)], check=True, cwd=REPO)


def move_episode_or_short(html: Path, category: str):
    slug = html.stem
    dest_dir = STUDIO / category
    dst_html = dest_dir / html.name
    git_mv(html, dst_html)

    src_img = STUDIO / "img" / slug
    if src_img.is_dir():
        git_mv(src_img, dest_dir / "img" / slug)

    src_cap = STUDIO / "captures" / slug
    if src_cap.is_dir():
        git_mv(src_cap, dest_dir / "captures" / slug)

    return dst_html


def copy_parent_images_for_short(short_html_new_path: Path, original_text: str):
    """Si el short referencia img/<otro-slug>/ (box art reciclada del episodio
    padre), copia esas imagenes puntuales dentro de la carpeta img/<otro-slug>/
    del short movido, para que el src="img/<otro-slug>/x.jpg" siga resolviendo."""
    refs = set(re.findall(r'src="img/([^/]+)/([^"]+)"', original_text))
    if not refs:
        return
    dest_dir = short_html_new_path.parent
    for folder, filename in refs:
        # Si el short ya tiene su propia carpeta img/<folder>/ (folder == su propio
        # slug), no hay nada que copiar -- ya se movio en move_episode_or_short.
        if (dest_dir / "img" / folder / filename).exists():
            continue
        # Buscar la imagen original en CUALQUIER carpeta img/<folder>/ ya movida
        candidates = list(STUDIO.glob(f"**/img/{folder}/{filename}"))
        if not candidates:
            print(f"  [WARN] no encontre img/{folder}/{filename} para copiar a {dest_dir}")
            continue
        target = dest_dir / "img" / folder / filename
        print(f"  copy (reciclada) {candidates[0].relative_to(REPO)} -> {target.relative_to(REPO)}")
        if not DRY_RUN:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidates[0], target)


def main():
    print("=== Episodios largos ===")
    episodios = sorted(p for p in STUDIO.glob("*.html")
                        if not p.stem.startswith("_") and not p.stem.startswith("tarroshort-"))
    for html in episodios:
        cat = episode_category(html.stem)
        move_episode_or_short(html, cat)

    print("\n=== TarroShorts ===")
    shorts = sorted(STUDIO.glob("tarroshort-*.html"))
    for html in shorts:
        original_text = html.read_text(encoding="utf-8")
        cat = short_category(html.stem)
        new_path = move_episode_or_short(html, f"shorts-html/{cat}")
        copy_parent_images_for_short(new_path, original_text)

    print(f"\n{'(DRY RUN, nada se movio)' if DRY_RUN else 'LISTO.'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry run primero**

Run: `python .cache/migrate_studio_folders.py --dry-run`
Expected: 47 líneas `git mv` para episodios + sus img/captures, luego 32 líneas
para shorts (algunas con línea extra `copy (reciclada)` para los que reusan caja
del padre), sin ningún `[WARN]`. Si aparece un `[WARN]`, esa imagen reciclada no
se va a poder encontrar — investigar antes de correr en serio (probablemente el
episodio padre correspondiente no se listó en el orden esperado; los episodios se
mueven ANTES que los shorts en el script, así que sus imágenes ya deberían estar
en su carpeta nueva para cuando el short las busca).

- [ ] **Step 3: Correr en serio**

Run: `python .cache/migrate_studio_folders.py`
Expected: mismo output que el dry-run, sin `(DRY RUN...)`, termina en `LISTO.`

- [ ] **Step 4: Verificar que no quedó nada huérfano**

Run: `git status --short`
Expected: solo líneas `R  ` (renamed, de los `git mv`) y algunas `A  ` (las
imágenes copiadas por `copy_parent_images_for_short`, que son archivos nuevos, no
renames). **No debe haber ninguna línea `D ` suelta sin su `R` correspondiente** —
eso significaría que algo se borró sin moverse a destino.

Run: `find studio -maxdepth 1 -name "*.html" | grep -v "^studio/_"`
Expected: vacío — no debe quedar ningún episodio o short suelto en la raíz de
`studio/` (solo deben quedar los `_template-*.html`).

---

### Task 3: Verificación automática de imágenes (Playwright, 100% de los archivos)

**Files:**
- Create: `.cache/verify_studio_images.py` (gitignored)

**Interfaces:**
- Consumes: ninguna de las tasks anteriores directamente — recorre el filesystem.

- [ ] **Step 1: Escribir el verificador**

```python
"""
.cache/verify_studio_images.py
Abre CADA .html movido (episodios + shorts) con Playwright y confirma que todas
las <img> referenciadas cargaron (naturalWidth > 0). No es una muestra: son los
79 archivos completos. Lección de la migracion de Resenas: un solo "../" mal
puesto rompe la caja y un spot-check de 2-3 archivos no lo habria detectado.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent
STUDIO = REPO / "studio"

targets = sorted(
    p for p in STUDIO.rglob("*.html")
    if not p.stem.startswith("_") and "img" not in p.relative_to(STUDIO).parts
    and "captures" not in p.relative_to(STUDIO).parts
)

rotas = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    for html in targets:
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        broken = page.evaluate(
            "Array.from(document.querySelectorAll('img'))"
            ".filter(i => i.src && i.naturalWidth === 0 && getComputedStyle(i).display !== 'none')"
            ".map(i => i.getAttribute('src'))"
        )
        if broken:
            rotas.append((html.relative_to(REPO), broken))
            print(f"  [ROTO] {html.relative_to(REPO)}: {broken}")
        else:
            print(f"  [OK]   {html.relative_to(REPO)}")
    browser.close()

print(f"\n{len(targets)} archivos revisados, {len(rotas)} con imagenes rotas.")
if rotas:
    sys.exit(1)
```

- [ ] **Step 2: Correr la verificación**

Run: `python .cache/verify_studio_images.py`
Expected: una línea `[OK]` por cada uno de los 79 archivos, terminando en
`79 archivos revisados, 0 con imagenes rotas.` Si algo sale `[ROTO]`, corregir esa
carpeta específica (revisar si el `git mv` de su `img/<slug>/` falló o si es un
short con imagen reciclada que no se copió) y volver a correr este script — no
seguir a la Task 4 hasta que dé `0 con imagenes rotas`.

---

### Task 4: Actualizar los generadores de deck (BASE + carpeta de salida)

**Files:**
- Modify: `scripts/coleccion_deck.py`
- Modify: `scripts/saga_deck.py`
- Modify: `scripts/top_deck.py`
- Modify: `scripts/tarroshort_datos.py`
- Modify: `scripts/tarroshort_render.py`

**Interfaces:**
- Consumes: `episode_category`, `short_category` de `scripts/_studio_layout.py` (Task 1).

- [ ] **Step 1: `coleccion_deck.py` — BASE fijo + salida a `colecciones/`**

Reemplazar:
```python
BASE = REPO / "studio" / "n64-coleccion.html"  # fuente de CSS/JS canonico
```
por:
```python
BASE = REPO / "studio" / "colecciones" / "n64-coleccion.html"  # fuente de CSS/JS canonico
```

Reemplazar:
```python
    out = REPO / "studio" / f"{out_slug}.html"
```
por:
```python
    out_dir = REPO / "studio" / "colecciones"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
```

- [ ] **Step 2: `saga_deck.py` — BASE fijo + salida a `sagas/`**

`saga_deck.py` no clona CSS de un archivo externo (el CSS está inline en el propio
script, variable `CSS`), así que no tiene un `BASE` que ajustar. Solo cambia la
salida. Reemplazar:
```python
    out = REPO / "studio" / f"{out_slug}.html"
```
por:
```python
    out_dir = REPO / "studio" / "sagas"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
```

- [ ] **Step 3: `top_deck.py` — BASE fijo + salida enrutada por categoría**

Reemplazar:
```python
BASE = REPO / "studio" / "snes-top-mundial.html"
```
por:
```python
BASE = REPO / "studio" / "rankings" / "top-mundial" / "snes-top-mundial.html"
```

Al inicio del archivo, después de `REPO = _repo()`, agregar el import:
```python
import sys
sys.path.insert(0, str(REPO / "scripts"))
from _studio_layout import episode_category
```

Reemplazar (dentro de `generar_top`):
```python
    out = REPO / "studio" / f"{out_slug}.html"
```
por:
```python
    out_dir = REPO / "studio" / episode_category(out_slug)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{out_slug}.html"
```

- [ ] **Step 4: `tarroshort_datos.py` — BASE se mantiene (es un template, no se
  movió), salida a `shorts-html/datos/`**

`BASE = REPO / "studio" / "_template-tarroshort.html"` no cambia (los templates
`_template-*` quedan en la raíz de `studio/`, fuera del alcance de esta migración).

Reemplazar:
```python
    out = REPO / "studio" / f"tarroshort-{slug}.html"
```
por:
```python
    out_dir = REPO / "studio" / "shorts-html" / "datos"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"tarroshort-{slug}.html"
```

- [ ] **Step 5: `tarroshort_render.py` — leer/escribir episodios y shorts en su
  nueva carpeta**

Al inicio del archivo, después de `def _resolve_repo() -> Path:` y su uso, agregar:
```python
import sys as _sys
_sys.path.insert(0, str(_resolve_repo() / "scripts"))
from _studio_layout import find_html, episode_category, short_category
```

En `generar_tarroshort`, reemplazar:
```python
    html_path = studio / f"{slug}.html"
    if not html_path.exists():
        raise FileNotFoundError(f"No existe el HTML del short: {html_path}")
```
por:
```python
    try:
        html_path = find_html(slug)
    except FileNotFoundError:
        raise FileNotFoundError(f"No existe el HTML del short: studio/**/{slug}.html")
```

En `construir_desde_pauta`, reemplazar:
```python
    out_path = repo / "studio" / f"tarroshort-{out_slug}.html"
```
por:
```python
    out_dir = repo / "studio" / "shorts-html" / short_category(f"tarroshort-{out_slug}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"tarroshort-{out_slug}.html"
```

En `construir_short_highlights`, reemplazar:
```python
    html_src = repo / "studio" / f"{source_slug}.html"
    if not html_src.exists():
        raise FileNotFoundError(f"No existe el episodio: {html_src}")
```
por:
```python
    try:
        html_src = find_html(source_slug)
    except FileNotFoundError:
        raise FileNotFoundError(f"No existe el episodio: studio/**/{source_slug}.html")
```

y reemplazar:
```python
    out_path = repo / "studio" / f"tarroshort-{out_slug}.html"
```
(la segunda ocurrencia, dentro de `construir_short_highlights`) por:
```python
    cat = "colecciones" if formato == "coleccion" else "abriendo-el-tarro"
    out_dir = repo / "studio" / "shorts-html" / cat
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"tarroshort-{out_slug}.html"
```

- [ ] **Step 6: Verificar que los generadores siguen corriendo**

Run: `python -c "import sys; sys.path.insert(0,'scripts'); from resena_deck import generar_resena; print('resena_deck OK, sin tocar')"`
(confirma que no rompimos nada fuera del alcance — `resena_deck.py` no se toca en
esta migración, ya vive en su propia carpeta desde ayer)

Run: `python .cache/test_studio_layout_full.py`
Expected: sigue en `OK: todos matchean.` (no debería haber cambiado nada acá,
es solo para confirmar que Task 1 sigue intacta antes de seguir)

- [ ] **Step 7: Commit**

```bash
git add scripts/coleccion_deck.py scripts/saga_deck.py scripts/top_deck.py scripts/tarroshort_datos.py scripts/tarroshort_render.py
git commit -m "feat(generadores): apuntar BASE + salida a las carpetas de categoria nuevas"
```

---

### Task 5: Actualizar `capture-slides.py`

**Files:**
- Modify: `scripts/capture-slides.py`

**Interfaces:**
- Consumes: `find_html` de `scripts/_studio_layout.py` (Task 1).

- [ ] **Step 1: Buscar el HTML recursivo + guardar capturas al lado (no en un árbol aparte)**

Reemplazar:
```python
    repo_root = Path(__file__).parent.parent
    html_path = repo_root / "studio" / f"{slug}.html"
    out_dir = repo_root / "studio" / "captures" / slug
```
por:
```python
    import sys
    repo_root = Path(__file__).parent.parent
    sys.path.insert(0, str(repo_root / "scripts"))
    from _studio_layout import find_html
    html_path = find_html(slug)
    out_dir = html_path.parent / "captures" / slug
```

- [ ] **Step 2: Probar con un slug real ya migrado**

Run: `python scripts/capture-slides.py n64-top-precios`
Expected: genera PNGs en `studio/rankings/top-precios/captures/n64-top-precios/`
(mismo comando que Luis usaba antes, mismo resultado, carpeta destino distinta).

- [ ] **Step 3: Commit**

```bash
git add scripts/capture-slides.py
git commit -m "feat(capture-slides): buscar HTML recursivo, guardar captures al lado del episodio"
```

---

### Task 6: Actualizar los DOS scripts de sync a Drive

> Foco especial pedido por Luis — son los scripts que más importan para que nada
> se pierda al ir a grabar.

**Files:**
- Modify: `scripts/sync-to-drive.ps1`
- Modify: `scripts/sync-tarrobot-to-drive.ps1`

- [ ] **Step 1: `sync-to-drive.ps1` — recorrer recursivo, reflejar la carpeta de categoría en destino**

Reemplazar:
```powershell
$htmlFiles = Get-ChildItem -Path $RepoStudio -Filter "*.html" -File
```
por:
```powershell
# Recursivo: los episodios y shorts viven en subcarpetas por categoria desde
# 2026-07-21 (rankings/top-precios/, colecciones/, shorts-html/datos/, etc.)
$htmlFiles = Get-ChildItem -Path $RepoStudio -Filter "*.html" -File -Recurse |
    Where-Object { $_.DirectoryName -notmatch '\\resenas($|\\)' }
```
(se excluye `resenas\` porque ya tiene su propio bloque de sync, más abajo en el
script, con la lógica especial de imágenes compartidas)

El resto del bucle (`foreach ($html in $htmlFiles) { ... }`) queda igual — sigue
usando `$slug = [System.IO.Path]::GetFileNameWithoutExtension($html.Name)` y
`$destDir = Join-Path $DriveRoot $slug`, que no cambia: la carpeta de Drive por
episodio sigue siendo plana por slug (`Studio\n64-top-precios\`), solo el ORIGEN
en el repo ahora es recursivo. **La carpeta de Drive NO se anida** — ver Step 2
para la corrección de eso.

Ahora, para que el Drive SÍ quede con el árbol de categorías (pedido explícito de
Luis: "espejo exacto de la nueva estructura"), reemplazar:
```powershell
    $destDir = Join-Path $DriveRoot $slug
```
por:
```powershell
    $relCategoria = $html.DirectoryName.Substring($RepoStudio.Length).TrimStart('\')
    $destDir = if ($relCategoria) { Join-Path $DriveRoot (Join-Path $relCategoria $slug) } else { Join-Path $DriveRoot $slug }
```

Y en la sección `# === 2. VERIFICACION ===`, reemplazar:
```powershell
    $destHtml = Join-Path (Join-Path $DriveRoot $slug) "$slug.html"
```
por:
```powershell
    $relCategoria = $html.DirectoryName.Substring($RepoStudio.Length).TrimStart('\')
    $destSlugDir = if ($relCategoria) { Join-Path $DriveRoot (Join-Path $relCategoria $slug) } else { Join-Path $DriveRoot $slug }
    $destHtml = Join-Path $destSlugDir "$slug.html"
```

- [ ] **Step 2: Actualizar el comentario de cabecera del script**

Reemplazar:
```powershell
# Estructura resultante en Drive (G:\Mi unidad\Studio\):
#   <slug>/<slug>.html
#   <slug>/img/<slug>/*.{jpg,png}
#   pautas/pauta-<slug>.docx
#   pautas/discusion-<slug>.docx
```
por:
```powershell
# Estructura resultante en Drive (G:\Mi unidad\Studio\), espejo del repo desde
# la reorganizacion de 2026-07-21:
#   <categoria>/[<subcategoria>/]<slug>/<slug>.html
#   <categoria>/[<subcategoria>/]<slug>/img/<slug>/*.{jpg,png}
#   pautas/pauta-<slug>.docx
#   pautas/discusion-<slug>.docx
# Ejemplo: rankings/top-precios/n64-top-precios/n64-top-precios.html
```

- [ ] **Step 3: `sync-tarrobot-to-drive.ps1` — el bloque de episodios (2b) ya
  necesitaba `-Recurse` desde el fix de Reseñas, extenderlo al resto**

Ya se corrigió para `studio\resenas` el 2026-07-21 anterior (bloque "2b-bis").
Ahora hace falta lo mismo para el resto de episodios y shorts. Reemplazar:
```powershell
$episodios = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Filter "*.html" -File |
    Where-Object { $_.Name -notlike "_*" }
foreach ($ep in $episodios) {
    $relPath = "studio\$($ep.Name)"
    Sync-Item $relPath
}
```
por:
```powershell
$episodios = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Filter "*.html" -Recurse -File |
    Where-Object { $_.Name -notlike "_*" -and $_.DirectoryName -notmatch '\\resenas($|\\)' }
foreach ($ep in $episodios) {
    $relPath = $ep.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath
}
```

(el bloque `studio\img` ya se sincroniza completo con `-Recursive` desde antes,
así que las imágenes en sus nuevas subcarpetas de categoría se llevan solas — no
hace falta tocar esa parte)

- [ ] **Step 4: Probar ambos scripts en modo lectura antes de correr en serio**

Run: `powershell -File scripts/sync-to-drive.ps1` (no tiene modo dry-run — leer
la salida con cuidado antes de confirmar que está bien)
Expected: una línea `HTML → G:\Mi unidad\Studio\rankings\top-precios\n64-top-precios\n64-top-precios.html`
por cada episodio (con la ruta de categoría de verdad, no plana), termina en
`OK - los 79 HTMLs estan en su carpeta por-episodio.` (más las 5 reseñas de ayer
si `resenas` no quedó excluido correctamente — revisar que no se dupliquen).

- [ ] **Step 5: Commit**

```bash
git add scripts/sync-to-drive.ps1 scripts/sync-tarrobot-to-drive.ps1
git commit -m "feat(sync): reflejar la nueva estructura de carpetas de studio/ en el Drive"
```

---

### Task 7: Actualizar los links en docs/ (~81 referencias)

**Files:**
- Create: `.cache/fix_doc_links.py` (gitignored, one-shot)
- Modify: ~30-40 archivos dentro de `docs/` (los que tengan links `studio/<slug>.html`)

- [ ] **Step 1: Escribir el script de reemplazo**

```python
"""
.cache/fix_doc_links.py
Reescribe links "studio/<slug>.html" -> "studio/<categoria>/<slug>.html" en todo
docs/*.md y docs/arcos/*.md, usando el mismo mapeo de _studio_layout.py.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _studio_layout import REPO, episode_category, short_category

DOCS = REPO / "docs"
PATTERN = re.compile(r'studio/(tarroshort-)?([a-z0-9-]+)\.html')

cambios = 0
for md in list(DOCS.glob("*.md")) + list(DOCS.glob("arcos/*.md")) + list(DOCS.glob("superpowers/**/*.md")):
    text = md.read_text(encoding="utf-8")

    def repl(m):
        global cambios
        prefix, slug = m.group(1), m.group(2)
        full_slug = f"{prefix or ''}{slug}"
        try:
            cat = short_category(full_slug) if prefix else episode_category(slug)
            folder = f"shorts-html/{cat}" if prefix else cat
        except ValueError:
            return m.group(0)  # no matchea ninguna regla (ej. _template-*) -> no tocar
        cambios += 1
        return f"studio/{folder}/{full_slug}.html"

    new_text = PATTERN.sub(repl, text)
    if new_text != text:
        md.write_text(new_text, encoding="utf-8")
        print(f"  {md.relative_to(REPO)}")

print(f"\n{cambios} links actualizados.")
```

- [ ] **Step 2: Correr y revisar el diff**

Run: `python .cache/fix_doc_links.py`
Expected: lista de archivos tocados + `N links actualizados.` (N cercano a 81,
puede ser menos si algunos links ya apuntaban a `resenas/` que no se toca).

Run: `git diff --stat docs/`
Expected: ~30-40 archivos modificados, diffs chicos (una línea por link).

- [ ] **Step 3: Revisar manualmente que no se rompió nada raro**

Run: `git diff docs/arcos/n64.md | head -60`
Expected: los links de la tabla de inventario de episodios ahora apuntan a
`../../studio/curaduria-n64/n64-hardware-raro.html` etc. (la ruta relativa desde
`docs/arcos/` sigue siendo `../../studio/...`, eso NO cambia — solo lo que viene
después de `studio/`).

- [ ] **Step 4: Commit**

```bash
git add docs/
git commit -m "docs: actualizar ~81 links a studio/ con las carpetas de categoria nuevas"
```

---

### Task 8: Verificación final + push

- [ ] **Step 1: Re-correr la verificación de imágenes completa una vez más**

Run: `python .cache/verify_studio_images.py`
Expected: `79 archivos revisados, 0 con imagenes rotas.` (confirma que los cambios
de las Tasks 4-7 no rompieron nada que la Task 3 ya había dejado bien)

- [ ] **Step 2: Confirmar que no queda nada suelto en la raíz de studio/**

Run: `ls studio/*.html`
Expected: solo los `_template-*.html` (ningún episodio ni short suelto).

- [ ] **Step 3: Push**

Pedir confirmación a Luis antes de este paso (regla del proyecto: operaciones
remotas piden confirmación explícita). Comando concreto:
```bash
git push origin master
```

---

### Task 9: Sync a Drive real + verificación en el Drive

- [ ] **Step 1: Correr ambos scripts de sync**

Run: `powershell -File scripts/sync-to-drive.ps1`
Run: `powershell -File scripts/sync-tarrobot-to-drive.ps1`
Expected: ambos terminan en su mensaje de "Sincronización/SYNC completa", sin
`[ERROR]` en la verificación de `sync-to-drive.ps1`.

- [ ] **Step 2: Verificar en el Drive real que el árbol quedó como se espera**

Run (PowerShell):
```powershell
Get-ChildItem "G:\Mi unidad\Studio\rankings\top-precios" -Directory | Select-Object Name
Test-Path "G:\Mi unidad\Studio\rankings\top-precios\n64-top-precios\n64-top-precios.html"
```
Expected: lista las 8 carpetas de consola, y `Test-Path` da `True`.

- [ ] **Step 3: Avisar a Luis**

Resumen de qué carpetas quedaron dónde (repo + Drive), el SHA del commit
pusheado, y recordar que las carpetas viejas planas de Drive (si Google Drive
Desktop no las borró solas al mover) puede que necesiten limpieza manual — Drive
Desktop a veces deja carpetas vacías huérfanas tras un `Move-Item`; revisar
`G:\Mi unidad\Studio\` a simple vista y borrar a mano las que quedaron vacías.

---

## Self-Review

**Spec coverage:** taxonomía completa (Task 2 + `_studio_layout.py`), assets
co-ubicados sin tocar rutas internas (Task 2), caso especial de shorts con caja
reciclada (Task 2 `copy_parent_images_for_short`), scripts de sync con foco
especial (Task 6), docs (Task 7), verificación total no-muestra (Task 3 + Task 8
Step 1), orden repo-antes-que-Drive (Tasks 1-8 antes de Task 9). Todo cubierto.

**Placeholder scan:** sin TBD/TODO, todo el código de cada step es completo y
ejecutable tal cual está escrito.

**Consistencia de tipos/nombres:** `episode_category`, `short_category`,
`find_html`, `REPO`, `STUDIO` se usan con el mismo nombre y firma en todas las
tasks que los consumen (definidos una sola vez en Task 1).
