from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ApplicationCreate(BaseModel):
    job_id: int = Field(gt=0)
    cover_letter: str | None = Field(
        default=None,
        max_length=2000
    )


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    cover_letter: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(
        pattern="^(reviewing|shortlisted|rejected|hired)$"
    )