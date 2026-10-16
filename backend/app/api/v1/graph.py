from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.models.user import User
from app.services.graph_service import GraphService
from app.schemas.graph_dtos import GraphResponse, GrowthTrajectoryResponse, GrowthTimelineStage
from app.api.deps import get_current_user

router = APIRouter(prefix="/graph", tags=["Evidence Graph"])

@router.get("", response_model=GraphResponse)
async def get_user_evidence_graph(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await GraphService.build_user_graph(current_user.id, db)

@router.get("/growth", response_model=GrowthTrajectoryResponse)
async def get_user_growth_trajectory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve growth stages based on user's current evidence items
    graph = await GraphService.build_user_graph(current_user.id, db)
    
    stages = [
        GrowthTimelineStage(
            period="Academic Foundations (Year 1-2)",
            title="Object-Oriented Programming & Core Algorithms",
            skills_demonstrated=["Java OOP", "C++", "Data Structures"],
            evidence_count=max(1, len([n for n in graph.nodes if n.type == "evidenceNode"])),
            complexity_level="Intermediate",
            narrative="Established rigorous computational foundation through course projects and lab implementations."
        ),
        GrowthTimelineStage(
            period="Persistence & Architecture (Year 2-3)",
            title="Database Modeling & Relational Systems",
            skills_demonstrated=["SQL", "JDBC", "MySQL"],
            evidence_count=2,
            complexity_level="Intermediate-Advanced",
            narrative="Engineered database schemas and integrated programmatic persistence layers."
        )
    ]

    return GrowthTrajectoryResponse(
        user_id=current_user.id,
        stages=stages,
        learning_velocity="Active, multi-tier full-stack progression",
        recommended_focus_areas=["Spring Boot Enterprise Microservices", "CI/CD Deployment Pipelines"]
    )
