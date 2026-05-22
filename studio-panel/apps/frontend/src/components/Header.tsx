import { cn } from '../lib/cn';

interface HeaderProps {
  connected: boolean;
}

export function Header({ connected }: HeaderProps) {
  return (
    <header className="border-b border-white/10 bg-dark/80 backdrop-blur">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-baseline gap-3">
          <h1 className="font-display text-2xl font-black tracking-wider text-cream">
            RETROTARROS
          </h1>
          <span className="text-xs text-cyan font-mono">· STUDIO PANEL</span>
        </div>
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'h-2 w-2 rounded-full',
              connected ? 'bg-green-500 animate-pulse' : 'bg-red-500',
            )}
            aria-label={connected ? 'Conectado' : 'Desconectado'}
          />
          <span className="font-mono text-xs uppercase tracking-wider text-cream/70">
            {connected ? 'EN VIVO' : 'OFFLINE'}
          </span>
        </div>
      </div>
      <div className="scanline-border" />
    </header>
  );
}
