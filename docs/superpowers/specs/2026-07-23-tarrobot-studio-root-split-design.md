# TarroBot: separar "app root" de "studio content root"

## Problema

`sync-tarrobot-to-drive.ps1` mirrorea el arbol completo de `studio/` (HTML + img +
captures de los 79 episodios/shorts) dentro de `G:\Mi unidad\Studio\tarrobot\studio\`,
ademas del mirror ya existente en la raiz de `G:\Mi unidad\Studio\` (creado por
`sync-to-drive.ps1`). Esto duplica ~150 MB de contenido y, mas importante, mezcla
conceptualmente "la app TarroBot" con "el contenido del canal": TarroBot es una
herramienta aparte que deberia consumir el contenido de estudio navegando a la
ubicacion compartida, no mantener su propia copia (decision de Luis, 2026-07-23).

Investigando el codigo para hacer el cambio aparecieron dos bugs preexistentes, sin
relacion directa con el pedido de Luis pero que hay que arreglar en el mismo trabajo
porque el fix de esta spec los toca de cerca:

1. **`scripts/_studio_layout.py` no esta en la lista de scripts que
   `sync-tarrobot-to-drive.ps1` copia al PC del estudio.** Si TarroBot se instalara
   hoy ahi, `tarroshort_render.py` y `capture-slides.py` (que importan
   `find_html`/`episode_category`/`short_category` de ese modulo) fallarian con
   `ImportError` al primer uso.
2. **`scripts/capcut_ready.py` todavia asume la ruta plana pre-reorganizacion**
   `studio/captures/<slug>` (linea 94) en vez de la ruta anidada por categoria que
   existe desde la reorganizacion de carpetas de 2026-07-21.

No hay un PC de estudio con TarroBot instalado todavia (confirmado por Luis), asi
que no hace falta un paso de migracion inmediato — pero el diseño debe dejar
documentado como configurar el PC cuando se instale por primera vez.

## Diseño aprobado

### Dos roots, dos variables de entorno

- **`RETROTARROS_REPO`** (existente, sin cambios de significado): raiz de la app
  TarroBot — sus propios scripts Python, base de datos, pautas (JSON + audio
  precargado), melodias (MIDI + soundfont), shorts MP4 finales, branding, kit
  instalador, templates propios de TarroBot (`_template-tarrobot-*.html`). En Drive:
  `G:\Mi unidad\Studio\tarrobot\`.
- **`RETROTARROS_STUDIO_ROOT`** (nueva): raiz del contenido real de estudio — los
  HTML + `img/<slug>/` + `captures/<slug>/` de cada episodio/short, organizados por
  categoria. En Drive: `G:\Mi unidad\Studio\` (la raiz, ya poblada correctamente por
  `sync-to-drive.ps1`).
- **Fallback sin variable seteada:** `RETROTARROS_STUDIO_ROOT` ausente ⇒ usar
  `REPO/studio` (mismo comportamiento de hoy). Esto mantiene el desarrollo local en
  el repo funcionando sin cambios — el fallback solo importa para la instalacion
  futura en el PC del estudio.

### Modulo compartido: `scripts/_studio_layout.py`

Hoy `STUDIO` se calcula como `REPO / "studio"` donde `REPO` sale de
`Path(__file__).resolve().parent.parent` (ignora cualquier variable de entorno).
Pasa a resolverse asi:

```
STUDIO = Path(os.environ["RETROTARROS_STUDIO_ROOT"]) si esta seteada y existe,
         si no: REPO / "studio"  (comportamiento actual)
```

`REPO` (usado para ubicar el propio `scripts/_studio_layout.py`, no cambia).
`find_html`, `episode_category`, `short_category` siguen funcionando igual, solo
cambia de donde parte `STUDIO`.

### Scripts que pasan a usar `STUDIO_ROOT` (contenido de episodios)

- **`tarroshort_render.py`**: las rutas que leen/escriben contenido de episodios
  (via `_studio_layout` — `find_html`, salida de `studio/shorts-html/<categoria>/`)
  pasan a resolverse contra `STUDIO_ROOT`. Las rutas que son datos propios de
  TarroBot dentro de `studio/` (pautas JSON, template `_template-tarroshort.html`,
  MP4s finales en `studio/shorts/`) se quedan en `REPO` — son output/config de la
  app, no contenido de episodios.
- **`capcut_ready.py`**: `studio/teasers/<slug>` y `studio/captures/<slug>` pasan a
  `STUDIO_ROOT`. De paso se corrige el bug #2 (ruta plana vieja de captures →
  resolver via `find_html`/categoria, igual que hace `capture-slides.py` desde la
  reorganizacion).
- **`tarroteaser.py`**: `studio/teasers/<slug>` pasa a `STUDIO_ROOT`.

### Scripts que NO cambian

- **`tarrobot.py`**: sus 4 usos de `studio/` (`_template-tarrobot-slide.html`,
  `studio/tarrobot-out`, `studio/pautas`, `studio/melodias`) son datos propios de la
  app, no contenido de episodios. Se quedan en `REPO` sin cambios.
- **`obs_recorder.py`**: no referencia `studio/` en absoluto. Sin cambios.

### `scripts/sync-tarrobot-to-drive.ps1`

**Se eliminan** los 4 bloques que mirrorean contenido de episodios dentro de
`Studio\tarrobot\studio\`:
- Bloque "2b. HTMLs de episodios" (copia recursiva de todo `studio/*.html`)
- Bloque "2b-bis. Resenas"
- Bloque "2c. Imagenes de episodios"
- Bloque "2c-bis. Capturas de slides"

**Se agrega** `scripts\_studio_layout.py` a la lista de "Scripts:" que se sincronizan
(arregla el bug #1 — sin esto `tarroshort_render.py`/`capture-slides.py` no importan
en el PC del estudio).

**No se toca:**
- Bloque "1/2. Templates" (`_template-tarrobot-*.html`, `obs-aliases.json`,
  `tarrobot-recetas.json`) — propios de TarroBot.
- Bloque "2d. Carpetas de produccion" — este ya escribe en `G:\Mi unidad\Studio\<slug>\`
  (la raiz, hermano de `tarrobot\`, no adentro), asi que no es parte del problema
  que describio Luis. Sigue refrescando las carpetas de produccion planas que Luis
  usa para grabar, sin cambios.
- Bloques de Database, Pautas, Melodias, Shorts MP4, Branding, Instalador, Modus
  operandi — todos datos/artefactos propios de la app TarroBot.

**Se actualiza** el texto de `INSTALL-INFO.txt` (generado al final del script) y el
comentario de cabecera del script para documentar que la instalacion en el PC del
estudio requiere configurar AMBAS variables:
```
setx RETROTARROS_REPO "G:\Mi unidad\Studio\tarrobot"
setx RETROTARROS_STUDIO_ROOT "G:\Mi unidad\Studio"
```
No se modifica ningun instalador binario existente (`install.bat` vive fuera del
repo, en el paquete `installers/tarrobot-studio/`) — alcanza con dejar la
instruccion textual clara, ya que no hay instalacion activa que migrar (confirmado
por Luis).

### `scripts/sync-to-drive.ps1`

Sin cambios. Ya es la fuente que puebla `G:\Mi unidad\Studio\` con el contenido real
por categoria — es exactamente lo que `RETROTARROS_STUDIO_ROOT` va a consumir.

## Fuera de alcance

- No se toca la app TarroBot en si (UI, logica de streaming, OBS, etc.) mas alla de
  la resolucion de rutas descrita arriba.
- No se escribe un paso de migracion para un PC de estudio ya instalado, porque no
  existe todavia.
- No se cambia `installers/tarrobot-studio/` (el instalador binario) — queda para
  cuando se instale por primera vez, con la instruccion de las 2 variables ya
  documentada en el script de sync.
- No se borra el contenido duplicado que ya quedo en `G:\Mi unidad\Studio\tarrobot\studio\`
  (residuo de sincronizaciones anteriores) como parte de esta spec — es limpieza de
  Drive, se hace en la ejecucion de las tareas de implementacion como paso final, no
  como parte del diseño de codigo.
