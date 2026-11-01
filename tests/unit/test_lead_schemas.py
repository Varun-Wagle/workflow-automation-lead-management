import pytest
from pydantic import ValidationError

from app.schemas.lead import LeadCreate


def test_valid_lead_with_email():
    lead = LeadCreate(
        company_name="Apex Manufacturing",
        contact_name="Anita Sharma",
        email="anita@example.com",
        location="Raipur",
    )

    assert lead.company_name == "Apex Manufacturing"
    assert lead.email == "anita@example.com"
    assert lead.location == "Raipur"
    assert lead.source == "website"


def test_valid_lead_with_phone_only():
    lead = LeadCreate(
        company_name="Central Industries",
        contact_name="Rahul Verma",
        phone="+919876543210",
    )

    assert lead.phone == "+919876543210"


def test_lead_requires_contact_method():
    with pytest.raises(ValidationError):
        LeadCreate(
            company_name="Apex Manufacturing",
            contact_name="Anita Sharma",
        )


def test_lead_rejects_invalid_email():
    with pytest.raises(ValidationError):
        LeadCreate(
            company_name="Apex Manufacturing",
            contact_name="Anita Sharma",
            email="not-an-email",
        )


def test_lead_rejects_blank_company_name():
    with pytest.raises(ValidationError):
        LeadCreate(
            company_name="   ",
            contact_name="Anita Sharma",
            email="anita@example.com",
        )


def test_lead_rejects_unexpected_fields():
    with pytest.raises(ValidationError):
        LeadCreate.model_validate({
            "company_name": "Apex Manufacturing",
            "contact_name": "Anita Sharma",
            "email": "anita@example.com",
            "status": "converted",
        })

def test_lead_update_rejects_null_company_name():
    from app.schemas.lead import LeadUpdate

    with pytest.raises(ValidationError):
        LeadUpdate(company_name=None)


def test_lead_update_rejects_null_contact_name():
    from app.schemas.lead import LeadUpdate

    with pytest.raises(ValidationError):
        LeadUpdate(contact_name=None)


def test_lead_update_rejects_blank_company_name():
    from app.schemas.lead import LeadUpdate

    with pytest.raises(ValidationError):
        LeadUpdate(company_name="   ")


def test_lead_update_accepts_partial_priority_update():
    from app.schemas.lead import LeadUpdate

    update = LeadUpdate(priority="high")

    assert update.priority == "high"
    assert "company_name" not in update.model_fields_set
