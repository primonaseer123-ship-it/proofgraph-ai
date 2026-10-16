from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ContradictionResponse(BaseModel):
    id: str
    user_id: str
    claim_id: Optional[str] = None
    claim_text: Optional[str] = None
    contradiction_type: str # EXAGGERATION, TIMELINE_OVERLAP, CONFLICTING_METRIC, GHOST_CLAIM
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    explanation: str
    conflicting_evidence_ids: List[str]
    is_resolved: bool
    resolution_note: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ContradictionAcknowledgeRequest(BaseModel):
    resolution_note: str = Field(description="Explanation or adjustment provided by user")
