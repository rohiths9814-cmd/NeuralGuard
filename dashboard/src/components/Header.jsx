/**
 * Header — Top bar with NeuralGuard branding, connection status, and system stats.
 */

export default function Header({ status, connected }) {
  const threat = status?.last_threat_level || 'low';
  const threatColor = {
    low: 'text-neural-green',
    moderate: 'text-neural-amber',
    high: 'text-orange-400',
    critical: 'text-neural-red',
  }[threat];

  return (
    <header className="glass-card border-b border-neural-border/50 px-6 py-3 flex items-center justify-between">
      {/* Left — Branding */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-neural-accent to-neural-purple flex items-center justify-center">
          <span className="text-lg">🛡️</span>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">
            NeuralGuard
          </h1>
          <p className="text-[10px] font-mono text-neural-muted uppercase tracking-widest">
            Autonomous Security System
          </p>
        </div>
      </div>

      {/* Center — Threat Level */}
      <div className="hidden md:flex items-center gap-6">
        <div className="text-center">
          <p className="text-[10px] font-mono text-neural-muted uppercase">Threat Level</p>
          <p className={`text-sm font-bold font-mono uppercase ${threatColor}`}>
            {threat}
          </p>
        </div>
        <div className="w-px h-8 bg-neural-border" />
        <div className="text-center">
          <p className="text-[10px] font-mono text-neural-muted uppercase">Frames</p>
          <p className="text-sm font-mono text-white">
            {status?.frames_processed?.toLocaleString() || '0'}
          </p>
        </div>
        <div className="w-px h-8 bg-neural-border" />
        <div className="text-center">
          <p className="text-[10px] font-mono text-neural-muted uppercase">Alerts</p>
          <p className="text-sm font-mono text-neural-amber">
            {status?.alerts_generated || 0}
          </p>
        </div>
      </div>

      {/* Right — Connection */}
      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono
          ${connected
            ? 'bg-neural-green/10 text-neural-green border border-neural-green/30'
            : 'bg-neural-red/10 text-neural-red border border-neural-red/30'
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-neural-green animate-pulse' : 'bg-neural-red'}`} />
          {connected ? 'LIVE' : 'OFFLINE'}
        </div>
        <div className="text-right hidden sm:block">
          <p className="text-[10px] font-mono text-neural-muted">
            Uptime {formatUptime(status?.uptime_seconds)}
          </p>
        </div>
      </div>
    </header>
  );
}

function formatUptime(seconds) {
  if (!seconds) return '00:00:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}
