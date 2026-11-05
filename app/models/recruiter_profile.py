
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class RecruiterProfile(Base):

    __tablename__ = "recruiter_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    company_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    company_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    designation: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    company_website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    company_location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
