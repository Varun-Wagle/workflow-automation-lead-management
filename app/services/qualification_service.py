from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.scoring import (
    QualificationResult,
    calculate_rule_score,
)
from app.models.lead import Lead
from app.qualification_config.qualification import APEXFLOW_CONFIG


class QualificationPersistenceError(Exception):
    """Raised when qualification results cannot be persisted."""


def qualify_lead(
    db: Session,
    lead_id: UUID,
) -> tuple[Lead, QualificationResult] | None:
    """
    Calculate and persist rule-based qualification results.

    Returns None if the lead does not exist.
    """

    try:
        lead = db.get(Lead, lead_id)

        if lead is None:
            return None

        # Calculate the deterministic rule-based score.
        result = calculate_rule_score(
            lead,
            APEXFLOW_CONFIG,
        )

        # Update qualification fields.
        lead.rule_score = result.rule_score
        lead.priority = result.priority
        lead.qualification_updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(lead)

        return lead, result

    except SQLAlchemyError as exc:
        db.rollback()

        raise QualificationPersistenceError(
            "Unable to persist lead qualification results."
        ) from exc