from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Float, Integer, ForeignKey, JSON
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.skill import Skill
    from app.models.claim import Claim

class EvidenceSource(Base, TimestampMixin):
    __tablename__ = "evidence_sources"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # pdf, docx, github_repo, transcript, certificate
    uri: Mapped[str] = mapped_column(String(500), nullable=False)
    file_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True) # Cryptographic checksum
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="evidence_sources")
    evidence_items: Mapped[List["EvidenceItem"]] = relationship("EvidenceItem", back_populates="source", cascade="all, delete-orphan")

class EvidenceItem(Base, TimestampMixin):
    __tablename__ = "evidence_items"

    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("evidence_sources.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_slug: Mapped[str] = mapped_column(String(100), ForeignKey("skills.slug", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Exact provenance coordinates
    byte_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    byte_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    line_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    evidence_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # YYYY-MM-DD or date string
    
    # Quality metrics
    directness_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False) # 0.0 - 1.0
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    strength_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    verification_status: Mapped[str] = mapped_column(String(50), default="AI_INFERRED", nullable=False)

    # Relationships
    source: Mapped["EvidenceSource"] = relationship("EvidenceSource", back_populates="evidence_items")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="evidence_items")
    claim_links: Mapped[List["ClaimEvidenceLink"]] = relationship("ClaimEvidenceLink", back_populates="evidence_item", cascade="all, delete-orphan")

class ClaimEvidenceLink(Base, TimestampMixin):
    __tablename__ = "claim_evidence_links"

    claim_id: Mapped[str] = mapped_column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("evidence_items.id", ondelete="CASCADE"), nullable=False, index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    relevance_rationale: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    claim: Mapped["Claim"] = relationship("Claim", back_populates="evidence_links")
    evidence_item: Mapped["EvidenceItem"] = relationship("EvidenceItem", back_populates="claim_links")
