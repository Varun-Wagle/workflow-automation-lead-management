from dataclasses import dataclass
from typing import Any

from app.qualification_config.qualification import QualificationConfig


@dataclass(frozen=True)
class QualificationResult:
    """Structured result returned by the scoring engine."""

    rule_score: int
    priority: str
    score_breakdown: dict[str, int]
    missing_information: tuple[str, ...]
    unconfigured_criteria: tuple[str, ...]
    unrecognized_values: tuple[str, ...]


def _normalize(value: Any) -> str:
    """Normalize values for case-insensitive comparison."""
    return str(value).strip().casefold() if value is not None else ""


def calculate_priority(
    score: int,
    config: QualificationConfig,
) -> str:
    """Classify a score using configured priority thresholds."""

    if not 0 <= score <= 100:
        raise ValueError("Score must be between 0 and 100.")

    if score <= config.thresholds.low_max:
        return "low"

    if score <= config.thresholds.medium_max:
        return "medium"

    return "high"


def calculate_rule_score(
    lead: Any,
    config: QualificationConfig,
) -> QualificationResult:
    """
    Calculate a deterministic lead score.

    Accepts either a dictionary or an object with lead attributes.
    Business-specific values come exclusively from the supplied
    qualification configuration.
    """

    def get_value(field: str) -> Any:
        if isinstance(lead, dict):
            return lead.get(field)

        return getattr(lead, field, None)

    weights = config.weights

    breakdown: dict[str, int] = {}
    missing: list[str] = []
    unconfigured: list[str] = []
    unrecognized: list[str] = []

    # 1. Company size
    company_size = _normalize(get_value("company_size"))

    if not company_size:
        breakdown["company_size"] = 0
        missing.append("company_size")
    else:
        size_scores = {
            _normalize(key): value
            for key, value in config.company_size_scores.items()
        }

        if company_size in size_scores:
            breakdown["company_size"] = size_scores[company_size]
        else:
            breakdown["company_size"] = 0
            unrecognized.append("company_size")

    # 2. Industry relevance
    industry = _normalize(get_value("industry"))

    if not industry:
        breakdown["industry_relevance"] = 0
        missing.append("industry")
    elif not config.target_industries:
        breakdown["industry_relevance"] = 0
        unconfigured.append("industry_relevance")
    else:
        target_industries = {
            _normalize(value)
            for value in config.target_industries
        }

        breakdown["industry_relevance"] = (
            weights.industry_relevance
            if industry in target_industries
            else 0
        )

    # 3. Contact completeness
    email = _normalize(get_value("email"))
    phone = _normalize(get_value("phone"))

    if email and phone:
        breakdown["contact_completeness"] = (
            weights.contact_completeness
        )
    elif email or phone:
        breakdown["contact_completeness"] = round(
            weights.contact_completeness * 2 / 3
        )
    else:
        breakdown["contact_completeness"] = 0
        missing.append("contact_method")

    # 4. Location relevance
    location = _normalize(get_value("location"))

    if not config.target_locations:
        breakdown["location_relevance"] = 0
        unconfigured.append("location_relevance")
    elif not location:
        breakdown["location_relevance"] = 0
        missing.append("location")
    else:
        target_locations = {
            _normalize(value)
            for value in config.target_locations
        }

        breakdown["location_relevance"] = (
            weights.location_relevance
            if location in target_locations
            else 0
        )

    # 5. Lead source
    source = _normalize(get_value("source"))

    source_scores = {
        _normalize(key): value
        for key, value in config.lead_source_scores.items()
    }

    if not source:
        breakdown["lead_source"] = 0
        missing.append("source")
    elif source in source_scores:
        breakdown["lead_source"] = source_scores[source]
    else:
        breakdown["lead_source"] = 0
        unrecognized.append("source")

    # 6. Business information
    product = _normalize(get_value("interested_product"))
    message = _normalize(get_value("message"))

    business_weights = config.business_information_weights

    product_points = (
        business_weights.get("interested_product", 0)
        if product
        else 0
    )

    message_points = (
        business_weights.get("message", 0)
        if len(message) >= 20
        else 0
    )

    breakdown["business_information"] = (
        product_points + message_points
    )

    if not product:
        missing.append("interested_product")

    if len(message) < 20:
        missing.append("message")

    # Final score
    rule_score = sum(breakdown.values())

    if not 0 <= rule_score <= 100:
        raise ValueError("Calculated score is outside the valid range.")

    priority = calculate_priority(rule_score, config)

    return QualificationResult(
        rule_score=rule_score,
        priority=priority,
        score_breakdown=breakdown,
        missing_information=tuple(sorted(set(missing))),
        unconfigured_criteria=tuple(sorted(set(unconfigured))),
        unrecognized_values=tuple(sorted(set(unrecognized))),
    )