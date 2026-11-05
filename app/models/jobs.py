from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Job(Base):

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    employment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    experience_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    salary_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    salary_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    recruiter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )