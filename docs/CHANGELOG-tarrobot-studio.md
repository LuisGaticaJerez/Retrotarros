# CHANGELOG · TarroBot Studio / Retrotarros Studio Suite

Historial de releases del instalador del estudio. Cada version se publica
en GitHub Releases con ZIP + .exe firmados.

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
