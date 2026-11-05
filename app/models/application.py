from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False
    )

    cover_letter: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="applied",
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False
    )

    cover_letter: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="applied",
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )