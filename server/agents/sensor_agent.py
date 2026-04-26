"""
Sensor Agent — Simulates IoT environmental sensor data.

Generates temperature, humidity, smoke, and noise readings with
configurable anomaly injection for demo scenarios.
"""

import random
import logging
from server.utils.helpers import get_timestamp

logger = logging.getLogger(__name__)


class SensorAgent:
    """
    Reads (or simulates) IoT sensor data and flags environmental anomalies.
    In production, this would connect to real MQTT / sensor APIs.
    """

    def __init__(self):
        self.name = "sensor"
        self.read_count = 0

        # Normal operating ranges
        self.normal_temp = (18.0, 28.0)
        self.normal_humidity = (30.0, 60.0)
        self.normal_smoke = (0.0, 0.1)
        self.normal_noise = (0.1, 0.4)

    def process(self) -> dict:
        """
        Generate a sensor reading with occasional anomalies (~12% chance).

        Returns:
            dict matching SensorOutput schema.
        """
        self.read_count += 1
        anomalies = []

        # Decide if this cycle has an anomaly
        has_anomaly = random.random() < 0.12

        if has_anomaly:
            anomaly_type = random.choice(["temperature", "smoke", "noise"])
        else:
            anomaly_type = None

        # Temperature
        if anomaly_type == "temperature":
            temperature = round(random.uniform(55.0, 85.0), 1)
            anomalies.append("high_temperature")
        else:
            temperature = round(random.uniform(*self.normal_temp), 1)

        # Humidity
        humidity = round(random.uniform(*self.normal_humidity), 1)

        # Smoke level
        if anomaly_type == "smoke":
            smoke_level = round(random.uniform(0.6, 0.95), 3)
            anomalies.append("smoke_detected")
        else:
            smoke_level = round(random.uniform(*self.normal_smoke), 3)

        # Noise level
        if anomaly_type == "noise":
            noise_level = round(random.uniform(0.7, 1.0), 3)
            anomalies.append("loud_noise")
        else:
            noise_level = round(random.uniform(*self.normal_noise), 3)

        # Assess risk
        risk = self._assess_risk(temperature, smoke_level, noise_level, anomalies)

        return {
            "timestamp": get_timestamp(),
            "temperature": temperature,
            "humidity": humidity,
            "smoke_level": smoke_level,
            "noise_level": noise_level,
            "anomalies": anomalies,
            "risk_level": risk,
        }

    @staticmethod
    def _assess_risk(temp: float, smoke: float, noise: float, anomalies: list) -> str:
        """Combine sensor values into a single risk level."""
        if "smoke_detected" in anomalies or temp > 70:
            return "critical"
        if "high_temperature" in anomalies or "loud_noise" in anomalies:
            return "high"
        if smoke > 0.2 or noise > 0.6 or temp > 35:
            return "moderate"
        return "low"
