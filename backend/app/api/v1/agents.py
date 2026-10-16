from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from app.database.session import get_db
from app.models.user import User
from app.models.claim import Claim
from app.models.evidence import EvidenceSource
from app.agents.supervisor.orchestrator import ProofGraphSupervisor
from app.api.deps import get_current_user
import os

router = APIRouter(prefix="/agents", tags=["Agents"])
supervisor = ProofGraphSupervisor()

@router.post("/run")
async def run_pipeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Gather user's stored evidence files and manual entries
    ev_res = await db.execute(select(EvidenceSource).where(EvidenceSource.user_id == current_user.id))
    sources = ev_res.scalars().all()

    raw_inputs = []
    for s in sources:
        data_bytes = b""
        if s.uri.startswith("file://"):
            local_path = s.uri.replace("file://", "")
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    data_bytes = f.read()
        elif s.uri.startswith("manual://"):
            data_bytes = s.original_name.encode("utf-8")

        raw_inputs.append({
            "filename": s.original_name,
            "source_type": s.source_type,
            "data_bytes": data_bytes
        })

    # Gather user's active claims
    c_res = await db.execute(select(Claim).where(Claim.user_id == current_user.id))
    claims = c_res.scalars().all()
    user_claims = [
        {
            "claim_id": c.id,
            "skill_slug": c.skill_slug,
            "stated_proficiency": c.stated_proficiency,
            "claim_text": c.claim_text
        } for c in claims
    ]

    result = await supervisor.execute_pipeline(
        user_id=current_user.id,
        raw_inputs=raw_inputs,
        user_claims=user_claims,
        db=db
    )

    return result
