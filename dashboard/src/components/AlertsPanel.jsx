/**
 * AlertsPanel — Real-time scrolling alert feed color-coded by threat level.
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

  const recentAlerts = [...alerts].reverse().slice(0, 50);

  return (
    <div className="glass-card flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-neural-border/50 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-neural-amber">⚡</span>
          <span className="text-xs font-mono text-neural-muted uppercase tracking-wider">
            Alert Feed
          </span>
        </div>
        <span className="text-xs font-mono text-neural-muted">{alerts.length} total</span>
      </div>

      {/* Alert list */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2 min-h-0">
        {recentAlerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-neural-muted">
            <span className="text-3xl mb-2">🔒</span>
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

  return (
    <div
      className={`bg-neural-surface/60 rounded-lg border border-neural-border/30 border-l-[3px] ${borderMap[threat]}
        p-3 animate-slide-up`}
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 min-w-0">
          <span className="text-base shrink-0 mt-0.5">{icon}</span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white truncate">
              {alert.title}
            </p>
            <p className="text-xs text-neural-muted mt-0.5 line-clamp-2">
              {alert.message}
            </p>
          </div>
        </div>
        <div className="flex flex-col items-end shrink-0 gap-1">
          <span className={`badge-${threat}`}>{threat}</span>
          <span className="text-[10px] font-mono text-neural-muted">{time}</span>
        </div>
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-3 mt-2 text-[10px] font-mono text-neural-muted">
        <span>📹 {alert.camera_id || 'cam_01'}</span>
        <span>👥 {alert.people_count ?? 0}</span>
        <span>🎯 {((alert.confidence || 0) * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}
