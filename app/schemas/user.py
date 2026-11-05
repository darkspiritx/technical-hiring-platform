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


class UserResponse(BaseModel):

    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

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

    model_config = ConfigDict(from_attributes=True)