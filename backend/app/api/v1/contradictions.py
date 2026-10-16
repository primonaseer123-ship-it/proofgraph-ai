from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database.session import get_db
from app.models.user import User
from app.models.contradiction import Contradiction
from app.models.claim import Claim
from app.schemas.contradiction_dtos import ContradictionResponse, ContradictionAcknowledgeRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/contradictions", tags=["Contradictions"])

@router.get("", response_model=List[ContradictionResponse])
async def list_contradictions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Contradiction).where(Contradiction.user_id == current_user.id))
    items = res.scalars().all()
    
    responses = []
    for c in items:
        claim_text = None
        if c.claim_id:
            cl_res = await db.execute(select(Claim).where(Claim.id == c.claim_id))
            cl = cl_res.scalars().first()
            if cl:
                claim_text = cl.claim_text

        responses.append(ContradictionResponse(
            id=c.id,
            user_id=c.user_id,
            claim_id=c.claim_id,
            claim_text=claim_text,
            contradiction_type=c.contradiction_type,
            severity=c.severity,
            explanation=c.explanation,
            conflicting_evidence_ids=c.conflicting_evidence_ids,
            is_resolved=c.is_resolved,
            resolution_note=c.resolution_note,
            created_at=c.created_at
        ))
    return responses

@router.post("/{id}/resolve", response_model=ContradictionResponse)
async def resolve_contradiction(
    id: str,
    req: ContradictionAcknowledgeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Contradiction).where(Contradiction.id == id, Contradiction.user_id == current_user.id))
    c = res.scalars().first()
    if not c:
        raise HTTPException(status_code=404, detail="Contradiction not found.")
    
    c.is_resolved = True
    c.resolution_note = req.resolution_note
    await db.commit()
    await db.refresh(c)

    return ContradictionResponse(
        id=c.id,
        user_id=c.user_id,
        claim_id=c.claim_id,
        contradiction_type=c.contradiction_type,
        severity=c.severity,
        explanation=c.explanation,
        conflicting_evidence_ids=c.conflicting_evidence_ids,
        is_resolved=c.is_resolved,
        resolution_note=c.resolution_note,
        created_at=c.created_at
    )
