/**
 * Hub central de mensajes.
 *
 * Los conectores (Twitch, YouTube, Discord, ...) publican mensajes acá.
 * Las conexiones WebSocket activas se suscriben para reenviar al frontend.
 *
 * Simple pub/sub in-memory. Si en el futuro necesitamos escalar a múltiples
 * instancias del backend, esto migra a Redis pub/sub.
 */

import type { WsServerMessage } from '@retrostudio/shared';

type Subscriber = (msg: WsServerMessage) => void;

class MessageHub {
  private subscribers = new Set<Subscriber>();

  subscribe(fn: Subscriber): () => void {
    this.subscribers.add(fn);
    return () => this.subscribers.delete(fn);
  }

  publish(msg: WsServerMessage): void {
    for (const fn of this.subscribers) {
      try {
        fn(msg);
      } catch {
        // No dejamos que un suscriptor roto tire el resto.
      }
    }
  }

  subscriberCount(): number {
    return this.subscribers.size;
  }
}

export const messageHub = new MessageHub();
