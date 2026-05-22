-- Studio Panel · Supabase schema multi-tenant
-- =====================================================
-- Ejecutar este SQL en el SQL Editor de Supabase para crear las tablas iniciales.
-- Multi-tenant desde día 1: cada fila tiene org_id, RLS filtra por org_id.

-- Habilitar uuid_generate_v4 (Supabase ya tiene pgcrypto activo).
create extension if not exists "pgcrypto";

-- =====================================================
-- TABLAS
-- =====================================================

-- Organizaciones (tenants). Hoy hay 1 = Retrotarros. Soporta N.
create table if not exists orgs (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null,        -- ej. 'retrotarros'
  name        text not null,               -- ej. 'Retrotarros Studio'
  created_at  timestamptz not null default now()
);

-- Miembros de cada org. Usa auth.users de Supabase.
create table if not exists memberships (
  id          uuid primary key default gen_random_uuid(),
  org_id      uuid not null references orgs(id) on delete cascade,
  user_id     uuid not null references auth.users(id) on delete cascade,
  role        text not null default 'member', -- 'owner' | 'admin' | 'member'
  created_at  timestamptz not null default now(),
  unique (org_id, user_id)
);

create index if not exists idx_memberships_user on memberships(user_id);
create index if not exists idx_memberships_org on memberships(org_id);

-- Sesiones de stream (1 por stream/podcast).
create table if not exists streams (
  id          uuid primary key default gen_random_uuid(),
  org_id      uuid not null references orgs(id) on delete cascade,
  title       text,                         -- ej. 'Stream N64 Top Mundial'
  slug        text,                         -- ej. 'n64-top-mundial' para integración con monitor
  started_at  timestamptz not null default now(),
  ended_at    timestamptz,
  metadata    jsonb default '{}'::jsonb     -- platforms activas, etc.
);

create index if not exists idx_streams_org on streams(org_id, started_at desc);

-- Mensajes del chat unificado.
create table if not exists messages (
  id            uuid primary key default gen_random_uuid(),
  org_id        uuid not null references orgs(id) on delete cascade,
  stream_id     uuid references streams(id) on delete cascade,
  platform      text not null,                  -- 'twitch' | 'youtube' | 'discord' | 'instagram' | 'facebook' | 'whatsapp' | 'ssn'
  external_id   text,                           -- ID en la plataforma origen, para evitar duplicados
  author_name   text not null,
  author_id     text,                           -- ID externo del autor
  author_color  text,                           -- color HEX asignado por la plataforma
  author_badges text[],                         -- badges/roles
  text          text not null,
  html          text,                           -- texto con emotes formateados
  slide_id      text,                           -- slide HTML activa cuando llegó (integración monitor estudio)
  pinned        boolean not null default false,
  replied       boolean not null default false,
  created_at    timestamptz not null default now(),
  unique (platform, external_id)
);

create index if not exists idx_messages_stream on messages(stream_id, created_at);
create index if not exists idx_messages_org_recent on messages(org_id, created_at desc);
create index if not exists idx_messages_pinned on messages(org_id, pinned) where pinned = true;

-- =====================================================
-- RLS (Row Level Security)
-- =====================================================

alter table orgs enable row level security;
alter table memberships enable row level security;
alter table streams enable row level security;
alter table messages enable row level security;

-- Helper: tu org_id basado en membership del usuario logueado.
create or replace function auth_user_org_ids()
returns setof uuid
language sql stable security definer
as $$
  select org_id from memberships where user_id = auth.uid();
$$;

-- orgs: ves solo las orgs en las que sos miembro.
create policy "orgs: select by membership"
  on orgs for select
  using (id in (select auth_user_org_ids()));

-- memberships: ves los memberships de tus orgs.
create policy "memberships: select by org"
  on memberships for select
  using (org_id in (select auth_user_org_ids()));

-- streams: ves los streams de tus orgs.
create policy "streams: select by org"
  on streams for select
  using (org_id in (select auth_user_org_ids()));

create policy "streams: insert by org member"
  on streams for insert
  with check (org_id in (select auth_user_org_ids()));

create policy "streams: update by org member"
  on streams for update
  using (org_id in (select auth_user_org_ids()));

-- messages: ves los mensajes de tus orgs.
create policy "messages: select by org"
  on messages for select
  using (org_id in (select auth_user_org_ids()));

create policy "messages: insert by org member"
  on messages for insert
  with check (org_id in (select auth_user_org_ids()));

create policy "messages: update by org member"
  on messages for update
  using (org_id in (select auth_user_org_ids()));

-- =====================================================
-- SEED · Org Retrotarros
-- =====================================================
insert into orgs (slug, name)
  values ('retrotarros', 'Retrotarros Studio')
  on conflict (slug) do nothing;

-- NOTA: después de correr este SQL, en Supabase Authentication crear el primer
-- usuario (Luis) y desde el SQL editor insertar la membership manualmente:
--
--   insert into memberships (org_id, user_id, role)
--   values (
--     (select id from orgs where slug = 'retrotarros'),
--     '<USER_UUID_DE_LUIS>',
--     'owner'
--   );
