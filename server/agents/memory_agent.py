"""
Memory Agent — Short-term event store for the last N minutes.

Provides recent context to other agents so they can reason
about temporal patterns and escalation trends.
"""

import time
import logging
from typing import List, Dict, Any
from collections import deque
from server.utils.helpers import get_timestamp

logger = logging.getLogger(__name__)


class MemoryAgent:
    """
    Maintains a bounded, time-windowed buffer of recent security events.
    Default window: 5 minutes (configurable).
    """

    def __init__(self, window_seconds: int = 300, max_entries: int = 150):
        self.name = "memory"
        self.window = window_seconds
        self.buffer: deque = deque(maxlen=max_entries)
        self.event_count = 0

    def store(self, event_data: Dict[str, Any]) -> dict:
        """
        Store an event in memory with automatic timestamp.

        Args:
            event_data: Combined agent outputs for one processing cycle.

        Returns:
            Confirmation dict with memory stats.
        """
        self.event_count += 1

        # Determine the highest threat level from any agent output
        threat = self._extract_threat(event_data)

        entry = {
            "timestamp": get_timestamp(),
            "epoch": time.time(),
            "event_id": self.event_count,
            "threat_level": threat,
            "data": event_data,
        }

        self.buffer.append(entry)
        self._prune_old()

        return {
            "stored": True,
            "event_id": self.event_count,
            "buffer_size": len(self.buffer),
        }

    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the last N events from memory."""
        self._prune_old()
        return list(self.buffer)[-n:]

    def get_summary(self) -> dict:
        """Return a summary of the current memory state."""
        if not self.buffer:
            return {
                "total_events": 0,
                "window_seconds": self.window,
                "threat_distribution": {},
            }

        threats = {}
        for entry in self.buffer:
            level = entry.get("threat_level", "low")
            threats[level] = threats.get(level, 0) + 1

        return {
            "total_events": len(self.buffer),
            "window_seconds": self.window,
            "threat_distribution": threats,
            "oldest_event": self.buffer[0]["timestamp"],
            "newest_event": self.buffer[-1]["timestamp"],
        }

    def clear(self):
        """Clear all stored events."""
        self.buffer.clear()
        logger.info("Memory cleared")

    # ── Internal ─────────────────────────────────────────────────────────

    def _prune_old(self):
        """Remove events outside the time window."""
        cutoff = time.time() - self.window
        while self.buffer and self.buffer[0].get("epoch", 0) < cutoff:
            self.buffer.popleft()

    @staticmethod
    def _extract_threat(event_data: dict) -> str:
        """Extract the highest threat level from any agent's output."""
        threat_priority = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
        max_threat = "low"

        for key in ("vision", "sensor", "behavior"):
            agent_data = event_data.get(key, {})
            level = agent_data.get("risk_level", "low")
            if threat_priority.get(level, 0) > threat_priority.get(max_threat, 0):
                max_threat = level

        return max_threat
