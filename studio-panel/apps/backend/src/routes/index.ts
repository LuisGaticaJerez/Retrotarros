/**
 * Rutas HTTP REST del backend.
 *
 * Por ahora solo health + stats. Cuando agreguemos persistencia con Supabase,
 * acá vivirán los endpoints de history, pin/unpin, etc.
 */

import type { FastifyInstance } from 'fastify';
import { messageHub } from '../hub.js';

export async function registerRoutes(app: FastifyInstance): Promise<void> {
  app.get('/health', async () => ({
    ok: true,
    timestamp: new Date().toISOString(),
    subscribers: messageHub.subscriberCount(),
  }));

  app.get('/api/stats', async () => ({
    wsSubscribers: messageHub.subscriberCount(),
    uptime: process.uptime(),
    node: process.version,
  }));
}
