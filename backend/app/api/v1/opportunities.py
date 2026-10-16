from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.session import get_db
from app.models.user import User
from app.models.opportunity import Opportunity, OpportunityRequirement
from app.models.claim import Claim
from app.schemas.opportunity_dtos import OpportunityResponse, OpportunityRequirementDTO, OpportunityMatchDTO
from app.api.deps import get_current_user

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

@router.get("", response_model=List[OpportunityResponse])
async def list_opportunities(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Opportunity))
    opps = res.scalars().all()
    
    results = []
    for o in opps:
        req_res = await db.execute(select(OpportunityRequirement).where(OpportunityRequirement.opportunity_id == o.id))
        reqs = req_res.scalars().all()
        results.append(OpportunityResponse(
            id=o.id,
            title=o.title,
            organization=o.organization,
            opportunity_type=o.opportunity_type,
            location=o.location,
            external_url=o.external_url,
            deadline=o.deadline,
            description=o.description,
            requirements=[
                OpportunityRequirementDTO(
                    skill_slug=r.skill_slug,
                    skill_name=r.skill_slug.replace("-", " ").title(),
                    minimum_proficiency=r.minimum_proficiency,
                    is_mandatory=r.is_mandatory,
                    matched=False
                ) for r in reqs
            ]
        ))
    return results

@router.get("/matches", response_model=List[OpportunityMatchDTO])
async def get_opportunity_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch user's verified or evidence-supported claims
    claim_res = await db.execute(select(Claim).where(Claim.user_id == current_user.id))
    claims = claim_res.scalars().all()
    verified_map = {
        c.skill_slug: c for c in claims 
        if c.current_status in ["EVIDENCE_SUPPORTED", "HUMAN_VERIFIED", "PARTIALLY_SUPPORTED"]
    }

    opp_res = await db.execute(select(Opportunity))
    opps = opp_res.scalars().all()

    matches: List[OpportunityMatchDTO] = []
    for o in opps:
        req_res = await db.execute(select(OpportunityRequirement).where(OpportunityRequirement.opportunity_id == o.id))
        reqs = req_res.scalars().all()

        breakdown = []
        matched_mand_count = 0
        total_mand_count = 0
        missing_skills = []

        for r in reqs:
            if r.is_mandatory:
                total_mand_count += 1

            if r.skill_slug in verified_map:
                user_claim = verified_map[r.skill_slug]
                if r.is_mandatory:
                    matched_mand_count += 1
                breakdown.append(OpportunityRequirementDTO(
                    skill_slug=r.skill_slug,
                    skill_name=r.skill_slug.replace("-", " ").title(),
                    minimum_proficiency=r.minimum_proficiency,
                    is_mandatory=r.is_mandatory,
                    matched=True,
                    evidence_status=user_claim.current_status
                ))
            else:
                missing_skills.append(r.skill_slug)
                breakdown.append(OpportunityRequirementDTO(
                    skill_slug=r.skill_slug,
                    skill_name=r.skill_slug.replace("-", " ").title(),
                    minimum_proficiency=r.minimum_proficiency,
                    is_mandatory=r.is_mandatory,
                    matched=False,
                    evidence_status="UNSUPPORTED"
                ))

        total_reqs = max(1, len(reqs))
        match_percentage = round((len([b for b in breakdown if b.matched]) / total_reqs) * 100.0, 1)

        matches.append(OpportunityMatchDTO(
            opportunity_id=o.id,
            title=o.title,
            organization=o.organization,
            opportunity_type=o.opportunity_type,
            location=o.location,
            external_url=o.external_url,
            match_percentage=match_percentage,
            matched_mandatory_count=matched_mand_count,
            total_mandatory_count=total_mand_count,
            requirements_breakdown=breakdown,
            missing_unsupported_skills=missing_skills
        ))

    matches.sort(key=lambda x: x.match_percentage, reverse=True)
    return matches
