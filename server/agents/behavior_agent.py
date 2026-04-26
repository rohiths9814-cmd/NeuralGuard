"""
Behavior Agent — Compares current observations against historical patterns
to detect anomalous behavior (sudden crowd surges, unusual motion, etc.).
"""

import logging
from typing import List, Dict, Any
from server.utils.helpers import get_timestamp, clamp

logger = logging.getLogger(__name__)


class BehaviorAgent:
    """
    Analyses temporal patterns by comparing the current vision data
    with recent history to detect deviations from normal behavior.
    """

    def __init__(self):
        self.name = "behavior"
        # Rolling averages for baseline comparison
        self.avg_people = 5.0
        self.avg_motion = 0.2
        self.alpha = 0.15  # Exponential moving average decay

    def process(self, vision_output: dict, recent_memory: List[Dict[str, Any]]) -> dict:
        """
        Compare current vision data against historical baseline.

        Args:
            vision_output: Latest output from VisionAgent.
            recent_memory: Last N events from MemoryAgent.

        Returns:
            dict matching BehaviorOutput schema.
        """
        people = vision_output.get("people_count", 0)
        motion = vision_output.get("motion_intensity", 0.0)

        # Compute deviation from rolling baseline
        people_dev = abs(people - self.avg_people) / max(self.avg_people, 1)
        motion_dev = abs(motion - self.avg_motion) / max(self.avg_motion, 0.01)
        deviation_score = clamp((people_dev * 0.6 + motion_dev * 0.4) / 3.0)

        # Detect anomaly
        is_anomalous = deviation_score > 0.45
        anomaly_type = None
        pattern = "normal activity"

        if is_anomalous:
            if people_dev > motion_dev:
                anomaly_type = "crowd_surge"
                pattern = f"Sudden crowd increase: {people} people (baseline: {self.avg_people:.0f})"
            else:
                anomaly_type = "unusual_motion"
                pattern = f"Abnormal motion: {motion:.2f} (baseline: {self.avg_motion:.2f})"
        else:
            pattern = f"Normal: {people} people, motion {motion:.2f}"

        # Update rolling averages (exponential moving average)
        self.avg_people = self.alpha * people + (1 - self.alpha) * self.avg_people
        self.avg_motion = self.alpha * motion + (1 - self.alpha) * self.avg_motion

        # Assess risk
        risk = self._assess_risk(deviation_score, is_anomalous, recent_memory)

        return {
            "timestamp": get_timestamp(),
            "is_anomalous": is_anomalous,
            "anomaly_type": anomaly_type,
            "deviation_score": round(deviation_score, 3),
            "pattern_description": pattern,
            "risk_level": risk,
        }

    @staticmethod
    def _assess_risk(deviation: float, anomalous: bool, memory: list) -> str:
        """Factor in recent threat escalation from memory."""
        # Check if recent history shows escalating threats
        recent_high = sum(
            1 for m in memory[-5:]
            if m.get("threat_level") in ("high", "critical")
        )

        if anomalous and (deviation > 0.7 or recent_high >= 3):
            return "critical"
        if anomalous:
            return "high"
        if deviation > 0.3:
            return "moderate"
        return "low"
