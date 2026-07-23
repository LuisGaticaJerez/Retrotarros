# TarroBot Studio-Root Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar la raiz de la app TarroBot (`RETROTARROS_REPO`) de la raiz del contenido de estudio (`RETROTARROS_STUDIO_ROOT`, nueva), y dejar de mirrorear el contenido completo de `studio/` dentro de `Studio\tarrobot\` en el sync de Drive.

**Architecture:** Un modulo compartido (`_studio_layout.py`) resuelve `STUDIO` leyendo `RETROTARROS_STUDIO_ROOT` si esta seteada, si no cae a `REPO/studio` (comportamiento actual, sin cambios en desarrollo local). Los scripts que leen/escriben contenido de episodios (no datos propios de la app) importan `STUDIO` de ahi en vez de calcular `repo / "studio"` a mano. El script de sync a Drive deja de copiar HTML/img/captures de episodios dentro de `Studio\tarrobot\studio\`.

**Tech Stack:** Python 3 (stdlib `pathlib`/`os`/`re`), PowerShell 5.1+.

## Global Constraints

- No hay PC de estudio con TarroBot instalado todavia (confirmado por Luis) -> no hace falta paso de migracion inmediato, solo dejar la instruccion documentada.
- `RETROTARROS_STUDIO_ROOT` ausente -> fallback a `REPO/studio`, para no romper el desarrollo local (repo = fuente unica hoy).
- No se toca `tarrobot.py` ni `obs_recorder.py` (su uso de `studio/` es datos propios de la app: templates, pautas, melodias, tarrobot-out, sesiones -- confirmado revisando cada linea antes de escribir este plan).
- No se toca `studio/exports/` (descripciones YouTube generadas por `tarrobot-live.py`) -- es output propio de la app, agrupado junto a `studio/shorts/`/`studio/sessions/` en la documentacion existente (`docs/HANDOFF-tarrobot.md:66`).
- Referencia de diseño completa: `docs/superpowers/specs/2026-07-23-tarrobot-studio-root-split-design.md`.

---

### Task 1: `_studio_layout.py` resuelve `STUDIO` via `RETROTARROS_STUDIO_ROOT`

**Files:**
- Modify: `scripts/_studio_layout.py:21-22`

**Interfaces:**
- Produces: `STUDIO: Path` (modulo-level, ya existia -- ahora es env-var-aware). `REPO: Path` sin cambios. `find_html`, `episode_category`, `short_category` sin cambios de firma (usan `STUDIO` internamente, ya lo hacian).

- [ ] **Step 1: Modificar la resolucion de `STUDIO`**

Reemplazar (líneas 21-22):
```python
REPO = _repo()
STUDIO = REPO / "studio"
```
por:
```python
import os

REPO = _repo()


def _studio_root() -> Path:
    env = os.environ.get("RETROTARROS_STUDIO_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return REPO / "studio"


STUDIO = _studio_root()
```

También hay que mover `import os` al bloque de imports de arriba del archivo (junto a `import re`), no dejarlo suelto en medio del modulo. El archivo completo de imports queda:
```python
from __future__ import annotations
import os
import re
from pathlib import Path
```
Y la funcion `_studio_root()` se define despues de `_repo()` y antes de `REPO = _repo()` no hace falta reordenar mas nada -- queda:
```python
def _repo() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent.parent] + list(here.parents):
        if (p / "studio").is_dir() and (p / "scripts").is_dir():
            return p
    return here.parent.parent


def _studio_root() -> Path:
    env = os.environ.get("RETROTARROS_STUDIO_ROOT")
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    return REPO / "studio"


REPO = _repo()
STUDIO = _studio_root()
```
(Nota: `_studio_root()` referencia `REPO`, que debe estar asignado ANTES de llamarla -- por eso `REPO = _repo()` va antes de `STUDIO = _studio_root()`, aunque la funcion se defina arriba. Python resuelve el nombre `REPO` en tiempo de llamada, no de definicion, asi que esto es valido.)

- [ ] **Step 2: Verificar que sigue funcionando sin la variable seteada (caso desarrollo local)**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "import sys; sys.path.insert(0,'scripts'); import importlib; import _studio_layout; importlib.reload(_studio_layout); print('STUDIO =', _studio_layout.STUDIO); print('existe:', _studio_layout.STUDIO.exists())"
```
Expected: `STUDIO = ...\studio` (ruta del repo local) y `existe: True`.

- [ ] **Step 3: Verificar que la variable de entorno SI se respeta cuando esta seteada**

Run (PowerShell):
```powershell
cd "D:\Recursos Retrotarros\repo"
$env:RETROTARROS_STUDIO_ROOT = "D:\Recursos Retrotarros\repo\studio\rankings"
python -c "import sys; sys.path.insert(0,'scripts'); import _studio_layout; print('STUDIO =', _studio_layout.STUDIO)"
Remove-Item Env:\RETROTARROS_STUDIO_ROOT
```
Expected: `STUDIO = D:\Recursos Retrotarros\repo\studio\rankings` (la carpeta que se seteo, no `studio/` a secas). El `Remove-Item` al final es obligatorio -- si queda seteada, los pasos siguientes de este plan (que corren `capture-slides.py`/`tarroshort_render.py` contra el repo real) van a fallar buscando HTMLs dentro de `studio/rankings` en vez de `studio/`.

- [ ] **Step 4: Confirmar que `find_html`/`episode_category`/`short_category` siguen funcionando igual (regresion)**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "
import sys; sys.path.insert(0,'scripts')
import _studio_layout as L
print(L.find_html('n64-top-precios'))
print(L.episode_category('n64-top-precios'))
print(L.short_category('tarroshort-datos-tetris'))
"
```
Expected: 3 lineas sin excepcion, la primera con la ruta real del HTML (`studio\rankings\top-precios\n64-top-precios.html`), la segunda `rankings/top-precios`, la tercera `datos`.

- [ ] **Step 5: Commit**

```bash
git add scripts/_studio_layout.py
git commit -m "feat(studio-layout): STUDIO respeta RETROTARROS_STUDIO_ROOT si esta seteada

Antes STUDIO siempre era REPO/studio, ignorando cualquier variable de
entorno. Ahora, si RETROTARROS_STUDIO_ROOT esta seteada y existe, se usa
esa ruta. Sin la variable (caso desarrollo local), el comportamiento no
cambia. Primer paso para que TarroBot deje de mantener su propia copia
de studio/ y lea el contenido compartido directo desde Drive/Studio."
```

---

### Task 2: `tarroshort_render.py` escribe HTML generado en `STUDIO`, no en `repo/studio`

**Files:**
- Modify: `scripts/tarroshort_render.py:65` (import), `scripts/tarroshort_render.py:529`, `scripts/tarroshort_render.py:671`

**Interfaces:**
- Consumes: `STUDIO` de `_studio_layout` (Task 1).

- [ ] **Step 1: Importar `STUDIO` junto al resto**

En la linea 65, reemplazar:
```python
from _studio_layout import find_html, episode_category, short_category
```
por:
```python
from _studio_layout import STUDIO, find_html, episode_category, short_category
```

- [ ] **Step 2: `construir_desde_pauta` escribe el HTML nuevo en `STUDIO`, no en `repo/studio`**

En la linea 529, reemplazar:
```python
    out_dir = repo / "studio" / "shorts-html" / short_category(f"tarroshort-{out_slug}")
```
por:
```python
    out_dir = STUDIO / "shorts-html" / short_category(f"tarroshort-{out_slug}")
```

- [ ] **Step 3: `construir_short_highlights` escribe el HTML nuevo en `STUDIO`, no en `repo/studio`**

En la linea 671, reemplazar:
```python
    out_dir = repo / "studio" / "shorts-html" / cat
```
por:
```python
    out_dir = STUDIO / "shorts-html" / cat
```

- [ ] **Step 4: Verificar que NO quedaron otros usos de `repo / "studio" / "shorts-html"` sueltos**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
grep -n "shorts-html" scripts/tarroshort_render.py
```
Expected: solo las 2 lineas ya cambiadas (529, 671) mencionan `shorts-html`, ambas usando `STUDIO` ahora, ninguna usando `repo / "studio"`.

- [ ] **Step 5: Verificar que el script sigue importando y parseando sin errores**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "import ast; ast.parse(open('scripts/tarroshort_render.py', encoding='utf-8').read()); print('parse OK')"
python -c "import sys; sys.path.insert(0,'scripts'); import tarroshort_render; print('import OK')"
```
Expected: `parse OK` y `import OK`, sin excepciones.

- [ ] **Step 6: Prueba funcional real -- generar un short de datos existente y confirmar que aterriza en el lugar correcto**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "
import sys; sys.path.insert(0,'scripts')
from tarroshort_render import construir_desde_pauta
p = construir_desde_pauta('n64-top-precios', out_slug='n64-top-precios')
print('generado en:', p)
print('existe:', p.exists())
"
```
Expected: `generado en: ...\studio\shorts-html\rankings\top-precios\tarroshort-n64-top-precios.html` y `existe: True`. Esto sobreescribe el short existente con el mismo contenido (la pauta no cambio), asi que `git status` no deberia mostrar diferencias de contenido despues -- solo confirma que la funcion sigue armando el HTML en la ruta correcta. Si `git diff` muestra cambios de contenido inesperados, investigar antes de continuar (no deberia pasar, la pauta JSON no se toco).

- [ ] **Step 7: Confirmar que no quedo diff sucio del test funcional**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
git status --short studio/
git diff --stat studio/
```
Expected: sin salida (el HTML regenerado es byte-identico al que ya estaba versionado -- estos HTML SI estan trackeados por git, a diferencia de `img/`/`captures/`). Si hay diferencias, revisar con `git diff studio/shorts-html/rankings/top-precios/tarroshort-n64-top-precios.html` antes de seguir.

- [ ] **Step 8: Commit**

```bash
git add scripts/tarroshort_render.py
git commit -m "feat(tarroshort-render): escribir HTML generado en STUDIO_ROOT, no en repo/studio

construir_desde_pauta y construir_short_highlights escribian el HTML
armado directo en repo/studio/shorts-html/<categoria>/. Ahora usan
STUDIO (de _studio_layout, Task 1) para que en el PC del estudio el
resultado aterrice en el contenido compartido de Drive/Studio, no
adentro de la carpeta propia de TarroBot."
```

---

### Task 3: `capcut_ready.py` usa `STUDIO` y arregla la ruta plana vieja de capturas

**Files:**
- Modify: `scripts/capcut_ready.py:30-104`

**Interfaces:**
- Consumes: `STUDIO`, `find_html` de `_studio_layout` (Task 1).

- [ ] **Step 1: Agregar el import de `_studio_layout`, con el mismo patron de `sys.path.insert` que ya usa `tarroshort_render.py`**

Despues de la linea 48 (cierre de `_resolve_repo`), agregar:
```python


import sys as _sys
_sys.path.insert(0, str(_resolve_repo() / "scripts"))
from _studio_layout import STUDIO, find_html
```

- [ ] **Step 2: `_find_teaser` usa `STUDIO` en vez de `repo / "studio"`**

Reemplazar (lineas 74-88):
```python
def _find_teaser(slug: str) -> Optional[Path]:
    """Teaser generado por TarroTeaser."""
    repo = _resolve_repo()
    teaser_dir = repo / "studio" / "teasers" / slug
```
por:
```python
def _find_teaser(slug: str) -> Optional[Path]:
    """Teaser generado por TarroTeaser."""
    teaser_dir = STUDIO / "teasers" / slug
```
(el resto de la funcion, desde `if not teaser_dir.exists():` en adelante, no cambia)

- [ ] **Step 3: `_find_cartelas` usa `find_html` + ruta anidada, arreglando el bug de la ruta plana vieja**

Reemplazar (lineas 91-97):
```python
def _find_cartelas(slug: str) -> list[Path]:
    """Cartelas PNG del slide del estudio (capture-slides output)."""
    repo = _resolve_repo()
    cap_dir = repo / "studio" / "captures" / slug
    if not cap_dir.exists():
        return []
    return sorted(cap_dir.glob("*.png"))
```
por:
```python
def _find_cartelas(slug: str) -> list[Path]:
    """Cartelas PNG del slide del estudio (capture-slides output)."""
    try:
        html_path = find_html(slug)
    except (FileNotFoundError, FileExistsError):
        return []
    cap_dir = html_path.parent / "captures" / slug
    if not cap_dir.exists():
        return []
    return sorted(cap_dir.glob("*.png"))
```
(Antes asumia `studio/captures/<slug>/` plano -- ruta que ya no existe desde la reorganizacion de carpetas de 2026-07-21. Ahora ubica el HTML real con `find_html` y busca `captures/<slug>/` como hermano, igual que hace `capture-slides.py`.)

- [ ] **Step 4: Verificar que `_find_descripcion` NO se toco (sigue en `repo/studio/exports`, es dato propio de la app)**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
grep -n "_find_descripcion" -A 4 scripts/capcut_ready.py
```
Expected: la funcion sigue usando `repo = _resolve_repo()` y `repo / "studio" / "exports" / ...`, sin cambios.

- [ ] **Step 5: Verificar que el modulo importa sin errores**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "import ast; ast.parse(open('scripts/capcut_ready.py', encoding='utf-8').read()); print('parse OK')"
python -c "import sys; sys.path.insert(0,'scripts'); import capcut_ready; print('import OK')"
```
Expected: `parse OK` y `import OK`.

- [ ] **Step 6: Prueba funcional real -- confirmar que encuentra las capturas de un episodio real post-reorganizacion**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "
import sys; sys.path.insert(0,'scripts')
from capcut_ready import _find_cartelas, _find_teaser
cartelas = _find_cartelas('n64-top-precios')
print('cartelas encontradas:', len(cartelas))
assert len(cartelas) > 0, 'deberia encontrar las capturas movidas en la sesion de hoy'
teaser = _find_teaser('n64-top-precios')
print('teaser:', teaser)
"
```
Expected: `cartelas encontradas: 17` (o el numero que corresponda -- el punto es que sea mayor a 0, ya que antes de este fix `_find_cartelas` SIEMPRE devolvia lista vacia post-reorganizacion). `teaser:` puede imprimir `None` si no hay ningun teaser generado para ese slug todavia -- eso es esperado, no es un fallo.

- [ ] **Step 7: Commit**

```bash
git add scripts/capcut_ready.py
git commit -m "fix(capcut-ready): leer capturas/teasers desde STUDIO_ROOT, arreglar ruta plana vieja

_find_cartelas todavia asumia studio/captures/<slug>/ (ruta plana
pre-reorganizacion de carpetas) y por eso SIEMPRE devolvia lista vacia
para cualquier episodio real -- bug preexistente, no relacionado al
cambio de STUDIO_ROOT pero encontrado al revisar este archivo. Ahora
usa find_html() + captures/<slug>/ como hermano, igual que
capture-slides.py. De paso, _find_teaser tambien pasa a leer desde
STUDIO en vez de repo/studio."
```

---

### Task 4: `tarroteaser.py` escribe el teaser MP4 en `STUDIO`, no en `repo/studio`

**Files:**
- Modify: `scripts/tarroteaser.py:86-111`

**Interfaces:**
- Consumes: `STUDIO` de `_studio_layout` (Task 1).

- [ ] **Step 1: Agregar el import de `_studio_layout` despues de `_resolve_repo`**

Despues de la linea 94 (cierre de `_resolve_repo`), agregar:
```python


import sys as _sys
_sys.path.insert(0, str(_resolve_repo() / "scripts"))
from _studio_layout import STUDIO
```

- [ ] **Step 2: `_resolve_teaser_out` usa `STUDIO` en vez de `_resolve_repo() / "studio"`**

Reemplazar (lineas 97-102):
```python
def _resolve_teaser_out(slug: str) -> Path:
    """Resuelve el directorio donde guardar el teaser. Override por env."""
    env_out = os.environ.get("RETROTARROS_TEASER_OUT")
    if env_out:
        return Path(env_out).resolve() / slug
    return _resolve_repo() / "studio" / "teasers" / slug
```
por:
```python
def _resolve_teaser_out(slug: str) -> Path:
    """Resuelve el directorio donde guardar el teaser. Override por env."""
    env_out = os.environ.get("RETROTARROS_TEASER_OUT")
    if env_out:
        return Path(env_out).resolve() / slug
    return STUDIO / "teasers" / slug
```

- [ ] **Step 3: `DRIVE_STUDIO` (alias legacy) tambien usa `STUDIO`**

Reemplazar (linea 111):
```python
DRIVE_STUDIO = REPO / "studio" / "teasers"
```
por:
```python
DRIVE_STUDIO = STUDIO / "teasers"
```

- [ ] **Step 4: Verificar que el modulo importa sin errores**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
python -c "import ast; ast.parse(open('scripts/tarroteaser.py', encoding='utf-8').read()); print('parse OK')"
python -c "import sys; sys.path.insert(0,'scripts'); import tarroteaser; print('import OK'); print('DRIVE_STUDIO =', tarroteaser.DRIVE_STUDIO)"
```
Expected: `parse OK`, `import OK`, y `DRIVE_STUDIO = ...\studio\teasers` (ruta del repo local, ya que no hay variable de entorno seteada en esta verificacion).

- [ ] **Step 5: Verificar la resolucion con la variable de entorno seteada**

Run (PowerShell):
```powershell
cd "D:\Recursos Retrotarros\repo"
$env:RETROTARROS_STUDIO_ROOT = "G:\Mi unidad\Studio"
python -c "import sys; sys.path.insert(0,'scripts'); import tarroteaser; print(tarroteaser._resolve_teaser_out('n64-top-precios'))"
Remove-Item Env:\RETROTARROS_STUDIO_ROOT
```
Expected: `G:\Mi unidad\Studio\teasers\n64-top-precios`. El `Remove-Item` final es obligatorio (mismo motivo que Task 1 Step 3).

- [ ] **Step 6: Commit**

```bash
git add scripts/tarroteaser.py
git commit -m "feat(tarroteaser): escribir el MP4 del teaser en STUDIO_ROOT, no en repo/studio

Mismo criterio que Task 2/3: el teaser generado es contenido de
episodio (vive junto a teaser-<slug>.html), no dato propio de la app.
DRIVE_STUDIO (alias legacy) tambien actualizado."
```

---

### Task 5: `sync-tarrobot-to-drive.ps1` deja de mirrorear `studio/` completo

**Files:**
- Modify: `scripts/sync-tarrobot-to-drive.ps1:19-20` (comentario de cabecera), `scripts/sync-tarrobot-to-drive.ps1:126` (agregar `_studio_layout.py`), `scripts/sync-tarrobot-to-drive.ps1:146-194` (eliminar bloques 2b/2b-bis/2c/2c-bis), `scripts/sync-tarrobot-to-drive.ps1:378-386` (INSTALL-INFO.txt), `scripts/sync-tarrobot-to-drive.ps1:401-404` (mensaje final)

**Interfaces:**
- Ninguna -- este script no es importado por otros, es standalone.

- [ ] **Step 1: Actualizar el comentario de cabecera (lineas 19-20) para reflejar el nuevo alcance**

Reemplazar:
```
#   - studio/*.html (TODOS los HTMLs de episodios del canal · fix 2026-05-27)
#   - studio/img/* recursive (imagenes de episodios, box arts, sprites)
```
por:
```
#   - (2026-07-23: studio/*.html, img/ y captures/ de episodios DEJARON de
#     sincronizarse aca -- TarroBot ya no mantiene su propia copia del
#     contenido de estudio. Ese contenido vive en G:\Mi unidad\Studio\ y se
#     lee via RETROTARROS_STUDIO_ROOT, poblado por scripts/sync-to-drive.ps1)
```

- [ ] **Step 2: Agregar `_studio_layout.py` a la lista de scripts sincronizados**

En la linea 126 (justo despues de `Sync-Item "scripts\capture-slides.py"`), agregar:
```powershell
Sync-Item "scripts\capture-slides.py"
Sync-Item "scripts\_studio_layout.py"
```
(la primera linea ya existe, solo se agrega la segunda debajo. `_studio_layout.py` lo importan `capture-slides.py` y `tarroshort_render.py` -- sin copiarlo, esos dos scripts fallarian con `ImportError` en el PC del estudio.)

- [ ] **Step 3: Eliminar los bloques 2b, 2b-bis, 2c, 2c-bis completos**

Eliminar TODO el bloque desde la linea `# 2b. HTMLs de EPISODIOS del canal...` hasta la linea en blanco justo antes de `# 2d. CARPETAS DE PRODUCCION...` (lineas 146-195 del archivo actual, incluyendo las 4 lineas en blanco intermedias que separan cada sub-bloque). Es decir, eliminar exactamente esto:
```powershell
# 2b. HTMLs de EPISODIOS del canal (lo que se proyecta en grabacion)
# FIX 2026-05-27: estos faltaban en el sync. Sin esto, Luis va al estudio,
# abre n64-coleccion.html y no la encuentra. Sync masivo de todos los HTMLs
# que NO empiezan con underscore (esos son templates internos).
Write-Host "HTMLs de episodios:" -ForegroundColor Cyan
$episodios = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Filter "*.html" -Recurse -File |
    Where-Object { $_.Name -notlike "_*" -and $_.DirectoryName -notmatch '\\resenas($|\\)' }
foreach ($ep in $episodios) {
    $relPath = $ep.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath
}
Write-Host ""

# 2b-bis. Resenas (carpeta APARTE studio\resenas\, no la raiz plana de studio\).
# FIX 2026-07-21: el Get-ChildItem de arriba no es recursivo, asi que las resenas
# quedaban fuera del sync sin este bloque.
if (Test-Path (Join-Path $RepoRoot "studio\resenas")) {
    Write-Host "Resenas:" -ForegroundColor Cyan
    Sync-Item "studio\resenas" -Recursive
    Write-Host ""
}

# 2c. Carpetas de imagenes de episodios (box arts, sprites, paneos)
# Necesarias para que los HTMLs con <img src="img/..."> renderizen bien.
# FIX 2026-07-21 (reorg): "studio\img" plano solo tiene resenas/ y thumbnails/
# desde la reorganizacion; las imagenes por-episodio ahora viven en
# "studio\<categoria>\img\<slug>\" (hermanas del HTML). Sync-Item plano de
# "studio\img" dejaba de copiar el 90% de las box arts sin ningun error visible.
# Recorremos TODAS las carpetas llamadas "img" bajo studio\ (incluye la raiz
# resenas/thumbnails y cada carpeta anidada por categoria).
Write-Host "Imagenes de episodios:" -ForegroundColor Cyan
$imgDirs = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Directory -Recurse -Filter "img" -ErrorAction SilentlyContinue
foreach ($imgDir in $imgDirs) {
    $relPath = $imgDir.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath -Recursive
}
Write-Host ""

# 2c-bis. Capturas PNG de slides (generadas por capture-slides.py). Las usa Luis
# para edicion/CapCut y como respaldo de cada slide. Fix 2026-06-25: faltaban en el sync.
# FIX 2026-07-21 (reorg): mismo problema que 2c -- las carpetas "captures\<slug>"
# ahora viven anidadas por categoria, no en la raiz plana "studio\captures".
Write-Host "Capturas de slides (PNG):" -ForegroundColor Cyan
$capDirs = Get-ChildItem -Path (Join-Path $RepoRoot "studio") -Directory -Recurse -Filter "captures" -ErrorAction SilentlyContinue
foreach ($capDir in $capDirs) {
    $relPath = $capDir.FullName.Substring($RepoRoot.Length + 1)
    Sync-Item $relPath -Recursive
}
Write-Host ""

```
Dejando el archivo con el bloque "2. Templates" seguido directo por el bloque "2d. CARPETAS DE PRODUCCION..." (sin nada en medio salvo la linea en blanco que ya separaba "2. Templates" del resto).

- [ ] **Step 4: Renombrar el bloque "2d" a "2b" ya que ahora es el siguiente bloque tras Templates (opcional pero prolijo)**

Cambiar el comentario:
```
# 2d. CARPETAS DE PRODUCCION por episodio: "G:\Mi unidad\Studio\<slug>\"
```
por:
```
# 2b. CARPETAS DE PRODUCCION por episodio: "G:\Mi unidad\Studio\<slug>\"
# (renombrado de "2d" a "2b" el 2026-07-23 al eliminar los bloques 2b/2b-bis/2c/2c-bis
# que mirroreaban studio/ completo -- ver spec 2026-07-23-tarrobot-studio-root-split)
```
El resto del bloque (contenido interno) no cambia -- ya quedo correcto en la sesion anterior (busqueda recursiva del HTML).

- [ ] **Step 5: Actualizar el bloque de texto `INSTALL-INFO.txt` para mencionar las 2 variables**

Reemplazar (dentro del heredoc `@"..."@`, buscar el texto):
```
1. Al correr install.bat, en el paso [6/8] "Configurando ubicacion
   del repo Retrotarros", pega esta ruta:

   $Destino

2. install.bat valida que existan scripts/tarrobot-live.py y
   data/tarrobot-database.json. Si la estructura quedo bien, queda
   guardado como RETROTARROS_REPO.
```
por:
```
1. Al correr install.bat, en el paso [6/8] "Configurando ubicacion
   del repo Retrotarros", pega esta ruta:

   $Destino

2. install.bat valida que existan scripts/tarrobot-live.py y
   data/tarrobot-database.json. Si la estructura quedo bien, queda
   guardado como RETROTARROS_REPO.

2b. ADEMAS, configura la variable RETROTARROS_STUDIO_ROOT apuntando a
    la raiz de Studio (el contenido real de episodios/shorts, NO esta
    carpeta tarrobot). Corre una vez en el PC del estudio:

      setx RETROTARROS_STUDIO_ROOT "$(Split-Path -Parent $Destino)"

    Sin esto, TarroBot no encuentra las capturas/box arts de los
    episodios (viven en Studio\, no en Studio\tarrobot\).
```

- [ ] **Step 6: Actualizar el mensaje final impreso en pantalla para mencionar la variable nueva**

Reemplazar:
```powershell
Write-Host "En el estudio: para apuntar a esta carpeta, corre una vez:" -ForegroundColor Cyan
Write-Host "  setx RETROTARROS_REPO `"$Destino`"" -ForegroundColor Yellow
Write-Host ""
```
por:
```powershell
Write-Host "En el estudio: para apuntar a esta carpeta, corre una vez:" -ForegroundColor Cyan
Write-Host "  setx RETROTARROS_REPO `"$Destino`"" -ForegroundColor Yellow
Write-Host "  setx RETROTARROS_STUDIO_ROOT `"$(Split-Path -Parent $Destino)`"" -ForegroundColor Yellow
Write-Host ""
```

- [ ] **Step 7: Verificar sintaxis PowerShell**

Run (PowerShell):
```powershell
$e = $null
[void][System.Management.Automation.PSParser]::Tokenize((Get-Content "D:\Recursos Retrotarros\repo\scripts\sync-tarrobot-to-drive.ps1" -Raw), [ref]$e)
Write-Host "errores: $($e.Count)"
```
Expected: `errores: 0`.

- [ ] **Step 8: Verificar que los bloques eliminados ya no aparecen y que `_studio_layout.py` si esta en la lista**

Run:
```bash
cd "D:\Recursos Retrotarros\repo"
grep -n "HTMLs de episodios\|Imagenes de episodios\|Capturas de slides\|_studio_layout" scripts/sync-tarrobot-to-drive.ps1
```
Expected: SOLO una linea con `_studio_layout.py` (el `Sync-Item` agregado en el Step 2). Ninguna linea debe mencionar "HTMLs de episodios", "Imagenes de episodios" ni "Capturas de slides" -- esos bloques deben haber desaparecido por completo.

- [ ] **Step 9: Commit**

```bash
git add scripts/sync-tarrobot-to-drive.ps1
git commit -m "refactor(sync-tarrobot): dejar de mirrorear studio/ completo dentro de tarrobot/

TarroBot es una app aparte -- no deberia mantener su propia copia del
contenido de estudio (decision de Luis, 2026-07-23). Se eliminan los
bloques 2b/2b-bis/2c/2c-bis (HTMLs, resenas, imagenes, capturas de
episodios) que copiaban todo studio/ dentro de Studio\tarrobot\studio\.
Ese contenido ya vive completo en Studio\ (raiz), poblado por
sync-to-drive.ps1, y ahora se lee via RETROTARROS_STUDIO_ROOT (Task 1-4).

Se agrega _studio_layout.py a los scripts sincronizados (sin el, capture-
slides.py y tarroshort_render.py fallarian con ImportError en el PC del
estudio -- bug preexistente encontrado al hacer este cambio, no habia
causado problemas porque TarroBot no esta instalado ahi todavia).

Se documentan las 2 variables de entorno requeridas (RETROTARROS_REPO +
RETROTARROS_STUDIO_ROOT) en INSTALL-INFO.txt y el mensaje final del script."
```

---

### Task 6: Limpiar el contenido residual en el Drive real y verificar el resultado final

**Files:** ninguno (solo operaciones sobre el Drive real, no sobre el repo)

**Interfaces:** ninguna.

Este task corre el script ya arreglado contra el Drive real de Luis, y limpia el
contenido que quedo duplicado en `Studio\tarrobot\studio\` de sincronizaciones
anteriores (ya no se recrea, pero lo viejo no se borra solo).

- [ ] **Step 1: Correr `sync-tarrobot-to-drive.ps1` real y confirmar que ya NO escribe dentro de `studio\`**

Run (PowerShell):
```powershell
cd "D:\Recursos Retrotarros\repo"
.\scripts\sync-tarrobot-to-drive.ps1 2>&1 | Select-String -Pattern "HTMLs de episodios|Imagenes de episodios|Capturas de slides|_studio_layout|SYNC COMPLETO"
```
Expected: una linea con `_studio_layout.py` (el `[COPY]` del script nuevo), una linea `SYNC COMPLETO`, y NINGUNA linea con "HTMLs de episodios", "Imagenes de episodios" ni "Capturas de slides" (esos bloques ya no existen).

- [ ] **Step 2: Confirmar que `Studio\tarrobot\scripts\_studio_layout.py` llego**

Run (Bash):
```bash
ls "G:/Mi unidad/Studio/tarrobot/scripts/_studio_layout.py"
```
Expected: el archivo existe.

- [ ] **Step 3: Borrar el contenido residual de sincronizaciones anteriores dentro de `Studio\tarrobot\studio\`**

El sync ya no recrea nada de esto, pero lo que quedo de sesiones pasadas (HTML +
`img/` + `captures/` de episodios, organizados por categoria) sigue ahi ocupando
espacio y podria confundir a futuro. Es contenido 100% duplicado del que ya vive
en `Studio\` (raiz) -- confirmar antes de borrar, no asumir:

Run (Bash):
```bash
echo "=== Categorias duplicadas dentro de tarrobot/studio/ ==="
ls "G:/Mi unidad/Studio/tarrobot/studio/" | grep -v "^_template\|^desktop.ini\|^melodias$\|^pautas$\|^shorts$\|^tarrobot-out$"
```
Expected: una lista de carpetas de categoria (`archivo-koko`, `colecciones`,
`curaduria-n64`, `img`, `rankings`, `resenas`, `sagas`, `shorts-html`, `specials`,
`teasers`, `captures`) -- exactamente las que el sync ya NO vuelve a escribir.

Confirmar que cada una tiene su version real en `Studio\` (raiz) antes de tocar
nada:
```bash
for d in archivo-koko colecciones curaduria-n64 rankings resenas sagas shorts-html specials teasers; do
  if [ -d "G:/Mi unidad/Studio/tarrobot/studio/$d" ] && [ ! -d "G:/Mi unidad/Studio/$d" ]; then
    echo "FALTA en la raiz, NO BORRAR: $d"
  fi
done
echo "chequeo terminado"
```
Expected: `chequeo terminado` sin ninguna linea de "FALTA en la raiz" -- si aparece alguna, DETENERSE y no borrar esa carpeta especifica hasta investigar por que no esta en la raiz.

Si el chequeo pasa limpio, borrar:
```powershell
$stale = @("archivo-koko","colecciones","curaduria-n64","img","rankings","resenas","sagas","shorts-html","specials","teasers","captures")
foreach ($d in $stale) {
    $p = "G:\Mi unidad\Studio\tarrobot\studio\$d"
    if (Test-Path $p) {
        Remove-Item -LiteralPath $p -Recurse -Force -Confirm:$false
        Write-Host "Borrado: $p"
    }
}
```

- [ ] **Step 4: Verificar que `Studio\tarrobot\studio\` solo quedo con lo propio de la app**

Run (Bash):
```bash
ls "G:/Mi unidad/Studio/tarrobot/studio/"
```
Expected: solo `_template-tarrobot-*.html`, `desktop.ini`, `melodias`, `pautas`,
`shorts`, `tarrobot-out`, `obs-aliases.json`, `tarrobot-recetas.json` -- nada de
categorias de episodios.

- [ ] **Step 5: Verificar que `Studio\` (raiz) sigue teniendo todo el contenido real, sin tocar**

Run (Bash):
```bash
ls "G:/Mi unidad/Studio/rankings/top-precios/n64-top-precios/"
ls "G:/Mi unidad/Studio/rankings/top-precios/n64-top-precios/captures/" | wc -l
```
Expected: el HTML, `img/`, `captures/` siguen ahi con contenido (no se toco nada
fuera de `Studio\tarrobot\studio\`).

- [ ] **Step 6: Reportar a Luis el resultado final**

Sin commit de codigo en este step (es limpieza de Drive, no de repo). Avisar el
espacio liberado aproximado y confirmar que TarroBot en Drive quedo solo con sus
propios archivos.

---

## Orden de ejecucion

Los tasks 1-5 son secuenciales (cada uno depende del anterior via el import de
`STUDIO`). El Task 6 depende de que el Task 5 este commiteado (necesita el script
ya arreglado corriendo desde el repo).
