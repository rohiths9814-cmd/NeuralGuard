import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * WebSocket hook for real-time NeuralGuard event streaming.
 *
 * Auto-reconnects on disconnect with exponential backoff.
 * Keeps only the last `bufferSize` events for the timeline chart.
 */
export function useWebSocket(bufferSize = 60) {
  const [event, setEvent] = useState(null);
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const retryRef = useRef(0);
  const timerRef = useRef(null);

  const connect = useCallback(() => {
    // Build WebSocket URL dynamically
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/dashboard`;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retryRef.current = 0;
        console.log('[WS] Connected to NeuralGuard');
      };

      ws.onmessage = (msg) => {
        try {
          const data = JSON.parse(msg.data);
          setEvent(data);
          setEvents((prev) => {
            const next = [...prev, data];
            return next.slice(-bufferSize);
          });
        } catch (err) {
          console.warn('[WS] Parse error:', err);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        // Exponential backoff: 1s, 2s, 4s, 8s, max 15s
        const delay = Math.min(1000 * 2 ** retryRef.current, 15000);
        retryRef.current += 1;
        console.log(`[WS] Disconnected. Reconnecting in ${delay}ms…`);
        timerRef.current = setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch (err) {
      console.error('[WS] Connection error:', err);
    }
  }, [bufferSize]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [connect]);

  return { event, events, connected };
}
