from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from typing import Optional, List, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.claim import Claim

class Contradiction(Base, TimestampMixin):
    __tablename__ = "contradictions"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("claims.id", ondelete="SET NULL"), nullable=True, index=True)
    
    contradiction_type: Mapped[str] = mapped_column(String(50), nullable=False) # EXAGGERATION, TIMELINE_OVERLAP, CONFLICTING_METRIC, GHOST_CLAIM
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    conflicting_evidence_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="contradictions")
    claim: Mapped[Optional["Claim"]] = relationship("Claim", back_populates="contradictions")
