"""
Async frame queue — decouples frame ingestion from processing.
"""

import asyncio
from collections import deque


class FrameQueue:
    """
    Thread-safe async queue with bounded size.
    Drops oldest frames when full to maintain real-time processing.
    """

    def __init__(self, maxsize: int = 30):
        self.queue: deque = deque(maxlen=maxsize)
        self._event = asyncio.Event()

    async def put(self, frame_data):
        """Add a frame to the queue (drops oldest if full)."""
        self.queue.append(frame_data)
        self._event.set()

    async def get(self):
        """Get the next frame, waiting if empty."""
        while not self.queue:
            self._event.clear()
            await self._event.wait()
        return self.queue.popleft()

    @property
    def size(self) -> int:
        return len(self.queue)

    @property
    def empty(self) -> bool:
        return len(self.queue) == 0
