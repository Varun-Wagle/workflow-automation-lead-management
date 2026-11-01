from fastapi.testclient import TestClient
from unittest.mock import patch
from uuid import uuid4
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy import select
from app.services.lead_service import LeadPersistenceError

from app.database import SessionLocal
from app.main import app
from app.models.lead import Lead


client = TestClient(app)

def create_test_leads():
    """Create isolated test leads directly in the database."""
    test_id = uuid4().hex[:12]

    test_data = [
        {
            "company_name": f"Filtering Alpha {test_id}",
            "contact_name": "Test Contact Alpha",
            "email": f"alpha.{test_id}@example.com",
            "status": "new",
            "priority": "high",
            "location": "Raipur",
        },
        {
            "company_name": f"Filtering Beta {test_id}",
            "contact_name": "Test Contact Beta",
            "email": f"beta.{test_id}@example.com",
            "status": "contacted",
            "priority": "medium",
            "location": "Bilaspur",
        },
        {
            "company_name": f"Filtering Gamma {test_id}",
            "contact_name": "Test Contact Gamma",
            "email": f"gamma.{test_id}@example.com",
            "status": "new",
            "priority": "low",
            "location": "Raipur",
        },
    ]

    created_ids = []

    try:
        with SessionLocal() as db:
            for data in test_data:
                lead = Lead(**data)
                db.add(lead)
                db.flush()
                created_ids.append(str(lead.id))

            db.commit()

        return test_id, created_ids

    except Exception:
        with SessionLocal() as db:
            if created_ids:
                db.query(Lead).filter(
                    Lead.id.in_(created_ids)
                ).delete(synchronize_session=False)
                db.commit()
        raise

def create_test_lead_for_update():
    """Create an isolated lead for update tests."""
    test_id = uuid4().hex[:12]

    lead = Lead(
        company_name=f"Update Test Company {test_id}",
        contact_name="Test Contact",
        email=f"update.{test_id}@example.com",
        industry="Manufacturing",
        location="Raipur",
    )

    with SessionLocal() as db:
        db.add(lead)
        db.commit()
        db.refresh(lead)

        return str(lead.id)


def delete_test_lead(lead_id: str):
    """Remove a test lead after verification."""
    with SessionLocal() as db:
        lead = db.get(Lead, lead_id)
        if lead is not None:
            db.delete(lead)
            db.commit()

def test_create_lead_rejects_missing_contact_method():
    response = client.post(
        "/api/v1/leads",
        json={
            "company_name": "Apex Manufacturing",
            "contact_name": "Anita Sharma",
        },
    )

    assert response.status_code == 422


def test_create_lead_rejects_invalid_email():
    response = client.post(
        "/api/v1/leads",
        json={
            "company_name": "Apex Manufacturing",
            "contact_name": "Anita Sharma",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422


def test_create_lead_rejects_unexpected_fields():
    response = client.post(
        "/api/v1/leads",
        json={
            "company_name": "Apex Manufacturing",
            "contact_name": "Anita Sharma",
            "email": "anita@example.com",
            "status": "converted",
        },
    )

    assert response.status_code == 422


def test_create_lead_persists_record():
    payload = {
        "company_name": "Apex Manufacturing Test",
        "contact_name": "Anita Sharma",
        "email": "anita.test@example.com",
        "industry": "Manufacturing",
        "location": "Raipur",
    }

    lead_id = None

    try:
        response = client.post("/api/v1/leads", json=payload)

        assert response.status_code == 201

        result = response.json()

        assert result["company_name"] == payload["company_name"]
        assert result["contact_name"] == payload["contact_name"]
        assert result["email"] == payload["email"]
        assert result["location"] == payload["location"]
        assert result["status"] == "new"
        assert result["priority"] == "medium"

        lead_id = result["id"]

        with SessionLocal() as db:
            stored_lead = db.get(Lead, lead_id)

            assert stored_lead is not None
            assert stored_lead.company_name == payload["company_name"]

    finally:
        if lead_id is not None:
            with SessionLocal() as db:
                stored_lead = db.get(Lead, lead_id)

                if stored_lead is not None:
                    db.delete(stored_lead)
                    db.commit()

def test_create_lead_returns_500_when_persistence_fails():
    payload = {
        "company_name": "Apex Manufacturing Error Test",
        "contact_name": "Anita Sharma",
        "email": "anita.error@example.com",
    }

    with patch(
        "app.api.v1.leads.create_lead",
        side_effect=LeadPersistenceError("The lead could not be saved."),
    ):
        response = client.post("/api/v1/leads", json=payload)

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to save the lead at this time."
    }

def test_list_leads_returns_list():
    response = client.get("/api/v1/leads")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_leads_rejects_invalid_limit():
    response = client.get("/api/v1/leads?limit=0")

    assert response.status_code == 422


def test_list_leads_rejects_negative_offset():
    response = client.get("/api/v1/leads?offset=-1")

    assert response.status_code == 422


def test_list_leads_returns_empty_list_for_unmatched_location():
    response = client.get(
        "/api/v1/leads",
        params={"location": "NoSuchLocationForTest"},
    )

    assert response.status_code == 200
    assert response.json() == []

# Test A — Filter by status
def test_list_leads_filters_by_status():
    test_id, created_ids = create_test_leads()

    try:
        response = client.get(
            "/api/v1/leads",
            params={"status": "new"},
        )

        assert response.status_code == 200

        results = response.json()
        matching = [
            lead for lead in results
            if lead["company_name"].startswith(f"Filtering ")
            and lead["id"] in created_ids
        ]

        assert len(matching) == 2
        assert all(lead["status"] == "new" for lead in matching)

    finally:
        with SessionLocal() as db:
            db.query(Lead).filter(
                Lead.id.in_(created_ids)
            ).delete(synchronize_session=False)
            db.commit()

# Test B — Filter by priority
def test_list_leads_filters_by_priority():
    test_id, created_ids = create_test_leads()

    try:
        response = client.get(
            "/api/v1/leads",
            params={"priority": "high"},
        )

        assert response.status_code == 200

        matching = [
            lead for lead in response.json()
            if lead["id"] in created_ids
        ]

        assert len(matching) == 1
        assert matching[0]["priority"] == "high"

    finally:
        with SessionLocal() as db:
            db.query(Lead).filter(
                Lead.id.in_(created_ids)
            ).delete(synchronize_session=False)
            db.commit()

# Test C — Filter by location
def test_list_leads_filters_by_location():
    test_id, created_ids = create_test_leads()

    try:
        response = client.get(
            "/api/v1/leads",
            params={"location": "Bilaspur"},
        )

        assert response.status_code == 200

        matching = [
            lead for lead in response.json()
            if lead["id"] in created_ids
        ]

        assert len(matching) == 1
        assert matching[0]["location"] == "Bilaspur"

    finally:
        with SessionLocal() as db:
            db.query(Lead).filter(
                Lead.id.in_(created_ids)
            ).delete(synchronize_session=False)
            db.commit()

# Test D — Pagination
def test_list_leads_paginates_results():
    test_id, created_ids = create_test_leads()

    try:
        with SessionLocal() as db:
            expected_ids = [
                str(lead.id)
                for lead in db.scalars(
                    select(Lead)
                    .where(Lead.id.in_(created_ids))
                    .order_by(Lead.created_at.desc(), Lead.id.desc())
                ).all()
            ]

        first_response = client.get(
            "/api/v1/leads",
            params={"limit": 2, "offset": 0},
        )

        second_response = client.get(
            "/api/v1/leads",
            params={"limit": 2, "offset": 2},
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200

        first_page_ids = [
            lead["id"]
            for lead in first_response.json()
            if lead["id"] in created_ids
        ]

        second_page_ids = [
            lead["id"]
            for lead in second_response.json()
            if lead["id"] in created_ids
        ]

        assert first_page_ids == expected_ids[:2]
        assert second_page_ids == expected_ids[2:]

    finally:
        with SessionLocal() as db:
            db.query(Lead).filter(
                Lead.id.in_(created_ids)
            ).delete(synchronize_session=False)
            db.commit()

def test_get_lead_by_id_returns_lead():
    lead = Lead(
        company_name="Individual Retrieval Test",
        contact_name="Test Contact",
        email="retrieval.test@example.com",
        location="Raipur",
    )

    with SessionLocal() as db:
        db.add(lead)
        db.commit()
        db.refresh(lead)
        lead_id = str(lead.id)

    try:
        response = client.get(f"/api/v1/leads/{lead_id}")

        assert response.status_code == 200
        assert response.json()["id"] == lead_id
        assert response.json()["company_name"] == "Individual Retrieval Test"

    finally:
        with SessionLocal() as db:
            stored_lead = db.get(Lead, lead_id)
            if stored_lead is not None:
                db.delete(stored_lead)
                db.commit()

def test_get_lead_by_id_returns_404_when_not_found():
    nonexistent_id = str(uuid4())

    response = client.get(f"/api/v1/leads/{nonexistent_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Lead not found."}

def test_get_lead_by_id_rejects_invalid_uuid():
    response = client.get("/api/v1/leads/invalid-uuid")

    assert response.status_code == 422

def test_update_lead_priority():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"priority": "high"},
        )

        assert response.status_code == 200
        assert response.json()["priority"] == "high"

    finally:
        delete_test_lead(lead_id)

def test_update_lead_status():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "qualified"},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "qualified"

    finally:
        delete_test_lead(lead_id)

def test_update_lead_preserves_unchanged_fields():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"priority": "high"},
        )

        assert response.status_code == 200

        result = response.json()

        assert result["priority"] == "high"
        assert result["company_name"].startswith("Update Test Company")
        assert result["contact_name"] == "Test Contact"
        assert result["email"].startswith("update.")
        assert result["location"] == "Raipur"

    finally:
        delete_test_lead(lead_id)

def test_update_lead_contact_information():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={
                "email": "updated.contact@example.com",
                "phone": "9876543210",
            },
        )

        assert response.status_code == 200

        result = response.json()

        assert result["email"] == "updated.contact@example.com"
        assert result["phone"] == "9876543210"

    finally:
        delete_test_lead(lead_id)

def test_update_lead_rejects_removing_only_contact_method():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"email": None},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "At least one contact method is required."
        )

    finally:
        delete_test_lead(lead_id)

def test_update_lead_rejects_invalid_status():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"status": "pending"},
        )

        assert response.status_code == 422

    finally:
        delete_test_lead(lead_id)

def test_update_lead_rejects_invalid_priority():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"priority": "urgent"},
        )

        assert response.status_code == 422

    finally:
        delete_test_lead(lead_id)

def test_update_lead_returns_404_when_not_found():
    nonexistent_id = str(uuid4())

    response = client.patch(
        f"/api/v1/leads/{nonexistent_id}",
        json={"priority": "high"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Lead not found."}

def test_update_lead_rejects_empty_payload():
    lead_id = create_test_lead_for_update()

    try:
        response = client.patch(
            f"/api/v1/leads/{lead_id}",
            json={},
        )

        assert response.status_code == 422

    finally:
        delete_test_lead(lead_id)

def test_update_lead_returns_500_and_rolls_back_on_persistence_failure():
    lead_id = create_test_lead_for_update()

    try:
        # Capture the original database value.
        with SessionLocal() as db:
            original_lead = db.get(Lead, lead_id)
            original_priority = original_lead.priority

        # Simulate a database commit failure during PATCH.
        with patch(
            "sqlalchemy.orm.Session.commit",
            side_effect=SQLAlchemyError("Simulated database failure."),
        ):
            response = client.patch(
                f"/api/v1/leads/{lead_id}",
                json={"priority": "high"},
            )

        # Verify that the API reports a server error.
        assert response.status_code == 500

        # Verify that the failed transaction did not change the record.
        with SessionLocal() as db:
            stored_lead = db.get(Lead, lead_id)

            assert stored_lead is not None
            assert stored_lead.priority == original_priority

    finally:
        delete_test_lead(lead_id)