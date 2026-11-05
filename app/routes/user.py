from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from sqlalchemy.orm import Session

from app.core.security import verify_password, hash_password
from app.schemas.user import PasswordChange

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):

    return current_user

@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    update_data = user_data.model_dump(exclude_unset=True)

    if "full_name" in update_data and update_data["full_name"] is None:
        raise HTTPException(
            status_code=422,
            detail="Full name cannot be null"
        )

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user

@router.patch("/me/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Verify current password
    if not verify_password(
        password_data.current_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    # Prevent using the same password
    if verify_password(
        password_data.new_password,
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=400,
            detail="New password must be different"
        )

    # Hash new password
    current_user.password_hash = hash_password(
        password_data.new_password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }