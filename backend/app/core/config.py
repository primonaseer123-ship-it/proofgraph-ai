import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProofGraph AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "proofgraph-insecure-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database: defaults to async SQLite for immediate local execution, seamlessly upgradable to PostgreSQL
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/proofgraph.db"
    
    # Storage
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOAD_MAX_SIZE_MB: int = 50
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # LLM Settings (Optional API key, fallback heuristic/deterministic rules-based execution enabled by default)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore"
    )

settings = Settings()
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
