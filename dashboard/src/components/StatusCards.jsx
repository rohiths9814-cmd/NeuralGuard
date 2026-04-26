/**
 * StatusCards — Agent status grid and system metrics.
 */

const AGENT_ICONS = {
  vision: '👁️',
  sensor: '📡',
  behavior: '🧠',
  memory: '💾',
  fusion: '⚡',
  decision: '🎯',
  response: '🚨',
};

const STATUS_COLORS = {
  active: 'bg-neural-green',
  fallback: 'bg-neural-amber',
  offline: 'bg-neural-red',
};

export default function StatusCards({ status, event }) {
  const agents = status?.agent_statuses || {};
  const fusion = event?.fusion || {};
  const sensor = event?.sensor || {};

  return (
    <div className="space-y-4">
      {/* System Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <MetricCard
          label="People Detected"
          value={event?.vision?.people_count ?? '-'}
          icon="👥"
          color="text-neural-accent"
        />
        <MetricCard
          label="Motion Intensity"
          value={event?.vision ? `${(event.vision.motion_intensity * 100).toFixed(0)}%` : '-'}
          icon="📊"
          color="text-neural-purple"
        />
        <MetricCard
          label="Temperature"
          value={sensor.temperature ? `${sensor.temperature}°C` : '-'}
          icon="🌡️"
          color={sensor.temperature > 40 ? 'text-neural-red' : 'text-neural-green'}
        />
        <MetricCard
          label="Confidence"
          value={fusion.confidence ? `${(fusion.confidence * 100).toFixed(0)}%` : '-'}
          icon="🎯"
          color="text-neural-amber"
        />
      </div>

      {/* Agent Status Grid */}
      <div className="glass-card">
        <div className="px-4 py-2.5 border-b border-neural-border/50">
          <div className="flex items-center gap-2">
            <span className="text-neural-accent">⚙️</span>
            <span className="text-xs font-mono text-neural-muted uppercase tracking-wider">
              Agent Status — {Object.keys(agents).length} Active
            </span>
          </div>
        </div>
        <div className="p-3 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
          {Object.entries(agents).map(([key, agent]) => (
            <AgentCard key={key} id={key} agent={agent} />
          ))}
        </div>
      </div>

      {/* Fusion Explanation */}
      {fusion.explanation && (
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-2">
            <span>🤖</span>
            <span className="text-xs font-mono text-neural-accent uppercase tracking-wider">
              AI Analysis {fusion.gemini_analysis ? '(Gemini)' : '(Rule-based)'}
            </span>
          </div>
          <p className="text-sm text-neural-text leading-relaxed">
            {fusion.explanation}
          </p>
          {fusion.contributing_factors?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {fusion.contributing_factors.map((f, i) => (
                <span key={i} className="px-2 py-0.5 rounded bg-neural-accent/10 text-neural-accent text-[10px] font-mono">
                  {f}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, icon, color }) {
  return (
    <div className="glass-card-hover p-3">
      <div className="flex items-center justify-between">
        <span className="text-lg">{icon}</span>
        <span className={`text-xl font-bold font-mono ${color}`}>{value}</span>
      </div>
      <p className="text-[10px] font-mono text-neural-muted uppercase tracking-wider mt-1.5">
        {label}
      </p>
    </div>
  );
}

function AgentCard({ id, agent }) {
  const icon = AGENT_ICONS[id] || '🔧';
  const statusColor = STATUS_COLORS[agent.status] || STATUS_COLORS.offline;

  return (
    <div className="bg-neural-surface/60 rounded-lg border border-neural-border/30 p-2.5 flex items-center gap-2.5">
      <span className="text-base">{icon}</span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-white truncate">{agent.name}</p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className={`w-1.5 h-1.5 rounded-full ${statusColor}`} />
          <span className="text-[10px] font-mono text-neural-muted uppercase">{agent.status}</span>
        </div>
      </div>
    </div>
  );
}
