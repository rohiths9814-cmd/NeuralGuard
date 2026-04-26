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
    <header className="glass-card rounded-none border-x-0 border-t-0 border-b border-neural-border/30 px-6 py-3 flex items-center justify-between">
      {/* Left — Branding */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neural-accent to-neural-purple flex items-center justify-center shadow-lg shadow-neural-accent/20">
          <span className="text-lg">🛡️</span>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white">
            Neural<span className="text-neural-accent">Guard</span>
          </h1>
          <p className="text-[10px] font-mono text-neural-muted uppercase tracking-widest">
            Autonomous Security System
          </p>
        </div>
      </div>

      {/* Center — Stats */}
      <div className="hidden md:flex items-center gap-1">
        <StatPill label="Threat" value={threat.toUpperCase()} valueClass={threatColor} />
        <div className="w-px h-6 bg-neural-border/40 mx-1" />
        <StatPill label="Frames" value={status?.frames_processed?.toLocaleString() || '0'} />
        <div className="w-px h-6 bg-neural-border/40 mx-1" />
        <StatPill label="Alerts" value={status?.alerts_generated || 0} valueClass="text-neural-amber" />
      </div>

      {/* Right — Connection */}
      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-mono font-semibold
          ${connected
            ? 'bg-neural-green/10 text-neural-green border border-neural-green/25'
            : 'bg-neural-red/10 text-neural-red border border-neural-red/25'
          }`}
        >
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-neural-green animate-pulse' : 'bg-neural-red'}`} />
          {connected ? 'LIVE' : 'OFFLINE'}
        </div>
        <div className="text-right hidden sm:block">
          <p className="text-[10px] font-mono text-neural-muted">
            {formatUptime(status?.uptime_seconds)}
          </p>
        </div>
      </div>
    </header>
  );
}

function StatPill({ label, value, valueClass = 'text-white' }) {
  return (
    <div className="bg-neural-surface/60 rounded-lg px-3 py-1.5 text-center min-w-[70px]">
      <p className="text-[9px] font-mono text-neural-muted uppercase">{label}</p>
      <p className={`text-sm font-bold font-mono ${valueClass}`}>{value}</p>
    </div>
  );
}

function formatUptime(seconds) {
  if (!seconds) return '00:00:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}
