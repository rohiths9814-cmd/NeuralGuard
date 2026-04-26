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
          color="text-neural-cyan"
          glow="shadow-neural-cyan/10"
        />
        <MetricCard
          label="Motion Intensity"
          value={event?.vision ? `${(event.vision.motion_intensity * 100).toFixed(0)}%` : '-'}
          icon="📊"
          color="text-neural-purple"
          glow="shadow-neural-purple/10"
        />
        <MetricCard
          label="Temperature"
          value={sensor.temperature ? `${sensor.temperature}°C` : '-'}
          icon="🌡️"
          color={sensor.temperature > 40 ? 'text-neural-red' : 'text-neural-green'}
          glow={sensor.temperature > 40 ? 'shadow-neural-red/10' : 'shadow-neural-green/10'}
        />
        <MetricCard
          label="Confidence"
          value={fusion.confidence ? `${(fusion.confidence * 100).toFixed(0)}%` : '-'}
          icon="🎯"
          color="text-neural-amber"
          glow="shadow-neural-amber/10"
        />
      </div>

      {/* Agent Status Grid */}
      <div className="glass-card">
        <div className="px-4 py-3 border-b border-neural-border/40">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-neural-accent/15 flex items-center justify-center">
              <span className="text-sm">⚙️</span>
            </div>
            <span className="section-label">
              Agent Pipeline — {Object.keys(agents).length} Active
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
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-lg bg-neural-accent/15 flex items-center justify-center">
              <span className="text-sm">🤖</span>
            </div>
            <span className="section-label">
              AI Analysis {fusion.gemini_analysis ? '(Gemini)' : '(Rule-based)'}
            </span>
          </div>
          <p className="text-sm text-neural-text/90 leading-relaxed">
            {fusion.explanation}
          </p>
          {fusion.contributing_factors?.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-3">
              {fusion.contributing_factors.map((f, i) => (
                <span key={i} className="px-2.5 py-1 rounded-lg bg-neural-accent/10 text-neural-accent-light text-[10px] font-mono border border-neural-accent/15">
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

function MetricCard({ label, value, icon, color, glow }) {
  return (
    <div className={`glass-card-hover p-4 shadow-lg ${glow}`}>
      <div className="flex items-center justify-between">
        <span className="text-xl">{icon}</span>
        <span className={`text-2xl font-bold font-mono ${color}`}>{value}</span>
      </div>
      <p className="text-[10px] font-mono text-neural-muted uppercase tracking-wider mt-2">
        {label}
      </p>
    </div>
  );
}

function AgentCard({ id, agent }) {
  const icon = AGENT_ICONS[id] || '🔧';
  const statusColor = STATUS_COLORS[agent.status] || STATUS_COLORS.offline;

  return (
    <div className="bg-neural-surface/50 rounded-xl border border-neural-border/25 p-3 flex items-center gap-3 hover:border-neural-border/50 transition-colors">
      <span className="text-lg">{icon}</span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-neural-text truncate">{agent.name}</p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className={`w-1.5 h-1.5 rounded-full ${statusColor}`} />
          <span className="text-[10px] font-mono text-neural-muted uppercase">{agent.status}</span>
        </div>
      </div>
    </div>
  );
}
