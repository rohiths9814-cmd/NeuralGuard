"""
Fusion Agent — Integrates Google Gemini API for intelligent threat reasoning.

Combines outputs from all other agents and uses LLM reasoning to produce
a holistic threat assessment. Falls back to rule-based fusion if the
Gemini API is unavailable.
"""

import os
import json
import asyncio
import logging
from server.utils.helpers import get_timestamp, score_to_threat, threat_to_score

logger = logging.getLogger(__name__)

# Try importing Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.info("google-generativeai not installed — using rule-based fusion")


class FusionAgent:
    """
    The brain of NeuralGuard. Combines all agent outputs and uses
    Gemini to produce a final, explainable threat assessment.
    """

    def __init__(self):
        self.name = "fusion"
        self.model = None
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.call_count = 0

        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                logger.info("Gemini API configured (model: gemini-2.0-flash)")
            except Exception as exc:
                logger.warning("Gemini configuration failed: %s", exc)

    async def process(
        self,
        vision: dict,
        sensor: dict,
        behavior: dict,
        memory: list,
    ) -> dict:
        """
        Fuse all agent outputs into a single threat assessment.

        Uses Gemini API if available, otherwise falls back to
        weighted rule-based scoring.
        """
        self.call_count += 1

        if self.model:
            return await self._gemini_fusion(vision, sensor, behavior, memory)
        return self._rule_based_fusion(vision, sensor, behavior)

    # ── Gemini-Powered Fusion ────────────────────────────────────────────

    async def _gemini_fusion(
        self, vision: dict, sensor: dict, behavior: dict, memory: list
    ) -> dict:
        prompt = self._build_prompt(vision, sensor, behavior, memory)

        try:
            # Run the blocking Gemini call in a thread to keep async
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            text = response.text.strip()

            # Strip markdown fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                text = text.rsplit("```", 1)[0].strip()

            result = json.loads(text)

            # Validate required fields
            return {
                "timestamp": get_timestamp(),
                "overall_threat": result.get("overall_threat", "low"),
                "confidence": round(float(result.get("confidence", 0.5)), 3),
                "explanation": result.get("explanation", "No explanation provided"),
                "contributing_factors": result.get("contributing_factors", []),
                "gemini_analysis": text,
            }

        except Exception as exc:
            logger.warning("Gemini fusion failed, falling back to rules: %s", exc)
            return self._rule_based_fusion(vision, sensor, behavior)

    # ── Rule-Based Fallback ──────────────────────────────────────────────

    def _rule_based_fusion(self, vision: dict, sensor: dict, behavior: dict) -> dict:
        """Weighted scoring across agent risk levels."""
        weights = {"vision": 0.45, "sensor": 0.25, "behavior": 0.30}

        score = (
            threat_to_score(vision.get("risk_level", "low")) * weights["vision"]
            + threat_to_score(sensor.get("risk_level", "low")) * weights["sensor"]
            + threat_to_score(behavior.get("risk_level", "low")) * weights["behavior"]
        )

        overall_threat = score_to_threat(score)
        factors = []

        if vision.get("people_count", 0) > 15:
            factors.append(f"High crowd density: {vision['people_count']} people")
        if vision.get("motion_intensity", 0) > 0.6:
            factors.append(f"Elevated motion: {vision['motion_intensity']:.2f}")
        if sensor.get("anomalies"):
            factors.append(f"Sensor anomalies: {', '.join(sensor['anomalies'])}")
        if behavior.get("is_anomalous"):
            factors.append(f"Behavioral anomaly: {behavior.get('anomaly_type', 'unknown')}")

        if not factors:
            factors.append("All systems nominal")

        return {
            "timestamp": get_timestamp(),
            "overall_threat": overall_threat,
            "confidence": round(min(score + 0.3, 1.0), 3),
            "explanation": f"Threat level {overall_threat} based on weighted analysis of {len(factors)} factors.",
            "contributing_factors": factors,
            "gemini_analysis": None,
        }

    # ── Prompt Engineering ───────────────────────────────────────────────

    @staticmethod
    def _build_prompt(vision: dict, sensor: dict, behavior: dict, memory: list) -> str:
        recent_threats = [m.get("threat_level", "low") for m in memory[-5:]]

        return f"""You are an AI security analyst for an autonomous surveillance system called NeuralGuard.
Analyze the following multi-sensor security data and provide a threat assessment.

═══ VISION DATA ═══
• People detected: {vision.get('people_count', 0)}
• Motion intensity: {vision.get('motion_intensity', 0):.3f}
• Vision risk: {vision.get('risk_level', 'low')}
• Confidence: {vision.get('confidence', 0):.3f}

═══ SENSOR DATA ═══
• Temperature: {sensor.get('temperature', 22)}°C
• Humidity: {sensor.get('humidity', 45)}%
• Smoke level: {sensor.get('smoke_level', 0):.3f}
• Noise level: {sensor.get('noise_level', 0):.3f}
• Anomalies: {', '.join(sensor.get('anomalies', [])) or 'None'}
• Sensor risk: {sensor.get('risk_level', 'low')}

═══ BEHAVIOR ANALYSIS ═══
• Anomalous: {behavior.get('is_anomalous', False)}
• Deviation score: {behavior.get('deviation_score', 0):.3f}
• Pattern: {behavior.get('pattern_description', 'N/A')}
• Behavior risk: {behavior.get('risk_level', 'low')}

═══ RECENT THREAT HISTORY ═══
Last 5 threat levels: {recent_threats}

INSTRUCTIONS:
Respond with ONLY a valid JSON object (no markdown, no explanation outside JSON):
{{
    "overall_threat": "low|moderate|high|critical",
    "confidence": <float 0.0 to 1.0>,
    "explanation": "<concise 1-2 sentence threat summary>",
    "contributing_factors": ["<factor1>", "<factor2>"]
}}"""
