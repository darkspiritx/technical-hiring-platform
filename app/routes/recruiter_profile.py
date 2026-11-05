from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.permissions import require_role
from app.models import User
from app.models.recruiter_profile import RecruiterProfile

from app.schemas.recruiter_profile import (
    RecruiterProfileCreate,
    RecruiterProfileUpdate,
    RecruiterProfileResponse
)


router = APIRouter(
    prefix="/api/v1/recruiter/profile",
    tags=["Recruiter Profile"]
)


@router.post(
    "",
    response_model=RecruiterProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_recruiter_profile(
    profile_data: RecruiterProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):

    existing_profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Recruiter profile already exists"
        )

    new_profile = RecruiterProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get(
    "",
    response_model=RecruiterProfileResponse
)
def get_recruiter_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):

    profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )

    return profile


@router.patch(
    "",
    response_model=RecruiterProfileResponse
)
def update_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):

    profile = db.query(RecruiterProfile).filter(
        RecruiterProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )

    update_data = profile_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile