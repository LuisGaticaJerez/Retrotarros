# TarroBot — Handoff Doc

> Estado de TarroBot Studio para retomar en otra sesion. **Leer este archivo + `installers/tarrobot-studio/README-ESTUDIO.txt` antes de tocar codigo.**

## Estado al 2026-05-21

**Version actual:** `v1.2-tarrobot` (release publico en GitHub).

**12 commits desde v1.1.** 4 sprints cerrados hoy (9, 10, 11, 12) + paquete distribuible + instalador `.exe` profesional.

### Distribuibles publicados

| Archivo | Tamaño | Donde |
|---|---|---|
| `TarroBot-Studio-Setup-v1.2.exe` | 33 MB | GitHub Release + `G:\Mi unidad\Studio\tarrobot\` |
| `TarroBot-Studio-v1.2.zip` (full) | 34 MB | GitHub Release + Drive |
| `TarroBot-Studio-v1.2-slim.zip` (slim) | 3 MB | GitHub Release + Drive |

**URL release:** https://github.com/LuisGaticaJerez/Retrotarros/releases/tag/v1.2-tarrobot

### Lo que esta funcionando

- TarroBot habla con personalidad (saludos, despedidas, opiniones, catchphrases, lore personal, datos curiosos, melodias MIDI)
- Control de OBS por voz y panel: cambio de escenas, toggles de overlays, tomas cercanas con reaccion WOW, "gracias TarroBot" cierra el close-up
- Hook auto-escena al hablar (toggle en panel)
- Musica de fondo controlable por voz y panel (sube, baja, mute)
- Cola del episodio con pautas precargadas + melodias separadas
- Quiz interactivo trivia (lleva score acumulado)
- Recetas/secuencias con un click (intro_episodio, outro_episodio, transicion_a_koko, tomar_aire)
- Generar pauta auto desde tema (1-3 min con LLM): `--pauta-tema "tema"`
- Presentador asistente (Claude reordena pauta para retencion)
- Exportar descripcion + titulos + thumbnails post-grabacion
- Exportar dato como Short (MP3 + SRT individual)
- Anti-repeticion en todas las frases random
- Memoria de sesion (contadores + ultimo tema)
- Jitter pitch/rate sutil
- Whisper con contexto de pauta cargada
- Rate limit LLM (3s cooldown)

## Backlog: mejoras propuestas para la proxima sesion

Lista priorizada despues de revisar el sistema end-to-end. Total estimado: ~5h para las 5 primeras.

### Prioridad alta (resuelven dolor real)

#### 1. Sesion persistente en disco
**Problema:** `SessionStats` y `session_log` viven en memoria. Si el server crashea o cierras sin querer, **perdes toda la grabacion**: contadores, ultimo dato, timestamps reales para SRT/descripcion.

**Fix propuesto:**
- Append-only a `studio/sessions/<fecha>-<slug>.jsonl` cada vez que un evento muta estado.
- Al arrancar, ofrecer "tu ultima sesion fue 2h atras, dato 7 de 10, retomas?"
- Endpoint `/api/session/load <fecha>` para resumir sesion previa.
- Beneficio adicional: **timestamps reales SIEMPRE** para exportar descripcion (hoy es opcional segun si hay session_log).

**Esfuerzo:** 1h. **Archivos:** `tarrobot-live.py` (SessionStats + new dump_event), `studio/sessions/` (gitignored).

#### 2. Healthcheck endpoint + boton PRE-FLIGHT CHECK
**Problema:** Descubres que algo falla **en pleno programa** (Whisper no descargado, OBS no conectado, API key vencida, soundfont faltante, permisos de escritura).

**Fix propuesto:** `/api/health` que verifica en paralelo:
- Claude API responde (timeout 3s)
- OBS conectado + escenas esperadas existen
- ffmpeg encontrable en PATH/bin
- Whisper model cacheado
- soundfont.sf2 presente
- Permisos escritura en `studio/exports/`, `studio/shorts/`, `studio/sessions/`
- Disk space disponible (min 1 GB)

Boton **"PRE-FLIGHT CHECK"** en panel con checklist verde/rojo en 5s.

**Esfuerzo:** 1h. **Archivos:** `tarrobot-live.py` (endpoint), `_template-tarrobot-control.html` (card).

#### 3. Modo "ensayar" (preview en cascos)
**Problema:** Todo lo que TarroBot dice va al live. Para verificar un dato antes de grabar, tenes que tirarlo en vivo y reiniciar.

**Fix propuesto:** Toggle **MODO ENSAYO** en panel. Cuando esta on:
- TarroBot genera el MP3 pero NO broadcastea al live
- NO cuenta para SessionStats
- Solo se reproduce en el navegador del operador
- Indicador visual en el panel "ENSAYO" en color amarillo

**Esfuerzo:** 45 min. **Archivos:** `tarrobot-live.py` (flag ensayo en _hablar_frase, _reproducir_dato_de_cola), `_template-tarrobot-control.html` (toggle).

#### 4. Prompt caching de Anthropic
**Problema:** Cada llamada a `cuentame`, `opinar`, `generar_quiz_con_llm`, `generar_pauta_tema_con_llm`, `generar_reorden_pauta_con_llm`, `generar_descripcion_episodio_con_llm` manda **200+ lineas de system prompt repetidas**. Para uso semanal durante meses = costo + latencia significativos.

**Fix propuesto:** Agregar `cache_control: {"type": "ephemeral"}` en bloques estables del system prompt (las reglas de chileno neutro + filtros que se repiten). **Ahorra ~50% latencia y costo.**

**Esfuerzo:** 45 min. **Archivos:** `tarrobot.py` (todas las funciones LLM), `tarrobot-live.py` (idem).

#### 5. Pre-flight de la pauta antes de grabar
**Problema:** Al cargar una pauta nueva no sabes si todos los MP3s estan precargados hasta que aprietes NEXT y descubras que el dato 7 no tiene audio.

**Fix propuesto:** Boton **"VERIFICAR PAUTA"** en la card COLA que en 3s te dice:
- 10/10 datos con MP3 OK
- O 8/10 OK, 2 faltantes + click para precargarlos
- Duracion total estimada (suma `duracion_ms`): "Episodio durara ~24 min"
- Distribucion de estados emocionales: "5 talking, 3 excited, 2 fact - bien variado"

**Esfuerzo:** 1h. **Archivos:** `tarrobot-live.py` (endpoint `/api/queue/verify`), `_template-tarrobot-control.html` (boton + render).

### Prioridad media (cuando sobre tiempo)

#### 6. Tests unitarios para funciones criticas
**Cero tests hoy.** Las criticas a cubrir:
- `parsear_intent` (35+ keywords, faciles colisiones)
- `chilenizar` (regex anti-voseo, casos borde)
- `pick_no_repeat` (logica de ventana)
- `_aplicar_wake_word` (17 variantes)
- `_clamp_volumen_db`, `_jitter_pitch`, `_jitter_rate`

Pytest, 30-40 casos.

**Esfuerzo:** 2h.

### Prioridad baja (ambicioso, requiere validacion en uso real)

#### 7. Awareness conversacional (always-on listening)
**Problema:** Hoy TarroBot solo reacciona a comandos explicitos. Si Luis dice "esto me recuerda al Mario Kart de Wii", TarroBot no interviene.

**Fix propuesto:** Modo "escucha activa":
- Whisper transcribe todo en streaming (sin requerir push-to-talk)
- Cada 15-20s: ventana de transcripcion → Claude haiku → "¿hay algo aca que TarroBot deberia comentar?"
- Si responde si → interviene espontaneo
- Si no → queda callado

**Riesgos:**
- Latencia: 5-8s entre el comentario y la intervencion (puede interrumpir mal)
- Costo: ~180 llamadas LLM por hora de grabacion
- Whisper falla mas en habla casual de dos personas que en comandos
- Necesita UI de controles (sensibilidad, cooldown entre intervenciones, lista de bloqueo de temas)

**Esfuerzo:** 3-4h + sesiones de ajuste fino en grabacion real.

### NO hacer (descartadas con argumento)

- **Multimodal con OBS** (Claude vision viendo lo que esta en pantalla): latencia mata el flow en vivo. Mejor que el operador diga "TarroBot, lo que ves es un Conker's Bad Fur Day".
- **Render video TarroBot para Shorts auto** (C4 pleno): requiere toolchain de video aparte (Remotion, headless browser). Proyecto de 2-3 dias. La version lite (audio + SRT) ya cubre el caso, CapCut hace el resto.
- **App movil nativa**: el panel web ya funciona desde el celu por wifi. App nativa es overkill por ~3h de trabajo + mantenimiento extra.

## Como retomar la proxima sesion

### Si vienes a meter mejoras del backlog

1. Lee este HANDOFF + `installers/tarrobot-studio/README-ESTUDIO.txt`
2. `git pull origin master` (estamos en `master`)
3. Crear branch `tarrobot/sprint-13` o similar
4. Elegir top de prioridad. Las 5 primeras son ~5h en total, hacelas en una pasada.
5. Tests rapidos: `python -c "import ast; ast.parse(open('scripts/tarrobot-live.py').read())"` despues de cada edicion
6. Al cerrar: `git commit` + `sync-tarrobot-to-drive.ps1` + opcional `build-package.ps1` + `gh release create v1.3-tarrobot`

### Si Luis trae cambios a una pauta existente

1. Identificar slug de la pauta (`studio/pautas/<slug>.tarrobot.json`)
2. Editar JSON directamente o regenerar con `python scripts/tarrobot.py --pauta-tema "..." --slug <slug> --force`
3. Si cambian textos: regenerar MP3s con `python scripts/tarrobot.py --pauta-preload <slug> --force`
4. Sync al Drive: `.\scripts\sync-tarrobot-to-drive.ps1`
5. Commit: `git commit -m "pauta: actualiza <slug> con cambios de <fecha>"`

### Si Luis pide nueva feature inesperada

1. Antes de codear, releer este backlog → quiza ya esta propuesto
2. Si es nuevo: discutir prioridad real vs las 5 prioritarias del backlog
3. Si es chico (<1h): meter en sprint 13 junto con otras
4. Si es grande (>2h): proponer como sprint propio

## Archivos clave del proyecto

```
scripts/
  tarrobot.py                     # CLI principal (1800+ lineas, modular pendiente)
  tarrobot-live.py                # Servidor FastAPI + WebSocket (2700+ lineas)
  tarrobot-tray.py                # Tray icon wrapper (sin cmd visible)
  obs_controller.py               # Cliente WebSocket obs-websocket v5
  sync-tarrobot-to-drive.ps1      # Sync selectivo al Drive

studio/
  _template-tarrobot-live.html    # SVG TarroBot + animaciones + oscilloscope
  _template-tarrobot-control.html # Panel control (cards modulares)
  obs-aliases.json                # Mapeo alias voz → escenas reales OBS
  tarrobot-recetas.json           # Secuencias compuestas (intro, outro, etc)
  pautas/<slug>.tarrobot.json     # Pautas de episodios
  pautas/audio/<slug>/*.mp3       # MP3s precargados
  melodias/<consola>/*.mid        # MIDIs por contexto (gitignored)
  melodias/soundfont.sf2          # Soundfont SNES (gitignored, ~30MB)

installers/tarrobot-studio/
  install.bat                     # Instalador interno (Python + deps + ffmpeg + FluidSynth)
  TarroBot.bat / TarroBot-debug.bat
  installer.iss                   # Script Inno Setup para .exe
  build-package.ps1               # Genera ZIP + .exe (si Inno esta instalado)
  README-ESTUDIO.txt              # Manual usuario final
  dist/                           # Output del build (gitignored)
```

## Reglas inmutables del proyecto

Cualquier mejora futura DEBE respetar (ver `CLAUDE.md` del repo):

- **Chileno neutro tuteo** en TODO output (chat, textos LLM, frases curadas)
- **Sin voseo argentino**: prohibido `tenés/querés/decime/vos/sos/podés` etc
- **TarroBot TTS:** CON tildes ortograficas + numeros en palabras ("20 mil" no "20,000")
- **HTMLs y assets visuales del canal:** SIN tildes (regla general Retrotarros, exception para TTS)
- **Filtro `chilenizar()`** aplicado a todos los outputs LLM antes de devolver
- **Anti-repeticion** via `pick_no_repeat` en cualquier lista random nueva
- **Rate limit LLM** en endpoints que llaman Claude
- **Sin nuevas deps Python** si se puede evitar (uvicorn[standard] trae mucho gratis)
- **Tolerancia a OBS desconectado**: si no esta conectado, helpers devuelven False sin romper voz
- **Git workflow:** Claude commitea/pushea directo. Pide confirmacion solo para operaciones destructivas o cambios de schema/release.

## Contacto Sprint 12 (lo que cerramos hoy 2026-05-21)

Commits del dia:
- `1329fb5` instalador .exe profesional con Inno Setup
- `7f4d4bf` gitignore: excluir bin/ del installer + exports/shorts/sessions
- `379f541` paquete v1.2 con todo el sprint 9-12 incluido
- `a15c1a5` sprint 12 - cerrando backlog (C1 C2 C4-lite C5 C7)
- `9e02c5f` sprint 11 - auto-pauta desde tema libre con LLM
- `1bc2918` sprint 10 - menos artificial, mas vivo
- `7f04620` sprint 9 control OBS por voz + reaccion toma cercana

Estado git: `master` sincronizado con `origin/master`. Tag `v1.2-tarrobot` creado y pusheado. Release publicado.

---

**Ultima actualizacion:** 2026-05-21 por Luis + Claude (12 commits, 4 sprints).
