from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class OpportunityRequirementDTO(BaseModel):
    skill_slug: str
    skill_name: Optional[str] = None
    minimum_proficiency: str
    is_mandatory: bool
    matched: bool = False
    evidence_status: str = "UNSUPPORTED"
    supporting_evidence_ids: List[str] = Field(default_factory=list)

class OpportunityResponse(BaseModel):
    id: str
    title: str
    organization: str
    opportunity_type: str
    location: str
    external_url: Optional[str] = None
    deadline: Optional[str] = None
    description: str
    requirements: List[OpportunityRequirementDTO] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class OpportunityMatchDTO(BaseModel):
    opportunity_id: str
    title: str
    organization: str
    opportunity_type: str
    location: str
    external_url: Optional[str] = None
    match_percentage: float
    matched_mandatory_count: int
    total_mandatory_count: int
    requirements_breakdown: List[OpportunityRequirementDTO]
    missing_unsupported_skills: List[str]
    advisory_notice: str = "This match evaluates evidence alignment only and does not predict admission or hiring."
