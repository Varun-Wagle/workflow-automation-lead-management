import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.schemas.qualification import QualificationResponse
from app.services.lead_service import (
    LeadPersistenceError,
    LeadUpdateError,
    create_lead,
    get_lead_by_id,
    get_leads,
    update_lead,
)
from app.services.qualification_service import (
    QualificationPersistenceError,
    qualify_lead,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead_endpoint(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
) -> LeadResponse:
    """Create a new lead."""
    try:
        lead = create_lead(db, lead_data)
        return LeadResponse.model_validate(lead)

    except LeadPersistenceError as exc:
        logger.exception("Lead persistence failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the lead at this time.",
        ) from exc


@router.get("", response_model=list[LeadResponse])
def list_leads_endpoint(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        min_length=1,
    ),
    priority: str | None = Query(
        default=None,
        min_length=1,
    ),
    location: str | None = Query(
        default=None,
        min_length=1,
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[LeadResponse]:
    """Retrieve leads with optional filters and pagination."""
    try:
        leads = get_leads(
            db,
            status=status_filter,
            priority=priority,
            location=location,
            limit=limit,
            offset=offset,
        )
        return [LeadResponse.model_validate(lead) for lead in leads]

    except SQLAlchemyError as exc:
        logger.exception("Lead retrieval failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve leads at this time.",
        ) from exc


@router.post(
    "/{lead_id}/qualify",
    response_model=QualificationResponse,
)
def qualify_lead_endpoint(
    lead_id: UUID,
    db: Session = Depends(get_db),
) -> QualificationResponse:
    """Calculate and persist rule-based lead qualification."""
    try:
        qualification = qualify_lead(db, lead_id)

        if qualification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found.",
            )

        lead, result = qualification

        return QualificationResponse(
            lead=LeadResponse.model_validate(lead),
            rule_score=result.rule_score,
            priority=result.priority,
            score_breakdown=result.score_breakdown,
            missing_information=list(result.missing_information),
            unconfigured_criteria=list(result.unconfigured_criteria),
            unrecognized_values=list(result.unrecognized_values),
        )

    except QualificationPersistenceError as exc:
        logger.exception("Lead qualification persistence failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to qualify the lead at this time.",
        ) from exc


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead_endpoint(
    lead_id: UUID,
    db: Session = Depends(get_db),
) -> LeadResponse:
    """Retrieve a single lead by UUID."""
    try:
        lead = get_lead_by_id(db, lead_id)

        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found.",
            )

        return LeadResponse.model_validate(lead)

    except SQLAlchemyError as exc:
        logger.exception("Lead retrieval failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve the lead at this time.",
        ) from exc


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead_endpoint(
    lead_id: UUID,
    lead_data: LeadUpdate,
    db: Session = Depends(get_db),
) -> LeadResponse:
    """Partially update an existing lead."""
    try:
        lead = update_lead(db, lead_id, lead_data)

        if lead is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found.",
            )

        return LeadResponse.model_validate(lead)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    except LeadUpdateError as exc:
        logger.exception("Lead update failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update the lead at this time.",
        ) from exc