/**
 * TimelineChart — Recharts-based real-time threat / people / motion chart.
 */

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const THREAT_MAP = { low: 1, moderate: 2, high: 3, critical: 4 };

export default function TimelineChart({ events }) {
  // Transform websocket events into chart data
  const data = events.map((e, i) => {
    const vision = e.vision || {};
    const fusion = e.fusion || {};
    const sensor = e.sensor || {};
    const ts = e.timestamp ? new Date(e.timestamp) : new Date();

    return {
      time: ts.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }),
      people: vision.people_count || 0,
      motion: Math.round((vision.motion_intensity || 0) * 100),
      threat: THREAT_MAP[fusion.overall_threat] || 1,
      smoke: Math.round((sensor.smoke_level || 0) * 100),
      idx: i,
    };
  });

  // Show last 30 data points
  const chartData = data.slice(-30);

  return (
    <div className="glass-card">
      <div className="px-4 py-3 border-b border-neural-border/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-neural-cyan/15 flex items-center justify-center">
            <span className="text-sm">📈</span>
          </div>
          <span className="section-label">
            Real-time Timeline
          </span>
        </div>
        <span className="text-[10px] font-mono text-neural-muted bg-neural-surface/80 px-2 py-0.5 rounded-md">
          {chartData.length} pts
        </span>
      </div>

      <div className="p-4" style={{ height: 280 }}>
        {chartData.length < 2 ? (
          <div className="flex items-center justify-center h-full text-neural-muted">
            <div className="text-center">
              <span className="text-3xl">📡</span>
              <p className="text-xs font-mono mt-2">Collecting data…</p>
            </div>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gradPeople" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#22d3ee" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="gradMotion" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#a855f7" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="gradThreat" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#f43f5e" stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid strokeDasharray="3 6" stroke="#1f2937" />
              <XAxis
                dataKey="time"
                stroke="#64748b"
                tick={{ fontSize: 9, fontFamily: '"JetBrains Mono"' }}
                interval="preserveStartEnd"
              />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 9, fontFamily: '"JetBrains Mono"' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                height={28}
                iconType="rect"
                wrapperStyle={{ fontSize: 10, fontFamily: '"JetBrains Mono"' }}
              />

              <Area
                type="monotone"
                dataKey="people"
                name="People"
                stroke="#22d3ee"
                strokeWidth={2}
                fill="url(#gradPeople)"
              />
              <Area
                type="monotone"
                dataKey="motion"
                name="Motion %"
                stroke="#a855f7"
                strokeWidth={1.5}
                fill="url(#gradMotion)"
              />
              <Area
                type="monotone"
                dataKey="threat"
                name="Threat"
                stroke="#f43f5e"
                strokeWidth={2}
                fill="url(#gradThreat)"
                yAxisId={0}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  const threatLabels = { 1: 'LOW', 2: 'MODERATE', 3: 'HIGH', 4: 'CRITICAL' };

  return (
    <div className="bg-neural-card/95 backdrop-blur-md border border-neural-border rounded-lg p-3 shadow-xl">
      <p className="text-[10px] font-mono text-neural-muted mb-1.5">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs font-mono">
          <span className="w-2 h-2 rounded-sm" style={{ background: p.color }} />
          <span className="text-neural-muted">{p.name}:</span>
          <span className="text-white font-medium">
            {p.name === 'Threat' ? threatLabels[p.value] || p.value : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}
