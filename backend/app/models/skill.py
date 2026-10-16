from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from typing import List, TYPE_CHECKING
from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.claim import Claim
    from app.models.evidence import EvidenceItem

class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # e.g. Languages, Databases, Web, DevOps
    taxonomy_path: Mapped[str] = mapped_column(String(255), nullable=False) # e.g. Software Development/Languages/Java
    level_depth: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="skill")
    evidence_items: Mapped[List["EvidenceItem"]] = relationship("EvidenceItem", back_populates="skill")

class SkillRelationship(Base, TimestampMixin):
    __tablename__ = "skill_relationships"

    parent_slug: Mapped[str] = mapped_column(String(100), ForeignKey("skills.slug", ondelete="CASCADE"), nullable=False, index=True)
    child_slug: Mapped[str] = mapped_column(String(100), ForeignKey("skills.slug", ondelete="CASCADE"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(50), default="parent_child", nullable=False) # parent_child, prerequisite, related
