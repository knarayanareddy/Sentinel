from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel
import uuid
import time


class ActionStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FROZEN = "frozen"
    RESUMED = "resumed"
    ABORTED = "aborted"


class EventType(str, Enum):
    AGENT_PLAN = "AGENT_PLAN"
    ACTION_PROPOSED = "ACTION_PROPOSED"
    RETRIEVAL_PASS = "RETRIEVAL_PASS"
    TOOL_CALLED = "TOOL_CALLED"
    DRIFT_SCORED = "DRIFT_SCORED"
    MAARS_PROBE = "MAARS_PROBE"
    CITATION_CHECKED = "CITATION_CHECKED"
    ACTION_EXECUTED = "ACTION_EXECUTED"
    ACTION_FROZEN = "ACTION_FROZEN"
    INCIDENT_SEALED = "INCIDENT_SEALED"
    OPERATOR_DECISION = "OPERATOR_DECISION"
    ERROR = "ERROR"


@dataclass
class RetrievalCitation:
    document: str
    clause: str
    excerpt: str
    retrieval_score: Optional[float] = None


@dataclass
class Action:
    action_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    tool_name: str = ""
    parameters: dict = field(default_factory=dict)
    is_irreversible: bool = False
    citations: list[RetrievalCitation] = field(default_factory=list)
    status: ActionStatus = ActionStatus.PENDING
    created_at: float = field(default_factory=time.time)

    drift_score: Optional[float] = None
    drift_model: Optional[str] = None
    maars_verdict: Optional[str] = None
    maars_confidence: Optional[int] = None
    maars_reasoning: Optional[str] = None
    maars_model: Optional[str] = None
    citation_score: Optional[float] = None
    citation_model: Optional[str] = None
    freeze_reason: Optional[str] = None
    resolved_at: Optional[float] = None
    operator_decision: Optional[str] = None


@dataclass
class SentinelEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.ERROR
    timestamp: float = field(default_factory=time.time)
    payload: Any = None
    action_id: Optional[str] = None


class DecisionRequest(BaseModel):
    """Request model for the /api/decide endpoint."""
    action_id: str
    approved: bool


class RunRequest(BaseModel):
    """Request model for the /api/run endpoint."""
    scenario: str = "breach"
