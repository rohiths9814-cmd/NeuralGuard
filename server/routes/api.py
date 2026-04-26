"""
API routes for the NeuralGuard backend.

Endpoints:
  GET  /api/status   → System status + agent health
  GET  /api/alerts   → Recent alert history
  GET  /api/latest   → Latest pipeline event
  GET  /api/stream   → Video stream info
  GET  /api/memory   → Memory agent summary
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["NeuralGuard API"])

# The pipeline instance is injected at app startup via `set_pipeline()`
_pipeline = None


def set_pipeline(pipeline):
    """Inject the pipeline instance into the router."""
    global _pipeline
    _pipeline = pipeline


@router.get("/status")
async def get_status():
    """System status: uptime, agent health, alert counts."""
    return _pipeline.get_status()


@router.get("/alerts")
async def get_alerts(limit: int = 50):
    """Retrieve recent alerts, newest first."""
    alerts = list(reversed(_pipeline.alerts[-limit:]))
    return {"count": len(alerts), "alerts": alerts}


@router.get("/latest")
async def get_latest():
    """Get the latest pipeline processing event."""
    if _pipeline.latest_event:
        return _pipeline.latest_event
    return {"message": "No events processed yet. Pipeline is starting up."}


@router.get("/stream")
async def get_stream_info():
    """Video stream metadata."""
    return {
        "source": _pipeline.video.source,
        "is_real": _pipeline.video.is_real,
        "frames_processed": _pipeline.frames_processed,
        "pipeline_running": _pipeline.running,
    }


@router.get("/memory")
async def get_memory():
    """Memory agent state summary."""
    return _pipeline.memory.get_summary()
