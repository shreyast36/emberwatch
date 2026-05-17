"""Core data types shared across AlignGuard and the sample system."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class SignalType(str, Enum):
    GAMING = "gaming"
    DECEPTIVE_REASONING = "deceptive_reasoning"
    CANARY_FAIL = "canary_fail"
    DRIFT = "drift"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolCall(BaseModel):
    tool_name: str
    args: dict
    result: str


class AgentTrace(BaseModel):
    agent_name: str
    input: str
    reasoning: str
    output: str
    tools_used: list[ToolCall] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionTrace(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    query: str
    traces: list[AgentTrace]
    final_response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AlignmentSignal(BaseModel):
    signal_type: SignalType
    agent_name: str
    # 0.0 = fully misaligned (bad), 1.0 = fully aligned (good)
    score: float
    evidence: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Alert(BaseModel):
    risk_level: RiskLevel
    signals: list[AlignmentSignal]
    summary: str
    session_id: str
    recommended_actions: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
