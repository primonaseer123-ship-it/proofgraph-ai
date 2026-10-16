from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ClaimCreate(BaseModel):
    skill_slug: str
    stated_proficiency: str = Field(default="Intermediate", description="Beginner | Intermediate | Advanced | Expert")
    claim_text: str = Field(description="The exact text or assertion made by the user")

class ClaimResponse(BaseModel):
    id: str
    user_id: str
    skill_slug: str
    skill_name: Optional[str] = None
    stated_proficiency: str
    claim_text: str
    claim_type: str # USER_CLAIM, AI_INFERRED, EVIDENCE_SUPPORTED, HUMAN_VERIFIED
    current_status: str # UNSUPPORTED, SELF_REPORTED, AI_INFERRED, PARTIALLY_SUPPORTED, EVIDENCE_SUPPORTED, HUMAN_VERIFIED
    confidence_score: float
    justification_summary: Optional[str] = None
    created_at: datetime
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class ClaimHumanVerifyRequest(BaseModel):
    decision: str = Field(description="APPROVED | REJECTED | AMENDED")
    commentary: str = Field(description="Human verifier rationale or observations")
    amended_proficiency: Optional[str] = None
