# HANDOFF — Studio Panel

> Última actualización: 2026-05-15 · Sprint 1 cerrado.

## 🚦 Estado actual

**Sprint 1 completo y pusheado a GitHub** (commit `133341f` en `master`).

Repo: https://github.com/LuisGaticaJerez/retrotarros-studio-panel (privado)

### Lo que funciona

- ✅ Monorepo pnpm con `apps/backend`, `apps/frontend`, `packages/shared`.
- ✅ Backend Fastify levanta en `:3001` con WebSocket en `/ws`.
- ✅ Conector Twitch IRC vía `tmi.js` (anónimo, sin OAuth) conectándose y leyendo chats públicos.
- ✅ Hub pub/sub central de mensajes en backend.
- ✅ Frontend React 19 + Vite + Tailwind con paleta Retrotarros synthwave.
- ✅ Hook `useChatStream` con WebSocket + auto-reconnect.
- ✅ Componentes: `Header`, `ConnectorStatusBar`, `MessageFeed` con filtros por plataforma.
- ✅ Schema SQL multi-tenant listo en `apps/backend/src/db/schema.sql`.
- ✅ Typecheck backend + frontend passing.

### Lo que falta (Sprint 2 propuesto)

#### Tareas que requieren acción de Luis primero

1. **Crear proyecto Supabase nuevo** (`retrotarros-studio` o similar).
   - Correr `apps/backend/src/db/schema.sql` en SQL Editor.
   - Pegar `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` en `.env` local.
   - Crear primer user en Supabase Auth (luis@retrotarros) y agregarse a `memberships` como `owner` de la org `retrotarros`.
2. **YouTube Data API key**: Google Cloud Console → habilitar YouTube Data API v3 → crear API key. Pegar en `.env`.
3. **Discord bot**: crear app en Discord Developer Portal → bot → copiar token. Pegar en `.env`.
4. **Decidir hosting backend**: Railway vs Fly.io. Recomendación: Railway por simplicidad.

#### Tareas que Claude puede ejecutar solo

5. Integrar Supabase client en backend (persistir cada `ChatMessage` recibido).
6. Implementar conector YouTube Live Chat (poll cada 5s, manejar quota).
7. Implementar conector Discord (`discord.js` bot, leer guild + canales configurados).
8. Implementar conector SSN bridge (consumir WS de Social Stream Ninja, parsear mensajes).
9. Sumar pin/unpin (UI + persistencia + sync en WS).
10. Sumar "stream activo" — crear `stream` al primer mensaje y cerrarlo manualmente.
11. Sumar Supabase Auth en frontend (login Luis/Koko).
12. Deploy: backend a Railway + frontend a Netlify + smoke test en prod.

## ⚡ Comandos clave para retomar

```bash
# Levantar dev local (backend :3001 + frontend :5173)
cd "D:\Recursos Retrotarros\studio-panel"
pnpm install   # solo si node_modules no existe
pnpm dev

# Solo backend
pnpm dev:backend

# Solo frontend
pnpm dev:frontend

# Typecheck
pnpm typecheck

# Git
git status
git log --oneline -10
```

## 🔌 Conectores — estado por plataforma

| Plataforma | Estado | Notas |
|---|---|---|
| Twitch | ✅ Funcional | tmi.js anónimo, sin OAuth, lee chats públicos. Reconnect auto. |
| YouTube Live Chat | ⏳ Pendiente | Necesita API key + integración con `googleapis`. Polling 5s. Cuidado quota. |
| Discord | ⏳ Pendiente | Bot token + guilds permission. |
| Instagram Live | ⏳ Pendiente | Vía SSN WebSocket bridge (no hay API oficial). |
| Facebook Live | ⏳ Pendiente | Vía SSN bridge. Graph API requiere app review Meta. |
| WhatsApp | ⏳ Pendiente | Vía SSN o `whatsapp-web.js`. Solo grupos donde Luis es admin. |

## 🗃️ Schema Supabase (resumen)

Ya escrito en `apps/backend/src/db/schema.sql`. Tablas:

- `orgs` — tenants (hoy 1: Retrotarros).
- `memberships` — usuarios miembros de cada org (relación con `auth.users`).
- `streams` — sesiones de stream/podcast (1 por evento en vivo).
- `messages` — todos los mensajes agregados, con `org_id`, `stream_id`, `platform`, `slide_id` opcional.

RLS habilitado en todas. Helper `auth_user_org_ids()` filtra por membership.

## 🌐 Variables de entorno (Sprint 2)

Ver `.env.example`. Las que faltan completar:

```bash
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
YOUTUBE_API_KEY=
DISCORD_BOT_TOKEN=
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

## 🚀 Deploy plan (Sprint 2 último paso)

| Servicio | Where |
|---|---|
| Backend | Railway (Dockerfile o nixpacks autodetect) o Fly.io |
| Frontend | Netlify (build `pnpm --filter @retrostudio/frontend run build`, publish `apps/frontend/dist/`) |
| DB | Supabase (proyecto nuevo) |

CORS_ORIGIN del backend → URL de Netlify. `VITE_WS_URL` del frontend → URL de Railway/Fly.

## 📋 Decisiones pendientes (no urgentes)

- ¿Modelo de monetización si se vuelve SaaS? Free tier + pago por canales conectados / mensajes/mes / branding removed.
- ¿Nombre comercial si se publica? "Studio Panel" es genérico. Pensar.
- ¿OSS o closed source si llega a producto? Por ahora privado.

## 💡 Para próxima sesión Claude

Cuando arranques una sesión nueva en este proyecto:

1. Leé este HANDOFF.md + `CLAUDE.md` antes de cualquier acción.
2. Chequeá `git log --oneline -5` y `git status` para saber qué cambió.
3. Si Luis ya creó Supabase / API keys, integrá. Si no, preguntale por dónde quiere arrancar.
4. Las preview tools (Vite + Fastify) funcionan limpio desde esta sesión porque el `.claude/launch.json` está adentro del proyecto.

---

*Sprint 1 cerrado — base sólida para construir.*
