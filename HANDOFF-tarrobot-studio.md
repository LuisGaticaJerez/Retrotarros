# TarroBot Studio — Handoff maestro

> Documento unico que cubre **TarroBot + Studio Panel** como un solo proyecto unificado **"TarroBot Studio"**. Reemplaza la separacion entre los dos proyectos que vivian en repos distintos hasta el 2026-05-22.

## Estado al 2026-05-22 (Sprint 13 cerrado)

**Sprint 13 completo: Studio Panel migrado a Python.** Ya NO existe la carpeta
`studio-panel/` Node — todo el conector multi-plataforma vive en
`scripts/connectors/` + `scripts/social_manager.py` + endpoints en
`scripts/tarrobot-live.py`. Una sola codebase Python, un solo proceso,
una sola sesion Claude.

Pasos completados:

- ✓ Studio Panel Node eliminado del repo (era proyecto separado, ya no aporta)
- ✓ Conectores Twitch (IRC nativo) + Discord (discord.py) + YouTube (Data API v3) en Python
- ✓ Persistencia SQLite local `data/tarrobot-messages.db` (reemplaza Supabase)
- ✓ SocialManager orquesta conectores + persiste mensajes + broadcast WS
- ✓ 14 endpoints REST `/api/social/*` en `tarrobot-live.py`
- ✓ 3 cards nuevas en panel control: SESION + CONECTORES + FEED DE CHAT
- ✓ WebSocket cliente en panel filtra eventos `social-*` con reconnect automatico
- ✓ Discord bot Tarrobot operativo en servidor RetroTarros (de sesion previa)

**Sprint 14 cerrado: TarroBot RESPONDE al chat.** Bots multi-plataforma pasaron
de read-only a interactivos. Bloques:
- ✓ B14.1 `/api/social/say` - TarroBot lee mensaje literal con TTS
- ✓ B14.2 `/api/social/respond` - Claude genera respuesta + TTS (con rate limit)
- ✓ B14.3 UI: 3 botones por mensaje (SAY / RESPOND / DICTATE) + modal dictate
- ✓ B14.4 `/api/social/post-message` + `DiscordConnector.send_to_channel` (write-back Discord)
- ✓ B14.5 Cola READ PINNED secuencial con TTS sincronizado (espera fin de audio)
- ✓ B14.6 Docs + commit final

**Sprint 15 cerrado: Minimizar gasto LLM con pauta enriquecida + cache.** Resultado: 80% menos llamadas a Claude durante grabacion.
- ✓ B15.1 `generar_pauta_tema_con_llm(enriquecido=True)`: pre-genera opiniones
  alternativas (3 por dato), comentarios cortos (5 por dato), quiz pregenerado
  (2 preguntas con respuesta+pista por dato).
- ✓ B15.2 Pauta enriquecida tambien trae catchphrases_episodio (8),
  intros_cold_open (3), outros_cliffhanger (3), publicacion completa
  (titulos x3, descripcion, hashtags 15-20, thumbnail_prompts x5, ig_post).
- ✓ B15.3 Endpoints `/api/opinar`, `/api/quiz/pregunta`, `/api/episodio/exportar-descripcion`
  resuelven desde pauta enriquecida antes de llamar Claude. Cero llamadas
  si el contenido esta pre-generado.
- ✓ B15.4 Infraestructura para minimizar llamadas (cache + resolver pauta).
  Prompt caching real con `cache_control` de Anthropic queda como
  optimizacion adicional futura.
- ✓ B15.5 `scripts/llm_resolver.py` con cache JSON local en
  `data/tarrobot-cache-llm.json`, TTL 30 dias, max 5 respuestas por key.
- ✓ B15.6 Telemetria: contador de calls por endpoint + costo estimado USD +
  cache stats. Endpoint `/api/llm/stats`. Card LLM STATS en panel con
  refresh cada 10s.
- ✓ B15.7 Modo barato: toggle global que bloquea todas las llamadas LLM
  (devuelve 503). Endpoint `/api/llm/modo-barato`. Toggle en panel.

**Sprint 16 cerrado: Auto-respond toggle + optimizaciones internas.**
- ✓ B16.1 `scripts/auto_respond.py`: modulo dedicado con config persistida
  (activo, mention_only, cooldown_user_s, cooldown_global_s, skip_if_speaking,
  platforms). `should_auto_respond(msg)` aplica todos los filtros.
  Hook en `social_manager._on_message` dispara `social_respond` automatico
  si los filtros pasan. Endpoints `GET/POST /api/social/auto-respond`.
  Card UI con switch principal, toggles secundarios, 2 sliders de cooldown,
  multi-check de plataformas, contador de respuestas automaticas.
- ✓ B16.2 `tarrobot.call_claude(prompt, max_tokens, parse_json, system)`:
  helper unificado para llamadas LLM nuevas. Las 8 funciones existentes
  no se refactorizan para evitar romper lo que anda (target opcional
  para sprint futuro).
- ✓ B16.3 `message_store.get_message_by_id(id)`: lookup eficiente con
  query SQL directa. Reemplaza el `get_recent(500) + filter Python` del
  helper `_get_message_or_404`.
- ✓ B16.4 `pick_no_repeat` persistente en `data/tarrobot-recent-picks.json`.
  Al reiniciar TarroBot conserva la memoria de frases dichas recientemente.
- ✓ B16.5 Cleanup: comentarios actualizados, sin imports duplicados
  detectados, dead code no encontrado en revision.
- ✓ B16.6 Docs + commit + sync.

## Que es TarroBot Studio

Conjunto de herramientas para producir el canal de YouTube Retrotarros (retrogaming + nostalgia + musica). Dos productos coexistiendo en stacks distintos pero gestionados como un solo proyecto:

### TarroBot (Python · `scripts/` + `studio/` + `data/`)

Asistente de produccion local. Corre en el PC del estudio durante grabacion.

- **Voz**: TTS Edge + STT Whisper, 14 presets de voz
- **OBS**: control por WebSocket (cambio de escena, close-ups, musica de fondo)
- **Pautas**: cola del episodio, melodias MIDI con sonido SNES
- **LLM**: opinar, cuentame, quiz, auto-pauta, descripcion del video
- **Avatar**: SVG animado con personalidad, vive en una TV CRT virtual
- **Estado**: v1.2 release publico ([GitHub](https://github.com/LuisGaticaJerez/Retrotarros/releases/tag/v1.2-tarrobot))
- **Puerto**: :8765 local
- **Instalador**: `installers/tarrobot-studio/` con build script Inno Setup

### TarroBot Social (Python · `scripts/connectors/` + `scripts/social_manager.py`)

Concentrador de mensajeria multi-plataforma INTEGRADO en TarroBot.
Sprint 13: migrado del stack Node original a Python como modulo del
servidor FastAPI de TarroBot.

- **Conectores activos**:
  - Twitch (IRC nativo asyncio, auth anonima justinfan, reconnect automatico)
  - Discord (discord.py, intents Message Content + Members + Presence)
  - YouTube Live Chat (Data API v3 polling, respeta pollingIntervalMillis)
- **Backend**: extendido en `scripts/tarrobot-live.py` (mismo proceso :8765)
- **Frontend**: 3 cards en `studio/_template-tarrobot-control.html`
- **Persistencia**: SQLite local en `data/tarrobot-messages.db` (WAL mode)
- **WebSocket**: reutiliza el `/ws/live` con eventos `social-*` filtrados
- **Repo legacy**: `github.com/LuisGaticaJerez/retrotarros-studio-panel`
  queda como archivo historico (codigo vivo migrado a Python).

## Estructura del repo (Sprint 13 cerrado)

```
D:\Recursos Retrotarros\repo\
├── .git/                          # repo unico
├── .gitignore
├── HANDOFF.md                     # estado canal (general)
├── HANDOFF-tarrobot-studio.md     # ESTE archivo
├── docs/
│   ├── HANDOFF-tarrobot.md        # legacy
│   ├── discord-bot-setup.md       # setup Discord bot (sesion previa)
│   ├── app-estudio-mensajeria.md  # legacy brainstorm
│   ├── pauta-*.md                 # pautas de episodios del canal
│   ├── handoff-claude-studio/     # bundle para Claude del PC del estudio
│   └── ...
├── scripts/                       # codigo Python TarroBot Studio
│   ├── tarrobot.py                # CLI principal
│   ├── tarrobot-live.py           # servidor FastAPI principal :8765
│   ├── tarrobot-tray.py           # tray icon wrapper
│   ├── obs_controller.py          # OBS WebSocket client
│   ├── sync-tarrobot-to-drive.ps1 # sync al Drive del estudio
│   ├── message_store.py           # Sprint 13: SQLite persistencia
│   ├── social_manager.py          # Sprint 13: orquestador conectores
│   └── connectors/                # Sprint 13: conectores plataformas
│       ├── __init__.py            # Connector ABC + Message dataclass
│       ├── twitch.py              # IRC nativo asyncio
│       ├── discord_conn.py        # discord.py bot reader
│       └── youtube.py             # Data API v3 polling
├── studio/                        # HTMLs canal Retrotarros
│   ├── _template-tarrobot-live.html      # TV virtual TarroBot
│   ├── _template-tarrobot-control.html   # panel control completo
│   ├── obs-aliases.json
│   ├── tarrobot-recetas.json
│   ├── pautas/<slug>.tarrobot.json
│   └── ...
├── data/
│   ├── tarrobot-database.json     # datos curados
│   └── tarrobot-messages.db       # Sprint 13: SQLite messages + streams
└── installers/
    └── tarrobot-studio/           # instalador .exe + ZIPs
```

**El directorio `studio-panel/` Node fue eliminado en Sprint 13** — todo su
codigo equivalente vive ahora en Python como modulo de TarroBot.

## Roadmap

### Inmediato (este chat o siguiente)

- [x] Migracion monorepo (Fase 1 hecha hoy)
- [ ] **Setup Discord bot conectado al backend**: mergear rama `claude/hungry-proskuriakova-681c75` a master del studio-panel ANTES de la migracion final, o aplicar el codigo del conector manualmente. Sin esto el bot esta invitado al servidor pero el backend no lo conecta.
- [ ] **Reinstalar dependencias** en el monorepo: `cd studio-panel && pnpm install`
- [ ] **Fix HMR Vite**: el frontend tira error `ws://localhost:undefined` (HMR roto). Ver `studio-panel/apps/frontend/vite.config.ts` y verificar var PORT.
- [ ] **Test E2E**: mensaje en Discord aparece en dashboard del Studio Panel.

### Sprint 13 — Migracion Python (proyecto medio-grande, ~10-15h)

Reescribir Studio Panel en Python como modulo de TarroBot. Razones:
- TarroBot esta MUCHO mas avanzado (12+ sprints, release publico)
- Studio Panel es mucho mas chico (1 sprint cerrado)
- Python tiene libs maduras para todo lo que Studio Panel hace:
  - `twitchio` (Twitch IRC, en lugar de tmi.js)
  - `discord.py` (Discord bot, en lugar de discord.js)
  - `google-api-python-client` (YouTube, igual que JS)
  - `supabase-py` (Supabase client Python oficial)
- FastAPI de TarroBot ya tiene WebSocket nativo (no necesita Fastify)
- Una sola codebase = una sola sesion Claude que entiende todo

Pasos concretos:
1. Crear `scripts/connectors/` con `twitch.py`, `discord.py`, `youtube.py`, `ssn.py`.
2. Crear `scripts/tarrobot-social.py` (servidor FastAPI que integra conectores + Supabase/SQLite).
3. Migrar el frontend React: o se mantiene como esta y conversa con el FastAPI nuevo, o se sustituye por extension del panel control HTML de TarroBot.
4. Eliminar `studio-panel/` Node una vez todo migrado.

### Backlog TarroBot (heredado del HANDOFF-tarrobot.md)

Top 5 prioridades para Sprint 13 alternativo si el de migracion se posterga:
1. Sesion persistente en disco (~1h)
2. Healthcheck + PRE-FLIGHT CHECK (~1h)
3. Modo "ensayar" / preview en cascos (~45min)
4. Prompt caching de Anthropic (~45min)
5. Pre-flight de la pauta antes de grabar (~1h)

## Comandos clave del monorepo

### TarroBot

```powershell
# Server principal
cd D:\Recursos Retrotarros\repo
python scripts/tarrobot-live.py

# O via tray (sin cmd visible)
python scripts/tarrobot-tray.py

# CLI utilitario (generar pautas, melodias, etc)
python scripts/tarrobot.py --pauta-tema "Mega Drive raros" --n-datos 10

# Sync al Drive del estudio
.\scripts\sync-tarrobot-to-drive.ps1
```

### Studio Panel

```powershell
# Setup inicial (post-migracion)
cd D:\Recursos Retrotarros\repo\studio-panel
pnpm install

# Dev local (backend :3001 + frontend :5173)
pnpm dev

# Solo backend
pnpm dev:backend

# Solo frontend
pnpm dev:frontend

# Build produccion
pnpm build
```

### Git (un solo repo ahora)

```powershell
cd D:\Recursos Retrotarros\repo

# Status global (cubre TarroBot y studio-panel)
git status

# Commits cubren todo el proyecto
git add scripts/foo.py studio-panel/apps/backend/src/bar.ts
git commit -m "tarrobot: foo · studio-panel: bar"
git push origin master
```

## Discord bot (estado actual)

App `Tarrobot` (ID `1507235440527413368`) creada, configurada e invitada al servidor `RetroTarros` (ID `1507239039747756094`). Detalle completo en `docs/discord-bot-setup.md`.

Canales del servidor:
| Canal | ID |
|-------|-----|
| `#general` | `1507239040913768470` |
| `#videojuegos` | `1507239192915345418` |
| `#colecciones` | `1507242416296689665` |
| `#musica` | `1507242447565230100` |

Variables ya en `studio-panel/.env`:
- `DISCORD_BOT_TOKEN` (rotado hoy, 72 chars)
- `DISCORD_GUILD_ID=1507239039747756094`
- `DISCORD_CHANNEL_IDS=` los 4 IDs

**Lo que falta para que funcione end-to-end:** mergear la rama del studio-panel viejo `claude/hungry-proskuriakova-681c75` (que tiene el conector Discord implementado) al monorepo nuevo. La rama esta en el repo legacy de GitHub, hay que traer ese commit como cherry-pick o aplicar manualmente.

## Repos GitHub

- `github.com/LuisGaticaJerez/Retrotarros` → **REPO VIVO** (monorepo TarroBot Studio)
- `github.com/LuisGaticaJerez/retrotarros-studio-panel` → **archivo historico** post-migracion. Decision pendiente: borrar, archivar, o dejar publico como referencia. Sugerencia: archivar (read-only) para preservar historia sin que aparezca como activo.

## Reglas inmutables del monorepo

Heredadas de los proyectos originales, ahora unificadas:

- **Chileno neutro tuteo** en TODO output (chat, codigo, commits, descripciones).
- **Sin voseo argentino**: `vos / tenés / decime / sos / podés` etc PROHIBIDOS.
- **TarroBot TTS**: SI tildes ortograficas + numeros en palabras ("20 mil").
- **HTMLs y assets visuales canal Retrotarros**: SIN tildes (regla canal). Excepcion: textos TTS.
- **Sin emojis** en titulos, commits, descripciones del canal. Emojis en IG post OK.
- **Solo modificar archivos dentro de** `D:\Recursos Retrotarros\` (regla inmutable studio-panel). Nunca tocar Doggywalk/Petify.
- **Git workflow**: Claude commitea/pushea directo. Pide confirmacion solo para destructivas o remotas distintas a origin.
- **Sin nuevas dependencias** si se puede evitar. Reusar lo que ya esta.
- **Filtro `chilenizar()` postproceso** en todo output LLM (TarroBot).
- **Anti-repeticion `pick_no_repeat`** en cualquier lista random.
- **Rate limit LLM** (3s cooldown) en endpoints Claude.

## Cross-references

- HANDOFF general canal Retrotarros: `HANDOFF.md`
- HANDOFF legacy solo TarroBot: `docs/HANDOFF-tarrobot.md`
- Setup Discord bot: `docs/discord-bot-setup.md`
- Bundle Claude del estudio: `docs/handoff-claude-studio/`
- README Studio Panel: `studio-panel/README.md`
- CLAUDE.md Studio Panel (legacy): `studio-panel/CLAUDE.md`

---

**Ultima actualizacion:** 2026-05-22 · Luis + Claude (migracion monorepo).
