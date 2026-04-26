"""
Pydantic schemas for all agent inputs/outputs.
Every agent accepts and returns structured JSON — these models enforce that contract.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class ThreatLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(str, Enum):
    LOG = "log"
    MONITOR = "monitor"
    ALERT = "alert"
    LOCKDOWN = "lockdown"
    EVACUATE = "evacuate"


# ─── Vision Agent ─────────────────────────────────────────────────────────────

class Detection(BaseModel):
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: List[float] = Field(description="[x1, y1, x2, y2]")


class VisionOutput(BaseModel):
    frame_id: str
    timestamp: str
    camera_id: str = "cam_01"
    people_count: int = Field(ge=0)
    motion_intensity: float = Field(ge=0.0, le=1.0)
    detections: List[Detection] = []
    risk_level: ThreatLevel
    confidence: float = Field(ge=0.0, le=1.0)


# ─── Sensor Agent ─────────────────────────────────────────────────────────────

class SensorOutput(BaseModel):
    timestamp: str
    temperature: float = Field(description="Celsius")
    humidity: float = Field(ge=0.0, le=100.0)
    smoke_level: float = Field(ge=0.0, le=1.0)
    noise_level: float = Field(ge=0.0, le=1.0)
    anomalies: List[str] = []
    risk_level: ThreatLevel


# ─── Behavior Agent ──────────────────────────────────────────────────────────

class BehaviorOutput(BaseModel):
    timestamp: str
    is_anomalous: bool
    anomaly_type: Optional[str] = None
    deviation_score: float = Field(ge=0.0, le=1.0)
    pattern_description: str
    risk_level: ThreatLevel


# ─── Memory Agent ─────────────────────────────────────────────────────────────

class MemoryEntry(BaseModel):
    timestamp: str
    event_type: str
    data: Dict[str, Any]
    threat_level: ThreatLevel


# ─── Fusion Agent ─────────────────────────────────────────────────────────────

class FusionOutput(BaseModel):
    timestamp: str
    overall_threat: ThreatLevel
    confidence: float = Field(ge=0.0, le=1.0)
    explanation: str
    contributing_factors: List[str] = []
    gemini_analysis: Optional[str] = None


# ─── Decision Agent ──────────────────────────────────────────────────────────

class DecisionOutput(BaseModel):
    timestamp: str
    threat_level: ThreatLevel
    action: ActionType
    priority: int = Field(ge=1, le=5)
    requires_human: bool = False
    details: str


# ─── Response Agent ──────────────────────────────────────────────────────────

class AlertMessage(BaseModel):
    id: str
    timestamp: str
    threat_level: ThreatLevel
    title: str
    message: str
    action: str
    camera_id: str
    people_count: int = 0
    confidence: float = 0.0


# ─── System Status ───────────────────────────────────────────────────────────

class AgentInfo(BaseModel):
    name: str
    status: str = "active"
    last_run: Optional[str] = None


class SystemStatus(BaseModel):
    pipeline_running: bool
    agents_active: int
    total_agents: int = 7
    uptime_seconds: float
    frames_processed: int
    alerts_generated: int
    last_threat_level: ThreatLevel = ThreatLevel.LOW
    agent_statuses: Dict[str, AgentInfo] = {}
