"""
Decision Agent — Maps threat assessments to concrete security actions.

Implements a priority system and cooldown to prevent alert fatigue.
"""

import time
import logging
from server.utils.helpers import get_timestamp

logger = logging.getLogger(__name__)


# ── Action Mapping ────────────────────────────────────────────────────────────

ACTION_MAP = {
    "low":      {"action": "log",      "priority": 1, "requires_human": False,
                 "details": "Routine monitoring — no action required."},
    "moderate": {"action": "monitor",   "priority": 2, "requires_human": False,
                 "details": "Elevated activity detected — increased monitoring enabled."},
    "high":     {"action": "alert",     "priority": 4, "requires_human": True,
                 "details": "Significant threat detected — security team alerted."},
    "critical": {"action": "lockdown",  "priority": 5, "requires_human": True,
                 "details": "Critical threat — initiating emergency protocols."},
}


class DecisionAgent:
    """
    Takes a FusionOutput and decides what action to take.
    Includes cooldown logic to prevent duplicate alerts.
    """

    def __init__(self, cooldown_seconds: int = 30):
        self.name = "decision"
        self.cooldown = cooldown_seconds
        self.last_alert_time: float = 0
        self.last_alert_level: str = "low"
        self.decision_count = 0

    def process(self, fusion_output: dict) -> dict:
        """
        Map threat level to an action with cooldown enforcement.

        Args:
            fusion_output: Output from FusionAgent.

        Returns:
            dict matching DecisionOutput schema.
        """
        self.decision_count += 1
        threat = fusion_output.get("overall_threat", "low")
        now = time.time()

        # Get base action from map
        base = ACTION_MAP.get(threat, ACTION_MAP["low"]).copy()

        # Cooldown: suppress repeated alerts of same or lower level
        if threat in ("high", "critical"):
            elapsed = now - self.last_alert_time
            if elapsed < self.cooldown and threat == self.last_alert_level:
                # Downgrade to monitoring during cooldown
                base = ACTION_MAP["moderate"].copy()
                base["details"] += f" (alert cooldown: {self.cooldown - elapsed:.0f}s remaining)"
            else:
                self.last_alert_time = now
                self.last_alert_level = threat

        return {
            "timestamp": get_timestamp(),
            "threat_level": threat,
            **base,
        }
