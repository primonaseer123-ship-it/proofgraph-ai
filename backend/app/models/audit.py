from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, JSON
from typing import Optional, Dict, Any, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.claim import Claim

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. UPLOAD_EVIDENCE, VERIFY_CLAIM, FLAG_CONTRADICTION
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False) # Claim, EvidenceItem, User
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False) # SHA-256
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

class HumanVerification(Base, TimestampMixin):
    __tablename__ = "human_verifications"

    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    verifier_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    decision: Mapped[str] = mapped_column(String(50), nullable=False) # APPROVED, REJECTED, AMENDED
    commentary: Mapped[str] = mapped_column(Text, nullable=False)
    signature_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Relationships
    claim: Mapped["Claim"] = relationship("Claim", back_populates="human_verifications")
