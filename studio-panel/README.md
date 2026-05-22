# Retrotarros Studio Panel

> Concentrador de mensajería multi-plataforma para streams y podcasts de [Retrotarros](https://github.com/LuisGaticaJerez/Retrotarros). Diseñado para crecer de herramienta interna a SaaS si lo amerita.

## Qué es

Un panel web que durante streams y grabaciones agrega mensajes de:

- **Twitch** (IRC nativo)
- **YouTube Live Chat** (Data API v3)
- **Discord** (Bot API)
- **Instagram / Facebook Live / WhatsApp** (vía Social Stream Ninja bridge)

Y permite:

- Leer todo en un feed unificado con filtros por plataforma.
- Pinear preguntas para responder en cámara.
- Marcar tiempos del stream (para edición post-producción).
- Integrarse con el monitor HTML del estudio Retrotarros (slide actual ↔ mensajes).
- Exportar "top preguntas" y highlights para descripciones de video.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Node 20+ · TypeScript · Fastify · WebSockets nativos |
| Frontend | React 19 · Vite · TypeScript · Tailwind · shadcn/ui |
| DB / Auth | Supabase (PostgreSQL + RLS multi-tenant) |
| Realtime | Supabase Realtime + WebSocket directo backend ↔ frontend |
| Deploy | Backend → Railway o Fly.io · Frontend → Netlify |

## Estructura monorepo

```
studio-panel/
├── apps/
│   ├── backend/       Servidor Fastify + conectores plataformas
│   └── frontend/      Dashboard React
└── packages/
    └── shared/        Tipos TypeScript compartidos
```

## Empezar (dev local)

```bash
# Instalar dependencias
pnpm install

# Copiar env y completar
cp .env.example .env
# Editar .env con credenciales (Supabase, YouTube, Discord)

# Levantar backend + frontend juntos
pnpm dev
```

Backend en `http://localhost:3001` · Frontend en `http://localhost:5173`.

## Arquitectura multi-tenant

Desde día 1 todas las tablas tienen `org_id`. Hoy hay 1 organización (Retrotarros) pero el modelo soporta N sin rehacer. Si decidimos venderlo como SaaS, solo agregamos onboarding + billing — el data layer ya está listo.

## Estado actual

**Sprint 1 (en curso):**
- [x] Scaffold monorepo pnpm
- [ ] Schema Supabase multi-tenant
- [ ] Conector Twitch funcionando
- [ ] Dashboard mínimo conectado por WebSocket

**Próximo:** Sprint 2 — YouTube + Discord + deploy.

## Licencia

Propietario · uso interno Retrotarros por ahora. A futuro se decide entre OSS y SaaS.
