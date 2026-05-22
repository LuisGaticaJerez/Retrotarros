/**
 * Servidor principal del Studio Panel.
 *
 * Hace 3 cosas:
 * 1. Expone WebSocket en /ws para que el frontend reciba mensajes en vivo.
 * 2. Levanta los conectores de plataformas (Twitch hoy, otros próximamente).
 * 3. Sirve HTTP REST para control (start/stop conectores, listar canales, etc.).
 */

import 'dotenv/config';
import Fastify from 'fastify';
import cors from '@fastify/cors';
import websocket from '@fastify/websocket';
import type { WsServerMessage } from '@retrostudio/shared';
import { createTwitchConnector } from './connectors/twitch.js';
import { messageHub } from './hub.js';
import { registerRoutes } from './routes/index.js';

const PORT = Number(process.env.PORT ?? 3001);
const CORS_ORIGIN = process.env.CORS_ORIGIN ?? 'http://localhost:5173';

const fastify = Fastify({
  logger: {
    level: process.env.LOG_LEVEL ?? 'info',
  },
});

await fastify.register(cors, {
  origin: CORS_ORIGIN,
  credentials: true,
});

await fastify.register(websocket);

// REST routes (status, control, history)
await registerRoutes(fastify);

// WebSocket endpoint: stream de mensajes en vivo al frontend
fastify.register(async function wsRoutes(app) {
  app.get('/ws', { websocket: true }, (socket /*, req */) => {
    fastify.log.info('Cliente WS conectado');

    const unsubscribe = messageHub.subscribe((msg: WsServerMessage) => {
      if (socket.readyState === socket.OPEN) {
        socket.send(JSON.stringify(msg));
      }
    });

    socket.on('close', () => {
      fastify.log.info('Cliente WS desconectado');
      unsubscribe();
    });

    socket.on('message', (raw: Buffer) => {
      // Cliente puede enviar acciones (pin/reply). Por ahora solo logueamos.
      try {
        const data = JSON.parse(raw.toString());
        fastify.log.debug({ data }, 'Mensaje del cliente WS');
      } catch {
        fastify.log.warn('WS payload inválido');
      }
    });
  });
});

// Arrancar conectores que se autoconfiguran (Twitch chat público no requiere creds)
// Por defecto conectamos al canal "retrotarros" si existe. Configurable por env.
const TWITCH_CHANNELS = (process.env.TWITCH_CHANNELS ?? 'retrotarros')
  .split(',')
  .map((c) => c.trim())
  .filter(Boolean);

const twitch = createTwitchConnector({
  channels: TWITCH_CHANNELS,
  onMessage: (msg) => messageHub.publish({ type: 'chat', payload: msg }),
  onStatus: (status) => messageHub.publish({ type: 'connector_status', payload: status }),
  logger: fastify.log,
});

try {
  await fastify.listen({ port: PORT, host: '0.0.0.0' });
  fastify.log.info(`Backend HTTP+WS escuchando en :${PORT}`);
  fastify.log.info(`Twitch channels: ${TWITCH_CHANNELS.join(', ')}`);
  await twitch.start();
} catch (err) {
  fastify.log.error(err);
  process.exit(1);
}

// Shutdown limpio
const shutdown = async (signal: string) => {
  fastify.log.info(`Recibido ${signal}, cerrando...`);
  try {
    await twitch.stop();
    await fastify.close();
    process.exit(0);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

process.on('SIGINT', () => void shutdown('SIGINT'));
process.on('SIGTERM', () => void shutdown('SIGTERM'));
