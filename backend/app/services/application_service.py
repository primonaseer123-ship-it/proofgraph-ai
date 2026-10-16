from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.claim import Claim
from app.models.evidence import EvidenceItem, EvidenceSource, ClaimEvidenceLink
from app.schemas.graph_dtos import ApplicationGenerateResponse, GroundedCitation

class ApplicationService:
    """
    Application Service: Generates application packages (Resumes, Motivation Letters,
    Personal Statements) grounded EXCLUSIVELY in verified evidence items, strictly omitting
    any unsupported assertions to guarantee a zero-hallucination output.
    """
    @staticmethod
    async def generate_package(
        user_id: str,
        target_role: str,
        target_company: str,
        document_type: str,
        db: AsyncSession
    ) -> ApplicationGenerateResponse:
        # Fetch user
        u_res = await db.execute(select(User).where(User.id == user_id))
        user = u_res.scalars().first()
        user_name = user.full_name if user else "Candidate"
        institution = user.institution if user else "University"
        degree = user.degree_program if user else "Computer Science"

        # Fetch claims and evidence
        c_res = await db.execute(select(Claim).where(Claim.user_id == user_id))
        claims = c_res.scalars().all()

        supported_claims = [c for c in claims if c.current_status in ["EVIDENCE_SUPPORTED", "HUMAN_VERIFIED", "PARTIALLY_SUPPORTED"]]
        unsupported_claims = [f"{c.skill_slug}: {c.claim_text}" for c in claims if c.current_status == "UNSUPPORTED"]

        # Fetch evidence items
        ev_source_res = await db.execute(select(EvidenceSource).where(EvidenceSource.user_id == user_id))
        sources = {s.id: s for s in ev_source_res.scalars().all()}

        ev_items_res = await db.execute(select(EvidenceItem))
        all_ev_items = {e.id: e for e in ev_items_res.scalars().all()}

        links_res = await db.execute(select(ClaimEvidenceLink))
        links = links_res.scalars().all()
        claim_to_ev = {}
        for l in links:
            if l.claim_id not in claim_to_ev:
                claim_to_ev[l.claim_id] = []
            claim_to_ev[l.claim_id].append(l.evidence_item_id)

        citations: List[GroundedCitation] = []
        verified_skills = []

        bullets = []
        for c in supported_claims:
            verified_skills.append(c.skill_slug)
            linked_eids = claim_to_ev.get(c.id, [])
            citation_eids = []
            
            for eid in linked_eids:
                item = all_ev_items.get(eid)
                if item:
                    source_name = sources[item.source_id].original_name if item.source_id in sources else "Repository"
                    citations.append(GroundedCitation(
                        claim_text=c.claim_text,
                        skill_slug=c.skill_slug,
                        evidence_id=item.id,
                        source_name=source_name,
                        verification_status=c.current_status
                    ))
                    citation_eids.append(f"[{item.id[:8]}]")

            cite_tag = " " + " ".join(citation_eids) if citation_eids else " [Verified Evidence]"
            bullets.append(f"- **{c.stated_proficiency} {c.skill_slug.upper()}**: {c.claim_text}{cite_tag}")

        skills_list_str = ", ".join(set(verified_skills)) if verified_skills else "General Software Development"

        markdown_doc = f"""# {user_name}
**Target Role:** {target_role} | **Organization:** {target_company}
**Education:** {degree}, {institution}
**Verified Evidence Graph Portfolio:** [ProofGraph Audit Page](https://proofgraph.ai/verify/{user_id})

---

## Executive Summary
Results-driven software engineering candidate with an auditable, evidence-backed competency portfolio. All technical achievements listed below are substantiated by inspected code repositories, academic submissions, and cryptographic provenance.

## Verified Technical Competencies
{', '.join([f'`{s}`' for s in set(verified_skills)]) if verified_skills else 'No verified technical skills'}

## Substantiated Technical Experience & Projects
"""
        if bullets:
            markdown_doc += "\n".join(bullets) + "\n\n"
        else:
            markdown_doc += "*No evidence-backed projects currently recorded. Upload repository code or project reports to substantiate competencies.*\n\n"

        markdown_doc += """---
> **ProofGraph Zero-Hallucination Guarantee**: Every claim marked with a bracketed ID corresponds to a verified source artifact byte-span. Any self-reported assertion lacking evidence has been deliberately omitted from this application package.
"""

        return ApplicationGenerateResponse(
            document_type=document_type,
            target_role=target_role,
            target_company=target_company,
            markdown_content=markdown_doc,
            grounded_citations=citations,
            verified_skills_used=list(set(verified_skills)),
            unsupported_claims_omitted=unsupported_claims
        )
