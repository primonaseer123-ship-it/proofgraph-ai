from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.init_db import init_db_schema
from app.api.v1 import (
    auth,
    claims,
    evidence,
    graph,
    contradictions,
    opportunities,
    verification,
    agents,
    applications,
    research
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure schema & standard ontology are ready
    await init_db_schema()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "ProofGraph AI: Research-Grade Evidence-Based Personal Skill & Growth Intelligence System.\n\n"
        "Core Pipeline: Input -> Evidence Extraction -> Verification -> Skill Mapping -> "
        "Evidence Graph -> Growth Analysis -> Opportunity Matching -> Human Verification."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(claims.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(contradictions.router, prefix=settings.API_V1_STR)
app.include_router(opportunities.router, prefix=settings.API_V1_STR)
app.include_router(verification.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(research.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "anti_hallucination_rule": "NO EVIDENCE -> NO FACTUAL CLAIM"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
