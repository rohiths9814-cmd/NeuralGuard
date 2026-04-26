"""
Response Agent — Generates human-readable alert messages
from Decision Agent outputs.
"""

import logging
from server.utils.helpers import generate_id, get_timestamp

logger = logging.getLogger(__name__)


# ── Alert Templates ──────────────────────────────────────────────────────────

TEMPLATES = {
    "log": {
        "title": "📊 Routine Log",
        "template": "Normal activity recorded. {people} people detected, motion at {motion:.0%}.",
    },
    "monitor": {
        "title": "👁️ Elevated Monitoring",
        "template": "Increased activity detected. {people} people, motion {motion:.0%}. Auto-monitoring enabled.",
    },
    "alert": {
        "title": "⚠️ Security Alert",
        "template": "ALERT: {explanation} {people} people counted, motion at {motion:.0%}. Immediate review required.",
    },
    "lockdown": {
        "title": "🚨 CRITICAL — Emergency Protocol",
        "template": "EMERGENCY: {explanation} {people} people detected with {motion:.0%} motion. Lockdown initiated.",
    },
    "evacuate": {
        "title": "🔴 EVACUATION ORDER",
        "template": "EVACUATE: {explanation} All personnel must exit immediately.",
    },
}


class ResponseAgent:
    """
    Generates structured alert messages for the dashboard and
    notification systems.
    """

    def __init__(self):
        self.name = "response"
        self.alert_count = 0

    def process(self, decision_output: dict, vision_output: dict) -> dict:
        """
        Generate an alert message from a decision + vision context.

        Args:
            decision_output: Output from DecisionAgent.
            vision_output: Output from VisionAgent (for context).

        Returns:
            dict matching AlertMessage schema, or None for log-level events.
        """
        action = decision_output.get("action", "log")
        threat = decision_output.get("threat_level", "low")

        # Only generate alerts for moderate and above
        if action == "log":
            return None

        self.alert_count += 1
        template_data = TEMPLATES.get(action, TEMPLATES["monitor"])

        people = vision_output.get("people_count", 0)
        motion = vision_output.get("motion_intensity", 0.0)
        explanation = decision_output.get("details", "")

        message = template_data["template"].format(
            people=people,
            motion=motion,
            explanation=explanation,
        )

        return {
            "id": generate_id(),
            "timestamp": get_timestamp(),
            "threat_level": threat,
            "title": template_data["title"],
            "message": message,
            "action": action,
            "camera_id": vision_output.get("camera_id", "cam_01"),
            "people_count": people,
            "confidence": vision_output.get("confidence", 0.0),
        }
