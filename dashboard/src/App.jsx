/**
 * App — Main NeuralGuard Dashboard layout.
 *
 * Composes: Header, LiveVideoPanel, AlertsPanel, StatusCards, TimelineChart.
 * Connects to the backend via WebSocket + REST polling.
 */

import { useState, useEffect } from 'react';
import Header from './components/Header';
import LiveVideoPanel from './components/LiveVideoPanel';
import AlertsPanel from './components/AlertsPanel';
import StatusCards from './components/StatusCards';
import TimelineChart from './components/TimelineChart';
import { useWebSocket } from './hooks/useWebSocket';
import { api } from './lib/api';

export default function App() {
  const { event, events, connected } = useWebSocket(60);
  const [status, setStatus] = useState(null);
  const [alerts, setAlerts] = useState([]);

  // Poll system status every 3 seconds
  useEffect(() => {
    let active = true;

    async function poll() {
      try {
        const [statusData, alertData] = await Promise.all([
          api.getStatus(),
          api.getAlerts(100),
        ]);
        if (active) {
          setStatus(statusData);
          setAlerts(alertData.alerts || []);
        }
      } catch (err) {
        // Silently retry — backend may not be up yet
      }
    }

    poll();
    const id = setInterval(poll, 3000);
    return () => { active = false; clearInterval(id); };
  }, []);

  // Merge WebSocket alerts into state
  useEffect(() => {
    if (event?.alert) {
      setAlerts((prev) => {
        // Avoid duplicates
        if (prev.some((a) => a.id === event.alert.id)) return prev;
        return [...prev, event.alert].slice(-100);
      });
    }
  }, [event]);

  return (
    <div className="min-h-screen flex flex-col grid-bg">
      {/* Header */}
      <Header status={status} connected={connected} />

      {/* Main Content */}
      <main className="flex-1 p-4 lg:p-6 space-y-4 lg:space-y-6">
        {/* Top Row: Video + Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6">
          {/* Video Panel — 3 columns */}
          <div className="lg:col-span-3">
            <LiveVideoPanel event={event} />
          </div>

          {/* Alerts Panel — 2 columns */}
          <div className="lg:col-span-2 h-[400px] lg:h-auto">
            <AlertsPanel alerts={alerts} />
          </div>
        </div>

        {/* Status Cards */}
        <StatusCards status={status} event={event} />

        {/* Timeline */}
        <TimelineChart events={events} />
      </main>

      {/* Footer */}
      <footer className="border-t border-neural-border/30 px-6 py-3 text-center">
        <p className="text-[10px] font-mono text-neural-muted">
          NeuralGuard v1.0 │ AI-Powered Autonomous Security │ {new Date().getFullYear()}
        </p>
      </footer>
    </div>
  );
}
