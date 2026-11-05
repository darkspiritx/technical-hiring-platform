from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_role

from app.models import User, Job
from app.models.application import Application
from app.models import Notification


from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate
)

router = APIRouter(
    prefix="/api/v1/applications",
    tags=["Applications"]
)

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_for_job(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Check whether job exists and is active
    job = db.query(Job).filter(
        Job.id == application_data.job_id,
        Job.is_active == True
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found or inactive"
        )

    # Prevent duplicate applications
    existing_application = db.query(Application).filter(
        Application.candidate_id == current_user.id,
        Application.job_id == application_data.job_id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=409,
            detail="You have already applied for this job"
        )

    # Create application
    new_application = Application(
        candidate_id=current_user.id,
        job_id=application_data.job_id,
        cover_letter=application_data.cover_letter
    )

    db.add(new_application)

# Create notification for recruiter
    new_notification = Notification(
    user_id=job.recruiter_id,
    title="New Job Application",
    message=f"{current_user.full_name} applied for your job: {job.title}",
    notification_type="new_application"
)
    db.add(new_notification)

    db.commit()
    db.refresh(new_application)

    return new_application

@router.get(
    "/job/{job_id}",
    response_model=list[ApplicationResponse]
)
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    # Check job ownership
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Fetch applications
    applications = db.query(Application).filter(
        Application.job_id == job_id
    ).order_by(
        Application.created_at.desc()
    ).all()

    return applications

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    application = db.query(Application).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Application.id == application_id,
        Job.recruiter_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    old_status = application.status
    new_status = status_data.status

    application.status = new_status

    candidate_notification = Notification(
    user_id=application.candidate_id,
    title="Application Status Updated",
    message=(
        f"Your application status has changed "
        f"from {old_status} to {new_status} "
        f"for application ID {application.id}."
    ),
    notification_type="application_status"
)

    db.add(candidate_notification)

    db.commit()
    db.refresh(application)

    return application

@router.get(
    "/my-applications",
    response_model=list[ApplicationResponse]
)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    applications = db.query(Application).filter(
        Application.candidate_id == current_user.id
    ).order_by(
        Application.created_at.desc()
    ).all()

    return applications

@router.get(
    "/my-applications/{application_id}",
    response_model=ApplicationResponse
)
def get_my_application_details(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.candidate_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application

@router.get("/my-applications/stats")
def get_my_application_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    applications = db.query(Application).filter(
        Application.candidate_id == current_user.id
    ).all()

    total = len(applications)

    stats = {
        "total_applications": total,
        "applied": 0,
        "reviewing": 0,
        "shortlisted": 0,
        "rejected": 0,
        "hired": 0
    }

    for application in applications:
        if application.status in stats:
            stats[application.status] += 1

    return stats