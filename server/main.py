"""
NeuralGuard — FastAPI Application Entry Point.

Starts the security pipeline on boot and exposes REST + WebSocket APIs.
In production, also serves the React dashboard from dashboard/dist/.

Usage:
    python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

# Path to the React dashboard build output
DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard" / "dist"

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
    logger.info("  📂 Dashboard: %s", "Serving from dist/" if DASHBOARD_DIR.exists() else "Not built (API only)")
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


# ── Health ────────────────────────────────────────────────────────────────────

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


# ── Static Dashboard (production) ────────────────────────────────────────────
# Mount the built React app AFTER all API/WS routes so they take priority.

if DASHBOARD_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=DASHBOARD_DIR / "assets"), name="assets")

    # Serve root → index.html
    @app.get("/", tags=["Dashboard"])
    async def serve_dashboard():
        return FileResponse(DASHBOARD_DIR / "index.html")

    # Catch-all for SPA client-side routing (must be last)
    @app.get("/{full_path:path}", tags=["Dashboard"])
    async def serve_spa(full_path: str):
        """Serve index.html for any path not matched by API routes."""
        file_path = DASHBOARD_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(DASHBOARD_DIR / "index.html")
else:
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "system": "NeuralGuard",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
        }
