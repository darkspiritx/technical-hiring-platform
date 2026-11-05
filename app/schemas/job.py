from pydantic import BaseModel, Field, ConfigDict


class JobCreate(BaseModel):

    title: str = Field(min_length=3, max_length=150)

    description: str = Field(min_length=20)

    location: str = Field(min_length=2, max_length=100)

    employment_type: str = Field(
        pattern="^(full-time|part-time|internship|contract)$"
    )

    experience_level: str = Field(
        pattern="^(fresher|junior|mid|senior)$"
    )

    salary_min: int | None = Field(default=None, ge=0)

    salary_max: int | None = Field(default=None, ge=0)


class JobResponse(BaseModel):

    id: int
    title: str
    description: str
    location: str
    employment_type: str
    experience_level: str
    salary_min: int | None
    salary_max: int | None
    is_active: bool
    recruiter_id: int

    model_config = ConfigDict(from_attributes=True)

class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, min_length=20)
    location: str | None = Field(default=None, min_length=2, max_length=100)

    employment_type: str | None = Field(
        default=None,
        pattern="^(full-time|part-time|internship|contract)$"
    )

    experience_level: str | None = Field(
        default=None,
        pattern="^(fresher|junior|mid|senior)$"
    )

    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

