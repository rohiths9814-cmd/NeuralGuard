"""
Shared helper utilities used across the NeuralGuard backend.
"""

import uuid
from datetime import datetime, timezone


def generate_id() -> str:
    """Generate a short unique ID for events/alerts."""
    return str(uuid.uuid4())[:8]


def get_timestamp() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min and max bounds."""
    return max(min_val, min(max_val, value))


def threat_to_score(threat: str) -> float:
    """Convert a threat level string to a numeric score (0-1)."""
    mapping = {"low": 0.1, "moderate": 0.4, "high": 0.7, "critical": 1.0}
    return mapping.get(threat, 0.0)


def score_to_threat(score: float) -> str:
    """Convert a numeric score to a threat level string."""
    if score >= 0.75:
        return "critical"
    if score >= 0.5:
        return "high"
    if score >= 0.25:
        return "moderate"
    return "low"
