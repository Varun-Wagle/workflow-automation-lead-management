from pydantic import BaseModel, Field

from app.schemas.lead import LeadResponse


class QualificationResponse(BaseModel):
    """API response containing persisted lead and qualification results."""

    lead: LeadResponse

    rule_score: int = Field(ge=0, le=100)
    priority: str

    score_breakdown: dict[str, int]

    missing_information: list[str]
    unconfigured_criteria: list[str]
    unrecognized_values: list[str]