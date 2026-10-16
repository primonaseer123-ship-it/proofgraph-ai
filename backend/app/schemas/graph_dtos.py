from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ReactFlowPosition(BaseModel):
    x: float
    y: float

class ReactFlowNode(BaseModel):
    id: str
    type: str = "customNode" # userNode, claimNode, skillNode, evidenceNode, sourceNode
    position: ReactFlowPosition
    data: Dict[str, Any]

class ReactFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: bool = False
    style: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

class GraphResponse(BaseModel):
    nodes: List[ReactFlowNode]
    edges: List[ReactFlowEdge]
    stats: Dict[str, Any]

class GrowthTimelineStage(BaseModel):
    period: str
    title: str
    skills_demonstrated: List[str]
    evidence_count: int
    complexity_level: str
    narrative: str

class GrowthTrajectoryResponse(BaseModel):
    user_id: str
    stages: List[GrowthTimelineStage]
    learning_velocity: str
    recommended_focus_areas: List[str]

class ApplicationGenerateRequest(BaseModel):
    target_role: str = "Junior Software Engineer"
    target_company: str = "Systems Limited"
    document_type: str = Field(default="resume", description="resume | statement | cover_letter")

class GroundedCitation(BaseModel):
    claim_text: str
    skill_slug: str
    evidence_id: str
    source_name: str
    verification_status: str

class ApplicationGenerateResponse(BaseModel):
    document_type: str
    target_role: str
    target_company: str
    markdown_content: str
    grounded_citations: List[GroundedCitation]
    verified_skills_used: List[str]
    unsupported_claims_omitted: List[str]
