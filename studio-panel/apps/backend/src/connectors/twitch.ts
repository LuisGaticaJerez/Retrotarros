/**
 * Conector Twitch.
 *
 * Usa tmi.js para conectarse al chat IRC de Twitch como cliente ANÓNIMO
 * (justinfan<n>). Esto permite leer cualquier chat público sin OAuth.
 *
 * Si en el futuro queremos:
 *  - Identidad de bot (chatear de vuelta) → setear TWITCH_BOT_USERNAME + TWITCH_BOT_OAUTH.
 *  - EventSub (follows, raids, suscripciones) → integrar Twitch Helix API separado.
 */

import tmi from 'tmi.js';
import { randomUUID } from 'node:crypto';
import type { FastifyBaseLogger } from 'fastify';
import type { ChatMessage, Platform } from '@retrostudio/shared';

type ConnectorStatus = { platform: Platform; connected: boolean; error?: string };

interface CreateTwitchConnectorOpts {
  channels: string[];
  onMessage: (msg: ChatMessage) => void;
  onStatus: (status: ConnectorStatus) => void;
  logger: FastifyBaseLogger;
}

export function createTwitchConnector(opts: CreateTwitchConnectorOpts) {
  const { channels, onMessage, onStatus, logger } = opts;

  const username = process.env.TWITCH_BOT_USERNAME;
  const oauth = process.env.TWITCH_BOT_OAUTH;

  const identity = username && oauth ? { username, password: oauth } : undefined;

  const client = new tmi.Client({
    options: { debug: false, skipMembership: true },
    connection: { reconnect: true, secure: true },
    identity,
    channels,
  });

  client.on('connected', (addr, port) => {
    logger.info(`Twitch conectado a ${addr}:${port} (canales: ${channels.join(', ')})`);
    onStatus({ platform: 'twitch', connected: true });
  });

  client.on('disconnected', (reason) => {
    logger.warn(`Twitch desconectado: ${reason}`);
    onStatus({ platform: 'twitch', connected: false, error: reason });
  });

  client.on('message', (channel, tags, message, self) => {
    if (self) return;

    const msg: ChatMessage = {
      id: randomUUID(),
      platform: 'twitch',
      author: {
        name: tags['display-name'] ?? tags.username ?? 'anon',
        externalId: tags['user-id'],
        color: tags.color ?? undefined,
        badges: tags.badges ? Object.keys(tags.badges) : undefined,
      },
      text: message,
      timestamp: new Date().toISOString(),
      externalId: tags.id,
    };

    onMessage(msg);
  });

  return {
    start: async () => {
      try {
        await client.connect();
      } catch (err) {
        logger.error({ err }, 'Twitch connect failed');
        onStatus({
          platform: 'twitch',
          connected: false,
          error: err instanceof Error ? err.message : String(err),
        });
      }
    },
    stop: async () => {
      try {
        await client.disconnect();
      } catch {
        // ignore
      }
    },
  };
}
