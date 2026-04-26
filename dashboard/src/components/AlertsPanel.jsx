/**
 * AlertsPanel — Real-time scrolling alert feed color-coded by threat level.
 * Fixed height with internal scrolling — never overflows the layout.
 */

import { useEffect, useRef } from 'react';

const ICONS = {
  low: '📊',
  moderate: '👁️',
  high: '⚠️',
  critical: '🚨',
};

const TIME_FMT = new Intl.DateTimeFormat('en', {
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false,
});

export default function AlertsPanel({ alerts }) {
  const scrollRef = useRef(null);

  // Auto-scroll to newest alert
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [alerts.length]);

  // Show only 20 most recent alerts (keeps UI snappy)
  const recentAlerts = [...alerts].reverse().slice(0, 20);

  return (
    <div className="glass-card flex flex-col h-full max-h-[500px]">
      {/* Header */}
      <div className="px-4 py-3 border-b border-neural-border/40 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-neural-red/15 flex items-center justify-center">
            <span className="text-sm">⚡</span>
          </div>
          <span className="section-label">Alert Feed</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-neural-muted bg-neural-surface/80 px-2 py-0.5 rounded-md">
            {alerts.length} total
          </span>
        </div>
      </div>

      {/* Alert list — scrollable container */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0">
        {recentAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-neural-muted py-12">
            <span className="text-4xl mb-3 opacity-50">🔒</span>
            <p className="text-xs font-mono">No alerts — All clear</p>
          </div>
        ) : (
          recentAlerts.map((alert, i) => (
            <AlertCard key={alert.id || i} alert={alert} index={i} />
          ))
        )}
      </div>
    </div>
  );
}

function AlertCard({ alert, index }) {
  const threat = alert.threat_level || 'low';
  const icon = ICONS[threat] || '📊';
  const time = alert.timestamp
    ? TIME_FMT.format(new Date(alert.timestamp))
    : '--:--:--';

  const borderMap = {
    low: 'border-l-neural-green',
    moderate: 'border-l-neural-amber',
    high: 'border-l-orange-400',
    critical: 'border-l-neural-red',
  };

  const bgMap = {
    low: 'bg-neural-green/[0.03]',
    moderate: 'bg-neural-amber/[0.03]',
    high: 'bg-orange-500/[0.03]',
    critical: 'bg-neural-red/[0.04]',
  };

  return (
    <div
      className={`${bgMap[threat]} rounded-xl border border-neural-border/25 border-l-[3px] ${borderMap[threat]}
        p-3 animate-slide-up hover:border-neural-border/50 transition-colors duration-200`}
      style={{ animationDelay: `${Math.min(index, 5) * 40}ms` }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2.5 min-w-0">
          <span className="text-sm shrink-0 mt-0.5">{icon}</span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-neural-text truncate">
              {alert.title}
            </p>
            <p className="text-xs text-neural-muted mt-0.5 line-clamp-1">
              {alert.message}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end shrink-0 gap-1">
          <span className={`badge-${threat}`}>{threat}</span>
          <span className="text-[10px] font-mono text-neural-muted">{time}</span>
        </div>
      </div>

      {/* Compact meta row */}
      <div className="flex items-center gap-3 mt-2 text-[10px] font-mono text-neural-muted">
        <span>📹 {alert.camera_id || 'cam_01'}</span>
        <span>👥 {alert.people_count ?? 0}</span>
        <span>🎯 {((alert.confidence || 0) * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}
