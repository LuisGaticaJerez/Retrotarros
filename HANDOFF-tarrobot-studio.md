# TarroBot Studio — Handoff maestro

> Documento unico que cubre **TarroBot + Studio Panel** como un solo proyecto unificado **"TarroBot Studio"**. Reemplaza la separacion entre los dos proyectos que vivian en repos distintos hasta el 2026-05-22.

## Estado al 2026-05-22

**Decision tomada hoy:** unificar los dos productos en un monorepo bajo el repo Retrotarros principal. Pasos completados:

- ✓ Studio Panel migrado de repo independiente a subcarpeta `studio-panel/` del repo Retrotarros
- ✓ TarroBot v1.2 sigue intacto en sus paths tradicionales (`scripts/`, `studio/`, `data/`, `installers/`)
- ✓ `.gitignore` actualizado para soportar el monorepo
- ✓ Discord bot Tarrobot operativo en servidor RetroTarros, .env del studio-panel listo

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

### Studio Panel (Node/TypeScript · `studio-panel/`)

Concentrador de mensajeria multi-plataforma. Corre durante streams/podcasts para leer chat en vivo de varias plataformas en un solo dashboard.

- **Conectores**: Twitch (activo), Discord/YouTube/SSN (en rama `claude/hungry-proskuriakova-681c75`)
- **Backend**: Fastify + WebSocket en :3001
- **Frontend**: React 19 + Vite + Tailwind + paleta synthwave en :5173
- **Persistencia**: Supabase (multi-tenant: orgs/memberships/streams/messages con RLS)
- **Estado**: Sprint 1 cerrado, Sprint 2 + merge de conectores pendientes
- **Repo legacy**: `github.com/LuisGaticaJerez/retrotarros-studio-panel` (queda como archivo historico; el codigo vivo esta aca)

## Estructura del monorepo

```
D:\Recursos Retrotarros\repo\
├── .git/                          # repo unico
├── .gitignore                     # cubre TarroBot + Studio Panel
├── HANDOFF.md                     # estado canal (general)
├── HANDOFF-tarrobot-studio.md     # ESTE archivo (unificado)
├── docs/
│   ├── HANDOFF-tarrobot.md        # legacy: solo TarroBot
│   ├── discord-bot-setup.md       # setup Discord bot
│   ├── app-estudio-mensajeria.md  # legacy: brainstorm Studio Panel
│   ├── pauta-*.md                 # pautas de episodios del canal
│   ├── handoff-claude-studio/     # bundle para Claude del PC del estudio
│   └── ...
├── scripts/                       # TarroBot Python
│   ├── tarrobot.py                # CLI principal
│   ├── tarrobot-live.py           # servidor FastAPI
│   ├── tarrobot-tray.py
│   ├── obs_controller.py
│   └── sync-tarrobot-to-drive.ps1
├── studio/                        # HTMLs canal Retrotarros
│   ├── _template-tarrobot-live.html
│   ├── _template-tarrobot-control.html
│   ├── obs-aliases.json
│   ├── tarrobot-recetas.json
│   ├── pautas/<slug>.tarrobot.json
│   └── ...
├── data/
│   └── tarrobot-database.json
├── installers/
│   └── tarrobot-studio/           # instalador .exe + ZIPs
└── studio-panel/                  # Studio Panel Node/TS (NUEVA UBICACION)
    ├── apps/
    │   ├── backend/               # Fastify + WebSocket
    │   └── frontend/              # React 19 + Vite + Tailwind
    ├── packages/
    │   └── shared/
    ├── package.json
    ├── pnpm-workspace.yaml
    ├── .env                       # gitignored (creds Discord, Supabase, etc)
    ├── CLAUDE.md                  # instrucciones especificas studio-panel
    ├── HANDOFF.md                 # legacy: estado Sprint 1
    └── ...
```

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
