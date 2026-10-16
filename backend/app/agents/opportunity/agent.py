import time
from typing import List, Dict, Any
from app.agents.base import BaseProofGraphAgent, AgentExecutionContext, AgentExecutionResult
from app.schemas.agent_payloads import (
    VerificationAssessmentReport, 
    OpportunityMatchingReport, 
    OpportunityMatchEvaluationDTO,
    RequirementMatchItemDTO,
    VerificationStatusEnum
)

class OpportunityMatchingAgent(BaseProofGraphAgent):
    """
    Opportunity Matching Agent: Matches user's evidence-backed skills against requirement
    profiles for internships, fellowships, and scholarships, highlighting gaps with strict ethical humility.
    """
    def __init__(self):
        super().__init__(name="opportunity_matching_agent")

    async def run(self, context: AgentExecutionContext) -> AgentExecutionResult:
        start_time = time.time()
        try:
            ver_report: VerificationAssessmentReport = context.state.get("verification_report")
            opportunities: List[Dict[str, Any]] = context.state.get("available_opportunities", [])

            if not ver_report:
                return self.record_failure(start_time, "Missing verification_report in execution state.")

            # Index verified skills
            verified_skills_map = {
                e.skill_slug: e for e in ver_report.evaluations 
                if e.status in [VerificationStatusEnum.EVIDENCE_SUPPORTED, VerificationStatusEnum.PARTIALLY_SUPPORTED]
            }

            ranked_matches: List[OpportunityMatchEvaluationDTO] = []

            for opp in opportunities:
                reqs = opp.get("requirements", [])
                breakdown: List[RequirementMatchItemDTO] = []
                matched_count = 0
                missing_skills = []

                for req in reqs:
                    slug = req.get("skill_slug")
                    is_mand = req.get("is_mandatory", True)

                    if slug in verified_skills_map:
                        eval_item = verified_skills_map[slug]
                        matched_count += 1
                        breakdown.append(RequirementMatchItemDTO(
                            skill_slug=slug,
                            matched=True,
                            evidence_status=eval_item.status,
                            supporting_evidence_ids=eval_item.supporting_evidence_ids
                        ))
                    else:
                        missing_skills.append(slug)
                        breakdown.append(RequirementMatchItemDTO(
                            skill_slug=slug,
                            matched=False,
                            evidence_status=VerificationStatusEnum.UNSUPPORTED,
                            supporting_evidence_ids=[]
                        ))

                total_reqs = max(1, len(reqs))
                match_pct = round((matched_count / total_reqs) * 100.0, 1)

                ranked_matches.append(OpportunityMatchEvaluationDTO(
                    opportunity_id=opp.get("id", "opp_demo"),
                    title=opp.get("title", "Software Engineering Opportunity"),
                    organization=opp.get("organization", "Tech Enterprise"),
                    match_percentage=match_pct,
                    requirements_breakdown=breakdown,
                    missing_unsupported_skills=missing_skills,
                    advisory_notice="This match evaluates evidence alignment only and does not predict admission or hiring."
                ))

            # Sort by match percentage descending
            ranked_matches.sort(key=lambda x: x.match_percentage, reverse=True)

            report = OpportunityMatchingReport(
                user_id=context.user_id,
                ranked_opportunities=ranked_matches
            )
            context.state["opportunity_report"] = report
            return self.record_success(start_time, report)

        except Exception as e:
            return self.record_failure(start_time, f"OpportunityMatchingAgent failure: {str(e)}")
