from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadPersistenceError(Exception):
    """Raised when a lead cannot be persisted."""


class LeadUpdateError(Exception):
    """Raised when a lead update cannot be completed."""


def create_lead(db: Session, lead_data: LeadCreate) -> Lead:
    """Create and persist a new lead."""
    lead = Lead(**lead_data.model_dump())

    try:
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    except SQLAlchemyError as exc:
        db.rollback()
        raise LeadPersistenceError(
            "The lead could not be saved."
        ) from exc


def get_leads(
    db: Session,
    *,
    status: str | None = None,
    priority: str | None = None,
    location: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Lead]:
    """Retrieve leads with optional filters and pagination."""

    statement = select(Lead)

    if status is not None:
        statement = statement.where(Lead.status == status)

    if priority is not None:
        statement = statement.where(Lead.priority == priority)

    if location is not None:
        statement = statement.where(Lead.location == location)

    statement = (
        statement
        .order_by(Lead.created_at.desc(), Lead.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return list(db.scalars(statement).all())


def get_lead_by_id(db: Session, lead_id: UUID) -> Lead | None:
    """Retrieve a single lead by its UUID."""
    return db.get(Lead, lead_id)


def update_lead(
    db: Session,
    lead_id: UUID,
    lead_data: LeadUpdate,
) -> Lead | None:
    """Update an existing lead with the supplied fields."""

    try:
        lead = db.get(Lead, lead_id)

        if lead is None:
            return None

        update_data = lead_data.model_dump(exclude_unset=True)

        # Determine the resulting contact information.
        new_email = update_data.get("email", lead.email)
        new_phone = update_data.get("phone", lead.phone)

        if not new_email and not new_phone:
            raise ValueError(
                "At least one contact method is required."
            )

        for field, value in update_data.items():
            setattr(lead, field, value)

        db.commit()
        db.refresh(lead)

        return lead

    except SQLAlchemyError as exc:
        db.rollback()
        raise LeadUpdateError(
            "The lead could not be updated."
        ) from exc