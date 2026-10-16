import time
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.agents.base import AgentExecutionContext, AgentExecutionResult
from app.agents.collector.agent import CollectorAgent
from app.agents.evidence.agent import EvidenceExtractionAgent
from app.agents.skill.agent import SkillMappingAgent
from app.agents.verifier.agent import VerificationAgent
from app.agents.contradiction.agent import ContradictionDetectionAgent
from app.agents.growth.agent import GrowthAnalysisAgent
from app.agents.opportunity.agent import OpportunityMatchingAgent
from app.agents.human_verification.agent import HumanVerificationAgent

from app.models.evidence import EvidenceSource, EvidenceItem, ClaimEvidenceLink
from app.models.claim import Claim
from app.models.skill import Skill
from app.models.contradiction import Contradiction
from app.models.opportunity import Opportunity, OpportunityRequirement
from app.models.audit import AuditLog
from app.core.security import compute_sha256

class ProofGraphSupervisor:
    """
    Supervisor Orchestrator: Coordinates the 8-agent sequential DAG, validates state envelopes,
    enforces provenance hashing, and handles atomic persistence into the Personal Evidence Graph.
    """
    def __init__(self):
        self.collector = CollectorAgent()
        self.evidence_extractor = EvidenceExtractionAgent()
        self.skill_mapper = SkillMappingAgent()
        self.verifier = VerificationAgent()
        self.contradiction_detector = ContradictionDetectionAgent()
        self.growth_analyzer = GrowthAnalysisAgent()
        self.opportunity_matcher = OpportunityMatchingAgent()
        self.human_verifier = HumanVerificationAgent()

    async def execute_pipeline(
        self,
        user_id: str,
        raw_inputs: List[Dict[str, Any]],
        user_claims: List[Dict[str, Any]],
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Executes the entire multi-agent pipeline and persists results if db session is provided.
        """
        run_id = f"run_{uuid.uuid4().hex}"
        context = AgentExecutionContext(
            user_id=user_id,
            run_id=run_id,
            start_time=time.time(),
            state={
                "raw_inputs": raw_inputs,
                "user_claims": user_claims
            }
        )

        pipeline_log: List[AgentExecutionResult] = []

        # Fetch available opportunities if db is available
        if db:
            opp_res = await db.execute(select(Opportunity))
            opportunities = opp_res.scalars().all()
            opp_list = []
            for o in opportunities:
                req_res = await db.execute(select(OpportunityRequirement).where(OpportunityRequirement.opportunity_id == o.id))
                reqs = req_res.scalars().all()
                opp_list.append({
                    "id": o.id,
                    "title": o.title,
                    "organization": o.organization,
                    "requirements": [{"skill_slug": r.skill_slug, "is_mandatory": r.is_mandatory} for r in reqs]
                })
            context.state["available_opportunities"] = opp_list
        else:
            context.state["available_opportunities"] = []

        # 1. Collector Agent
        res_collector = await self.collector.run(context)
        pipeline_log.append(res_collector)
        if not res_collector.success:
            return {"run_id": run_id, "success": False, "error": res_collector.error_message, "logs": pipeline_log}

        # 2. Evidence Extraction Agent
        res_evidence = await self.evidence_extractor.run(context)
        pipeline_log.append(res_evidence)
        if not res_evidence.success:
            return {"run_id": run_id, "success": False, "error": res_evidence.error_message, "logs": pipeline_log}

        # 3. Skill Mapping Agent
        res_skill = await self.skill_mapper.run(context)
        pipeline_log.append(res_skill)
        if not res_skill.success:
            return {"run_id": run_id, "success": False, "error": res_skill.error_message, "logs": pipeline_log}

        # 4. Verification Agent
        res_ver = await self.verifier.run(context)
        pipeline_log.append(res_ver)
        if not res_ver.success:
            return {"run_id": run_id, "success": False, "error": res_ver.error_message, "logs": pipeline_log}

        # 5. Contradiction Detection Agent
        res_contra = await self.contradiction_detector.run(context)
        pipeline_log.append(res_contra)

        # 6. Growth Analysis Agent
        res_growth = await self.growth_analyzer.run(context)
        pipeline_log.append(res_growth)

        # 7. Opportunity Matching Agent
        res_opp = await self.opportunity_matcher.run(context)
        pipeline_log.append(res_opp)

        # 8. Human Verification Agent
        res_human = await self.human_verifier.run(context)
        pipeline_log.append(res_human)

        # Atomic Database Persistence
        if db:
            await self._persist_graph_state(user_id, context, db)

        return {
            "run_id": run_id,
            "success": True,
            "user_id": user_id,
            "collector_manifest": context.state.get("collector_manifest"),
            "extracted_evidence": context.state.get("extracted_evidence"),
            "skill_mapping": context.state.get("skill_mapping"),
            "verification_report": context.state.get("verification_report"),
            "contradiction_report": context.state.get("contradiction_report"),
            "growth_report": context.state.get("growth_report"),
            "opportunity_report": context.state.get("opportunity_report"),
            "human_review_package": context.state.get("human_review_package"),
            "agent_logs": [log.model_dump() for log in pipeline_log]
        }

    async def _persist_graph_state(self, user_id: str, context: AgentExecutionContext, db: AsyncSession):
        """Atomically commits graph entities into the database."""
        collector_manifest = context.state.get("collector_manifest")
        extracted_evidence = context.state.get("extracted_evidence")
        verification_report = context.state.get("verification_report")
        contradiction_report = context.state.get("contradiction_report")

        # Map to save evidence sources
        source_id_map = {}
        if collector_manifest:
            for art in collector_manifest.artifacts:
                source = EvidenceSource(
                    user_id=user_id,
                    source_type=art.source_type,
                    uri=f"file://storage/{art.artifact_id}",
                    file_sha256=art.sha256_checksum,
                    original_name=art.original_file_name,
                    byte_size=art.byte_size,
                    metadata_json=art.metadata
                )
                db.add(source)
                await db.flush()
                source_id_map[art.artifact_id] = source.id

        # Save evidence items
        evidence_item_map = {}
        if extracted_evidence:
            for item in extracted_evidence.evidence_items:
                real_source_id = source_id_map.get(item.artifact_id)
                if real_source_id:
                    # Match skill slug from taxonomy
                    skill_slug = item.extracted_technologies[0].lower().replace(" ", "-") if item.extracted_technologies else "software-development"
                    # Ensure skill exists
                    skill_check = await db.execute(select(Skill).where(Skill.slug == skill_slug))
                    if not skill_check.scalars().first():
                        # Default to software-development if not in standard list
                        skill_slug = "software-development"

                    ev_item = EvidenceItem(
                        source_id=real_source_id,
                        skill_slug=skill_slug,
                        title=item.activity_name,
                        raw_snippet=item.provenance.raw_text,
                        byte_start=item.provenance.start_char_idx,
                        byte_end=item.provenance.end_char_idx,
                        line_start=item.provenance.line_start,
                        line_end=item.provenance.line_end,
                        evidence_date=item.evidence_date,
                        directness_score=item.directness_score,
                        confidence_score=item.confidence_score,
                        strength_score=0.85,
                        verification_status="EVIDENCE_SUPPORTED"
                    )
                    db.add(ev_item)
                    await db.flush()
                    evidence_item_map[item.evidence_id] = ev_item.id

        # Update or insert user claims with verification scores
        user_claims = context.state.get("user_claims", [])
        ver_evals = {e.skill_slug: e for e in verification_report.evaluations} if verification_report else {}

        for uc in user_claims:
            slug = uc.get("skill_slug")
            stated_prof = uc.get("stated_proficiency", "Intermediate")
            claim_text = uc.get("claim_text", "")
            claim_id = uc.get("claim_id")

            # Check if skill exists
            skill_res = await db.execute(select(Skill).where(Skill.slug == slug))
            if not skill_res.scalars().first():
                continue

            eval_item = ver_evals.get(slug)
            status = eval_item.status.value if eval_item else "UNSUPPORTED"
            confidence = eval_item.composite_strength_score if eval_item else 0.0
            justification = eval_item.justification_summary if eval_item else "No evidence available."

            if claim_id:
                # Update existing claim
                claim_res = await db.execute(select(Claim).where(Claim.id == claim_id))
                existing_claim = claim_res.scalars().first()
                if existing_claim:
                    existing_claim.current_status = status
                    existing_claim.confidence_score = confidence
                    existing_claim.justification_summary = justification
            else:
                new_claim = Claim(
                    user_id=user_id,
                    skill_slug=slug,
                    stated_proficiency=stated_prof,
                    claim_text=claim_text,
                    claim_type="USER_CLAIM",
                    current_status=status,
                    confidence_score=confidence,
                    justification_summary=justification
                )
                db.add(new_claim)
                await db.flush()
                claim_id = new_claim.id

            # Link evidence items to claim
            if eval_item:
                for eid in eval_item.supporting_evidence_ids:
                    real_ev_id = evidence_item_map.get(eid)
                    if real_ev_id and claim_id:
                        link = ClaimEvidenceLink(
                            claim_id=claim_id,
                            evidence_item_id=real_ev_id,
                            weight=1.0,
                            relevance_rationale=eval_item.justification_summary
                        )
                        db.add(link)

        # Save contradictions
        if contradiction_report:
            for ctd in contradiction_report.contradictions_found:
                contra = Contradiction(
                    user_id=user_id,
                    claim_id=ctd.claim_id if ctd.claim_id and not ctd.claim_id.startswith("claim_") else None,
                    contradiction_type=ctd.inconsistency_type,
                    severity=ctd.severity.value,
                    explanation=ctd.formal_explanation,
                    conflicting_evidence_ids=ctd.conflicting_evidence_ids,
                    is_resolved=False
                )
                db.add(contra)

        # Record Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="MULTI_AGENT_PIPELINE_RUN",
            entity_type="AgentRun",
            entity_id=context.run_id,
            payload_hash=compute_sha256(str(context.run_id).encode("utf-8")),
            details={
                "artifacts_count": len(collector_manifest.artifacts) if collector_manifest else 0,
                "evidence_count": len(extracted_evidence.evidence_items) if extracted_evidence else 0,
                "contradictions_count": len(contradiction_report.contradictions_found) if contradiction_report else 0
            }
        )
        db.add(audit)
        await db.commit()
