from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Float, ForeignKey
from typing import List, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.skill import Skill
    from app.models.evidence import ClaimEvidenceLink
    from app.models.contradiction import Contradiction
    from app.models.audit import HumanVerification

class Claim(Base, TimestampMixin):
    __tablename__ = "claims"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_slug: Mapped[str] = mapped_column(String(100), ForeignKey("skills.slug", ondelete="CASCADE"), nullable=False, index=True)
    
    # Claim specifics
    stated_proficiency: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False) # Beginner, Intermediate, Advanced, Expert
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    claim_type: Mapped[str] = mapped_column(String(50), default="USER_CLAIM", nullable=False) # USER_CLAIM, AI_INFERRED, EVIDENCE_SUPPORTED, HUMAN_VERIFIED
    current_status: Mapped[str] = mapped_column(String(50), default="UNSUPPORTED", nullable=False) # UNSUPPORTED, SELF_REPORTED, AI_INFERRED, PARTIALLY_SUPPORTED, EVIDENCE_SUPPORTED, HUMAN_VERIFIED
    
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    justification_summary: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="claims")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="claims")
    evidence_links: Mapped[List["ClaimEvidenceLink"]] = relationship("ClaimEvidenceLink", back_populates="claim", cascade="all, delete-orphan")
    contradictions: Mapped[List["Contradiction"]] = relationship("Contradiction", back_populates="claim", cascade="all, delete-orphan")
    human_verifications: Mapped[List["HumanVerification"]] = relationship("HumanVerification", back_populates="claim", cascade="all, delete-orphan")
