# Core memories · Studio Panel

> Momentos y decisiones clave del proyecto. NO sobrescribir, solo agregar.

## 2026-05-15 · Creación del proyecto

- Decisión: app concentradora de mensajería multi-plataforma para streams/podcasts de Retrotarros.
- Stack final: Node+TS+Fastify backend / React 19+Vite+Tailwind frontend / Supabase (pendiente).
- Repo separado en GitHub: `retrotarros-studio-panel` (privado).
- Visión dual: herramienta interna + potencial SaaS futuro.
- Multi-tenant desde día 1 (cada tabla tiene `org_id`, RLS Supabase).

## Diferenciadores vs competencia

**vs Restream Chat / Streamlabs / Social Stream Ninja:**

1. **Integración con monitor HTML del show** — mensajes se etiquetan con el `slide_id` del HTML activo en el monitor del estudio Retrotarros (`D:\Recursos Retrotarros\repo\studio\<slug>.html`).
2. **Tooling para editores post-stream** — export top preguntas, replay con timestamps, highlights para shorts. Esto es lo que justifica pagar suscripción si va a SaaS.
3. **Niche: creators latam** — UI español, paleta moderna, gaming + podcasts.

## Decisiones técnicas clave

- **WebSockets nativos** (no Socket.io) — más liviano.
- **tmi.js justinfan anónimo** para Twitch — lee chats públicos sin OAuth, sin app registration.
- **Conectores via DI** — exponen `{start, stop}`, reciben `{onMessage, onStatus, logger}`. Desacoplados del hub.
- **Hub pub/sub in-memory** — si necesitamos escalar a múltiples instancias, migra a Redis.
- **Schema multi-tenant** desde día 1 — `org_id` en todas las tablas, RLS Supabase filtra por membership.

## Decisiones que afectan workflow

- **Repo separado del proyecto Retrotarros principal** — no monorepo. El panel tiene su propio ciclo de vida.
- **No usar pnpm en background** (preview tools) — usar `npx` directo para evitar pre-checks que fallan.
- **`.claude/launch.json` versionado** — config compartida entre máquinas. `settings.json` también.
- **`.remember/now.md` versionado** — para que cualquier sesión nueva tenga contexto al instante.

## Plataformas a soportar (prioridad)

1. **Twitch** — API IRC nativa, fácil ✅ (Sprint 1)
2. **YouTube Live Chat** — Data API v3, polling 5s
3. **Discord** — Bot API, easy
4. **Instagram Live** — solo via Social Stream Ninja bridge (no hay API)
5. **Facebook Live** — Graph API requiere app review Meta; SSN como fallback
6. **WhatsApp** — solo grupos donde Luis es admin, vía whatsapp-web.js o SSN

## Repo

https://github.com/LuisGaticaJerez/retrotarros-studio-panel (privado)
Owner: LuisGaticaJerez

## ⚠️ REGLA INMUTABLE · alcance estricto al proyecto

**SOLO modificar archivos dentro de:**
- `D:\Recursos Retrotarros\studio-panel\` (este proyecto)
- `D:\Recursos Retrotarros\repo\` (proyecto Retrotarros principal — solo si la tarea lo requiere explícitamente)

**NUNCA tocar bajo ningún concepto:**
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\Doggywalk\` (proyecto Petify, otro cliente)
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\Impulsus\` (otro proyecto)
- `C:\Users\Balbr\OneDrive\Documentos\GitHub\centro-de-decisiones\` (otro proyecto)
- Cualquier `.claude/` o `settings.json` o `launch.json` que NO sea de Retrotarros / Studio Panel.

**Incidente histórico (2026-05-15):** En una sesión inicial accidentalmente modifiqué el `.claude/launch.json` del worktree de Petify para configurar un preview del Studio Panel. Tuve que revertir todo. Esto NO vuelve a pasar.

**Regla práctica:** si Luis está hablando de Retrotarros/Studio Panel, NUNCA escribir fuera del árbol `D:\Recursos Retrotarros\`. Si se necesita config para preview/CI/etc, va en este árbol o no se hace.
