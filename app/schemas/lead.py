from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


LeadStatus = Literal["new", "contacted", "qualified", "converted", "lost"]
LeadPriority = Literal["low", "medium", "high"]


class LeadCreate(BaseModel):
    """Validate data submitted when creating a lead."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    company_name: str = Field(min_length=1, max_length=200)
    contact_name: str = Field(min_length=1, max_length=150)

    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=30)

    industry: str | None = Field(default=None, max_length=100)
    company_size: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=150)

    source: str = Field(default="website", min_length=1, max_length=50)

    @model_validator(mode="after")
    def require_contact_method(self) -> "LeadCreate":
        """Require at least one contact method."""
        if not self.email and not self.phone:
            raise ValueError("At least one of email or phone is required.")

        return self


class LeadUpdate(BaseModel):
    """Validate partial updates to an existing lead."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    company_name: str | None = Field(default=None, min_length=1, max_length=200)
    contact_name: str | None = Field(default=None, min_length=1, max_length=150)

    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=30)

    industry: str | None = Field(default=None, max_length=100)
    company_size: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=150)

    status: LeadStatus | None = None
    priority: LeadPriority | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "LeadUpdate":
        """Validate supplied fields and reject empty updates."""

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        if "company_name" in self.model_fields_set:
            if self.company_name is None:
                raise ValueError("Company name cannot be null.")

        if "contact_name" in self.model_fields_set:
            if self.contact_name is None:
                raise ValueError("Contact name cannot be null.")

        if (
            self.email is None
            and "email" in self.model_fields_set
            and self.phone is None
            and "phone" in self.model_fields_set
        ):
            raise ValueError("At least one contact method is required.")

        return self


class LeadResponse(BaseModel):
    """Define the public representation of a stored lead."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_name: str
    contact_name: str
    email: str | None
    phone: str | None
    industry: str | None
    company_size: str | None
    location: str | None
    source: str
    status: LeadStatus
    priority: LeadPriority
    ai_score: int | None = Field(default=None, ge=0, le=100)
    ai_summary: str | None
    created_at: datetime
    updated_at: datetime
