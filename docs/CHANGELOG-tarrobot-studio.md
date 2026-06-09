# CHANGELOG · TarroBot Studio / Retrotarros Studio Suite

Historial de releases del instalador del estudio. Cada version se publica
en GitHub Releases con ZIP + .exe firmados.

---

## v1.5.2 · Hotfix instalador · "no se cierra mas"

Arregla el bug por el que el instalador **se cerraba de golpe sin dejar log**
al correr `install.bat`, especialmente en PCs con Python 3.13+ (como el del
estudio, que tiene 3.14).

### Causa raiz

Varios `echo` con **parentesis dentro de bloques `if/else`** rompian el parser
de cmd: el `)` del texto cerraba el bloque antes de tiempo y abortaba con
"No se esperaba . en este momento" (cierre instantaneo de la ventana, sin
rastro). Solo se disparaba al entrar a esas ramas: **no hay Python compatible**
(la que mata en PCs con Python muy nuevo), instalar Python, descargar
ffmpeg/FluidSynth, pedir repo manual, o "sin API key".

### Cambios

- `install.bat`: escapados los parentesis (`^(` `^)`) en las 6 lineas de `echo`
  dentro de bloques. Validado corriendo el flujo completo (todas las ramas) sin
  errores de sintaxis.
- `install.bat`: **log persistente** `install-log.txt` + `install-pip.txt`
  (detalle de pip via `--log`, donde mas falla) en la carpeta de instalacion.
  Los errores de pip/import/Python ahora quedan SIEMPRE en archivo.
- `installer.iss`: el postinstall ahora lanza `install.bat` via `cmd /k`
  (antes `shellexec`), asi la ventana **no se cierra sola** ni al terminar ni al
  fallar -- el usuario alcanza a leer el error.

### Para aplicar

- **Rebuild del .exe** (`build-package.ps1` / ISCC) para distribuir el fix.
- **Atajo rapido en el PC del estudio:** reemplazar el `install.bat` de la
  carpeta instalada por el corregido y volver a correrlo (ya no se cierra).

---

## v1.6.0 · Sprint 19 · "TarroShort" (en desarrollo)

Generador de shorts/reels verticales (1080x1920) donde TarroBot presenta y
comenta cada item con su voz y su cara MOVIENDOSE, listo para llevar a CapCut
(tu pones la musica). Pensado para rankings, piezas de coleccion y joyas de
invitados (Abriendo el Tarro).

### Componentes

- **`studio/_template-tarroshort.html`** (nuevo): template vertical 9:16.
  Intro (TarroBot se presenta) + items del 10 al 1 (foto + TarroBot esquina +
  linea breve) + cierre. Mascota TarroBot con boca + bob animados (clase
  `tb-talking`, solo activa al renderizar video; las capturas PNG quedan estaticas).
- **`scripts/tarroshort_render.py`** (nuevo): motor de render. Por escena:
  Playwright graba a TarroBot "hablando" -> edge-tts genera la voz Catalina
  desde el texto de la escena -> ffmpeg arma el clip (loop + voz) -> concatena
  todo en `studio/shorts/<slug>.mp4`. Respeta MP3 propios si los reemplazas en
  `studio/shorts/audio/<slug>/`.
- **`TarroBot-Short.bat`** (nuevo): launcher CLI (elige el slug y genera el MP4).

### Requisitos

Corre en el PC de autoria (igual que TarroTeaser / capture-slides): necesita
playwright + chromium + ffmpeg. Voz: es-CL-CatalinaNeural (+12Hz), igual al canal.

### Integracion en el panel (completado)

- **Auto-rellenar desde pauta**: `tarroshort_render.py --from-pauta <slug>` arma el
  HTML del short desde la pauta JSON (rank + nombre + meta + linea breve por item).
- **`scripts/tarroshort_jobs.py`** (nuevo): job manager async (1 a la vez) con
  progreso por WS, mismo patron que teaser_jobs.
- **Endpoints** en tarrobot-live.py: `POST /api/tarroshort/generar`
  (body `{pauta_slug}` o `{slug}`), `GET /api/tarroshort/job/{id}`, `/api/tarroshort/list`.
- **Card "TARROSHORT"** en el panel de control: input slug + checkbox "desde pauta"
  + barra de progreso en vivo + historial. WS `tarroshort.*`.

### Verificado

- Render end-to-end OK: MP4 1080x1920 h264+aac ~40s, TarroBot animado al hablar.
- Auto-rellenar desde pauta snes-top-precios: 10 items con datos reales.
- py_compile de tarroshort_render/jobs + tarrobot-live OK. JS del panel sin errores
  (validado en Playwright). Falta: smoke test del boton con el server vivo en el estudio.

---

## v1.5.1 · Hotfix · "Instalacion a prueba de balas"

**Fecha:** 2026-05-28
**Nombre clave:** que no se cuelgue mas en silencio

Fix de un cuelgue silencioso del instalador en PC limpio (sin Python) y
blindaje del arranque para que ningun fallo sea invisible.

### Sintoma

`install.bat` corria, no daba error, pero nunca terminaba (se quedaba en
un paso `[x/7]`). En produccion, a veces TarroBot "no abria" sin dejar rastro.

### Causa raiz

Windows 10/11 trae un alias falso `python.exe` en `WindowsApps` (abre la
Microsoft Store). `where python` lo detectaba como Python real -> el script
saltaba la descarga -> `python -m venv` ejecutaba el stub -> abria la Store
y se colgaba sin error.

### Fixes en `install.bat`

- **Deteccion de Python anti-stub**: ignora el `python.exe` de WindowsApps
  (filtra por ruta), usa el `py` launcher como respaldo y guarda la ruta
  COMPLETA del exe.
- **Gate de version**: rechaza Python 3.13+ (whisper/torch/numba sin wheels,
  causa cuelgue de pip) y fuerza la descarga del 3.12.7 dedicado.
- **venv robusto**: se crea con la ruta completa de Python, valida
  `.venv\Scripts\python.exe` y recrea un `.venv` incompleto de intentos previos.
- **deps sin cuelgue**: instala PyTorch desde el indice CPU PRIMERO (evita
  resolver wheels CUDA ~2.5 GB o compilar desde fuente), con progreso visible.
- **smoke-test**: tras instalar, verifica que las dependencias clave IMPORTEN.
  Si algo falla, lo dice en la instalacion en vez de fallar mudo al arrancar.

### Fixes en `scripts/tarrobot-tray.py`

- **Anti-fallo-silencioso bajo pythonw**: redirige stdout/stderr a
  `logs/tarrobot-tray.log`, captura cualquier crash de arranque y muestra un
  MessageBox de Windows con el detalle + ruta del log.
- **Chequeo de puerto previo**: si 8765 ya esta ocupado, avisa con un cartel
  claro (TarroBot ya corriendo) en vez de mostrar un icono "vivo" pero muerto.
- **Server thread con guarda**: si uvicorn no puede arrancar, loguea, avisa y
  mata el proceso (antes el icono aparecia pero la TV/panel no cargaban nunca).

### Docs

- `README-ESTUDIO.txt`: nuevas entradas en PROBLEMAS COMUNES para
  "no pasa nada al abrir TarroBot" (con ruta del log) y "la instalacion se
  queda pegada".

---

## v1.5.0 · Sprint 18 · "OBS Assistant + CapCut Ready"

**Fecha:** 2026-05-24
**Nombre clave:** cierre del loop estudio

TarroBot ahora optimiza tambien el setup y operacion de OBS, y entrega
todo el episodio empaquetado para abrir en CapCut. Cinco capacidades nuevas:

### A · OBS Healthcheck

Card en panel que diagnostica OBS: version, canvas 1080p/60fps, escenas
mapeadas, mic detectado, browser source TarroBot, directorio de grabacion.
Cada item te dice exactamente que hacer si esta mal. Toggle AUTO refresca
cada 30s.

- **`scripts/obs_healthcheck.py`** (nuevo): 12+ checks con status
  (ok/warn/error/skip) + instruccion de fix por item.
- **`GET /api/obs/healthcheck`** endpoint.
- Card UI 'OBS HEALTHCHECK' con items coloreados.

### B · OBS Auto-setup escenas Retrotarros Standard

Boton PREVIEW dry-run muestra que va a crear, APLICAR ejecuta. 9 escenas
(intro, cam-cenital, cam-luis, cam-koko, tarrobot-full, closeup-cartucho,
closeup-caja, transition, outro) + browser source TarroVision + text
source lower-third. **Idempotente** — nunca sobreescribe lo existente.

- **`scripts/obs_setup.py`** (nuevo): template + diff + apply.
- **`POST /api/obs/setup-auto`** con flag `dry_run`.

### C · Auto-record sincronizado con sesion

Toggle "auto-record al cargar pauta" → cuando cargas pauta, OBS arranca
grabacion automatica contra `recordings/<slug>/master-*.mp4`. La card
TarroTeaser ahora **autollena el video_path** con ese master.

Cierra el loop: pauta → grabacion → teaser sin tocar paths a mano.

- **`scripts/obs_recorder.py`** (nuevo): start/stop/status + auto-record
  in-memory toggle + busqueda del ultimo master por slug.
- **5 endpoints** `/api/obs/recording/{status,start,stop,auto-toggle,last}`.
- Hook en `queue_load` dispara StartRecord si auto-record on.

### D · Lower-thirds dinamicos

Toggle "auto-mostrar titulo al avanzar item" → cada NEXT en la pauta
actualiza el text source `lower-third` en OBS con el tema del item actual
(formato `TITULO - meta`). Tambien manual desde la card.

- **`_set_lower_third()`** + **`_format_lower_third()`** en tarrobot-live.py.
- **`POST /api/obs/lower-third`** (manual) + **`/auto-toggle`**.
- Hook en `queue_next` dispara si toggle on.

### E · CapCut Ready

Boton PREPARAR empaqueta `recordings/<slug>/capcut-ready/` con todo:
master OBS + teaser TarroTeaser + cartelas PNG + `descripcion.txt` +
`README.txt` con orden exacto de import a CapCut.

- **`scripts/capcut_ready.py`** (nuevo): empaquetado idempotente con
  inventario de assets disponibles vs faltantes.
- **`POST /api/capcut/preparar`** con flag `copy_videos` (default false,
  apunta sin copiar para ahorrar disco).
- Card UI 'CAPCUT READY' con boton abrir-carpeta nativo.

### Distribuible

- `installer.iss`: copia los 4 modulos nuevos + crea dir `{app}\recordings\`.
- `build-package.ps1`: incluye los 4 modulos al armar paquete.
- `sync-tarrobot-to-drive.ps1`: sincroniza los 4 modulos.
- `.gitignore`: ignora `recordings/`, `studio/teasers/`, `studio/captures/`
  (outputs locales del estudio).

### Reglas nuevas

- `docs/handoff-claude-studio/02-convenciones-proyecto.md`: regla nueva
  documentada — NO buildear paquete .exe durante la sesion, solo al cierre.

### Migracion desde v1.4.0

Limpia. Si auto-setup detecta escenas existentes con los mismos nombres
del template Standard, las respeta sin tocar.

---

## v1.4.0 · Sprint 17 · "Retrotarros Studio Suite"

**Fecha:** 2026-05-23
**Nombre clave:** integracion TarroTeaser al stack

TarroTeaser deja de ser un script huerfano de mi PC y queda como capacidad
nativa del panel del estudio. Ahora podes generar Shorts verticales desde el
master del episodio con tres formas distintas:

- **CLI:** corriendo `python scripts/tarroteaser.py <video.mp4> --slug <slug>`.
- **Launcher BAT:** doble click a `TarroBot-Teaser.bat` (Menu Inicio o Escritorio),
  te pide la ruta del video y el slug, te abre la carpeta al terminar.
- **Panel UI:** card `TARROTEASER · SHORT VERTICAL` en el control con barra
  de progreso en vivo, historial de los ultimos 5 teasers y boton re-generar.

### Que hay nuevo

- **`scripts/tarroteaser.py`**: refactor a modulo importable. Nueva funcion
  publica `generar_teaser(...)` con callback de progreso. CLI sigue funcionando
  como antes.
- **`scripts/teaser_jobs.py`** (nuevo): `TeaserJobManager` async que encola y
  procesa jobs de teaser de a uno (Whisper es CPU-heavy). Mantiene historial
  in-memory de los ultimos 50 jobs. Hooks a WebSocket broadcaster para que la
  UI muestre progreso en vivo sin polling.
- **Endpoints REST nuevos** en `tarrobot-live.py`:
    - `POST /api/teaser/generar` — encola un job. Body: `video_path`, `slug`,
      `ep_type?`, `num_highlights?`, `clip_duration?`, `max_clip_duration?`,
      `model?`, `out_dir?`. Devuelve `{job_id, queue_size}`.
    - `GET /api/teaser/job/{id}` — estado completo del job (log tail incluido).
    - `GET /api/teaser/list?limit=20` — historial reciente.
    - `POST /api/teaser/cancel/{id}` — cancela un job (queued = instantaneo,
      running = marca flag, ffmpeg actual termina).
- **Eventos WebSocket** nuevos en `/ws/live`:
    - `teaser.queued`, `teaser.started`, `teaser.progress`, `teaser.done`,
      `teaser.error`, `teaser.cancelled`.
- **Card UI** `🎬 TARROTEASER · SHORT VERTICAL` en `_template-tarrobot-control.html`:
    - Inputs: ruta video + slug (autollenado desde la pauta cargada).
    - Avanzado plegable: N highlights, clip min/max, modelo Whisper.
    - Barra de progreso + step actual en vivo via WS.
    - Resultado con tamaño, duracion, tipo episodio, link "abrir carpeta".
    - Historial ultimos 5 con estado (queued/running/done/error).
- **Launcher** `TarroBot-Teaser.bat`: prompt interactivo, lista pautas disponibles
  para sugerir slugs, abre carpeta destino al terminar.
- **Acceso directo** en Menu Inicio: `TarroTeaser (genera Short vertical)`.

### Fix bloqueante

- **Path hardcoded** en `tarroteaser.py` (`RECURSOS = Path("D:/Recursos Retrotarros")`)
  reemplazado por resolucion runtime via env `RETROTARROS_REPO` (que setea
  `install.bat` del estudio). Caso dev: fallback al parent del script.
- **Output dir** configurable via env `RETROTARROS_TEASER_OUT`. Default:
  `$REPO/studio/teasers/<slug>/`.

### Distribucion

- `installer.iss`: copia `tarroteaser.py`, `generate-teaser.py`, `capture-slides.py`
  a `{app}\scripts\`. Crea directorio `{app}\studio\teasers\`. Registra icono
  Menu Inicio para `TarroBot-Teaser.bat`.
- `sync-tarrobot-to-drive.ps1`: incluye los 3 scripts en la sincronizacion al
  Drive del estudio.

### Migracion desde v1.3.0

Limpia: no hay schemas que migrar. Solo correr el .exe nuevo o `install.bat`
otra vez.

---

## v1.3.0 · Sprint 13-16 · "Concentrador social + LLM resolver"

**Fecha:** 2026-05-21

- Conectores Twitch + Discord + YouTube live chat unificados en SQLite.
- Endpoints sociales (`/api/social/*`) + UI feed con SAY/RESPOND/DICTATE.
- LLM resolver: pauta pre-enriquecida + cache local + telemetria + modo barato.
- Auto-respond toggle con cooldowns anti-spam.
- Anti-repeticion persistente.

## v1.2.2

**Fecha:** 2026-05-XX

- Rediseño flujo `install.bat`: pre-flight + auto-detect Drive.
- Ascii puro en outputs (fix consola legacy cp1252).

## v1.2.0

- Sprint 9-12: TarroBot + OBS controller + memoria sesion + recetas + quiz +
  C2 generador descripcion + C4-lite Short export + C7 musica fondo.
