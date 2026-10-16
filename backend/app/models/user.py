from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text
from typing import List, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.claim import Claim
    from app.models.evidence import EvidenceSource
    from app.models.contradiction import Contradiction
    from app.models.audit import AuditLog

class User(Base, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution: Mapped[str] = mapped_column(String(255), nullable=True) # e.g. FAST-NUCES, NUST, etc.
    degree_program: Mapped[str] = mapped_column(String(255), nullable=True) # e.g. BS Computer Science
    role: Mapped[str] = mapped_column(String(50), default="student", nullable=False) # student, verifier, researcher
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="user", cascade="all, delete-orphan")
    evidence_sources: Mapped[List["EvidenceSource"]] = relationship("EvidenceSource", back_populates="user", cascade="all, delete-orphan")
    contradictions: Mapped[List["Contradiction"]] = relationship("Contradiction", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
