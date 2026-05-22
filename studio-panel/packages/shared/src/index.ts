/**
 * Tipos compartidos entre backend y frontend.
 * Mantener este archivo platform-agnostic (sin Node APIs ni DOM APIs).
 */

export type Platform =
  | 'twitch'
  | 'youtube'
  | 'discord'
  | 'instagram'
  | 'facebook'
  | 'whatsapp'
  | 'ssn'; // mensaje agregado por Social Stream Ninja sin platform tag identificable

export interface Author {
  /** Nombre visible en la plataforma origen. */
  name: string;
  /** ID interno opcional de la plataforma (login Twitch, ID YouTube). */
  externalId?: string;
  /** URL avatar opcional. */
  avatar?: string;
  /** Badges/roles opcionales (mod, subscriber, founder). */
  badges?: string[];
  /** Color HEX opcional asignado por la plataforma. */
  color?: string;
}

export interface ChatMessage {
  /** ID único interno (UUID). */
  id: string;
  /** Plataforma origen. */
  platform: Platform;
  /** Autor. */
  author: Author;
  /** Texto del mensaje (plain). */
  text: string;
  /** HTML del mensaje si trae emotes/formato. */
  html?: string;
  /** Cuándo llegó (ISO 8601, UTC). */
  timestamp: string;
  /** ID externo de la plataforma para evitar duplicados. */
  externalId?: string;
  /** ID interno del stream/sesión activa. */
  streamId?: string;
  /** Slide HTML activa en el monitor del estudio cuando llegó el mensaje. */
  slideId?: string;
  /** Pinned por moderador para responder en cámara. */
  pinned?: boolean;
  /** Ya fue respondido en cámara. */
  replied?: boolean;
}

/** Mensaje que viaja por el WebSocket backend → frontend. */
export type WsServerMessage =
  | { type: 'chat'; payload: ChatMessage }
  | { type: 'connector_status'; payload: { platform: Platform; connected: boolean; error?: string } }
  | { type: 'stream_started'; payload: { streamId: string } }
  | { type: 'stream_stopped'; payload: { streamId: string } };

/** Mensaje que viaja por el WebSocket frontend → backend. */
export type WsClientMessage =
  | { type: 'subscribe'; payload: { orgId: string } }
  | { type: 'pin'; payload: { messageId: string; pinned: boolean } }
  | { type: 'reply'; payload: { messageId: string } };

export const PLATFORM_LABELS: Record<Platform, string> = {
  twitch: 'Twitch',
  youtube: 'YouTube',
  discord: 'Discord',
  instagram: 'Instagram',
  facebook: 'Facebook',
  whatsapp: 'WhatsApp',
  ssn: 'Social Stream Ninja',
};

export const PLATFORM_COLORS: Record<Platform, string> = {
  twitch: '#9146FF',
  youtube: '#FF0000',
  discord: '#5865F2',
  instagram: '#E4405F',
  facebook: '#1877F2',
  whatsapp: '#25D366',
  ssn: '#888888',
};
