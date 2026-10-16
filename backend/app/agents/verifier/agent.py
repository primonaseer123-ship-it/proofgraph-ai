import time
from typing import List, Dict, Any
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    SkillMappingResult, 
    ExtractedEvidenceBatch,
    VerificationAssessmentReport, 
    SkillVerificationEvaluationDTO, 
    VerificationStatusEnum, 
    EvidenceStrengthTier
)

class VerificationAgent(BaseProofGraphAgent):
    """
    Verification Agent: Evaluates claims against concrete evidence items using the multi-factor
    Evidence Strength Model. Decisively classifies status into UNSUPPORTED, PARTIALLY_SUPPORTED,
    or EVIDENCE_SUPPORTED with full mathematical and contextual explainability.
    """
    def __init__(self):
        super().__init__(name="verification_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            mapping: SkillMappingResult = context.state.get("skill_mapping")
            evidence_batch: ExtractedEvidenceBatch = context.state.get("extracted_evidence")
            user_claims: List[Dict[str, Any]] = context.state.get("user_claims", [])

            if not mapping or not evidence_batch:
                return self.record_failure(start_time, "Missing skill_mapping or extracted_evidence in execution state.")

            # Create quick lookup for evidence items
            evidence_by_id = {item.evidence_id: item for item in evidence_batch.evidence_items}
            evaluations: List[SkillVerificationEvaluationDTO] = []

            # 1. Evaluate skills substantiated by mapped evidence
            for skill_node in mapping.mapped_skills:
                ev_ids = skill_node.substantiating_evidence_ids
                ev_items = [evidence_by_id[eid] for eid in ev_ids if eid in evidence_by_id]
                
                # Multi-Factor Evidence Scoring
                # S_e = 0.25*Reliability + 0.25*Directness + 0.15*Recency + 0.15*Specificity + 0.10*Consistency + 0.10*Independence
                reliability = 0.90 # Verified AST or code/report extract
                directness = sum(item.directness_score for item in ev_items) / max(1, len(ev_items))
                recency = 0.85     # Current submission
                specificity = min(1.0, 0.4 + (0.2 * len(ev_items)))
                consistency = 0.90
                independence = min(1.0, 0.5 + (0.25 * len(set(item.artifact_id for item in ev_items))))

                composite_score = round(
                    (0.25 * reliability) +
                    (0.25 * directness) +
                    (0.15 * recency) +
                    (0.15 * specificity) +
                    (0.10 * consistency) +
                    (0.10 * independence),
                    3
                )

                if composite_score >= 0.75 and len(ev_items) >= 2:
                    tier = EvidenceStrengthTier.STRONG
                    status = VerificationStatusEnum.EVIDENCE_SUPPORTED
                    justification = f"Substantiated by {len(ev_items)} grounded code/project artifacts across multiple files."
                    action = "Ready for verified badge or profile inclusion."
                elif composite_score >= 0.50:
                    tier = EvidenceStrengthTier.MODERATE
                    status = VerificationStatusEnum.PARTIALLY_SUPPORTED
                    justification = f"Supported by {len(ev_items)} extracted artifact snippet; additional independent corroboration recommended."
                    action = "Marked as partially supported. Recommend submitting repository link."
                else:
                    tier = EvidenceStrengthTier.WEAK
                    status = VerificationStatusEnum.PARTIALLY_SUPPORTED
                    justification = "Minimal evidence detected; lacks direct AST or implementation proof."
                    action = "Request code repository or assignment report."

                evaluations.append(SkillVerificationEvaluationDTO(
                    skill_slug=skill_node.skill_slug,
                    status=status,
                    strength_tier=tier,
                    composite_strength_score=composite_score,
                    score_breakdown={
                        "reliability": reliability,
                        "directness": directness,
                        "recency": recency,
                        "specificity": specificity,
                        "consistency": consistency,
                        "independence": independence
                    },
                    justification_summary=justification,
                    supporting_evidence_ids=ev_ids,
                    recommended_action=action
                ))

            # 2. Evaluate ungrounded claims (user claimed a skill but zero evidence was extracted)
            substantiated_slugs = {e.skill_slug for e in evaluations}
            for claim in user_claims:
                claimed_slug = claim.get("skill_slug")
                if claimed_slug and claimed_slug not in substantiated_slugs:
                    evaluations.append(SkillVerificationEvaluationDTO(
                        skill_slug=claimed_slug,
                        status=VerificationStatusEnum.UNSUPPORTED,
                        strength_tier=EvidenceStrengthTier.UNSUPPORTED,
                        composite_strength_score=0.0,
                        score_breakdown={"reliability": 0.0, "directness": 0.0},
                        justification_summary=f"Claimed '{claim.get('stated_proficiency', 'Intermediate')}' proficiency, but NO matching evidence, repository, or project artifact was found.",
                        supporting_evidence_ids=[],
                        recommended_action="Keep as Self-Reported or request user to upload proof."
                    ))

            report = VerificationAssessmentReport(
                user_id=context.user_id,
                evaluations=evaluations
            )
            context.state["verification_report"] = report
            return self.record_success(start_time, report)

        except Exception as e:
            return self.record_failure(start_time, f"VerificationAgent failure: {str(e)}")
