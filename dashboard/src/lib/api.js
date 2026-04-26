/**
 * NeuralGuard API client.
 * All endpoints proxy through Vite → FastAPI (localhost:8000).
 */

const BASE = '/api';

async function fetchJSON(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`);
  return res.json();
}

export const api = {
  getStatus:  () => fetchJSON('/status'),
  getAlerts:  (limit = 50) => fetchJSON(`/alerts?limit=${limit}`),
  getLatest:  () => fetchJSON('/latest'),
  getStream:  () => fetchJSON('/stream'),
  getMemory:  () => fetchJSON('/memory'),
};
