# App Estudio · Concentrador de mensajería

> **Estado:** brainstorm — sin código aún. Próximo paso: Fase 0 (validar Social Stream Ninja en un stream real).
> **Creado:** 2026-05-15 · Luis + Claude.

## Problema

Durante streams y podcasts de Retrotarros, los mensajes del público llegan por 6 canales paralelos: Twitch, YouTube, Instagram, Facebook, Discord y WhatsApp. Tener 6 pestañas abiertas mientras Koko toca + Luis presenta + ambos miran cámara es inviable. Necesitamos un solo panel.

Objetivos:
1. **Leer** todos los mensajes en un solo lugar durante grabación.
2. **Pinear** preguntas para responder en cámara, sin perderlas.
3. **Marcar tiempos** del stream para que el editor encuentre el momento exacto en post.
4. **Integrar** con el monitor HTML del estudio (`studio/<slug>.html`).

## Lo que NO vamos a hacer

- **No construir un agregador desde cero compitiendo con productos maduros.** Social Stream Ninja, Restream, Streamlabs ya resuelven el ingest multiplataforma para miles de streamers.
- **No reinventar protocolos.** Donde hay API oficial, la usamos. Donde no la hay (Instagram Live, WhatsApp), usamos puentes existentes.

## Realidad técnica por plataforma

| Plataforma | API oficial | Solución |
|---|---|---|
| Twitch | IRC / EventSub | `tmi.js` directo |
| YouTube Live Chat | Data API v3 (quota OK) | `googleapis` con polling 5s |
| Discord | Bot API | `discord.js` |
| Facebook Live | Graph API + app review Meta | Vía Social Stream Ninja |
| Instagram Live | **No hay API oficial** | Vía Social Stream Ninja (scraping browser) |
| WhatsApp | Business API pagado, no diseñado para chat de stream | Vía SSN o whatsapp-web.js |

## Arquitectura (4 fases)

### Fase 0 · Validación con SSN puro (0 código)

Probar Social Stream Ninja en un stream real. Si cubre el 80% del workflow → ahorramos 4 sesiones. Si no → sabemos exactamente qué falta.

**Entregable:** notas de "qué funciona, qué falta" después del stream.

### Fase 1 · Backend agregador

Stack:
- **Node.js + TypeScript** (familiar por Petiway)
- **Supabase** (proyecto separado `retrotarros-studio`) — para no mezclar con Petiway
- **WebSockets** (Socket.io o native ws) — push de mensajes al dashboard

Conectores nativos:
- `tmi.js` — Twitch IRC
- `googleapis` — YouTube Live Chat
- `discord.js` — Discord bot

Conectores via puente SSN:
- Instagram Live, Facebook Live, WhatsApp → SSN expone WebSocket, lo consumimos.

Schema normalizado:
```ts
interface Message {
  id: string;
  platform: 'twitch' | 'youtube' | 'discord' | 'instagram' | 'facebook' | 'whatsapp';
  user: { name: string; avatar?: string; badge?: string };
  text: string;
  timestamp: Date;
  stream_id: string;          // sesión de stream actual
  slide_id?: string;          // slide HTML activo cuando llegó
  pinned: boolean;
  replied: boolean;
}
```

### Fase 2 · Dashboard React

Stack:
- **React + Vite + TypeScript**
- **Tailwind con paleta Retrotarros** (`#FF2E88` magenta · `#00E5FF` cyan · `#FFD23F` amarillo · `#2D1B69` fondo)
- **shadcn/ui** para componentes base

Vistas:
- **Feed unificado** — todos los mensajes en tiempo real con filtros por plataforma + búsqueda.
- **Stage** — panel separado con preguntas pinned para responder en cámara.
- **Stream view** — modo fullscreen, fuente grande, leíble desde el estudio sin acercar la pantalla.
- **Timeline** — visualización de mensajes vs tiempo del stream, marcadores manuales.

### Fase 3 · Integración con monitor HTML del estudio

- WebSocket entre dashboard y `studio/<slug>.html`.
- Overlay opcional en una esquina del slide con el mensaje pinned actual.
- Dashboard sabe qué slide está activo (`current` variable del script de cada HTML) → cada mensaje queda etiquetado con `slide_id`.
- Edición: el editor abre el log post-stream y ve "esta pregunta llegó cuando estábamos en slide 7 mostrando Banjo-Kazooie".

### Fase 4 · Tooling para edición

- **Export** — top 10 preguntas del stream → pinned comment de YouTube + descripción del video.
- **Replay** — reconstruir el stream con cronómetro + mensajes para que el editor reviva y encuentre cortes.
- **Highlights** — momentos del stream con más mensajes en N segundos → cortes candidatos para shorts.

## Decisiones pendientes

- [ ] Validar SSN en próximo stream antes de codear.
- [ ] Confirmar Supabase como backend (vs PostgreSQL self-hosted en VPS chico).
- [ ] Modelo de auth — ¿solo Luis + Koko? ¿algún moderador externo del fandom?
- [ ] Hosting del backend — Netlify (función serverless con limitaciones de WS) vs Railway/Fly.io vs VPS.
- [ ] Privacidad WhatsApp — usar solo grupos públicos o también incluir grupos de amigos cercanos.

## Próximo paso concreto

Cuando hagamos el próximo stream o podcast (post N64 archivo / PS Vita rankings), arrancar con **Fase 0**: instalar Social Stream Ninja, conectar las 6 plataformas, grabar 1 sesión y reportar acá qué funcionó y qué no.

A partir de ese feedback, decidimos si Fase 1+ vale la pena o si SSN solo nos sirve.

---

*Brainstorm sin presión — construir cuando el problema esté claro, no antes.*
