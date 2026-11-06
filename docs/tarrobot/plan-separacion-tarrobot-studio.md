# Plan: separar TarroBot Studio del repo del canal

> Estado: PROPUESTA para que Luis la revise. No se movió ni se borró nada del repo del canal.
> Fecha: 2026-11-05. Base: `master` en `215f04d`. Autor: sesión de Claude (rama `claude/funny-wozniak-5c7e9e`).
> Meta: el repo del canal queda solo con contenido (pautas, discusiones, estudio, decks, reseñas, shorts, docs) y las herramientas viven en repos propios dentro de `D:\Recursos Retrotarros\TarroTools\`, como ya hacen TarroDL, TarroTVOS y TarroOBS.

## 1. Resumen y lo que necesito que decidas

**Lo que encontré, en una línea:** TarroBot Studio se puede sacar sin tocar el estudio porque ya funciona "plano" en el Drive: el PC de grabación corre desde `G:\Mi unidad\Studio\Tarrobot\` con la misma estructura `scripts\`, `studio\templates\`, `data\`. Si cada repo nuevo conserva esa estructura y se publica en esa misma carpeta, el estudio no nota el cambio. Lo comprobé armando una copia plana en una carpeta temporal: el panel importa y levanta sus 102 rutas sin tocar el repo.

**Propuesta de partición (recomendada):** tres repos de herramienta, más TarroOBS que ya existe.

| Repo | Qué lleva | Dónde se usa |
|---|---|---|
| `TarroTeaser` | `tarroteaser.py`, `teaser_jobs.py`, `capcut_ready.py`, `generate-teaser.py` | PC de edición (CLI) y botón del panel |
| `TarroShorts` | `tarroshort_render.py`, `tarroshort_jobs.py`, `tarroshort_datos.py`, `_template-tarroshort.html` | PC de edición (CLI) y botón del panel |
| `TarroBot` | panel, CLI de TarroBot, bandeja, chat social, LLM, plantillas del panel, instalador, entrega al estudio | PC de grabación (en vivo) |
| `TarroOBS` (existe) | cliente OBS y apoyo; lo lleva otra sesión | PC de grabación |

**Orden de migración, de menor a mayor riesgo:** TarroTeaser, luego TarroShorts, luego TarroBot (con el recorte de OBS al final de todo). Teaser y Shorts no se usan mientras se graba en vivo, así que un error ahí no arruina una grabación.

**Decisiones que necesito de ti** (mi recomendación va primero):

1. **¿Tres repos o uno solo?** Recomiendo tres. La alternativa de un solo repo `TarroBot` con todo adentro es más barata (no hace falta el truco de rutas hermanas de la sección 5.4) pero deja a TarroTeaser y TarroShorts atados al ciclo del panel. Si prefieres lo simple, se hace un repo y la fase 1 y 2 se juntan.
2. **¿Las pautas de TarroBot (`studio/pautas/*.tarrobot.json`) se quedan en el repo del canal?** Recomiendo que sí: son el guion de cada episodio, es contenido, y el CLAUDE.md ya dice que "el JSON se versiona". La herramienta las lee desde una variable nueva (`RETROTARROS_PAUTAS_DIR`) y el sync del canal sigue copiándolas al Drive como hoy.
3. **¿`data/tarrobot-database.json` (la base de datos curiosos de TarroBot) se va con la herramienta?** Recomiendo que sí: la herramienta la edita en vivo (`agregar_dato`). Hoy pesa 8,8 KB.
4. **¿`_studio_layout.py` queda canónico en el repo del canal y las herramientas llevan una copia vendida, con una prueba que avisa si se desfasan?** Recomiendo que sí (sección 4.3).
5. **¿Se conserva el historial de git al extraer?** Para TarroDL y TarroOBS se hizo "extracción inicial" sin historial. Recomiendo repetir eso y dejar en el README el commit de origen. Si quieres historial, se puede hacer con `git filter-repo`, pero cuesta más y el valor es bajo.
6. **¿El PC de edición se configura con `RETROTARROS_STUDIO_ROOT` apuntando al `studio\` del repo del canal?** Hoy funciona por casualidad (el repo del canal y la herramienta eran la misma carpeta). Al separarlos hay que decirlo explícito. Recomiendo `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"` en el PC de edición.
7. **Pregunta de hecho:** ¿hoy está corriendo TarroBot Studio en el PC de grabación? El spec de julio decía "no hay PC de estudio con TarroBot instalado"; sin embargo el Drive tiene `logs\tarrobot-tray.log` y `INSTALL-INFO.txt` con sync del 2026-11-04. Si ya está instalado, el plan lo trata como en producción (que es la lectura más prudente).

## 2. Inventario de TarroBot Studio dentro del repo del canal

Tamaños medidos en `215f04d`. "Canal" = lo que la pieza lee o escribe del contenido del canal.

### 2.1 Panel y núcleo (repo `TarroBot`)

| Pieza | Líneas | Qué hace | Qué usa del canal | Quién la usa |
|---|---|---|---|---|
| `scripts/tarrobot-live.py` | 4.751 | Panel FastAPI (:8765), 96 decoradores de ruta (21 social, 20 OBS, 13 cola, 4 teaser, 4 short, 3 quiz, 3 LLM, resto sueltas), WebSocket `/ws/live` | `STUDIO.glob("**/tarroshort-*.html")`, `**/*coleccion*.html`, `**/abriendo-el-tarro-*.html` (lista de fuentes para el dropdown), `find_html`, `studio/shorts`, `studio/exports` | `tarrobot-tray.py`, `Iniciar-TarroBot.bat`, `TarroBot*.bat` |
| `scripts/tarrobot.py` | 2.316 | Lógica y CLI (voces TTS, pautas, LLM, melodías MIDI, slides). Define `REPO` desde `RETROTARROS_REPO` | `data/tarrobot-database.json`, `studio/pautas`, `studio/melodias`, `studio/tarrobot-out`, `studio/templates/_template-tarrobot-slide.html`; `--pauta-auto <html>` exige que el HTML esté dentro de `REPO` | `tarrobot-live.py`, `auto_respond.py`, `llm_resolver.py`, `message_store.py`, `tarrobot-probar-voces.py` |
| `scripts/tarrobot-tray.py` | 264 | Bandeja de Windows, arranca el panel sin consola con `pythonw` | Nada del canal | `TarroBot.bat` |
| `scripts/tarrobot-probar-voces.py` | 101 | Genera muestras de voces | Nada | Solo Luis, a mano |
| `scripts/social_manager.py` | 143 | Orquesta conectores y persiste mensajes | Nada | `tarrobot-live.py` |
| `scripts/message_store.py` | 296 | SQLite de mensajes (`data/tarrobot-messages.db`, ignorado) | Nada | `social_manager.py`, `tarrobot-live.py` |
| `scripts/connectors/` (`discord_conn`, `twitch`, `youtube`) | 262, 273, 295 (+123 de `__init__`) | Conectores de chat | Nada | `social_manager.py` |
| `scripts/llm_resolver.py` | 330 | Cache LLM, telemetría, modo barato (`data/tarrobot-cache-llm.json`, ignorado) | Nada | `tarrobot-live.py` |
| `scripts/auto_respond.py` | 188 | Auto-respuesta al chat (`data/tarrobot-auto-respond.json`, ignorado) | Nada | `tarrobot-live.py`, `social_manager.py` |
| `studio/templates/_template-tarrobot-control.html` | 145 KB | Interfaz del panel (tarjetas) | Nada | `tarrobot-live.py` |
| `studio/templates/_template-tarrobot-live.html` | 40 KB | Pantalla en vivo (avatar, TV CRT) | Nada | `tarrobot-live.py` |
| `studio/templates/_template-tarrobot-slide.html` | 23 KB | Slide de un dato | Nada | `tarrobot.py` |
| `studio/templates/_template-tarrobot.html` | 997 | Plantilla base de TarroBot | Nada | Ningún script ni instalador la referencia, y no va en el sync; revisar si sigue en uso |
| `studio/tarrobot-recetas.json` | JSON | Recetas de un click | Nada | `tarrobot-live.py` |
| `studio/melodias/` | 4 KB en git | MIDIs y soundfont (los `.mid`/`.sf2` están ignorados) | Nada | `tarrobot.py` |
| `data/tarrobot-database.json` | 8,8 KB | Base de datos curiosos | Nada | `tarrobot.py` |
| `installers/tarrobot-studio/` | 9 archivos | `install.bat`, `TarroBot*.bat`, `build-package.ps1`, `installer.iss`, `requirements.txt` (v1.5.3) | `install.bat` guarda `RETROTARROS_REPO` | Luis, al armar el paquete |
| `Iniciar-TarroBot.bat` (raíz) | 1 archivo | Arranca el panel desde el repo en el PC de edición | Nada | Luis |
| `HANDOFF-tarrobot-studio.md`, `docs/tarrobot/` | 296 + 313 + 226 | Handoff, changelog, handoff viejo | Nada | Documentación |
| `scripts/obs_{controller,healthcheck,recorder,setup}.py`, `studio/obs-aliases.json` | 4 módulos y un JSON | OBS | Nada | Panel. **Ya copiado a TarroOBS** (otra sesión) |

### 2.2 TarroTeaser (repo `TarroTeaser`)

| Pieza | Líneas | Qué hace | Qué usa del canal | Quién la usa |
|---|---|---|---|---|
| `scripts/tarroteaser.py` | 736 | Teaser vertical 1080x1920 con 5 cortes (Whisper local + ffmpeg). CLI de "corré el tarroteaser" | `STUDIO/teasers/<slug>` (salida); `.cache/whisper` (cache propio); `RETROTARROS_TEASER_OUT` opcional | `teaser_jobs.py`, Luis por CLI |
| `scripts/teaser_jobs.py` | 265 | Cola de trabajos y progreso por WebSocket | Nada directo | `tarrobot-live.py` (4 rutas `/api/teaser/*`) |
| `scripts/capcut_ready.py` | 271 | Prepara carpeta "CapCut ready" (teaser, cartelas, audio) | `find_html`, capturas de `capture-slides`, `STUDIO/teasers`; escribe en `REPO/recordings/<slug>/capcut-ready` (ignorado) | `tarrobot-live.py` (`/api/capcut/...`) |
| `scripts/generate-teaser.py` | 898 | Versión "todo incluido" (backup) | Lee `docs/pautas/pauta-<slug>.md` del canal | Solo Luis, a mano |

### 2.3 TarroShorts (repo `TarroShorts`)

| Pieza | Líneas | Qué hace | Qué usa del canal | Quién la usa |
|---|---|---|---|---|
| `scripts/tarroshort_render.py` | 738 | HTML de short + TTS + ffmpeg -> MP4 vertical | **Lee** `studio/pautas/<slug>.tarrobot.json` y HTMLs de episodios (vía `find_html`); **escribe** HTML en `STUDIO/shorts/shorts-html/<categoria>/`, MP4 en `REPO/studio/shorts/` (ignorado), reacciones en `studio/shorts/highlights/` | `tarroshort_jobs.py`, Luis por CLI, drivers de `.cache/` |
| `scripts/tarroshort_jobs.py` | 195 | Cola de trabajos | Nada directo | `tarrobot-live.py` (4 rutas `/api/tarroshort/*`) |
| `scripts/tarroshort_datos.py` | 175 | Generador de TarroShorts de datos (HTML + guion TTS) | Escribe `studio/tarroshort-<slug>.html`, `studio/shorts/guion-<slug>.txt` | Drivers `.cache/gen_tarroshorts_batch.py` |
| `studio/templates/_template-tarroshort.html` | 10,7 KB | Molde HTML del short | Nada | `tarroshort_render.py`, `tarroshort_datos.py` |

El estilo vigente de los shorts (`docs/modus-operandi/convenciones-tarroshorts.md`) es de contenido y se queda en el canal.

### 2.4 Sincronización

| Pieza | Líneas | Qué hace hoy | Después |
|---|---|---|---|
| `scripts/sync-tarrobot-to-drive.ps1` | 386 | Copia al Drive `Studio\Tarrobot\`: scripts, plantillas, `obs-aliases`, DB, pautas (`/MIR`), melodías, `tarrobot-out`, MP4 de shorts, branding de poleras, instalador (`-slim.zip` más nuevo), `_modus-operandi`, y escribe `INSTALL-INFO.txt`. Modo `-Rapido` | Se parte: cada herramienta publica lo suyo (sección 6); lo que es contenido queda en el canal |
| `scripts/sync-to-drive.ps1` | 313 | Contenido del canal a `Studio\<categoria>\<slug>\`, pautas a DOCX. Ya excluye `tarrobot-out` | Sin cambios de fondo; se le suma el bloque de pautas JSON y shorts MP4 (sección 6.2) |

## 3. Mapa de dependencias

### 3.1 Entre scripts (calculado con un análisis de `import` y carga por nombre de archivo)

```
tarrobot-tray ──> tarrobot-live ──> tarrobot (REPO, DB, pautas, TTS, LLM)
                       │         ├─> social_manager ──> message_store ──> tarrobot
                       │         ├─> llm_resolver ───> tarrobot
                       │         ├─> auto_respond ───> tarrobot
                       │         ├─> obs_controller / obs_recorder / obs_setup / obs_healthcheck   (a TarroOBS)
                       │         ├─> teaser_jobs ───> tarroteaser ──> _studio_layout
                       │         ├─> capcut_ready ───────────────────> _studio_layout
                       │         ├─> tarroshort_jobs ─> tarroshort_render ─> _studio_layout
                       │         └─> _studio_layout (find_html)
tarroshort_datos, generate-teaser: sin imports locales (autónomos)
```

Hallazgos:

- **Nada del lado del contenido importa a TarroBot Studio.** Los generadores de decks (`top_deck`, `coleccion_deck`, `saga_deck`, `resena_deck`, `special_deck`, `retronota_deck`, `tarrovision`, `top_grafica`) y las herramientas de YouTube no importan ninguno de los módulos de arriba. La dependencia va en un solo sentido: herramientas -> contenido. Eso es lo que hace barata la separación.
- **Un único módulo compartido: `_studio_layout.py`.** Lo importan `tarrobot-live`, `tarroteaser`, `capcut_ready`, `tarroshort_render` (herramientas) y también `top_deck`, `capture-slides.py` y `test_top_grafica.py` (canal). Define las reglas slug -> carpeta de categoría. Ver 4.3.
- **`tarrobot.py` es el centro:** lo importan el panel, `auto_respond`, `llm_resolver`, `message_store` y `tarrobot-probar-voces`. Define `REPO` y de ahí cuelgan las rutas de datos propios.
- **Acoplamiento de la herramienta hacia el canal (hoy):** `tarrobot.py` (`_ejecutar_sync_drive`, línea ~455) llama a `scripts/sync-tarrobot-to-drive.ps1` al terminar de crear una pauta. Al separar, esa llamada tiene que apuntar al script de publicación de la propia herramienta (o desactivarse).
- **Los scripts de TarroBot buscan el repo de dos maneras:** `RETROTARROS_REPO` (en `tarrobot.py`, `tarroteaser.py`, `tarroshort_render.py`, `capcut_ready.py`) o "el padre de `scripts/`" como respaldo. Ese respaldo es lo que hace que hoy funcionen tanto en el repo como en el espejo del Drive.

### 3.2 Qué consume cada herramienta del canal

| Del canal | Lo consume | Mecanismo actual |
|---|---|---|
| HTMLs de episodios y shorts (`studio/<categoria>/...`) | panel (listas), TarroShorts, CapCut Ready | `_studio_layout.STUDIO` (`RETROTARROS_STUDIO_ROOT` o `REPO/studio`) |
| Capturas PNG de slides | CapCut Ready | `find_html` + `captures/<slug>/` |
| `studio/pautas/*.tarrobot.json` | TarroBot (cola), TarroShorts (`--from-pauta`) | `REPO/studio/pautas` |
| `docs/pautas/pauta-<slug>.md` | `generate-teaser.py` | `REPO/docs/pautas` |
| Master MP4 de videos | TarroTeaser | Ruta que se pasa por argumento |

### 3.3 Qué escriben las herramientas en el canal

| Salida | Escribe | Va al git del canal |
|---|---|---|
| `studio/teasers/<slug>/` | TarroTeaser | Parcial (hay 2 HTML versionados) |
| `studio/shorts/shorts-html/<categoria>/tarroshort-*.html` | TarroShorts | Sí (contenido) |
| `studio/shorts/guion-datos-*.txt`, `highlights/*.json` | TarroShorts | Sí |
| `studio/shorts/tarroshort-*.mp4`, `audio/` | TarroShorts | No (ignorado); van al Drive |
| `studio/pautas/*.tarrobot.json` | TarroBot (cola/pauta auto) | Sí |
| `studio/pautas/audio/` (MP3) | TarroBot | No (ignorado) |
| `studio/tarrobot-out/` | TarroBot | No (ignorado) |

## 4. Partición propuesta

### 4.1 Repos y qué se queda en el canal

**Se queda en el repo del canal** (es contenido o canal): pautas y discusiones, `studio/` (HTMLs, imágenes, capturas, shorts HTML, guiones, highlights), `docs/` (incluidos `modus-operandi`, `descripciones`, `canal`), `data/coleccion`, `data/resenas`, `data/youtube`, los decks (`top_deck`, `coleccion_deck`, `saga_deck`, `resena_deck`, `special_deck`, `retronota_deck`, `tarrovision`, `top_grafica` y sus pruebas), `capture-slides.py`, `fetch_boxart*.py`, `sync-to-drive.ps1`, `studio/pautas/*.tarrobot.json`, branding y merch (`branding_tarrobot.py`, `merch_poleras.py`, `tarjetas_qr.py`, `studio/branding`), `_studio_layout.py` canónico.

**Se va** a repos propios: lo de las tablas 2.1, 2.2 y 2.3.

**Fuera de alcance de este plan, candidatos futuros** (también son herramientas dentro del repo del canal, pero no son TarroBot): los scripts `youtube_*.py` y sus pruebas, y los generadores de decks. Los decks cambian casi a diario por sesiones de contenido y están acoplados a reglas del CLAUDE.md; separarlos sin una razón fuerte solo agrega conflictos entre sesiones. Los dejo anotados, no propuestos.

### 4.2 Estructura de cada repo: la regla que evita romper el estudio

**Cada repo conserva la misma estructura de carpetas que hoy tiene el espejo del Drive** (`scripts/`, `studio/templates/`, `data/`). Así su `publicar-en-drive.ps1` copia carpeta a carpeta, y en el PC de grabación `RETROTARROS_REPO` sigue apuntando a `Studio\Tarrobot\` con los mismos archivos en los mismos lugares. Ningún `import` cambia. Es el patrón que usa TarroDL.

Ejemplo, TarroTeaser:

```
TarroTeaser/
  scripts/tarroteaser.py  teaser_jobs.py  capcut_ready.py  generate-teaser.py  _studio_layout.py (copia)
  tests/
  README.md  HANDOFF.md  requirements.txt  publicar-en-drive.ps1
```

### 4.3 `_studio_layout.py`: un archivo, tres consumidores

Opciones: (a) copia vendida en cada herramienta con una prueba de desfase, (b) repo `TarroCommon` instalado como paquete, (c) que las herramientas lo carguen del repo del canal.

Recomiendo (a). Son ~100 líneas que cambian solo cuando nace una categoría nueva. (b) agrega un repo y un paso de instalación para un archivo chico. (c) no sirve en el PC de grabación, que no tiene el repo del canal. La prueba de desfase vive en el repo del canal (`scripts/test_studio_layout_copias.py`): si encuentra las carpetas de las herramientas hermanas, compara hashes y falla si difieren; si no las encuentra, se salta. Cada herramienta lo anuncia en su README.

### 4.4 Resolución de rutas: variables de entorno

| Variable | Significado hoy | Significado después | Cambio |
|---|---|---|---|
| `RETROTARROS_REPO` | Raíz de la app: en el PC de grabación es `Studio\Tarrobot`; en edición es el repo | Raíz de la **herramienta** (la carpeta que tiene `scripts/`). No cambia de significado en el estudio | En edición ya no coincide con el repo del canal: se resuelve sola (padre de `scripts/`), no hace falta setearla |
| `RETROTARROS_STUDIO_ROOT` | Contenido del canal; si falta, `REPO/studio` | Igual. **Pasa a ser obligatoria en edición** | `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"`; en el estudio sigue `G:\Mi unidad\Studio` |
| `RETROTARROS_TEASER_OUT` | Override de salida del teaser | Sin cambios | Ninguno |
| `RETROTARROS_FFMPEG` | Ruta de ffmpeg | Sin cambios | Ninguno |
| `RETROTARROS_PAUTAS_DIR` | No existe | Carpeta de `*.tarrobot.json`. Por defecto `REPO/studio/pautas` (comportamiento actual) | **Nueva.** En edición apunta a `...\repo\studio\pautas` |
| `RETROTARROS_CANAL_REPO` | No existe | Repo del canal, para `generate-teaser.py` (lee `docs/pautas`) | **Nueva, opcional.** Solo edición |
| `TARROTOOLS_ROOT` | No existe | Carpeta con los repos hermanos (`TarroBot`, `TarroTeaser`, `TarroShorts`, `TarroOBS`). Solo desarrollo | **Nueva.** Ver 5.4 |
| `ANTHROPIC_API_KEY` | `install.bat` la guarda | Sin cambios | Ninguno |

## 5. Orden de migración, de menor a mayor riesgo

Regla general para cada herramienta (la misma que usa la sesión de TarroOBS): **se migra por copia**. La herramienta nueva gana el código, el repo del canal conserva el suyo hasta un **paso de recorte** aparte, que necesita tu dale. Nada se borra del canal mientras la copia no esté probada con un uso real.

### Fase 0: red de seguridad (en el repo del canal, sin mover nada)

1. **Foto base del espejo del Drive**: lista de archivos y hash de `Studio\Tarrobot\` hoy. Es la vara de medir: el espejo que produzcan los scripts nuevos tiene que ser idéntico, salvo los cambios que decidamos a propósito.
2. **Prueba de humo del panel**: importar `tarrobot-live.py` contra una copia plana del espejo y comparar la lista de rutas con una foto (hoy 102 rutas: 96 decoradores más montajes y rutas de documentación). Ya la corrí a mano con éxito en una carpeta temporal.
3. **Pruebas de caracterización de rutas**: dado cierto `RETROTARROS_REPO` y `RETROTARROS_STUDIO_ROOT`, a dónde apunta cada módulo (`REPO`, `STUDIO`, salidas de teaser y short). Hoy no existe ninguna prueba para todo el bloque TarroBot (`scripts/test_*.py` cubre reseñas, rankings y YouTube, nada de esto).
4. **Cerrar los hallazgos de la sección 8** que conviene arreglar antes de mover (en especial el 1 y el 2).

### Fase 1: TarroTeaser (riesgo bajo)

Por qué primero: CLI con entrada y salida claras, sin tráfico en vivo, solo `_studio_layout` como dependencia, se usa ~1 vez por semana en el PC de edición.

- Repo `TarroTools\TarroTeaser`, GitHub `LuisGaticaJerez/TarroTeaser`.
- Variables: `RETROTARROS_STUDIO_ROOT` obligatoria en edición; `RETROTARROS_CANAL_REPO` opcional para `generate-teaser.py`. `.cache/whisper` pasa a vivir en la carpeta de la herramienta (se puede copiar el cache actual para no re-transcribir).
- Entrega: el panel del estudio importa `teaser_jobs` y `tarroteaser` de `scripts/` del espejo. `publicar-en-drive.ps1` de TarroTeaser copia esos 4 archivos más `_studio_layout.py` a `Studio\Tarrobot\scripts\`. Mismo destino que hoy.
- Pruebas: clasificación de tipo de episodio por slug, resolución de salida (`RETROTARROS_TEASER_OUT` y `STUDIO`), selección de segmentos con una transcripción de ejemplo (sin Whisper real), importabilidad de `teaser_jobs` sin FastAPI. Una prueba de integración opcional con un MP4 corto y ffmpeg.
- Hecho cuando: pruebas verdes, `python scripts\tarroteaser.py <mp4> --slug <slug>` genera un teaser igual de bueno que el del canal sobre el mismo master, y el espejo de Drive producido por `publicar-en-drive.ps1` coincide con la foto base en esos archivos.

### Fase 2: TarroShorts (riesgo bajo a medio)

Por qué segundo: igual que Teaser pero toca más contenido (lee pautas y HTMLs, escribe HTML versionado) y tiene drivers sueltos en `.cache/`.

- Repo `TarroTools\TarroShorts`.
- Variables: `RETROTARROS_STUDIO_ROOT` (HTMLs y salida de `shorts-html`), `RETROTARROS_PAUTAS_DIR` (lee `*.tarrobot.json`). Las salidas que hoy cuelgan de `REPO/studio/shorts` (MP4, `audio/`, `highlights/`) pasan a una carpeta de trabajo de la herramienta, con un paso explícito que copia a `STUDIO` lo que es contenido versionado. **Esta es la parte con más decisiones y la que más puede sorprender**: lo documento en la fase, no lo resuelvo acá.
- Los drivers `.cache/gen_tarroshort*.py` (gitignored) hoy hacen `import tarroshort_datos` por ruta relativa. Hay que ajustarles el `sys.path` a `TARROTOOLS_ROOT\TarroShorts\scripts`. Son pocos y viven solo en el PC de Luis.
- `_template-tarroshort.html` hoy **no** se sincroniza al Drive (ver hallazgo 1 en la sección 8): al publicar desde `TarroShorts` queda incluido.
- Pruebas: mapa de `short_category`, armado de HTML desde una pauta de ejemplo (`--from-pauta` con una pauta chica de fixtures), `tarroshort_datos` con un dict de ejemplo (compara contra un HTML de referencia), cola de `tarroshort_jobs`.
- Hecho cuando: un short real (por ejemplo `tarroshort-datos-pacman`) se rinde de punta a punta desde el repo nuevo y sale igual (mismos textos y duración; el MP4 no será bit a bit idéntico por el TTS) y el panel lo dispara desde la tarjeta.

### Fase 3: TarroBot, el panel y el núcleo (riesgo alto)

Por qué al final: es lo que usa el estudio en vivo, lo instala `install.bat` y tiene el mayor tamaño.

- Repo `TarroTools\TarroBot`.
- `tarrobot.py` mantiene `REPO` desde `RETROTARROS_REPO` o el padre de `scripts/` y sigue funcionando plano en el Drive. `studio/tarrobot-out` se crea al arrancar (hallazgo 2).
- Las rutas `/api/teaser/*`, `/api/tarroshort/*`, `/api/capcut/*` del panel importan módulos que viven en otros repos. En el espejo del Drive están planos y no pasa nada. En el PC de edición hace falta el truco de 5.4.
- `_ejecutar_sync_drive` pasa a llamar al `publicar-en-drive.ps1` de TarroBot.
- El instalador (`installers/tarrobot-studio/`) y su paquete `-slim.zip` salen del repo nuevo; `build-package.ps1` ajusta sus rutas de origen. Versión sigue en 1.5.3 hasta que se publique la primera versión desde el repo nuevo (tag `v1.6.0` propuesto, para no confundir con los tags `v1.x` del canal).
- Pruebas: la foto de rutas (102), `/api/ping` y `/api/state` con `TestClient`, importabilidad con la variable `RETROTARROS_REPO` sin `RETROTARROS_STUDIO_ROOT`, y con ambas; flujo de pauta (crear, guardar, cargar) sobre una carpeta temporal; mock de `edge_tts` y de `anthropic`.
- Hecho cuando: el espejo del Drive producido por los `publicar-en-drive.ps1` de las cuatro herramientas coincide con la foto base, y alguien (tú) hace en el PC de grabación una prueba de 10 minutos: abrir el panel, cargar una pauta, hablar un dato, cambiar escena en OBS y disparar un short.

### Fase 4: recorte en el repo del canal (aparte, con tu dale por herramienta)

Solo cuando una herramienta lleve al menos una sesión real de grabación o edición sin problemas:

- Borrar del canal los scripts y plantillas que migraron.
- Reescribir `sync-tarrobot-to-drive.ps1` (queda solo lo que es contenido: pautas JSON, MP4 de shorts, branding de poleras, `_modus-operandi`; o se absorbe en `sync-to-drive.ps1`).
- Actualizar las referencias de texto: CLAUDE.md (secciones TarroTeaser, TarroShorts, "workflow obligatorio" paso 3, "Capa de notas", "Cómo arrancar una sesión") y ~10 a 18 documentos que mencionan los scripts (`flujo-rankings.md`, `convenciones-tarroshorts.md`, `HANDOFF.md`, etc.). El atajo "corré el tarroteaser" pasa a `python D:\Recursos Retrotarros\TarroTools\TarroTeaser\scripts\tarroteaser.py ...`.
- Regla del CLAUDE.md "los DOS scripts siempre al cerrar" pasa a "`sync-to-drive.ps1` más el `publicar-en-drive.ps1` de cada herramienta que cambió". Propongo un `TarroTools\publicar-todo.ps1` que llame a los cuatro, para no depender de la memoria de nadie.
- Recortar `tarrobot-live.py` para que use TarroOBS (decisión de la sesión de OBS, en coordinación).

### 5.4 Cómo se encuentran las herramientas entre sí en el PC de edición

En el Drive todo está plano, así que el panel encuentra `teaser_jobs` y `tarroshort_jobs` sin trucos. En el PC de edición las herramientas están en carpetas hermanas. Propuesta mínima: al inicio de `tarrobot-live.py`, un bloque que agrega a `sys.path` las carpetas `scripts/` de `TarroTeaser`, `TarroShorts` y `TarroOBS` si existen bajo `TARROTOOLS_ROOT` (por defecto, la carpeta padre de `TarroBot`). Si no existen (caso Drive), no hace nada. Son unas 10 líneas y no cambia el comportamiento en el estudio.

## 6. Cómo llega cada herramienta al PC de grabación

### 6.1 Principio

El PC de grabación no cambia: sigue leyendo `Studio\Tarrobot\` (con `RETROTARROS_REPO`) y `Studio\` (con `RETROTARROS_STUDIO_ROOT`), y no necesita Git. Cada herramienta tiene su `publicar-en-drive.ps1` (como TarroDL) que copia **solo lo necesario para correr**, nunca `tests/`, `.git`, `.cache` ni `__pycache__`.

| Herramienta | Destino en Drive | Qué publica |
|---|---|---|
| TarroTeaser | `Studio\Tarrobot\scripts\` | `tarroteaser.py`, `teaser_jobs.py`, `capcut_ready.py`, `generate-teaser.py`, `_studio_layout.py` |
| TarroShorts | `Studio\Tarrobot\scripts\` y `...\studio\templates\` | los 3 `.py` de short, `_template-tarroshort.html`, `_studio_layout.py` |
| TarroBot | `Studio\Tarrobot\` | el resto de `scripts\`, `connectors\`, plantillas del panel, `tarrobot-recetas.json`, `data\tarrobot-database.json`, melodías, instalador, `INSTALL-INFO.txt` |
| TarroOBS | `Studio\Tarrobot\scripts\` (hoy) | los 4 `obs_*.py` y `studio\obs-aliases.json`; su sesión decide si pasa a `Studio\Tools\TarroOBS` |

Dos scripts que escriben el mismo archivo (`_studio_layout.py`) son seguros porque tienen que ser idénticos; la prueba de desfase de 4.3 lo vigila.

### 6.2 Lo que sigue publicando el canal

`sync-to-drive.ps1` (o un bloque nuevo en él) copia a `Studio\Tarrobot\studio\`: `pautas\*.tarrobot.json`, y los `tarroshort-*.mp4` finales. Es contenido, no código. El `/MIR` de `pautas` no debe correrse desde un worktree que no tenga `pautas\audio` (borraría los MP3 precargados del Drive); mejor `/E` sin `/MIR`, o `/XD audio`. Anotado en la sección 8.

### 6.3 Qué hace Luis una vez por PC

- **PC de grabación:** nada nuevo (ya tiene las dos variables). Si hace falta reinstalar, `install.bat` sigue igual.
- **PC de edición:** `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"` y `setx RETROTARROS_PAUTAS_DIR "D:\Recursos Retrotarros\repo\studio\pautas"`. Si la carpeta de herramientas no está en `D:\Recursos Retrotarros\TarroTools`, también `TARROTOOLS_ROOT`.

## 7. Riesgos y cómo se cubren

| Riesgo | Cómo se cubre |
|---|---|
| Romper la grabación en vivo | Fase 3 al final; el espejo del Drive se compara contra la foto base antes de publicar; prueba de 10 minutos con Luis |
| Desfase de `_studio_layout.py` entre repos | Prueba en el canal que compara hashes; README de cada herramienta lo declara |
| Sesiones de contenido tocan scripts que se movieron | El recorte (fase 4) se hace una herramienta a la vez, con aviso, y el CLAUDE.md se actualiza en el mismo commit |
| Pérdida de pautas, audio precargado o MP4 en Drive | Ningún script nuevo usa `/MIR` sobre carpetas con archivos que solo viven en Drive; `-DryRun` primero |
| Drivers de `.cache/` apuntando a rutas viejas | Se ajustan en la fase 2; viven solo en el PC de Luis |
| Dos sesiones en paralelo (regla del CLAUDE.md) | Cada fase en rama o repo propio; push solo con tu dale; `git fetch` y `git log origin/master..master` antes de cualquier push |
| Se pierde el historial de git | Se deja el commit de origen en el README de cada repo; el repo del canal conserva todo |

## 8. Hallazgos de paso (bugs o riesgos que ya existen hoy)

Los encontré al leer; ninguno lo arreglé (fuera de alcance), pero conviene resolver los 1 a 3 antes de mover:

1. **`_template-tarroshort.html` no está en el sync al Drive.** `tarroshort_render.py` y `tarroshort_datos.py` lo leen de `REPO/studio/templates`. En el espejo de `Studio\Tarrobot\studio\templates\` no está. Si alguna vez se renderiza un short en el PC de grabación desde el Drive, falla. En el PC de edición no pasa porque corre desde el repo.
2. **El panel se cae al importar si falta `studio/tarrobot-out/`.** Está en `.gitignore`, así que un clon limpio no lo trae: `tarrobot-live.py` línea ~1015 monta `StaticFiles` sobre esa carpeta y levanta `RuntimeError`. Lo comprobé en la prueba de humo. En el repo nuevo hay que crearla al arrancar (`mkdir(exist_ok=True)`).
3. **`sync-tarrobot-to-drive.ps1` hace `/MIR` sobre `studio\pautas`.** Desde el repo principal, donde existe `pautas\audio`, no pasa nada; desde un worktree o un clon limpio se llevaría los MP3 precargados que hay en el Drive.
4. **Quedó un resto viejo en el Drive:** `Studio\Tarrobot\studio\_template-tarrobot-*.html` (en la raíz de `studio\`, además de `studio\templates\`). Es de antes de la reorganización de julio. Limpieza pendiente, mencionada como pendiente en el spec del 2026-07-23.
5. **`--pauta-auto <html>` exige que el HTML esté dentro de `REPO`** (`_path_dentro_repo`). Con `RETROTARROS_STUDIO_ROOT` apuntando a otra parte, esa defensa rechaza HTMLs válidos. Hay que cambiarla por "dentro de `REPO` o de `STUDIO`" en la fase 3.
6. **El sync copia `capture-slides.py` y `generate-teaser.py` al espejo y nada del panel los usa** (el único mensaje que menciona `capture-slides` es un comentario de `capcut_ready.py`). `capture-slides.py` puede dejar de ir al Drive.
7. **`studio/templates/_template-tarrobot.html`** (997 líneas) no la referencia ningún script ni instalador, y no va en el sync. Confirmar si sigue en uso.
8. **No hay pruebas automáticas del bloque TarroBot.** Todo lo que migre queda cubierto por las pruebas nuevas de cada fase.
9. **`FFMPEG_BIN` apunta a `installers/tarrobot-studio/bin/ffmpeg.exe`** (ignorado en git): en el repo nuevo la carpeta tiene que existir igual, o el código caer a ffmpeg del `PATH`.

## 9. Lo que haría en el paso 3, con tu dale

Si apruebas el plan, parto por **TarroTeaser** y su fase 0 mínima:

1. Crear `D:\Recursos Retrotarros\TarroTools\TarroTeaser` con estructura `scripts/`, `tests/`, `README.md`, `HANDOFF.md`, `requirements.txt`, `publicar-en-drive.ps1`, copia de los 4 scripts más `_studio_layout.py`.
2. Escribir las pruebas descritas en la fase 1 y correrlas.
3. Generar un teaser de prueba desde un master que ya tengas, con el repo nuevo y con el del canal, y comparar los cortes elegidos.
4. Correr `publicar-en-drive.ps1` en modo prueba (`-DryRun`) y comparar el resultado con la foto base del espejo.
5. Commit en el repo nuevo. **No empujo a GitHub ni creo el repo remoto sin tu dale**, y **no toco** el repo del canal, el Drive ni el estudio.

Lo que no haré sin que lo pidas: borrar nada del canal, publicar en el Drive de verdad, crear repos en GitHub.

## 10. Preguntas abiertas (resumen)

Las 7 de la sección 1, más: ¿quieres que el repo nuevo de cada herramienta nazca con sus pruebas obligatorias en un `README` ("cómo probar"), como TarroDL? ¿Y quieres el `TarroTools\publicar-todo.ps1`? Las dos las daría por sí salvo que me digas lo contrario.
