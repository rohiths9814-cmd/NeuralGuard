"""
Security Pipeline — Orchestrates the full agent processing chain.

Data flow:
  Camera → Frame → VisionAgent → SensorAgent → BehaviorAgent →
  MemoryAgent → FusionAgent (Gemini) → DecisionAgent → ResponseAgent →
  WebSocket broadcast → Dashboard
"""

import asyncio
import json
import time
import logging
import os
from typing import List, Dict, Set, Any

from server.agents import (
    VisionAgent,
    SensorAgent,
    BehaviorAgent,
    MemoryAgent,
    FusionAgent,
    DecisionAgent,
    ResponseAgent,
)
from server.services.video_processor import VideoProcessor
from server.utils.helpers import get_timestamp

logger = logging.getLogger(__name__)


class SecurityPipeline:
    """
    The central orchestrator. Runs a continuous async loop that:
    1. Ingests a frame
    2. Runs it through all 7 agents
    3. Broadcasts results to connected WebSocket clients
    """

    def __init__(self):
        # ── Agents ────────────────────────────────────────────────────────
        self.vision = VisionAgent()
        self.sensor = SensorAgent()
        self.behavior = BehaviorAgent()
        self.memory = MemoryAgent()
        self.fusion = FusionAgent()
        self.decision = DecisionAgent()
        self.response = ResponseAgent()

        # ── Video source ──────────────────────────────────────────────────
        source = os.getenv("VIDEO_SOURCE", "mock")
        self.video = VideoProcessor(source=source)

        # ── State ─────────────────────────────────────────────────────────
        self.running = False
        self.frames_processed = 0
        self.alerts: List[Dict[str, Any]] = []
        self.latest_event: Dict[str, Any] = {}
        self.start_time: float = 0
        self.websocket_clients: Set = set()

        # Processing interval (seconds)
        self.interval = int(os.getenv("PIPELINE_INTERVAL", "2"))

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def start(self):
        """Start the processing loop."""
        self.running = True
        self.start_time = time.time()
        logger.info(
            "🚀 NeuralGuard pipeline started (interval=%ds, source=%s)",
            self.interval,
            self.video.source,
        )

        while self.running:
            try:
                await self._process_cycle()
            except Exception as exc:
                logger.error("Pipeline cycle error: %s", exc, exc_info=True)
            await asyncio.sleep(self.interval)

    async def stop(self):
        """Gracefully stop the pipeline."""
        self.running = False
        self.video.release()
        logger.info("🛑 NeuralGuard pipeline stopped")

    # ── Core Processing Cycle ────────────────────────────────────────────

    async def _process_cycle(self):
        """Single processing cycle through all agents."""
        cycle_start = time.time()

        # 1. INGESTION — get a frame
        frame = await self.video.get_frame()

        # 2. VISION AGENT — detect people and motion
        vision_out = self.vision.process(frame)

        # 3. SENSOR AGENT — read environment
        sensor_out = self.sensor.process()

        # 4. BEHAVIOR AGENT — detect anomalies
        behavior_out = self.behavior.process(vision_out, self.memory.get_recent())

        # 5. MEMORY AGENT — store this cycle
        self.memory.store({
            "vision": vision_out,
            "sensor": sensor_out,
            "behavior": behavior_out,
        })

        # 6. FUSION AGENT — Gemini-powered threat reasoning
        fusion_out = await self.fusion.process(
            vision=vision_out,
            sensor=sensor_out,
            behavior=behavior_out,
            memory=self.memory.get_recent(),
        )

        # 7. DECISION AGENT — map threat to action
        decision_out = self.decision.process(fusion_out)

        # 8. RESPONSE AGENT — generate alert message
        alert = self.response.process(decision_out, vision_out)

        # ── Update state ──────────────────────────────────────────────────
        self.frames_processed += 1
        cycle_ms = round((time.time() - cycle_start) * 1000, 1)

        self.latest_event = {
            "timestamp": get_timestamp(),
            "cycle_ms": cycle_ms,
            "vision": vision_out,
            "sensor": sensor_out,
            "behavior": behavior_out,
            "fusion": fusion_out,
            "decision": decision_out,
            "alert": alert,
        }

        # Store alerts (high/critical only)
        if alert and alert.get("threat_level") in ("high", "critical"):
            self.alerts.append(alert)
            self.alerts = self.alerts[-100:]  # Keep last 100
            logger.warning(
                "🔔 ALERT [%s]: %s",
                alert["threat_level"].upper(),
                alert["title"],
            )

        # Broadcast to all connected dashboards
        await self._broadcast(self.latest_event)

    # ── WebSocket Broadcasting ───────────────────────────────────────────

    async def _broadcast(self, event: dict):
        """Send event to all connected WebSocket clients."""
        if not self.websocket_clients:
            return

        message = json.dumps(event, default=str)
        dead = set()

        for ws in self.websocket_clients:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        self.websocket_clients -= dead

    # ── Status ───────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Return current system status for the /api/status endpoint."""
        uptime = time.time() - self.start_time if self.start_time else 0

        agents = {
            "vision": {"name": "Vision Agent", "status": "active"},
            "sensor": {"name": "Sensor Agent", "status": "active"},
            "behavior": {"name": "Behavior Agent", "status": "active"},
            "memory": {"name": "Memory Agent", "status": "active"},
            "fusion": {
                "name": "Fusion Agent (Gemini)",
                "status": "active" if self.fusion.model else "fallback",
            },
            "decision": {"name": "Decision Agent", "status": "active"},
            "response": {"name": "Response Agent", "status": "active"},
        }

        last_threat = "low"
        if self.latest_event:
            last_threat = self.latest_event.get("fusion", {}).get("overall_threat", "low")

        return {
            "pipeline_running": self.running,
            "agents_active": 7,
            "total_agents": 7,
            "uptime_seconds": round(uptime, 1),
            "frames_processed": self.frames_processed,
            "alerts_generated": len(self.alerts),
            "last_threat_level": last_threat,
            "agent_statuses": agents,
            "gemini_connected": self.fusion.model is not None,
            "video_source": self.video.source,
        }
