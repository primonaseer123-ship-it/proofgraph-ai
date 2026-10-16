from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class VerificationStatusEnum(str, Enum):
    UNSUPPORTED = "UNSUPPORTED"
    SELF_REPORTED = "SELF_REPORTED"
    AI_INFERRED = "AI_INFERRED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"

class EvidenceStrengthTier(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    UNSUPPORTED = "UNSUPPORTED"

class ContradictionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# 1. Collector Output
class IngestedArtifactItem(BaseModel):
    artifact_id: str
    source_type: str # pdf, docx, github_repo, transcript, certificate
    sha256_checksum: str
    original_file_name: str
    byte_size: int
    raw_text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CollectorOutputManifest(BaseModel):
    user_id: str
    artifacts: List[IngestedArtifactItem]
    total_tokens_extracted: int
    warnings: List[str] = Field(default_factory=list)

# 2. Evidence Extractor Output
class GroundedSnippetProvenance(BaseModel):
    artifact_id: str
    start_char_idx: Optional[int] = None
    end_char_idx: Optional[int] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    raw_text: str

class ExtractedEvidenceItemDTO(BaseModel):
    evidence_id: str
    artifact_id: str
    activity_name: str
    demonstrated_behavior: str
    extracted_technologies: List[str]
    evidence_date: Optional[str] = None
    provenance: GroundedSnippetProvenance
    directness_score: float = Field(ge=0.0, le=1.0)
    confidence_score: float = Field(ge=0.0, le=1.0)

class ExtractedEvidenceBatch(BaseModel):
    user_id: str
    evidence_items: List[ExtractedEvidenceItemDTO]

# 3. Skill Mapping Output
class MappedSkillNodeDTO(BaseModel):
    skill_slug: str
    canonical_name: str
    taxonomy_category: str
    taxonomy_path: str
    substantiating_evidence_ids: List[str]
    mapping_confidence: float = Field(ge=0.0, le=1.0)

class SkillMappingResult(BaseModel):
    user_id: str
    mapped_skills: List[MappedSkillNodeDTO]
    unmapped_raw_mentions: List[str] = Field(default_factory=list)

# 4. Verifier Output
class SkillVerificationEvaluationDTO(BaseModel):
    skill_slug: str
    status: VerificationStatusEnum
    strength_tier: EvidenceStrengthTier
    composite_strength_score: float = Field(ge=0.0, le=1.0)
    score_breakdown: Dict[str, float]
    justification_summary: str
    supporting_evidence_ids: List[str]
    recommended_action: str

class VerificationAssessmentReport(BaseModel):
    user_id: str
    evaluations: List[SkillVerificationEvaluationDTO]

# 5. Contradiction Output
class FlaggedContradictionDTO(BaseModel):
    contradiction_id: str
    severity: ContradictionSeverity
    claim_id: Optional[str] = None
    claim_text: Optional[str] = None
    conflicting_evidence_ids: List[str]
    inconsistency_type: str # EXAGGERATION, TIMELINE_OVERLAP, CONFLICTING_METRIC, GHOST_CLAIM
    formal_explanation: str
    recommended_remedy: str

class ContradictionAuditReport(BaseModel):
    user_id: str
    contradictions_found: List[FlaggedContradictionDTO]
    overall_profile_consistency_score: float = Field(ge=0.0, le=1.0)

# 6. Growth Output
class TrajectoryStageDTO(BaseModel):
    timestamp_period: str
    focus_domain: str
    acquired_skills: List[str]
    project_complexity_score: float = Field(ge=0.0, le=1.0)
    narrative: str

class GrowthTrajectoryReport(BaseModel):
    user_id: str
    chronological_stages: List[TrajectoryStageDTO]
    learning_patterns: List[str]
    dormant_skills: List[str]
    velocity_assessment: str

# 7. Opportunity Output
class RequirementMatchItemDTO(BaseModel):
    skill_slug: str
    matched: bool
    evidence_status: VerificationStatusEnum
    supporting_evidence_ids: List[str]

class OpportunityMatchEvaluationDTO(BaseModel):
    opportunity_id: str
    title: str
    organization: str
    match_percentage: float = Field(ge=0.0, le=100.0)
    requirements_breakdown: List[RequirementMatchItemDTO]
    missing_unsupported_skills: List[str]
    advisory_notice: str = "This match evaluates evidence alignment only and does not predict admission or hiring."

class OpportunityMatchingReport(BaseModel):
    user_id: str
    ranked_opportunities: List[OpportunityMatchEvaluationDTO]

# 8. Human Review Output
class HumanReviewActionItemDTO(BaseModel):
    claim_id: str
    user_claim_text: str
    ai_inferred_status: VerificationStatusEnum
    compiled_evidence_snippets: List[GroundedSnippetProvenance]
    proposed_action: str

class HumanReviewRequestPackage(BaseModel):
    review_session_id: str
    items_requiring_human_signoff: List[HumanReviewActionItemDTO]
