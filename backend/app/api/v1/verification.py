from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.user import User
from app.models.claim import Claim
from app.models.audit import HumanVerification, AuditLog
from app.schemas.claim_dtos import ClaimResponse, ClaimHumanVerifyRequest
from app.core.security import compute_sha256
from app.api.deps import get_current_user

router = APIRouter(prefix="/verification", tags=["Human Verification"])

@router.post("/{claim_id}/verify", response_model=ClaimResponse)
async def verify_claim_human(
    claim_id: str,
    req: ClaimHumanVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Claim).where(Claim.id == claim_id))
    claim = res.scalars().first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found.")

    sig_payload = f"{claim_id}_{current_user.id}_{req.decision}_{req.commentary}".encode("utf-8")
    sig_hash = compute_sha256(sig_payload)

    if req.decision == "APPROVED":
        claim.current_status = "HUMAN_VERIFIED"
        claim.claim_type = "HUMAN_VERIFIED"
        claim.justification_summary = f"Human verified by {current_user.full_name}: {req.commentary}"
    elif req.decision == "REJECTED":
        claim.current_status = "UNSUPPORTED"
        claim.justification_summary = f"Human audit rejected by {current_user.full_name}: {req.commentary}"
    elif req.decision == "AMENDED" and req.amended_proficiency:
        claim.stated_proficiency = req.amended_proficiency
        claim.current_status = "HUMAN_VERIFIED"
        claim.justification_summary = f"Proficiency amended to '{req.amended_proficiency}' by {current_user.full_name}: {req.commentary}"

    # Record HumanVerification entity
    ver_record = HumanVerification(
        claim_id=claim.id,
        verifier_user_id=current_user.id,
        decision=req.decision,
        commentary=req.commentary,
        signature_hash=sig_hash
    )
    db.add(ver_record)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="HUMAN_VERIFICATION_STAMP",
        entity_type="Claim",
        entity_id=claim.id,
        payload_hash=sig_hash,
        details={"decision": req.decision, "commentary": req.commentary}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(claim)

    return ClaimResponse(
        id=claim.id,
        user_id=claim.user_id,
        skill_slug=claim.skill_slug,
        skill_name=claim.skill_slug,
        stated_proficiency=claim.stated_proficiency,
        claim_text=claim.claim_text,
        claim_type=claim.claim_type,
        current_status=claim.current_status,
        confidence_score=claim.confidence_score,
        justification_summary=claim.justification_summary,
        created_at=claim.created_at,
        supporting_evidence_ids=[]
    )
