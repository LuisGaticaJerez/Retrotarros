# Retrotarros Studio Panel — Claude Code Project Instructions

> Lee este archivo completo antes de cualquier acción. Después lee `HANDOFF.md` para saber el estado actual.

## ⚠️ REGLA INMUTABLE · alcance estricto a Retrotarros

**SOLO modificar archivos dentro de:**
- `D:\Recursos Retrotarros\studio-panel\` (este proyecto)
- `D:\Recursos Retrotarros\repo\` (proyecto Retrotarros principal — solo si la tarea lo pide explícito)

**NUNCA bajo ningún concepto tocar:**
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\Doggywalk\` (Petify, proyecto de otro cliente)
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\Impulsus\`
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\centro-de-decisiones\`
- Cualquier `.claude/` / `settings.json` / `launch.json` que NO esté bajo `D:\Recursos Retrotarros\`.

Si una preview tool o config la pide fuera de Retrotarros, NO lo hagas — buscá otra forma o decile a Luis. **Incidente histórico:** en 2026-05-15 contaminé el `.claude/launch.json` de Petify por error. No vuelve a pasar.

## Qué es esto

App web concentradora de mensajería multi-plataforma para streams y podcasts de **Retrotarros** (canal YouTube de retrogaming + batería · ver repo Retrotarros principal en `D:\Recursos Retrotarros\repo\`).

**Visión dual:**
1. Herramienta interna para Luis + Koko durante streams.
2. **Potencial producto SaaS** para vender a otros creators (gaming + podcasts latam). El diseño multi-tenant desde día 1 deja esa puerta abierta sin rehacer nada.

**Diferenciador vs competencia (Restream / Streamlabs / SSN):**
- Integración con monitor HTML del show (mensajes etiquetados por slide activo).
- Tooling para editores post-stream (export top preguntas, replay con timestamps, highlights para shorts).
- Niche: creators latam · UI en español · paleta moderna.

## Stack

| Capa | Tecnología |
|---|---|
| Monorepo | pnpm workspaces |
| Backend | Node 20+ · TypeScript · Fastify · `@fastify/websocket` |
| Realtime | WebSockets nativos (no Socket.io) |
| Frontend | React 19 · Vite · TypeScript · Tailwind |
| DB / Auth | Supabase (PostgreSQL + RLS multi-tenant) — **pendiente crear proyecto** |
| Deploy | Backend → Railway/Fly.io · Frontend → Netlify — **pendiente** |
| Conectores | `tmi.js` (Twitch) · `googleapis` (YouTube) · `discord.js` · WebSocket bridge (SSN para IG/FB/WhatsApp) |

## Estructura monorepo

```
studio-panel/
├── apps/
│   ├── backend/                Fastify + conectores
│   │   ├── src/
│   │   │   ├── server.ts       Entry point
│   │   │   ├── hub.ts          Pub/sub central de mensajes
│   │   │   ├── connectors/     Un archivo por plataforma
│   │   │   ├── routes/         REST endpoints
│   │   │   └── db/schema.sql   Schema Supabase multi-tenant
│   │   └── package.json
│   └── frontend/               React + Vite dashboard
│       ├── src/
│       │   ├── App.tsx
│       │   ├── components/
│       │   ├── hooks/
│       │   └── lib/
│       └── package.json
├── packages/
│   └── shared/                 Tipos TypeScript compartidos
│       └── src/index.ts        ChatMessage, Platform, WsServerMessage
├── .claude/launch.json         Configs para preview tools (frontend + backend)
├── pnpm-workspace.yaml
├── tsconfig.base.json
└── .env.example
```

## Paleta visual (synthwave Retrotarros)

| Token | Color | Uso |
|---|---|---|
| `magenta` | `#FF2E88` | Primario · highlights · CTA |
| `cyan` | `#00E5FF` | Secundario · live status · accent |
| `yellow` | `#FFD23F` | Etiquetas · warnings |
| `purple` | `#2D1B69` | Fondo profundo |
| `cream` | `#F5F0E8` | Texto principal sobre dark |
| `dark` | `#06030F` | Fondo base |

Tipografía:
- `font-display` → Orbitron (logos, headers grandes)
- `font-mono` → Share Tech Mono (timestamps, metadata)
- `font-body` → Inter (UI normal, mensajes)

## Convenciones de código

- **TypeScript estricto.** Sin `any`. Sin `unknown` sin narrow.
- **Imports absolutos via aliases** cuando crezca. Por ahora rutas relativas son OK.
- **Tipos compartidos backend ↔ frontend** SIEMPRE en `packages/shared/src/index.ts`. NO duplicar tipos.
- **Conectores** siempre exponen `{ start(), stop() }` y reciben `{ onMessage, onStatus, logger }` por DI. NO acoplar directamente al hub.
- **Plataformas nuevas:** agregar al union `Platform` en shared + crear archivo en `apps/backend/src/connectors/<plataforma>.ts` + sumar a `PLATFORM_LABELS` y `PLATFORM_COLORS`.
- **Multi-tenant siempre.** Cada tabla nueva en Supabase tiene `org_id`. RLS filtra por membership.

## Comandos clave

```bash
# Instalar deps (primera vez o tras pull)
pnpm install

# Dev — backend + frontend en paralelo
pnpm dev

# Solo uno
pnpm dev:backend     # :3001
pnpm dev:frontend    # :5173

# Typecheck
pnpm typecheck

# Build prod
pnpm build
```

## Variables de entorno

Ver `.env.example`. Las críticas para empezar:

- `TWITCH_CHANNELS` — lista CSV de canales a leer. Default `retrotarros`.
- `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` — pendiente crear proyecto.
- `YOUTUBE_API_KEY` — pendiente crear key.
- `DISCORD_BOT_TOKEN` — pendiente crear bot.

NUNCA commitear `.env`. Está en `.gitignore`.

## Reglas operativas

### Git workflow (convención heredada del proyecto Retrotarros)

- **Claude ejecuta** los `git add`, `git commit`, `git push`, scripts y operaciones de archivo. Luis NO corre comandos manualmente — Claude tiene Bash en el sandbox.
- **Commits locales no destructivos**: Claude los ejecuta sin pedir permiso explícito, luego informa el SHA.
- **Operaciones remotas o destructivas** (push, rebase, reset --hard, rm -rf masivo, force push, cualquier acción contra GitHub o que sobreescriba historia): Claude **pide confirmación con un comando concreto** antes de ejecutar.
- **Nunca usar** `--force`, `--no-verify`, `commit --amend` (sobre commits ya pusheados), `git reset --hard` sin confirmación explícita en el mismo turno.

### Lengua

Español chileno neutro en todo output al usuario y en commits/docs visibles. Sin voseo rioplatense, sin mexicanismos pesados.

### Antes de afirmar que falta algo

NUNCA decir "falta X" sin buscar primero en repo + `D:\Recursos Retrotarros\` + Drive. Luis es estricto con esto.

## Anti-patrones — lo que NO hacer

- **NO duplicar tipos** entre backend y frontend. Todo lo compartido va en `@retrostudio/shared`.
- **NO acoplar conectores al hub directamente.** Usar callbacks por DI.
- **NO tablas sin `org_id`.** Romperíamos multi-tenancy.
- **NO commitear** `.env`, `node_modules/`, `dist/`, claves de API.
- **NO inventar features** sin discutir con Luis. Lo simple primero.
- **NO emojis en commits** (solo en captions y títulos YouTube en el proyecto Retrotarros principal).

## Integración con el proyecto Retrotarros principal

Este panel es **independiente** del repo Retrotarros (que vive en `D:\Recursos Retrotarros\repo\`). Pero la **Fase 3** del brainstorm plantea integración:

- WebSocket entre el panel y los HTMLs en `studio/<slug>.html` del repo Retrotarros.
- Cuando llega un mensaje, queda etiquetado con el `slide_id` activo en el monitor del estudio.
- Útil para edición: "esta pregunta llegó cuando estábamos en slide 7 mostrando Banjo-Kazooie".

Cuando lleguemos a esa fase, agregamos un endpoint WS al panel y un cliente WS en el `studio/*.html` que reporte el slide actual.

## Próximo paso

Ver `HANDOFF.md`.
