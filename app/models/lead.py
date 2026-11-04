import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Lead(Base):
    """SQLAlchemy model for a business prospect."""

    __tablename__ = "leads"

    __table_args__ = (
        CheckConstraint(
            "length(btrim(company_name)) > 0",
            name="leads_company_name_not_blank",
        ),
        CheckConstraint(
            "length(btrim(contact_name)) > 0",
            name="leads_contact_name_not_blank",
        ),
        CheckConstraint(
            """
            NULLIF(btrim(email), '') IS NOT NULL
            OR NULLIF(btrim(phone), '') IS NOT NULL
            """,
            name="leads_contact_method_required",
        ),
        CheckConstraint(
            "length(btrim(source)) > 0",
            name="leads_source_not_blank",
        ),
        CheckConstraint(
            "status IN ('new', 'contacted', 'qualified', 'converted', 'lost')",
            name="leads_status_valid",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="leads_priority_valid",
        ),
        CheckConstraint(
            "ai_score IS NULL OR ai_score BETWEEN 0 AND 100",
            name="leads_ai_score_valid",
        ),
        CheckConstraint(
            "rule_score IS NULL OR rule_score BETWEEN 0 AND 100",
            name="leads_rule_score_range_check",
        ),
        Index("leads_status_created_at_idx", "status", "created_at"),
        Index("leads_priority_created_at_idx", "priority", "created_at"),
        Index("leads_location_idx", "location"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[Optional[str]] = mapped_column(String(254), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        server_default=text("'website'"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'new'"),
    )

    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default=text("'medium'"),
    )

    interested_product: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    rule_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    qualification_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=text("now()"),
    )