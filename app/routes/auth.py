from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.models import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_email_verification_token
)
from app.services.email import send_verification_email

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse,
    EmailVerificationResponse
)



@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = User(
    full_name=user_data.full_name,
    email=user_data.email,
    password_hash=hash_password(user_data.password),
    role=user_data.role,
    phone_number=user_data.phone_number,
    is_verified=False,
    email_verification_token=create_email_verification_token(),
    email_verification_expires=(
        datetime.now(timezone.utc) + timedelta(minutes=30)
    )
)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    await send_verification_email(
        to_email=new_user.email,
        verification_token=new_user.email_verification_token
    )

    return new_user


@router.get(
    "/verify-email",
    response_model=EmailVerificationResponse
)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email_verification_token == token
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )

    if user.email_verification_expires is None:
        raise HTTPException(
            status_code=400,
            detail="Verification token has expired"
        )

    expiry = user.email_verification_expires

    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if expiry < datetime.now(timezone.utc):
        raise HTTPException(
        status_code=400,
        detail="Verification token has expired"
    )

    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None

    db.commit()

    return {
        "message": "Email verified successfully"
    }

@router.post("/login", response_model=TokenResponse)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is inactive"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in"
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }