from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    headline: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    skills: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    education: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    experience: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    resume_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )