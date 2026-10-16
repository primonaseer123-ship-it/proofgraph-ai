from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class GroundedSnippetDTO(BaseModel):
    artifact_id: str
    raw_snippet: str
    byte_start: Optional[int] = None
    byte_end: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None

class EvidenceItemResponse(BaseModel):
    id: str
    source_id: str
    skill_slug: str
    skill_name: Optional[str] = None
    title: str
    raw_snippet: str
    byte_start: Optional[int] = None
    byte_end: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    evidence_date: Optional[str] = None
    directness_score: float
    confidence_score: float
    strength_score: float
    verification_status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EvidenceSourceResponse(BaseModel):
    id: str
    user_id: str
    source_type: str
    uri: str
    file_sha256: str
    original_name: str
    byte_size: int
    metadata_json: Dict[str, Any]
    created_at: datetime
    evidence_items: List[EvidenceItemResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class ManualEvidenceInput(BaseModel):
    title: str
    source_type: str = Field(default="project_report", description="project_report | github_repo | transcript | certificate | manual")
    raw_text: str
    evidence_date: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
