import { PLATFORM_LABELS, PLATFORM_COLORS, type Platform } from '@retrostudio/shared';
import { cn } from '../lib/cn';

interface ConnectorStatusBarProps {
  statuses: Partial<Record<Platform, { connected: boolean; error?: string }>>;
}

const PLATFORMS: Platform[] = ['twitch', 'youtube', 'discord', 'instagram', 'facebook', 'whatsapp'];

export function ConnectorStatusBar({ statuses }: ConnectorStatusBarProps) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-white/5 bg-dark/40 px-6 py-2">
      {PLATFORMS.map((platform) => {
        const status = statuses[platform];
        const connected = status?.connected ?? false;
        return (
          <span
            key={platform}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider transition-colors',
              connected
                ? 'border-current bg-white/5 text-cream'
                : 'border-white/10 bg-transparent text-white/40',
            )}
            style={connected ? { color: PLATFORM_COLORS[platform] } : undefined}
            title={status?.error ?? (connected ? 'Conectado' : 'Sin conexión')}
          >
            <span
              className={cn('h-1.5 w-1.5 rounded-full', connected ? 'bg-current' : 'bg-white/20')}
            />
            {PLATFORM_LABELS[platform]}
          </span>
        );
      })}
    </div>
  );
}
