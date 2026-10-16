from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.session import get_db
from app.models.user import User
from app.models.claim import Claim
from app.models.skill import Skill
from app.models.evidence import ClaimEvidenceLink
from app.schemas.claim_dtos import ClaimCreate, ClaimResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/claims", tags=["Claims"])

@router.get("", response_model=List[ClaimResponse])
async def list_claims(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Claim).where(Claim.user_id == current_user.id))
    claims = result.scalars().all()
    
    responses = []
    for c in claims:
        # Fetch skill name
        sk_res = await db.execute(select(Skill).where(Skill.slug == c.skill_slug))
        sk = sk_res.scalars().first()
        
        # Fetch supporting evidence ids
        links_res = await db.execute(select(ClaimEvidenceLink).where(ClaimEvidenceLink.claim_id == c.id))
        links = links_res.scalars().all()
        
        resp = ClaimResponse(
            id=c.id,
            user_id=c.user_id,
            skill_slug=c.skill_slug,
            skill_name=sk.name if sk else c.skill_slug,
            stated_proficiency=c.stated_proficiency,
            claim_text=c.claim_text,
            claim_type=c.claim_type,
            current_status=c.current_status,
            confidence_score=c.confidence_score,
            justification_summary=c.justification_summary,
            created_at=c.created_at,
            supporting_evidence_ids=[l.evidence_item_id for l in links]
        )
        responses.append(resp)
    return responses

@router.post("", response_model=ClaimResponse)
async def create_claim(
    claim_in: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure skill exists
    sk_res = await db.execute(select(Skill).where(Skill.slug == claim_in.skill_slug))
    skill = sk_res.scalars().first()
    if not skill:
        # Create standard skill if missing
        skill = Skill(
            slug=claim_in.skill_slug,
            name=claim_in.skill_slug.replace("-", " ").title(),
            category="Custom",
            taxonomy_path=f"Custom/{claim_in.skill_slug}",
            level_depth=2
        )
        db.add(skill)
        await db.flush()

    new_claim = Claim(
        user_id=current_user.id,
        skill_slug=skill.slug,
        stated_proficiency=claim_in.stated_proficiency,
        claim_text=claim_in.claim_text,
        claim_type="USER_CLAIM",
        current_status="UNSUPPORTED", # Awaiting verification pipeline
        confidence_score=0.0,
        justification_summary="Newly registered claim awaiting evidence submission and multi-agent audit."
    )
    db.add(new_claim)
    await db.commit()
    await db.refresh(new_claim)

    return ClaimResponse(
        id=new_claim.id,
        user_id=new_claim.user_id,
        skill_slug=new_claim.skill_slug,
        skill_name=skill.name,
        stated_proficiency=new_claim.stated_proficiency,
        claim_text=new_claim.claim_text,
        claim_type=new_claim.claim_type,
        current_status=new_claim.current_status,
        confidence_score=new_claim.confidence_score,
        justification_summary=new_claim.justification_summary,
        created_at=new_claim.created_at,
        supporting_evidence_ids=[]
    )
