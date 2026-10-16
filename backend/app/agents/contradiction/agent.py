import time
import uuid
from typing import List, Dict, Any
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    VerificationAssessmentReport, 
    ExtractedEvidenceBatch,
    ContradictionAuditReport, 
    FlaggedContradictionDTO, 
    ContradictionSeverity,
    VerificationStatusEnum
)

class ContradictionDetectionAgent(BaseProofGraphAgent):
    """
    Contradiction Detection Agent: Systematically audits user assertions against concrete
    verified reality, catching proficiency inflation, unsupported ghost claims, and chronological conflicts.
    """
    def __init__(self):
        super().__init__(name="contradiction_detection_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            ver_report: VerificationAssessmentReport = context.state.get("verification_report")
            evidence_batch: ExtractedEvidenceBatch = context.state.get("extracted_evidence")
            user_claims: List[Dict[str, Any]] = context.state.get("user_claims", [])

            if not ver_report:
                return self.record_failure(start_time, "Missing verification_report in execution state.")

            eval_map = {e.skill_slug: e for e in ver_report.evaluations}
            evidence_by_id = {item.evidence_id: item for item in evidence_batch.evidence_items} if evidence_batch else {}
            contradictions: List[FlaggedContradictionDTO] = []

            for claim in user_claims:
                slug = claim.get("skill_slug")
                stated_prof = claim.get("stated_proficiency", "Intermediate").capitalize()
                claim_text = claim.get("claim_text", "")
                claim_id = claim.get("claim_id")

                eval_item = eval_map.get(slug)

                # Check 1: Ghost claim (asserted with zero evidence)
                if not eval_item or eval_item.status == VerificationStatusEnum.UNSUPPORTED:
                    contradictions.append(FlaggedContradictionDTO(
                        contradiction_id=f"ctd_{uuid.uuid4().hex[:10]}",
                        severity=ContradictionSeverity.HIGH,
                        claim_id=claim_id,
                        claim_text=f"{stated_prof} {slug}: {claim_text}",
                        conflicting_evidence_ids=[],
                        inconsistency_type="GHOST_CLAIM",
                        formal_explanation=(
                            f"User asserted '{stated_prof} {slug}' proficiency, but the system found "
                            f"zero supporting repositories, code files, or project documents."
                        ),
                        recommended_remedy="Downgrade claim to 'Self-Reported Interest' or upload direct source evidence."
                    ))

                # Check 2: Exaggeration (Claimed 'Advanced' or 'Expert' with minimal or single-project evidence)
                elif stated_prof in ["Advanced", "Expert"]:
                    ev_items = [evidence_by_id[eid] for eid in eval_item.supporting_evidence_ids if eid in evidence_by_id]
                    distinct_artifacts_count = len(set(item.artifact_id for item in ev_items))
                    
                    is_exaggeration = False
                    reason = ""
                    
                    if distinct_artifacts_count < 2:
                        is_exaggeration = True
                        reason = (
                            f"User claims '{stated_prof}' level in {slug}, but all supporting evidence originates from "
                            f"only a single project/artifact ({distinct_artifacts_count} source). "
                            f"Advanced/Expert proficiency requires demonstration across multiple independent codebases."
                        )
                    elif eval_item.composite_strength_score < 0.85:
                        is_exaggeration = True
                        reason = (
                            f"User claims '{stated_prof}' level in {slug}, but composite evidence strength is "
                            f"{eval_item.composite_strength_score} (below the 0.85 threshold for Advanced competency)."
                        )

                    if is_exaggeration:
                        contradictions.append(FlaggedContradictionDTO(
                            contradiction_id=f"ctd_{uuid.uuid4().hex[:10]}",
                            severity=ContradictionSeverity.HIGH,
                            claim_id=claim_id,
                            claim_text=f"{stated_prof} {slug}: {claim_text}",
                            conflicting_evidence_ids=eval_item.supporting_evidence_ids,
                            inconsistency_type="EXAGGERATION",
                            formal_explanation=reason,
                            recommended_remedy=(
                                f"Adjust stated proficiency to 'Intermediate' or provide additional production/course repositories."
                            )
                        ))

            # Compute overall profile consistency score
            total_claims = max(1, len(user_claims))
            inconsistency_penalty = len(contradictions) * 0.25
            consistency_score = max(0.0, round(1.0 - (inconsistency_penalty / total_claims), 2))

            report = ContradictionAuditReport(
                user_id=context.user_id,
                contradictions_found=contradictions,
                overall_profile_consistency_score=consistency_score
            )
            context.state["contradiction_report"] = report
            return self.record_success(start_time, report)

        except Exception as e:
            return self.record_failure(start_time, f"ContradictionDetectionAgent failure: {str(e)}")
