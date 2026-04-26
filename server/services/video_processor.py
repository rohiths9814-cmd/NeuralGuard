"""
Video Processor — Connects to RTSP streams or generates mock frames.

In production: captures frames from RTSP via OpenCV.
In demo mode: generates synthetic frames so the system runs without hardware.
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Graceful OpenCV import
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.info("OpenCV not installed — using synthetic frame generation")


class VideoProcessor:
    """
    Abstracts video input. Supports:
      • RTSP streams
      • Local video files
      • Mock frame generation (default)
    """

    def __init__(self, source: str = "mock"):
        self.source = source
        self.cap = None
        self.frame_count = 0
        self.width = 640
        self.height = 480

        # Try opening a real video source
        if source != "mock" and CV2_AVAILABLE:
            self.cap = cv2.VideoCapture(source)
            if self.cap.isOpened():
                self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                logger.info("Video source opened: %s (%dx%d)", source, self.width, self.height)
            else:
                logger.warning("Failed to open video source: %s — falling back to mock", source)
                self.cap = None

    async def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the next frame from the video source.

        Returns:
            np.ndarray of shape (H, W, 3) in BGR format, or None on failure.
        """
        if self.cap is not None:
            return self._read_real_frame()
        return self._generate_mock_frame()

    def _read_real_frame(self) -> Optional[np.ndarray]:
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
            return frame
        # Loop video file
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return None

    def _generate_mock_frame(self) -> np.ndarray:
        """Generate a dark synthetic frame that simulates a CCTV view."""
        self.frame_count += 1
        # Dark frame with subtle noise (mimics low-light CCTV)
        frame = np.random.randint(5, 35, (self.height, self.width, 3), dtype=np.uint8)
        return frame

    def release(self):
        """Release the video capture resource."""
        if self.cap:
            self.cap.release()
            logger.info("Video source released")

    @property
    def is_real(self) -> bool:
        return self.cap is not None
