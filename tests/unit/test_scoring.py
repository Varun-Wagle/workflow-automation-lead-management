import pytest

from app.core.scoring import (
    calculate_priority,
    calculate_rule_score,
)
from app.qualification_config.qualification import (
    APEXFLOW_CONFIG,
    PriorityThresholds,
    QualificationConfig,
    ScoringWeights,
)


@pytest.fixture
def complete_lead():
    return {
        "company_name": "Apex Industries",
        "contact_name": "Rahul Sharma",
        "email": "rahul@example.com",
        "phone": "+919876543210",
        "industry": "Manufacturing",
        "company_size": "201-500",
        "location": "Raipur",
        "source": "referral",
        "interested_product": "workflow_automation",
        "message": "We need an automated sales and lead management solution.",
    }


@pytest.mark.parametrize(
    ("score", "expected_priority"),
    [
        (0, "low"),
        (39, "low"),
        (40, "medium"),
        (69, "medium"),
        (70, "high"),
        (100, "high"),
    ],
)
def test_priority_classification_boundaries(score, expected_priority):
    result = calculate_priority(score, APEXFLOW_CONFIG)

    assert result == expected_priority


@pytest.mark.parametrize("score", [-1, 101])
def test_priority_rejects_out_of_range_scores(score):
    with pytest.raises(ValueError):
        calculate_priority(score, APEXFLOW_CONFIG)


def test_complete_lead_receives_expected_score(complete_lead):
    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert result.rule_score == 80
    assert result.priority == "high"


def test_score_breakdown_is_correct(complete_lead):
    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert result.score_breakdown == {
        "company_size": 20,
        "industry_relevance": 25,
        "contact_completeness": 15,
        "location_relevance": 0,
        "lead_source": 10,
        "business_information": 10,
    }


def test_scoring_identifies_unconfigured_location(complete_lead):
    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert "location_relevance" in result.unconfigured_criteria


def test_scoring_is_case_insensitive(complete_lead):
    complete_lead["industry"] = "MANUFACTURING"
    complete_lead["source"] = "REFERRAL"

    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert result.score_breakdown["industry_relevance"] == 25
    assert result.score_breakdown["lead_source"] == 10


def test_missing_information_is_reported(complete_lead):
    complete_lead["company_size"] = None
    complete_lead["email"] = None
    complete_lead["phone"] = None
    complete_lead["interested_product"] = None
    complete_lead["message"] = None

    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert "company_size" in result.missing_information
    assert "contact_method" in result.missing_information
    assert "interested_product" in result.missing_information
    assert "message" in result.missing_information


def test_unknown_company_size_is_reported(complete_lead):
    complete_lead["company_size"] = "unknown"

    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert result.score_breakdown["company_size"] == 0
    assert "company_size" in result.unrecognized_values


def test_unknown_lead_source_is_reported(complete_lead):
    complete_lead["source"] = "unknown"

    result = calculate_rule_score(complete_lead, APEXFLOW_CONFIG)

    assert result.score_breakdown["lead_source"] == 0
    assert "source" in result.unrecognized_values


def test_configuration_rejects_invalid_scoring_weights():
    with pytest.raises(ValueError):
        ScoringWeights(company_size=30)


def test_configuration_rejects_invalid_company_size_score():
    with pytest.raises(ValueError):
        QualificationConfig(
            business_name="Invalid Business",
            company_size_scores={"201-500": 30},
        )


def test_configuration_rejects_invalid_lead_source_score():
    with pytest.raises(ValueError):
        QualificationConfig(
            business_name="Invalid Business",
            lead_source_scores={"referral": 15},
        )


def test_configuration_rejects_invalid_business_information_weights():
    with pytest.raises(ValueError):
        QualificationConfig(
            business_name="Invalid Business",
            business_information_weights={
                "interested_product": 8,
                "message": 8,
            },
        )


def test_priority_thresholds_reject_invalid_boundaries():
    with pytest.raises(ValueError):
        PriorityThresholds(
            low_max=70,
            medium_max=40,
            high_max=100,
        )
