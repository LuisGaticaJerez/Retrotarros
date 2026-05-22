# Estado actual · Studio Panel

> Actualizar al cerrar cada sesión. Esto es lo PRIMERO que ve Claude al arrancar.

## 🚦 Última sesión

**Fecha:** 2026-05-15
**Sprint 1 cerrado y pusheado** · commit `f0514c9` en master.

## 📍 Dónde estamos

- ✅ Monorepo pnpm funcionando: `apps/backend` (Fastify+WS) + `apps/frontend` (React+Vite) + `packages/shared`.
- ✅ Conector Twitch IRC anónimo (sin OAuth) funciona y conecta al canal `#retrotarros` por defecto.
- ✅ Dashboard mínimo con paleta synthwave (`#FF2E88` magenta, `#00E5FF` cyan, `#FFD23F` yellow).
- ✅ Repo GitHub: https://github.com/LuisGaticaJerez/retrotarros-studio-panel (privado)
- ✅ Stack decidido: Node+TS+Fastify backend / React 19+Vite+Tailwind frontend / Supabase pendiente.
- ✅ Multi-tenant desde día 1 (schema SQL listo en `apps/backend/src/db/schema.sql`).

## 🎯 Próximo paso concreto

Sprint 2 — necesita acción de Luis primero para algunas cosas:
1. Crear proyecto Supabase nuevo y correr `apps/backend/src/db/schema.sql`.
2. Pegar credenciales Supabase en `.env`.

Después Claude puede:
3. Integrar Supabase client en backend (persistir mensajes).
4. Conector YouTube Live Chat (necesita YOUTUBE_API_KEY).
5. Conector Discord bot (necesita DISCORD_BOT_TOKEN).
6. Conector SSN bridge (Instagram/FB/WhatsApp via WebSocket).
7. Deploy backend Railway + frontend Netlify.

## ⚡ Comando rápido para arrancar dev

```bash
pnpm install   # solo si node_modules no existe
pnpm dev       # backend :3001 + frontend :5173
```

## 💡 Para preview en Claude Code

`.claude/launch.json` tiene 2 configs:
- `frontend` (puerto 5173) → `npx vite`
- `backend` (puerto 3001) → `npx tsx watch src/server.ts`

Las preview tools de Claude pueden levantar cualquiera.

## 📝 Notas importantes

- **Tagline público canónico:** `Nostalgia + Juegos + Música` (no usar "retrogames + batería" más).
- **No tocar el repo Retrotarros principal** (`D:\Recursos Retrotarros\repo\`) — este es un proyecto separado.
- **OneDrive está desinstalado** en este equipo. Todo Retrotarros vive en `D:\Recursos Retrotarros\`.
- **Google Drive G:\** sigue activo para sync del estudio (HTMLs + DOCX del repo principal).
