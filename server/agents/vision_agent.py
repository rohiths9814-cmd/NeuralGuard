"""
Vision Agent — Detects people, objects, and motion in video frames.

Supports two modes:
  • Real mode: Uses YOLOv8 via the `ultralytics` package.
  • Mock mode: Generates realistic synthetic detections for demo/testing.
"""

import random
import logging
from typing import Optional

import numpy as np

from server.utils.helpers import get_timestamp, clamp

logger = logging.getLogger(__name__)

# Try importing YOLO — gracefully degrade to mock if unavailable
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logger.info("ultralytics not installed — Vision Agent will use mock detections")


class VisionAgent:
    """
    Processes video frames to detect people count, motion intensity,
    and individual object detections. Returns a structured risk assessment.
    """

    def __init__(self, model_path: str = "yolov8n.pt"):
        self.name = "vision"
        self.model = None
        self.prev_frame: Optional[np.ndarray] = None
        self.frame_count = 0

        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_path)
                logger.info("YOLOv8 model loaded: %s", model_path)
            except Exception as exc:
                logger.warning("Failed to load YOLO model: %s", exc)

    # ── Public API ────────────────────────────────────────────────────────

    def process(self, frame: Optional[np.ndarray] = None, camera_id: str = "cam_01") -> dict:
        """
        Process a single video frame.

        Args:
            frame: BGR numpy array (H, W, 3), or None for mock mode.
            camera_id: Identifier for the camera source.

        Returns:
            dict matching VisionOutput schema.
        """
        self.frame_count += 1

        if frame is not None and self.model is not None:
            return self._process_real(frame, camera_id)
        return self._process_mock(camera_id)

    # ── Real YOLO Processing ─────────────────────────────────────────────

    def _process_real(self, frame: np.ndarray, camera_id: str) -> dict:
        results = self.model(frame, verbose=False)

        detections = []
        people_count = 0

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = result.names[cls_id]

                if class_name == "person":
                    people_count += 1

                detections.append({
                    "class_name": class_name,
                    "confidence": round(conf, 3),
                    "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                })

        motion = self._calculate_motion(frame)
        risk = self._assess_risk(people_count, motion)
        avg_conf = sum(d["confidence"] for d in detections) / max(len(detections), 1)

        return {
            "frame_id": f"frame_{self.frame_count}",
            "timestamp": get_timestamp(),
            "camera_id": camera_id,
            "people_count": people_count,
            "motion_intensity": round(motion, 3),
            "detections": detections,
            "risk_level": risk,
            "confidence": round(avg_conf, 3),
        }

    # ── Mock Processing ──────────────────────────────────────────────────

    def _process_mock(self, camera_id: str) -> dict:
        """Generate realistic synthetic data for demo without hardware."""
        # Occasional crowd surge (15% chance)
        spike = random.random() < 0.15
        base = random.randint(2, 8)
        people_count = base + (random.randint(10, 25) if spike else 0)

        motion = clamp(random.uniform(0.1, 0.4) + (0.5 if spike else 0))
        risk = self._assess_risk(people_count, motion)

        detections = [
            {
                "class_name": "person",
                "confidence": round(random.uniform(0.72, 0.98), 3),
                "bbox": [
                    round(random.uniform(10, 500), 1),
                    round(random.uniform(10, 350), 1),
                    round(random.uniform(60, 200), 1),
                    round(random.uniform(60, 200), 1),
                ],
            }
            for _ in range(people_count)
        ]

        return {
            "frame_id": f"frame_{self.frame_count}",
            "timestamp": get_timestamp(),
            "camera_id": camera_id,
            "people_count": people_count,
            "motion_intensity": round(motion, 3),
            "detections": detections,
            "risk_level": risk,
            "confidence": round(random.uniform(0.75, 0.97), 3),
        }

    # ── Internal Helpers ─────────────────────────────────────────────────

    def _calculate_motion(self, frame: np.ndarray) -> float:
        """Frame-differencing motion estimator."""
        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.prev_frame is None:
                self.prev_frame = gray
                return 0.0
            diff = cv2.absdiff(self.prev_frame, gray)
            self.prev_frame = gray
            return float(np.mean(diff) / 255.0)
        except Exception:
            return random.uniform(0.05, 0.3)

    @staticmethod
    def _assess_risk(people_count: int, motion: float) -> str:
        """Rule-based risk assessment from people count + motion."""
        score = (people_count / 30) * 0.6 + motion * 0.4
        if score > 0.7:
            return "critical"
        if score > 0.5:
            return "high"
        if score > 0.3:
            return "moderate"
        return "low"
