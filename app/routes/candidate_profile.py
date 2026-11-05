from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.permissions import require_role

from app.models import User
from app.models.candidate_profile import CandidateProfile

from app.schemas.candidate_profile import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    CandidateProfileResponse
)


router = APIRouter(
    prefix="/api/v1/candidate/profile",
    tags=["Candidate Profile"]
)

@router.post(
    "/",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_candidate_profile(
    profile_data: CandidateProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):

    existing_profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Candidate profile already exists"
        )

    new_profile = CandidateProfile(
        user_id=current_user.id,
        **profile_data.model_dump()
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile

@router.get(
    "/",
    response_model=CandidateProfileResponse
)
def get_candidate_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    return profile
@router.patch(
    "/",
    response_model=CandidateProfileResponse
)
def update_candidate_profile(
    profile_data: CandidateProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile