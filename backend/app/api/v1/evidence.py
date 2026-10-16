import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database.session import get_db
from app.models.user import User
from app.models.evidence import EvidenceSource, EvidenceItem
from app.schemas.evidence_dtos import EvidenceSourceResponse, EvidenceItemResponse, ManualEvidenceInput
from app.core.security import compute_sha256
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("", response_model=List[EvidenceSourceResponse])
async def list_evidence_sources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(EvidenceSource).where(EvidenceSource.user_id == current_user.id))
    sources = res.scalars().all()
    
    responses = []
    for s in sources:
        items_res = await db.execute(select(EvidenceItem).where(EvidenceItem.source_id == s.id))
        items = items_res.scalars().all()
        
        item_responses = [
            EvidenceItemResponse(
                id=item.id,
                source_id=item.source_id,
                skill_slug=item.skill_slug,
                skill_name=item.skill_slug,
                title=item.title,
                raw_snippet=item.raw_snippet,
                byte_start=item.byte_start,
                byte_end=item.byte_end,
                line_start=item.line_start,
                line_end=item.line_end,
                evidence_date=item.evidence_date,
                directness_score=item.directness_score,
                confidence_score=item.confidence_score,
                strength_score=item.strength_score,
                verification_status=item.verification_status,
                created_at=item.created_at
            ) for item in items
        ]
        
        responses.append(EvidenceSourceResponse(
            id=s.id,
            user_id=s.user_id,
            source_type=s.source_type,
            uri=s.uri,
            file_sha256=s.file_sha256,
            original_name=s.original_name,
            byte_size=s.byte_size,
            metadata_json=s.metadata_json,
            created_at=s.created_at,
            evidence_items=item_responses
        ))
    return responses

@router.post("/upload", response_model=EvidenceSourceResponse)
async def upload_evidence_file(
    file: UploadFile = File(...),
    source_type: Optional[str] = Form("project_report"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    if len(contents) > settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size.")

    sha256 = compute_sha256(contents)
    save_filename = f"{sha256[:16]}_{file.filename}"
    save_path = settings.STORAGE_DIR / save_filename
    with open(save_path, "wb") as f:
        f.write(contents)

    source = EvidenceSource(
        user_id=current_user.id,
        source_type=source_type,
        uri=f"file://{save_path}",
        file_sha256=sha256,
        original_name=file.filename or "uploaded_file",
        byte_size=len(contents),
        metadata_json={"content_type": file.content_type}
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    return EvidenceSourceResponse(
        id=source.id,
        user_id=source.user_id,
        source_type=source.source_type,
        uri=source.uri,
        file_sha256=source.file_sha256,
        original_name=source.original_name,
        byte_size=source.byte_size,
        metadata_json=source.metadata_json,
        created_at=source.created_at,
        evidence_items=[]
    )

@router.post("/manual", response_model=EvidenceSourceResponse)
async def create_manual_evidence(
    data: ManualEvidenceInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    raw_bytes = data.raw_text.encode("utf-8")
    sha256 = compute_sha256(raw_bytes)
    safe_title = "".join(c for c in data.title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    save_filename = f"{sha256[:16]}_{safe_title[:24]}.txt"
    save_path = settings.STORAGE_DIR / save_filename
    
    with open(save_path, "wb") as f:
        f.write(raw_bytes)

    source = EvidenceSource(
        user_id=current_user.id,
        source_type=data.source_type,
        uri=f"file://{save_path}",
        file_sha256=sha256,
        original_name=data.title,
        byte_size=len(raw_bytes),
        metadata_json={"technologies": data.technologies, "date": data.evidence_date}
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)

    return EvidenceSourceResponse(
        id=source.id,
        user_id=source.user_id,
        source_type=source.source_type,
        uri=source.uri,
        file_sha256=source.file_sha256,
        original_name=source.original_name,
        byte_size=source.byte_size,
        metadata_json=source.metadata_json,
        created_at=source.created_at,
        evidence_items=[]
    )
