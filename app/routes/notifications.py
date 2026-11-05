from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models import User, Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationReadUpdate
)

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["Notifications"]
)


# Get all notifications
@router.get("/", response_model=list[NotificationResponse])
def get_notifications(
    is_read: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if is_read is not None:
        query = query.filter(
            Notification.is_read == is_read
        )

    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()

    return notifications


# Get unread notification count
@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {
        "unread_count": count
    }


# Mark one notification as read or unread
@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def update_notification_read_status(
    notification_id: int,
    read_data: NotificationReadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = read_data.is_read

    db.commit()
    db.refresh(notification)

    return notification

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }


# Mark all notifications as read
@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update(
        {Notification.is_read: True},
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": updated_count
    }