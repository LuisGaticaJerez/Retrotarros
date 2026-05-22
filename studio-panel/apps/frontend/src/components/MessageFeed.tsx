import { useMemo, useState } from 'react';
import {
  PLATFORM_LABELS,
  PLATFORM_COLORS,
  type ChatMessage,
  type Platform,
} from '@retrostudio/shared';
import { cn } from '../lib/cn';

interface MessageFeedProps {
  messages: ChatMessage[];
}

const ALL_PLATFORMS: Platform[] = [
  'twitch',
  'youtube',
  'discord',
  'instagram',
  'facebook',
  'whatsapp',
  'ssn',
];

export function MessageFeed({ messages }: MessageFeedProps) {
  const [filter, setFilter] = useState<Set<Platform>>(new Set(ALL_PLATFORMS));

  const filtered = useMemo(
    () => messages.filter((m) => filter.has(m.platform)),
    [messages, filter],
  );

  const togglePlatform = (p: Platform) => {
    setFilter((curr) => {
      const next = new Set(curr);
      if (next.has(p)) next.delete(p);
      else next.add(p);
      return next;
    });
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex flex-wrap gap-1.5 border-b border-white/5 bg-dark/30 px-6 py-2">
        <span className="font-mono text-[10px] uppercase tracking-wider text-white/40 self-center mr-2">
          Filtros:
        </span>
        {ALL_PLATFORMS.map((p) => {
          const active = filter.has(p);
          return (
            <button
              key={p}
              onClick={() => togglePlatform(p)}
              className={cn(
                'rounded-sm border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider transition-colors',
                active ? 'border-current bg-white/5' : 'border-white/10 text-white/30',
              )}
              style={active ? { color: PLATFORM_COLORS[p] } : undefined}
            >
              {PLATFORM_LABELS[p]}
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
        {filtered.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="font-mono text-sm text-white/30">
              Esperando mensajes…
            </p>
          </div>
        ) : (
          filtered.map((msg) => <MessageRow key={msg.id} msg={msg} />)
        )}
      </div>
    </div>
  );
}

function MessageRow({ msg }: { msg: ChatMessage }) {
  const time = new Date(msg.timestamp).toLocaleTimeString('es-CL', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <article className="flex items-start gap-3 rounded-md border border-white/5 bg-white/[0.02] px-3 py-2 hover:bg-white/[0.04]">
      <div className="flex-shrink-0">
        <span
          className="inline-flex items-center rounded-sm px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wider"
          style={{
            color: PLATFORM_COLORS[msg.platform],
            border: `1px solid ${PLATFORM_COLORS[msg.platform]}40`,
          }}
        >
          {PLATFORM_LABELS[msg.platform]}
        </span>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span
            className="font-semibold text-sm truncate"
            style={msg.author.color ? { color: msg.author.color } : undefined}
          >
            {msg.author.name}
          </span>
          <span className="font-mono text-[10px] text-white/30">{time}</span>
        </div>
        <p className="text-sm text-cream/90 break-words">{msg.text}</p>
      </div>
    </article>
  );
}
