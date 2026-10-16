from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey
from typing import List, Optional
from app.database.base import Base, TimestampMixin

class Opportunity(Base, TimestampMixin):
    __tablename__ = "opportunities"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    opportunity_type: Mapped[str] = mapped_column(String(50), default="internship", nullable=False) # internship, job, scholarship, competition
    location: Mapped[str] = mapped_column(String(100), default="Remote / Pakistan", nullable=False)
    external_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    deadline: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    requirements: Mapped[List["OpportunityRequirement"]] = relationship("OpportunityRequirement", back_populates="opportunity", cascade="all, delete-orphan")

class OpportunityRequirement(Base, TimestampMixin):
    __tablename__ = "opportunity_requirements"

    opportunity_id: Mapped[str] = mapped_column(String(36), ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_slug: Mapped[str] = mapped_column(String(100), ForeignKey("skills.slug", ondelete="CASCADE"), nullable=False, index=True)
    minimum_proficiency: Mapped[str] = mapped_column(String(50), default="Intermediate", nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    opportunity: Mapped["Opportunity"] = relationship("Opportunity", back_populates="requirements")
