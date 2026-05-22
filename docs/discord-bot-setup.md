# Discord Bot Setup · Tarrobot

> Procedimiento documentado del setup de la aplicacion Discord "Tarrobot" para que el Studio Panel pueda leer chat del servidor y eventualmente publicar respuestas.
>
> **Estado al 2026-05-22:** App creada limpia (la anterior fue eliminada). URL de invitacion lista. Falta crear servidor Discord, invitar el bot y rotar token al .env del studio-panel.

---

## Datos de la app actual

| Campo | Valor |
|-------|-------|
| Nombre | `Tarrobot` |
| Username | `Tarrobot#3006` |
| App ID / Client ID | `1507235440527413368` |
| Clave publica | `9d772b5b0a707a719b5c4791eb7b66b1836e3c1437e5f724859cae154e59236d` |
| Etiquetas | `bot`, `camara`, `chat`, `obs`, `sonido` |
| Servidores | 0 (todavia no invitado) |

> **Token:** NO se guarda en este doc. Se rota cuando se necesite y se copia directo al `.env` del studio-panel.

---

## Privileged Gateway Intents

Los 3 activados (criticos para que el Studio Panel funcione):

- [x] **Presence Intent** — eventos de actualizacion de presencia
- [x] **Server Members Intent** — eventos GUILD_MEMBERS
- [x] **Message Content Intent** — el critico, sin esto el bot NO lee contenido de los mensajes

---

## OAuth2 Scopes seleccionados

| Scope | Razon |
|-------|-------|
| `bot` | Necesario para que el bot exista como miembro del servidor |
| `applications.commands` | Permite slash commands (para futuro `/tarrobot opinar tema`) |

---

## Permisos del bot (bitfield: 277025770560)

Modo **Lector + Reactor** elegido. Permisos especificos:

**Permisos generales**
- [x] Ver canales

**Permisos de texto**
- [x] Enviar mensajes
- [x] Enviar mensajes en hilos
- [x] Insertar enlaces (para embeds ricos)
- [x] Adjuntar archivos
- [x] Leer el historial de mensajes
- [x] Usar emojis externos
- [x] Añadir reacciones
- [x] Usar comandos de barra diagonal

**NO marcados a proposito** (mantener superficie de ataque chica):
- Administrador
- Gestionar servidor / roles / canales / webhooks
- Expulsar / banear miembros
- Mencionar a todos
- Gestionar mensajes (no podemos borrar mensajes ajenos)
- Permisos de voz (no necesarios para chat)

---

## URL de invitacion lista

```
https://discord.com/oauth2/authorize?client_id=1507235440527413368&permissions=277025770560&integration_type=0&scope=bot+applications.commands
```

`integration_type=0` = Guild Install (instalacion en un servidor especifico, NO User Install).

---

## Pasos pendientes (en orden)

### 1. Crear servidor Discord Retrotarros

Si no existe todavia:

1. Abrir Discord (app de escritorio o https://discord.com/channels/@me)
2. En la barra izquierda de servidores → click en boton **+** (debajo de todos los servidores)
3. Elegir **"Crear el mío"**
4. Despues **"Para mí y mis amigos"** (sin plantilla, queda mas limpio)
5. Nombre: **Retrotarros** (o el que prefieras)
6. Icono: opcional, el mismo logo del bot funciona bien
7. Click **Crear**

### 2. Invitar el bot al servidor

1. Copiar la URL de invitacion (la de arriba) en el browser
2. Discord pide elegir servidor → seleccionar **Retrotarros**
3. Revisar los permisos que mostro (deben coincidir con la tabla de arriba)
4. Click **Autorizar**
5. Resolver captcha si lo pide
6. Confirmar — el bot deberia aparecer en la lista de miembros del servidor (offline mientras no haya backend corriendo)

### 3. Crear canales del servidor (sugerido)

Estructura propuesta para Retrotarros Studio:

```
📋 ESTUDIO
  ├─ #anuncios          (publicaciones del bot)
  ├─ #bitacora          (logs del bot durante sesiones)
  └─ #publico-chat      (donde la audiencia escribe en lives)

🎥 GRABACION
  ├─ #cola-preguntas    (preguntas pinneadas para responder en camara)
  └─ #notas-rapidas     (recordatorios entre tomas)

🤖 BOT
  ├─ #tarrobot-test     (canal para probar comandos)
  └─ #tarrobot-logs     (errores y eventos del bot)
```

No es obligatorio, pero ayuda al Studio Panel a saber donde escuchar y donde publicar.

### 4. Obtener IDs que necesita el Studio Panel

Activar modo desarrollador primero:
- Configuracion de usuario → Avanzado → **Modo desarrollador: ON**

Despues:
- **DISCORD_GUILD_ID** = click derecho sobre el icono del servidor → "Copiar ID del servidor"
- **DISCORD_CHANNEL_IDS** = click derecho sobre cada canal relevante → "Copiar ID del canal"

Recomendado: copiar IDs de los canales donde el bot debe escuchar (ej. `#publico-chat` durante lives).

### 5. Rotar token y copiar al .env

1. Volver a https://discord.com/developers/applications/1507235440527413368/bot
2. Seccion **Token** → click **Restablecer token** → confirmar
3. Discord muestra el token UNA SOLA VEZ → copiarlo inmediatamente
4. Pegarlo en `D:\Recursos Retrotarros\studio-panel\.env` (en la variable `DISCORD_BOT_TOKEN`)
5. Tambien en el worktree si trabajas con varios

> **CRITICO:** nunca pegar el token en chats, screenshots, commits, ni archivos sin gitignore. Si por accidente queda expuesto, repetir el paso 5 inmediatamente.

### 6. Reiniciar el backend del Studio Panel

```powershell
cd D:\Recursos Retrotarros\studio-panel
pnpm dev
```

Verificar en los logs que el bot se conecta:

```
[discord] Bot conectado como Tarrobot#3006
[discord] Watching guild Retrotarros (ID: ...)
[discord] Listening to N channels
```

### 7. Probar end-to-end

1. Escribir un mensaje cualquiera en `#publico-chat` del servidor Discord.
2. Verificar que aparece en el feed del Studio Panel.
3. Pinear el mensaje desde el Studio Panel.
4. Confirmar que el mensaje queda guardado en Supabase tabla `messages` con `pinned=true`.

---

## Estado de cada paso (actualizado 2026-05-22)

- [x] App Discord "Tarrobot" creada (ID `1507235440527413368`)
- [x] Privileged Gateway Intents activados (Presence + Members + Message Content)
- [x] OAuth2 Scopes configurados (`bot` + `applications.commands`)
- [x] Permisos del bot configurados (bitfield `277025770560`)
- [x] URL de invitacion generada
- [x] Servidor Discord "RetroTarros" creado (ID `1507239039747756094`)
- [x] Bot invitado al servidor (con captcha resuelto por Luis)
- [x] 4 Canales creados (`#general`, `#videojuegos`, `#colecciones`, `#musica`)
- [ ] Modo desarrollador activado (no urgente, los IDs se capturaron desde URLs)
- [x] Token rotado y copiado al `.env` del studio-panel
- [x] DISCORD_GUILD_ID + DISCORD_CHANNEL_IDS copiados al `.env` (4 channel IDs)
- [ ] Backend reiniciado y bot conectado (BLOQUEADO: conector Discord vive en rama feature `claude/hungry-proskuriakova-681c75`, falta mergear)
- [ ] Test end-to-end OK (depende del paso anterior)

## IDs del servidor RetroTarros

```
DISCORD_GUILD_ID=1507239039747756094
DISCORD_CHANNEL_IDS=1507239040913768470,1507239192915345418,1507242416296689665,1507242447565230100
```

| Canal | ID |
|-------|-----|
| `#general` | `1507239040913768470` |
| `#videojuegos` | `1507239192915345418` |
| `#colecciones` | `1507242416296689665` |
| `#musica` | `1507242447565230100` |

## Migracion monorepo (2026-05-22)

El studio-panel fue movido como subcarpeta del repo Retrotarros. Paths nuevos:

- `.env` ahora en: `D:\Recursos Retrotarros\repo\studio-panel\.env`
- Comando dev: `cd D:\Recursos Retrotarros\repo\studio-panel && pnpm dev`

Ver `HANDOFF-tarrobot-studio.md` para detalle de la migracion.

## Pendiente para que el bot se conecte realmente

El conector Discord vive en la rama feature `claude/hungry-proskuriakova-681c75` del repo legacy `retrotarros-studio-panel`. Para activarlo:

1. Cherry-pick el commit `e1ac23c "feat: persistencia Supabase + conectores YouTube y Discord"` al monorepo nuevo
2. O aplicar manualmente el codigo del conector
3. Reinstalar deps: `cd studio-panel && pnpm install`
4. Reiniciar `pnpm dev`
5. Verificar logs: `[discord] Bot conectado como Tarrobot#3006`
6. Test E2E: mensaje en `#general` → aparece en dashboard

---

## Troubleshooting comun

| Problema | Causa | Fix |
|----------|-------|-----|
| Bot aparece offline despues de invitarlo | Backend no corriendo o token mal | Reiniciar `pnpm dev` y verificar `.env` |
| Bot no lee mensajes (recibe vacio) | Message Content Intent OFF | Volver a Bot → Privileged Intents → activar |
| Bot conecta pero no ve el servidor | Server Members Intent OFF | Activar en Privileged Intents |
| Error "Invalid token" en logs | Token vencido o mal pegado (espacios, comillas) | Rotar token y pegar SIN comillas ni espacios |
| Captcha bloquea autorizacion | Anti-bot de Discord para cuentas nuevas | Esperar 24h o autenticar con telefono primero |

---

## Cross-reference

- Studio Panel repo: `D:\Recursos Retrotarros\studio-panel\`
- Doc original concentrador: `docs/app-estudio-mensajeria.md`
- HANDOFF TarroBot: `docs/HANDOFF-tarrobot.md`
- Bundle Claude Studio: `docs/handoff-claude-studio/`

---

**Ultima actualizacion:** 2026-05-22 · Luis + Claude (via Chrome MCP).
