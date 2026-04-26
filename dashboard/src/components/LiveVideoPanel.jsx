/**
 * LiveVideoPanel — Simulated CCTV feed with animated detection overlays.
 *
 * Renders a canvas that draws a moving "surveillance" view with
 * detection bounding boxes matching the vision agent output.
 */

import { useRef, useEffect } from 'react';

const THREAT_COLORS = {
  low: '#34d399',
  moderate: '#fbbf24',
  high: '#fb923c',
  critical: '#f43f5e',
};

export default function LiveVideoPanel({ event }) {
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const particlesRef = useRef(
    Array.from({ length: 30 }, () => ({
      x: Math.random() * 640,
      y: Math.random() * 480,
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      size: Math.random() * 3 + 1,
    }))
  );

  const vision = event?.vision || {};
  const threat = vision.risk_level || 'low';
  const people = vision.people_count || 0;
  const motion = vision.motion_intensity || 0;
  const borderColor = THREAT_COLORS[threat] || THREAT_COLORS.low;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = 640, H = 480;
    canvas.width = W;
    canvas.height = H;

    let frame = 0;

    function draw() {
      frame++;

      // Dark background with noise
      ctx.fillStyle = '#0a0e18';
      ctx.fillRect(0, 0, W, H);

      // Grid
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.04)';
      ctx.lineWidth = 0.5;
      for (let x = 0; x < W; x += 40) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }
      for (let y = 0; y < H; y += 40) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }

      // Moving particles (simulate surveillance noise)
      const particles = particlesRef.current;
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.fillStyle = `rgba(99, 102, 241, ${0.1 + Math.sin(frame * 0.02 + p.x) * 0.05})`;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      });

      // Detection bounding boxes
      const detections = vision.detections || [];
      detections.slice(0, 12).forEach((det, i) => {
        const [x, y, w, h] = det.bbox || [50 + i * 45, 100 + (i % 3) * 80, 55, 120];
        const color = THREAT_COLORS[threat];
        const alpha = 0.5 + Math.sin(frame * 0.05 + i) * 0.2;

        // Box
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.setLineDash([6, 3]);
        ctx.strokeRect(x, y, w, h);
        ctx.setLineDash([]);

        // Corner brackets
        const corner = 10;
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = `rgba(${hexToRgb(color)}, ${alpha})`;
        // Top-left
        ctx.beginPath(); ctx.moveTo(x, y + corner); ctx.lineTo(x, y); ctx.lineTo(x + corner, y); ctx.stroke();
        // Top-right
        ctx.beginPath(); ctx.moveTo(x + w - corner, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + corner); ctx.stroke();
        // Bottom-left
        ctx.beginPath(); ctx.moveTo(x, y + h - corner); ctx.lineTo(x, y + h); ctx.lineTo(x + corner, y + h); ctx.stroke();
        // Bottom-right
        ctx.beginPath(); ctx.moveTo(x + w - corner, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - corner); ctx.stroke();

        // Label
        ctx.fillStyle = color;
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillText(`PERSON ${(det.confidence * 100).toFixed(0)}%`, x + 3, y - 4);
      });

      // HUD — top overlay
      ctx.fillStyle = 'rgba(129, 140, 248, 0.85)';
      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.fillText(`CAM_01 │ ${new Date().toLocaleTimeString()}`, 12, 22);

      ctx.fillStyle = THREAT_COLORS[threat];
      ctx.fillText(`THREAT: ${threat.toUpperCase()}`, W - 160, 22);

      // HUD — bottom stats
      ctx.fillStyle = 'rgba(226, 232, 240, 0.6)';
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillText(`PERSONS: ${people}  │  MOTION: ${(motion * 100).toFixed(0)}%  │  FPS: 30`, 12, H - 12);

      // Scan line
      const scanY = (frame * 2) % H;
      const grad = ctx.createLinearGradient(0, scanY - 20, 0, scanY + 20);
      grad.addColorStop(0, 'transparent');
      grad.addColorStop(0.5, 'rgba(99, 102, 241, 0.06)');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.fillRect(0, scanY - 20, W, 40);

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [vision, threat, people, motion]);

  return (
    <div className="glass-card overflow-hidden relative" style={{ boxShadow: `0 0 40px ${borderColor}10` }}>
      <div className="px-4 py-3 border-b border-neural-border/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-neural-red animate-pulse" />
          <span className="section-label">Live Feed — Camera 01</span>
        </div>
        <span className={`badge-${threat}`}>{threat}</span>
      </div>
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="w-full h-auto"
          style={{ imageRendering: 'pixelated' }}
        />
        <div className="scanline-overlay" />
      </div>
    </div>
  );
}

function hexToRgb(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r}, ${g}, ${b}`;
}
