from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    notification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )