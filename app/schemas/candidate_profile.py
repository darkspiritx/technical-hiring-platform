from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CandidateProfileCreate(BaseModel):

    headline: str | None = Field(
        default=None,
        max_length=150
    )

    bio: str | None = Field(
        default=None,
        max_length=2000
    )

    skills: str | None = Field(
        default=None,
        max_length=1000
    )

    education: str | None = Field(
        default=None,
        max_length=2000
    )

    experience: str | None = Field(
        default=None,
        max_length=2000
    )


class CandidateProfileUpdate(BaseModel):

    headline: str | None = Field(
        default=None,
        max_length=150
    )

    bio: str | None = Field(
        default=None,
        max_length=2000
    )

    skills: str | None = Field(
        default=None,
        max_length=1000
    )

    education: str | None = Field(
        default=None,
        max_length=2000
    )

    experience: str | None = Field(
        default=None,
        max_length=2000
    )


class CandidateProfileResponse(BaseModel):

    id: int
    user_id: int
    headline: str | None
    bio: str | None
    skills: str | None
    education: str | None
    experience: str | None
    resume_path: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)