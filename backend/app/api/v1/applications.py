from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.services.application_service import ApplicationService
from app.schemas.graph_dtos import ApplicationGenerateRequest, ApplicationGenerateResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/generate", response_model=ApplicationGenerateResponse)
async def generate_application_package(
    req: ApplicationGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ApplicationService.generate_package(
        user_id=current_user.id,
        target_role=req.target_role,
        target_company=req.target_company,
        document_type=req.document_type,
        db=db
    )
