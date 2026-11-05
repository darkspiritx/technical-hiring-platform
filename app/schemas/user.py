from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict,Field



class UserCreate(BaseModel):

    full_name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    role: str = Field(
        pattern="^(candidate|recruiter)$"
    )
    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )
class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    phone_number: str | None = None

    model_config = {
        "from_attributes": True
    }
class UserLogin(BaseModel):

    email: EmailStr

    password: str


class TokenResponse(BaseModel):

    access_token: str

    token_type: str

class AdminUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    phone_number: str | None = None
    model_config = ConfigDict(from_attributes=True)

    
class UserUpdate(BaseModel):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=20
    )

class PasswordChange(BaseModel):

    current_password: str = Field(
        min_length=8,
        max_length=128
    )

    new_password: str = Field(
        min_length=8,
        max_length=128
    )


class EmailVerificationResponse(BaseModel):
    message: str

class PasswordReset(BaseModel):

    token: str = Field(
        min_length=20,
        max_length=255
    )

    new_password: str = Field(
        min_length=8,
        max_length=128
    )