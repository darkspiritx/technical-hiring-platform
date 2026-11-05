from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class RecruiterProfileCreate(BaseModel):

    company_name: str | None = Field(
        default=None,
        max_length=150
    )

    company_description: str | None = Field(
        default=None,
        max_length=3000
    )

    designation: str | None = Field(
        default=None,
        max_length=100
    )

    company_website: str | None = Field(
        default=None,
        max_length=255
    )

    company_location: str | None = Field(
        default=None,
        max_length=150
    )


class RecruiterProfileUpdate(BaseModel):

    company_name: str | None = Field(
        default=None,
        max_length=150
    )

    company_description: str | None = Field(
        default=None,
        max_length=3000
    )

    designation: str | None = Field(
        default=None,
        max_length=100
    )

    company_website: str | None = Field(
        default=None,
        max_length=255
    )

    company_location: str | None = Field(
        default=None,
        max_length=150
    )


class RecruiterProfileResponse(BaseModel):

    id: int
    user_id: int
    company_name: str | None
    company_description: str | None
    designation: str | None
    company_website: str | None
    company_location: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)