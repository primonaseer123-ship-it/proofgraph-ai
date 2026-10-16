import time
import uuid
from typing import List
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    VerificationAssessmentReport, 
    ContradictionAuditReport, 
    HumanReviewRequestPackage, 
    HumanReviewActionItemDTO,
    ExtractedEvidenceBatch,
    VerificationStatusEnum
)

class HumanVerificationAgent(BaseProofGraphAgent):
    """
    Human Verification Agent: Curates claims requiring human review (professors, reviewers, or self-audit)
    whenever high-severity discrepancies, leadership assertions, or unverified claims arise.
    """
    def __init__(self):
        super().__init__(name="human_verification_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            ver_report: VerificationAssessmentReport = context.state.get("verification_report")
            contra_report: ContradictionAuditReport = context.state.get("contradiction_report")
            evidence_batch: ExtractedEvidenceBatch = context.state.get("extracted_evidence")

            items_for_review: List[HumanReviewActionItemDTO] = []
            
            # Map evidence
            evidence_snippets = []
            if evidence_batch:
                evidence_snippets = [item.provenance for item in evidence_batch.evidence_items]

            # 1. Process contradicted claims
            if contra_report:
                for ctd in contra_report.contradictions_found:
                    items_for_review.append(HumanReviewActionItemDTO(
                        claim_id=ctd.claim_id or f"claim_{ctd.contradiction_id}",
                        user_claim_text=ctd.claim_text or ctd.formal_explanation,
                        ai_inferred_status=VerificationStatusEnum.UNSUPPORTED,
                        compiled_evidence_snippets=evidence_snippets[:2],
                        proposed_action=ctd.recommended_remedy
                    ))

            # 2. Process high-level claims needing professor sign-off
            if ver_report:
                for ev in ver_report.evaluations:
                    if ev.composite_strength_score >= 0.75 and ev.skill_slug in ["java-oop", "sql"]:
                        items_for_review.append(HumanReviewActionItemDTO(
                            claim_id=f"claim_{ev.skill_slug}",
                            user_claim_text=f"Demonstrated Competence in {ev.skill_slug}",
                            ai_inferred_status=ev.status,
                            compiled_evidence_snippets=evidence_snippets[:2],
                            proposed_action="Request academic instructor confirmation to elevate to HUMAN_VERIFIED status."
                        ))

            pkg = HumanReviewRequestPackage(
                review_session_id=f"rev_{uuid.uuid4().hex[:12]}",
                items_requiring_human_signoff=items_for_review
            )

            context.state["human_review_package"] = pkg
            return self.record_success(start_time, pkg)

        except Exception as e:
            return self.record_failure(start_time, f"HumanVerificationAgent failure: {str(e)}")
