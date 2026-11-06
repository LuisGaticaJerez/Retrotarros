# Plan: separar TarroBot Studio del repo del canal (v2, con la visión de Luis)

> Estado: PROPUESTA v2 para que Luis la revise. No se movió ni se borró nada del repo del canal.
> v2 (2026-11-05, noche): reemplaza la partición TarroTeaser / TarroShorts / TarroBot de la v1 por la que describió Luis: TarroDL absorbe Teaser y Shorts, TarroStudio contiene a TarroOBS, TarroBot queda como mascota independiente, y todas se pueden usar entre sí.
> Fecha: 2026-11-05. Base: `master` en `215f04d`. Autor: sesión de Claude (rama `claude/funny-wozniak-5c7e9e`).
> v3 (2026-11-05, noche): Luis aprobó el plan y decidió que **TarroOBS se fusiona en TarroStudio** (Studio lo contiene). Ejecución en curso, ver "Estado de ejecución" al final.
> Meta: el repo del canal queda solo con contenido (pautas, discusiones, estudio, decks, reseñas, shorts, docs) y las herramientas viven en repos propios dentro de `D:\Recursos Retrotarros\TarroTools\`, como ya hacen TarroDL, TarroTVOS y TarroOBS.

## 1. Resumen y lo que necesito que decidas

**La visión (palabras de Luis):** el canal es la motivación; de ahí nacen herramientas que apoyan la creación de contenido, y cualquiera debería poder usar a cualquiera cuando haga falta, tanto para contenido grabado como en vivo. Cada herramienta es independiente, pero puede existir compartiendo contenido y llamando a las otras.

**Las herramientas y lo que contienen:**

| Herramienta | Rol | Contiene (desde el repo del canal) |
|---|---|---|
| **TarroDL** (existe) | Descargador, creador de clips y mosaicos; ahora también el taller de contenido grabado | Hoy: descargas, clips, mosaico. Suma: **TarroTeaser** (`tarroteaser.py`, `teaser_jobs.py`, `generate-teaser.py`), **TarroShorts** (`tarroshort_render.py`, `tarroshort_jobs.py`, `tarroshort_datos.py`, plantilla) y **CapCut Ready** (`capcut_ready.py`) |
| **TarroStudio** (nuevo nombre) | Multiherramienta para streaming; concentra todo lo que se desarrolla en vivo | Panel de control, concentrador de chat (Twitch, Discord, YouTube), recetas; orquesta a TarroBot y contiene a **TarroOBS** |
| **TarroBot** | La mascota y ayudante de los directos | Avatar, voz (TTS y escucha), datos curiosos, cola de pauta, quiz, LLM y su cache |
| **TarroOBS** (se fusiona en TarroStudio, decisión de Luis) | Control de OBS | Pasa a ser un módulo de TarroStudio (`obs/`): cliente, lower-third, música, grabación. El repo `TarroOBS` queda como origen de la copia y se archiva cuando el módulo esté probado dentro de TarroStudio |
| **TarroTVOS** (existe) | Fuera de este plan | |

El repo del canal queda con contenido (pautas, discusiones, estudio, decks, reseñas, shorts HTML, docs).

**Lo que encontré, en una línea:** nada del contenido importa a TarroBot Studio (la dependencia va solo de herramienta a contenido), y el estudio corre "plano" desde `Studio\Tarrobot\` en el Drive, así que se puede mover por etapas sin que el PC de grabación lo note. Comprobé que el panel actual levanta (102 rutas) desde una copia plana en una carpeta temporal.

**Lo que cambia respecto de la v1 y por qué importa:** en la v1 el panel se movía entero a un repo. Con tu visión hay que **partir el panel actual en dos** (Studio y Bot) y mandar sus botones de teaser y short a TarroDL. El panel de hoy es un solo proceso de 4.751 líneas con estado compartido, así que esa partición es lo más delicado y va al final (fases 3 y 4). La sección 3.3 lista los puntos exactos donde hoy Studio y Bot están pegados.

**Orden de migración, de menor a mayor riesgo:**

1. TarroDL gana **TarroTeaser** (no se usa en vivo, es CLI con entradas y salidas claras).
2. TarroDL gana **TarroShorts** y **CapCut Ready**.
3. El panel completo se mueve tal cual a **TarroStudio** (con OBS incorporado como módulo), todavía con Bot dentro del mismo proceso.
4. **TarroBot** se extrae de TarroStudio como herramienta propia, con un contrato de conversación entre las dos.
5. Mudanza de las carpetas del Drive al formato definitivo y recorte del repo del canal, una herramienta a la vez.

**Decisiones que necesito de ti** (mi recomendación va primero):

1. **TarroDL hoy usa solo librería estándar de Python** (y llama a `yt-dlp` y `ffmpeg` como programas externos). Teaser y Shorts necesitan librerías pesadas: Whisper, edge-tts, Playwright, mutagen, anthropic. Recomiendo que TarroDL siga arrancando sin ellas y que Teaser y Shorts sean **módulos opcionales** que se activan al instalar sus requisitos (`requirements-teaser.txt`, `requirements-shorts.txt`), con un aviso claro en pantalla cuando falte algo. Alternativa: que TarroDL dependa de todo siempre; más simple de programar, pero cualquier PC con TarroDL tendría que instalar Whisper (~250 MB de modelo más sus librerías).
2. **RESUELTA por Luis: TarroOBS se fusiona en TarroStudio** (Studio lo contiene). Consecuencias: el código OBS vive como módulo de TarroStudio, no como repo aparte con copia vendida; la sesión que hoy trabaja en `TarroOBS` (lower-third, música, servidor simulado, página mínima) debe seguir ahí solo hasta que exista el repo TarroStudio (fase 3) y entonces portar su trabajo adentro; hasta ese día `TarroOBS` es el lugar de trabajo de OBS y sus commits se portan por copia. El 'TarroOBS usable solo' del handoff de esa sesión se reemplaza por 'TarroStudio sin TarroBot abierto'.
3. **¿Quién es dueña del avatar de la pantalla?** OBS lo muestra como fuente de navegador en `http://localhost:8765/`. Recomiendo **TarroBot** (es su cara), que conserve el puerto 8765 y la ruta `/`, para no romper las escenas de OBS ya armadas. TarroStudio pasa a otro puerto (propongo 8770). Lo confirmo mirando tus escenas de OBS antes de la fase 4.
4. **Recetas** (`tarrobot-recetas.json`: "Arrancar episodio" cambia escena, espera, saluda...) son orquestación de OBS más voz. Recomiendo que vivan en **TarroStudio**, que llama a TarroBot para hablar y a TarroOBS para cambiar escena.
5. **¿Teaser y Short se lanzan desde el panel del directo o solo desde TarroDL?** Hoy hay botones en el panel. Recomiendo que los botones de TarroStudio **llamen a TarroDL si está abierto** en vez de repetir la lógica. Si prefieres que el panel de streaming no los tenga, mejor aún.
6. **Instalador.** Hoy hay uno solo ("TarroBot Studio v1.5.3"). Recomiendo que el PC de grabación instale **una suite** (TarroStudio, que ya trae OBS, más TarroBot) desde un único `install.bat`, y que TarroBot también pueda correr solo. TarroDL sigue con su propia publicación a Drive.
7. **Pautas y base de datos.** Recomiendo que las pautas (`studio/pautas/*.tarrobot.json`, el guion del episodio) **se queden en el canal**, y que `data/tarrobot-database.json` (datos curiosos que TarroBot edita en vivo) **se vaya a TarroBot**. Variable nueva `RETROTARROS_PAUTAS_DIR`.
8. **¿`_studio_layout.py` canónico en el canal y copia vendida en cada herramienta, con prueba de desfase?** Recomiendo que sí (4.4).
9. **¿Historial de git?** Para TarroDL y TarroOBS se hizo "extracción inicial" sin historial. Recomiendo repetir y anotar el commit de origen.
10. **PC de edición:** `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"` (hoy funciona por casualidad, porque la herramienta y el canal eran la misma carpeta).
11. **Pregunta de hecho:** ¿hoy está corriendo TarroBot Studio en el PC de grabación? El spec de julio decía que no, pero el Drive tiene `logs\tarrobot-tray.log` y un sync del 2026-11-04. Lo trato como producción.

## 2. Inventario de TarroBot Studio dentro del repo del canal

Tamaños medidos en `215f04d`. "Canal" = lo que la pieza lee o escribe del contenido del canal.

### 2.1 Panel y núcleo (se reparte entre TarroStudio y TarroBot, ver 3.3 y 4.2)

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

### 2.2 TarroTeaser (pasa a TarroDL)

| Pieza | Líneas | Qué hace | Qué usa del canal | Quién la usa |
|---|---|---|---|---|
| `scripts/tarroteaser.py` | 736 | Teaser vertical 1080x1920 con 5 cortes (Whisper local + ffmpeg). CLI de "corré el tarroteaser" | `STUDIO/teasers/<slug>` (salida); `.cache/whisper` (cache propio); `RETROTARROS_TEASER_OUT` opcional | `teaser_jobs.py`, Luis por CLI |
| `scripts/teaser_jobs.py` | 265 | Cola de trabajos y progreso por WebSocket | Nada directo | `tarrobot-live.py` (4 rutas `/api/teaser/*`) |
| `scripts/capcut_ready.py` | 271 | Prepara carpeta "CapCut ready" (teaser, cartelas, audio) | `find_html`, capturas de `capture-slides`, `STUDIO/teasers`; escribe en `REPO/recordings/<slug>/capcut-ready` (ignorado) | `tarrobot-live.py` (`/api/capcut/...`) |
| `scripts/generate-teaser.py` | 898 | Versión "todo incluido" (backup) | Lee `docs/pautas/pauta-<slug>.md` del canal | Solo Luis, a mano |

### 2.3 TarroShorts (pasa a TarroDL)

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

### 3.3 Dónde hoy Studio y Bot están pegados dentro del panel

Esto es lo que hay que cortar en la fase 4 (separar TarroBot de TarroStudio). Hoy todo vive en un proceso, con un solo `ConnectionManager` de WebSocket, una cola (`QueueManager`) y un rastreador de audio:

| Punto de contacto | Dónde | Quién habla con quién | Cómo queda separado |
|---|---|---|---|
| Auto-escena al hablar | `_hook_pre_hablar` / `_hook_post_hablar` (líneas ~909 y ~931), `/api/obs/auto-escena` | Bot habla -> Studio cambia escena | Bot emite eventos `hablando:inicio` y `hablando:fin` por WebSocket; Studio los escucha |
| Close-up y "gracias" | `/api/obs/close-up`, `/api/obs/gracias` (~1416 y ~1469) | Studio cambia escena y pide frases a Bot | Studio llama a `POST /api/decir` de Bot |
| Recetas | `/api/receta/run` y `studio/tarrobot-recetas.json` | Pasos de OBS más pasos de voz (`saludar`, etc.) | Studio las ejecuta: OBS directo, voz vía Bot |
| Chat -> voz | `/api/social/say`, `respond`, `dictate`, `read-pinned-queue`, auto-respond | Studio recibe el chat; Bot habla y razona (LLM) | Studio llama a Bot (`decir`, `responder`) |
| Cola y OBS | Al iniciar cola: grabación automática; al avanzar dato: lower-third automático (~3816, ~3871) | Bot (cola) -> Studio (OBS) | Bot emite `cola:inicio` y `cola:dato-avanzo`; Studio reacciona |
| Música de fondo | `/api/obs/musica/*` | Studio -> OBS | Va entera a Studio (módulo OBS) |
| Tarjetas de interfaz | `_template-tarrobot-control.html` (145 KB, una sola página con todas las tarjetas) | Todo | Cada herramienta sirve las tarjetas suyas; Studio muestra las de Bot incrustadas o enlazadas |
| Estadísticas LLM | `/api/llm/stats`, modo barato | Bot | Bot; Studio muestra la tarjeta |

Reparto de las rutas del panel actual (por prefijo):

| Va a | Rutas |
|---|---|
| **TarroDL** | `/api/teaser/*` (4), `/api/tarroshort/*` (4), `/api/capcut/preparar` (1) |
| **TarroStudio (con OBS)** | `/api/obs/*` (20, entre ellas música y lower-third), `/api/social/*` (21), `/api/recetas`, `/api/receta/run`, `/control` |
| **TarroBot** | `/` y `/ws/live` (avatar), `/api/state`, `/api/cuentame`, `/api/opinar`, `/api/precio`, `/api/random`, `/api/saludar`, `/api/despedir`, `/api/despertar`, `/api/escuchando`, `/api/personal`, `/api/como-estas`, `/api/que-hacemos`, `/api/catchphrase`, `/api/audio-finished`, `/api/listen`, `/api/voz` (2), `/api/quiz/*` (3), `/api/queue/*` (13, más `short-export`), `/api/pauta/auto-tema`, `/api/episodio/exportar-descripcion`, `/api/session/*` (2), `/api/llm/*` (3), `/api/ping` |

### 3.4 Qué escriben las herramientas en el canal

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

### 4.1 Qué se queda en el canal

Es contenido o canal: pautas y discusiones, `studio/` (HTMLs, imágenes, capturas, shorts HTML, guiones, highlights), `docs/` (incluidos `modus-operandi`, `descripciones`, `canal`), `data/coleccion`, `data/resenas`, `data/youtube`, los decks (`top_deck`, `coleccion_deck`, `saga_deck`, `resena_deck`, `special_deck`, `retronota_deck`, `tarrovision`, `top_grafica` y sus pruebas), `capture-slides.py`, `fetch_boxart*.py`, `sync-to-drive.ps1`, `studio/pautas/*.tarrobot.json`, branding y merch (`branding_tarrobot.py`, `merch_poleras.py`, `tarjetas_qr.py`, `studio/branding`) y `_studio_layout.py` canónico.

Fuera de alcance, candidatos futuros (también son herramientas dentro del repo del canal): los scripts `youtube_*.py` y los generadores de decks. Los decks cambian casi a diario por sesiones de contenido y están acoplados a reglas del CLAUDE.md; separarlos sin una razón fuerte solo agrega conflictos entre sesiones.

### 4.2 Qué va a cada herramienta

| Pieza | TarroDL | TarroStudio (incluye OBS) | TarroBot |
|---|---|---|---|
| `tarroteaser.py`, `teaser_jobs.py`, `generate-teaser.py` | X | | |
| `tarroshort_render.py`, `tarroshort_jobs.py`, `tarroshort_datos.py`, `_template-tarroshort.html` | X | | |
| `capcut_ready.py` | X | | |
| `social_manager.py`, `message_store.py`, `connectors/` | | X | |
| `auto_respond.py` | | X (decide y filtra) | responde cuando Studio se lo pide |
| Recetas (`tarrobot-recetas.json`) | | X | |
| Rutas `/api/obs/*`, tarjeta CONTROL OBS | | X (interfaz, orquestación y lógica OBS) | |
| `obs_*.py`, `obs-aliases.json` | | X (módulo `obs/`) | |
| `tarrobot.py` (voz, pautas, LLM, melodías), `llm_resolver.py` | | | X |
| `tarrobot-tray.py` | | X (arranca la suite) | |
| `_template-tarrobot-live.html`, `-slide.html` (avatar y slide) | | | X |
| `_template-tarrobot-control.html` | | X (se parte) | tarjetas de Bot |
| `data/tarrobot-database.json`, melodías | | | X |
| `installers/tarrobot-studio/` | | X (suite) | también corre solo |
| `Iniciar-TarroBot.bat`, `HANDOFF-tarrobot-studio.md`, `docs/tarrobot/` | | X | X (cada uno su parte) |
| `_studio_layout.py` | copia | copia | copia |

### 4.3 Cómo se usan entre sí (el contrato de interoperación)

Tu criterio: independientes, pero capaces de compartir contenido y usarse unas a otras. Propongo cuatro reglas simples:

1. **Cada herramienta funciona sola.** Si le falta una compañera, la función que depende de ella se oculta o avisa ("TarroBot no está abierto"); nada se cae. Prueba obligatoria en cada repo: arrancar sin las otras.
2. **Cada herramienta ofrece una API local en HTTP** (`127.0.0.1`, solo local) con `GET /api/ping` que responde `{herramienta, version, puerto, capacidades}`. TarroDL ya es un servidor local y TarroBot ya tiene `/api/ping`.
3. **Descubrimiento por archivo de ejecución.** Al arrancar, cada herramienta escribe `%LOCALAPPDATA%\TarroTools\<herramienta>.json` con puerto y PID (TarroDL usa puerto aleatorio, así que no se puede asumir uno fijo). Quien quiera llamar a otra lee ese archivo. Un cliente mínimo de unas 40 líneas con solo librería estándar (`tarrotools_cliente.py`: `descubrir()`, `llamar()`) se copia en cada repo, con la misma prueba de desfase de `_studio_layout`.
4. **Eventos en vivo por WebSocket** desde TarroBot (`hablando:inicio`, `hablando:fin`, `cola:inicio`, `cola:dato-avanzo`, `quiz:...`) y desde TarroStudio (`escena:cambio`, `grabacion:...`), para que las demás reaccionen sin acoplarse.

Contenido compartido: **la carpeta de contenido del canal** (`RETROTARROS_STUDIO_ROOT` para HTMLs, capturas, teasers y shorts; `RETROTARROS_PAUTAS_DIR` para pautas) y una carpeta de intercambio `TarroTools\_compartido` (o `Studio\Tools\_compartido` en el Drive) para clips y masters que una produce y otra consume. Ejemplos que ya tienen sentido:

- TarroDL baja un gameplay y corta clips -> TarroShorts los usa como B-roll en la TarroVisión.
- TarroDL hace el teaser de un master -> TarroStudio muestra el estado del trabajo en el panel del directo.
- TarroStudio recibe un mensaje del chat -> pide a TarroBot que lo lea o lo responda -> el módulo OBS de TarroStudio cambia la escena mientras habla.
- TarroBot narra un short -> TarroDL lo renderiza.

### 4.4 `_studio_layout.py` y el cliente común

Opciones: (a) copia vendida en cada herramienta con una prueba de desfase, (b) repo `TarroCommon` instalado como paquete, (c) cargarla del repo del canal.

Recomiendo (a). Son ~100 líneas que cambian solo cuando nace una categoría nueva. (b) agrega un repo y un paso de instalación para un archivo chico; (c) no sirve en el PC de grabación, que no tiene el repo del canal. La prueba vive en el canal (`scripts/test_studio_layout_copias.py`): si encuentra las carpetas de las herramientas hermanas, compara hashes y falla si difieren; si no, se salta. Lo mismo para `tarrotools_cliente.py`.

### 4.5 Estructura de cada repo: la regla que evita romper el estudio

Mientras dure la transición, **cada repo conserva la estructura plana que hoy tiene el espejo del Drive** (`scripts/`, `studio/templates/`, `data/`). Así su `publicar-en-drive.ps1` copia carpeta a carpeta y en el PC de grabación `RETROTARROS_REPO` sigue apuntando a `Studio\Tarrobot\` con los archivos en los mismos lugares. Ningún `import` cambia. Es el patrón de TarroDL.

TarroDL es la excepción por estar ya hecho: su código es un archivo grande (`tarrodl.py`, 1.728 líneas) más `ui/`. Teaser y Shorts entran como paquete aparte (`tarrodl_taller/` con `teaser/` y `shorts/`) para no tocar el archivo grande, y TarroDL los carga solo si están sus librerías.

### 4.6 Resolución de rutas: variables de entorno

| Variable | Hoy | Después | Cambio |
|---|---|---|---|
| `RETROTARROS_REPO` | Raíz de la app: en el PC de grabación es `Studio\Tarrobot`; en edición es el repo | Raíz de la **herramienta** (la carpeta con `scripts/`). Igual en el estudio | En edición ya no coincide con el repo del canal: se resuelve sola (padre de `scripts/`) |
| `RETROTARROS_STUDIO_ROOT` | Contenido del canal; si falta, `REPO/studio` | Igual. **Obligatoria en edición** | `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"`; en el estudio sigue `G:\Mi unidad\Studio` |
| `RETROTARROS_TEASER_OUT`, `RETROTARROS_FFMPEG`, `ANTHROPIC_API_KEY` | Existentes | Sin cambios | Ninguno |
| `RETROTARROS_PAUTAS_DIR` | No existe | Carpeta de `*.tarrobot.json`; por defecto `REPO/studio/pautas` | **Nueva** |
| `RETROTARROS_CANAL_REPO` | No existe | Repo del canal (`generate-teaser.py` lee `docs/pautas`) | **Nueva, opcional** |
| `TARROTOOLS_ROOT` | No existe | Carpeta con los repos de herramientas, para quien necesite encontrar a otra sin archivo de ejecución | **Nueva, opcional** |

## 5. Orden de migración, de menor a mayor riesgo

Regla general (la misma de la sesión de TarroOBS): **se migra por copia**. La herramienta nueva gana el código; el repo del canal conserva el suyo hasta un **paso de recorte** aparte, que necesita tu dale. Nada se borra del canal mientras la copia no esté probada con un uso real. Push a GitHub solo con tu dale.

### Fase 0: red de seguridad (en el repo del canal, sin mover nada)

1. **Foto base del espejo del Drive**: lista de archivos y hash de `Studio\Tarrobot\` hoy. El espejo que produzcan los scripts nuevos tiene que ser idéntico, salvo cambios hechos a propósito.
2. **Prueba de humo del panel**: importar `tarrobot-live.py` contra una copia plana del espejo y comparar la lista de rutas con una foto (hoy 102). Ya la corrí a mano con éxito.
3. **Pruebas de caracterización de rutas**: dado cierto `RETROTARROS_REPO` y `RETROTARROS_STUDIO_ROOT`, a dónde apunta cada módulo. Hoy no existe ninguna prueba para todo el bloque TarroBot (`scripts/test_*.py` cubre reseñas, rankings y YouTube).
4. **Cerrar los hallazgos 1 y 2 de la sección 8** antes de mover.
5. **Confirmar con Luis las escenas de OBS** (¿usan una fuente de navegador a `localhost:8765`?), por la decisión 3.

### Fase 1: TarroDL gana TarroTeaser (riesgo bajo)

- Por qué primero: CLI con entrada y salida claras, sin tráfico en vivo, solo `_studio_layout` como dependencia, ~1 uso por semana en el PC de edición.
- En TarroDL: paquete opcional `tarrodl_taller/teaser/` con `tarroteaser.py`, `teaser_jobs.py` y `generate-teaser.py`; pestaña "Teaser" en la interfaz; `requirements-teaser.txt` (Whisper y compañía). Rutas del servidor de TarroDL: `/api/teaser/*`, con la misma forma que las del panel actual.
- Variables: `RETROTARROS_STUDIO_ROOT` obligatoria en edición; `.cache/whisper` pasa a la carpeta de TarroDL (se copia el cache actual para no re-transcribir).
- Pruebas: **las 72 de TarroDL siguen verdes** (criterio duro: la base no se rompe), más las nuevas: clasificación de tipo de episodio por slug, resolución de salida, selección de segmentos con una transcripción de ejemplo (sin Whisper real), cola de trabajos, y TarroDL arranca sin las librerías del teaser mostrando el aviso.
- Hecho cuando: pruebas verdes; el teaser de un mismo master sale igual desde TarroDL y desde el canal; el espejo de Drive no cambia (TarroDL publica a `Studio\Tools\TarroDL`, y el panel de hoy sigue usando su copia).

### Fase 2: TarroDL gana TarroShorts y CapCut Ready (riesgo bajo a medio)

- Más decisiones que Teaser: lee pautas y HTMLs, escribe HTML versionado y tiene drivers sueltos en `.cache/gen_tarroshort*.py`. Dependencias: Playwright, edge-tts, mutagen, anthropic.
- Salidas: el HTML de `shorts-html`, los guiones y `highlights` (contenido versionado) van a `STUDIO_ROOT`; los MP4 y `audio/` (regenerables) a una carpeta de trabajo de TarroDL, con un paso explícito de copia al Drive. Es la parte con más decisiones y la que más puede sorprender; la dejo detallada al arrancar la fase.
- Los drivers de `.cache/` se ajustan (solo viven en el PC de Luis).
- `_template-tarroshort.html` viaja con TarroShorts (hoy no llega al Drive: hallazgo 1).
- CapCut Ready toma teaser y capturas y arma la carpeta; va junto a Teaser porque su insumo principal es el teaser.
- Pruebas: mapa de `short_category`, armado de HTML desde una pauta de ejemplo, `tarroshort_datos` con un dict de ejemplo contra un HTML de referencia, cola de trabajos.
- Hecho cuando: un short real (`tarroshort-datos-pacman`) se renderiza de punta a punta desde TarroDL con los mismos textos y duración (el MP4 no será bit a bit igual por el TTS).

### Fase 3: el panel completo se muda a TarroStudio (riesgo alto)

- Repo `TarroTools\TarroStudio`. Se mueve **tal cual**, con TarroBot todavía adentro del mismo proceso y con el código de OBS incorporado como módulo propio (fusión: se porta lo que haya avanzado en el repo `TarroOBS`). Sin cortar nada: es solo cambiar de casa, de nombre y de instalador.
- Los botones de teaser y short pasan a llamar a TarroDL (decisión 5) o se esconden si no está.
- `studio/tarrobot-out` se crea al arrancar (hallazgo 2).
- `_ejecutar_sync_drive` apunta al `publicar-en-drive.ps1` de TarroStudio.
- Versión: primera publicación desde el repo nuevo como `v2.0.0` (nueva generación, para no confundir con los tags `v1.x` del canal).
- Pruebas: la foto de rutas (102), `/api/ping` y `/api/state` con `TestClient`, importabilidad con y sin `RETROTARROS_STUDIO_ROOT`, flujo de pauta sobre una carpeta temporal, mock de `edge_tts` y `anthropic`.
- Hecho cuando: el espejo del Drive producido por el `publicar-en-drive.ps1` nuevo coincide con la foto base, y tú haces una prueba de 10 minutos en el PC de grabación (abrir panel, cargar pauta, hablar un dato, cambiar escena en OBS).

### Fase 4: TarroBot sale de TarroStudio (riesgo más alto)

- Se corta por los puntos de la sección 3.3: Bot pasa a un proceso propio en el puerto 8765 con el avatar en `/` (decisión 3); Studio a otro puerto. Entre los dos: HTTP y WebSocket (sección 4.3).
- Primero se define el contrato (nombres de rutas y de eventos) y se escribe una **prueba de contrato**: un TarroBot falso y un TarroStudio falso se hablan por ese contrato. Solo después se corta el código.
- Comportamiento sin compañera: Studio sin Bot muestra "TarroBot no está abierto" y deja usar OBS y chat; Bot sin Studio habla, lleva la cola y el quiz sin escenas.
- La tarjeta de interfaz de 145 KB se parte: Studio con OBS, chat y recetas; Bot con voz, cola, quiz y LLM.
- Hecho cuando: la prueba de contrato y las de cada herramienta pasan, y repites en el estudio la prueba de 10 minutos con los dos procesos, incluido el chat leído por Bot y la escena cambiando mientras habla.

### Fase 5: mudanza de Drive y recorte del canal (aparte, con tu dale por herramienta)

- **Drive**: hoy todo cuelga de `Studio\Tarrobot\`. El formato final es `Studio\Tools\<Herramienta>\` (como TarroDL). Es un paso deliberado, con reconfiguración única en el PC de grabación (`RETROTARROS_REPO` nuevo y reinstalar accesos directos). Hasta entonces se mantiene el espejo plano y compatible.
- **Canal**: borrar lo migrado; reescribir `sync-tarrobot-to-drive.ps1` (queda solo lo que es contenido: pautas JSON, MP4 de shorts, branding de poleras, `_modus-operandi`) o absorberlo en `sync-to-drive.ps1`; actualizar las referencias de texto: CLAUDE.md (secciones TarroTeaser, TarroShorts, "workflow obligatorio" paso 3) y los ~10 a 18 documentos que mencionan los scripts. El atajo "corré el tarroteaser" pasa a TarroDL.
- La regla "los DOS scripts siempre al cerrar" pasa a "`sync-to-drive.ps1` más el `publicar-en-drive.ps1` de cada herramienta que cambió". Propongo un `TarroTools\publicar-todo.ps1` que llame a todos.

## 6. Cómo llega cada herramienta a los PC

### 6.1 PC de grabación (estudio)

Transición (fases 1 a 4): el panel y sus módulos siguen leyendo `Studio\Tarrobot\` con las mismas variables; cada `publicar-en-drive.ps1` escribe ahí lo suyo. TarroDL sigue en `Studio\Tools\TarroDL`. Cuando una herramienta pasa a la mudanza (fase 5), su `publicar-en-drive.ps1` cambia de destino.

| Herramienta | Destino en transición | Qué publica |
|---|---|---|
| TarroDL | `Studio\Tools\TarroDL` (ya existe) | `tarrodl.py`, `ui\`, `tarrodl_taller\` e `iniciar-tarrodl.cmd`; los requisitos pesados se instalan solo en el PC que haga teasers o shorts |
| TarroStudio | `Studio\Tarrobot\` | `scripts\` del panel, `connectors\`, plantillas, recetas, instalador, `INSTALL-INFO.txt` |
| TarroBot (fase 4) | `Studio\Tarrobot\` | `tarrobot.py`, `llm_resolver.py`, avatar, base de datos, melodías |
| (OBS, dentro de TarroStudio) | `Studio\Tarrobot\scripts\` | `obs_*.py` y `studio\obs-aliases.json`, publicados por TarroStudio |

Nunca se publica `tests/`, `.git`, `.cache` ni `__pycache__`.

### 6.2 Lo que sigue publicando el canal

`sync-to-drive.ps1` (o un bloque nuevo) copia a `Studio\Tarrobot\studio\`: `pautas\*.tarrobot.json` y los `tarroshort-*.mp4` finales. El `/MIR` de `pautas` no debe correrse desde un worktree sin `pautas\audio` (borraría los MP3 precargados del Drive); usar `/E` o `/XD audio`.

### 6.3 Qué hace Luis una vez por PC

- **PC de grabación:** nada en las fases 1 a 3; en la fase 4, probar y, en la fase 5, la reconfiguración única.
- **PC de edición:** `setx RETROTARROS_STUDIO_ROOT "D:\Recursos Retrotarros\repo\studio"` y `setx RETROTARROS_PAUTAS_DIR "D:\Recursos Retrotarros\repo\studio\pautas"`. TarroDL en ese PC instala los requisitos de Teaser y Shorts.

## 7. Riesgos y cómo se cubren

| Riesgo | Cómo se cubre |
|---|---|
| Romper la grabación en vivo | Fases 3 y 4 al final; espejo del Drive comparado con la foto base; prueba de 10 minutos contigo |
| Las escenas de OBS dejan de ver el avatar (cambio de puerto o de ruta) | Bot conserva 8765 y `/`; se verifica contra tus escenas en la fase 0 |
| TarroDL pierde su simpleza (solo librería estándar) | Teaser y Shorts son módulos opcionales; las 72 pruebas de TarroDL son criterio duro; TarroDL arranca sin las librerías pesadas |
| Puertos en conflicto (TarroDL no tiene puerto fijo; TarroBot usa 8765) | Archivo de ejecución por herramienta; puertos por defecto documentados (Bot 8765, Studio 8770, el resto aleatorio) |
| Studio y Bot se llaman en círculo | Contrato escrito antes de cortar, con prueba de contrato; los eventos van solo de Bot a Studio y las órdenes de Studio a Bot |
| Desfase de `_studio_layout.py` o del cliente común | Prueba en el canal que compara hashes |
| Sesiones de contenido tocan scripts que se movieron | El recorte se hace una herramienta a la vez, con aviso, y el CLAUDE.md se actualiza en el mismo commit |
| Pérdida de pautas, audio o MP4 en Drive | Ningún script nuevo usa `/MIR` sobre carpetas con archivos que solo viven en Drive; `-DryRun` primero |
| Drivers de `.cache/` apuntando a rutas viejas | Se ajustan en la fase 2 |
| Dos sesiones en paralelo | Cada fase en rama o repo propio; push solo con tu dale; `git fetch` y `git log origin/master..master` antes de cualquier push |
| Se pierde el historial de git | Se anota el commit de origen en cada README; el canal conserva todo |

## 8. Hallazgos de paso (bugs o riesgos que ya existen hoy)

Los encontré al leer; ninguno lo arreglé (fuera de alcance), pero conviene resolver los 1 y 2 antes de mover:

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

Parto por la **fase 1: TarroDL gana TarroTeaser**, en una rama de TarroDL y sin tocar el canal:

1. Correr las 72 pruebas de TarroDL y anotar la línea base (tiempo y resultado).
2. Agregar `tarrodl_taller/teaser/` con los 3 scripts y `_studio_layout.py` (copia), cargados de forma opcional; ruta `/api/teaser/*` y pestaña en la interfaz.
3. Escribir las pruebas de la fase 1 y correr todo junto (72 más las nuevas).
4. Generar un teaser de prueba desde un master que ya tengas, con TarroDL y con el canal, y comparar los cortes elegidos.
5. Commit en TarroDL. **No empujo a GitHub, no publico en el Drive de verdad, no toco el canal ni el estudio** sin tu dale.

Antes necesito tus respuestas a las decisiones 1, 5 y 10 de la sección 1 (las que afectan esta fase). Las demás pueden esperar a las fases 3 y 4.

## 10. Preguntas abiertas (resumen)

Las 11 de la sección 1. Las más urgentes son la 1 (TarroDL con módulos opcionales), la 2 (resuelta: OBS se fusiona en Studio; falta avisar a la sesión de TarroOBS) y la 3 (puerto y avatar).

## Estado de ejecución

- **Decisiones tomadas por Luis (2026-11-05):** aprueba el plan y se parte según él; TarroOBS se fusiona en TarroStudio. Las decisiones 1, 5 y 10 de la sección 1 se toman con mi recomendación (módulos opcionales en TarroDL, botones del panel que llaman a TarroDL, `RETROTARROS_STUDIO_ROOT` explícita en edición).
- **Fase 1 (TarroDL gana TarroTeaser): hecha y mergeada a `main` de TarroDL** (avance rápido local, commit `a1dc6b5`, sin push). Pestaña TARROTEASER, rutas `/api/teaser` y `/api/teaser_status`, módulo en `tarrodl_taller/teaser/`. Pruebas verdes y pestaña revisada en el navegador.
- **Fase 2 (TarroDL gana TarroShorts y CapCut Ready): hecha, sin merge ni push.** Rama `claude/tarrodl-taller-shorts` del repo TarroDL (worktree `.claude\worktrees\taller-shorts`), commit `3405dac`. Pestaña TARROSHORT (short ya armado, desde pauta o desde episodio), tarjeta CAPCUT READY en TARROTEASER, rutas `/api/short`, `/api/shorts_status` y `/api/capcut`; `tarroshort_datos.py` viaja sin pestaña. `_studio_layout.py` pasó a `tarrodl_taller/` para compartirlo. **116 pruebas verdes** (72 de base, 23 del teaser, 21 de shorts y CapCut); el render completo de un short se probó de punta a punta (Playwright, voz, ffmpeg) con `TARRODL_TEST_SHORT_REAL=1`.
- **Hallazgo importante (afecta también al canal y al estudio):** `edge-tts` 7.2.8, la versión instalada en este PC, recibe **403 de Microsoft** al pedir voz; la 7.3.1 funciona (lo verifiqué en una carpeta temporal, sin tocar tu instalación). El instalador de TarroBot pide `edge-tts>=7.0`, así que cualquier PC con 7.2.8 se queda sin voz. Falta decidir: subir el piso a `>=7.3.1` en `installers/tarrobot-studio/requirements.txt` y actualizar el PC (`python -m pip install -U edge-tts`). Los requisitos de TarroShort en TarroDL ya piden 7.3.1.
- **Pendiente:** `generate-teaser.py` no se copió; falta la prueba del teaser con Whisper real sobre un master tuyo; el mergeo de la fase 2 a `main` de TarroDL; los drivers de `.cache/gen_tarroshort*.py` siguen apuntando a los scripts del canal (se ajustan al recorte, fase 5).
- **Fase 0 parcial:** foto base del espejo del Drive y foto de las 102 rutas del panel en la carpeta de notas de la sesión; la prueba de desfase de `_studio_layout.py` está en el canal (`scripts/test_studio_layout_copias.py`) y ya busca la copia nueva en `tarrodl_taller/`.
- **Siguiente:** fase 3 (el panel completo se muda a TarroStudio, con OBS adentro), cuando apruebes la fase 2.
