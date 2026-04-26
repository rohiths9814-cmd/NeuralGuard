"""
NeuralGuard — FastAPI Application Entry Point.

Starts the security pipeline on boot and exposes REST + WebSocket APIs.

Usage:
    python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from server.pipeline import SecurityPipeline
from server.routes.api import router as api_router, set_pipeline

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("neuralguard")

# ── Pipeline singleton ────────────────────────────────────────────────────────

pipeline = SecurityPipeline()


# ── App Lifespan ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start pipeline on boot, stop on shutdown."""
    set_pipeline(pipeline)
    task = asyncio.create_task(pipeline.start())
    logger.info("═══════════════════════════════════════════════")
    logger.info("  🛡️  NeuralGuard v1.0 — System Online")
    logger.info("  📡 API:       http://0.0.0.0:%s", os.getenv("PORT", "8000"))
    logger.info("  🔌 WebSocket: ws://0.0.0.0:%s/ws/dashboard", os.getenv("PORT", "8000"))
    logger.info("  🤖 Gemini:    %s", "Connected" if pipeline.fusion.model else "Offline (rule-based)")
    logger.info("  📹 Video:     %s", pipeline.video.source)
    logger.info("═══════════════════════════════════════════════")
    yield
    await pipeline.stop()
    task.cancel()


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="NeuralGuard",
    description="AI-Powered Autonomous Security System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow dashboard on any port during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routes
app.include_router(api_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "system": "NeuralGuard",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "pipeline": pipeline.running}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    Real-time event stream for the dashboard.
    Each pipeline cycle broadcasts the full event to all connected clients.
    """
    await websocket.accept()
    pipeline.websocket_clients.add(websocket)
    logger.info("Dashboard client connected (%d total)", len(pipeline.websocket_clients))

    try:
        while True:
            # Keep connection alive — client can send pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        pipeline.websocket_clients.discard(websocket)
        logger.info("Dashboard client disconnected (%d remaining)", len(pipeline.websocket_clients))
