from fastapi import APIRouter, Depends

from app.core.permissions import require_role
from app.models import User

router = APIRouter(
    prefix="/api/v1/candidate",
    tags=["Candidate"]
)


@router.get("/dashboard")
def candidate_dashboard(
    current_user: User = Depends(
        require_role("candidate")
    )
):

    return {
        "message": "Welcome to Candidate Dashboard",
        "user": current_user.full_name,
        "role": current_user.role
    }

