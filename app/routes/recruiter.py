from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.permissions import require_role
from app.database.connection import get_db
from app.models import User, Job
from app.models.application import Application

router = APIRouter(
    prefix="/api/v1/recruiter",
    tags=["Recruiter"]
)


@router.get("/dashboard")
def recruiter_dashboard(
    current_user: User = Depends(
        require_role("recruiter")
    )
):

    return {
        "message": "Welcome to Recruiter Dashboard",
        "user": current_user.full_name,
        "role": current_user.role
    }

@router.get("/dashboard/stats")
def recruiter_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("recruiter")
    )
):
    # Total jobs created by recruiter
    total_jobs = db.query(Job).filter(
        Job.recruiter_id == current_user.id
    ).count()

    # Active jobs
    active_jobs = db.query(Job).filter(
        Job.recruiter_id == current_user.id,
        Job.is_active == True
    ).count()

    # Inactive jobs
    inactive_jobs = db.query(Job).filter(
        Job.recruiter_id == current_user.id,
        Job.is_active == False
    ).count()

    # Total applications received
    total_applications = db.query(Application).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).count()

    # Application status statistics
    status_results = db.query(
        Application.status,
        func.count(Application.id)
    ).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).group_by(
        Application.status
    ).all()

    application_stats = {
        "applied": 0,
        "reviewing": 0,
        "shortlisted": 0,
        "rejected": 0,
        "hired": 0
    }

    for application_status, count in status_results:
        if application_status in application_stats:
            application_stats[application_status] = count

    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "inactive_jobs": inactive_jobs,
        "total_applications": total_applications,
        "application_statistics": application_stats
    }

@router.get("/dashboard/recent-applications")
def recruiter_recent_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("recruiter")
    )
):
    applications = db.query(
        Application,
        Job.title.label("job_title")
    ).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).order_by(
        Application.created_at.desc()
    ).limit(10).all()

    return [
        {
            "application_id": application.id,
            "candidate_id": application.candidate_id,
            "job_id": application.job_id,
            "job_title": job_title,
            "status": application.status,
            "applied_at": application.created_at
        }
        for application, job_title in applications
    ]

@router.get("/dashboard/job-performance")
def recruiter_job_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("recruiter")
    )
):
    results = db.query(
        Job.id,
        Job.title,
        Job.is_active,
        func.count(Application.id).label("total_applications")
    ).outerjoin(
        Application,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == current_user.id
    ).group_by(
        Job.id,
        Job.title,
        Job.is_active
    ).order_by(
        Job.id.desc()
    ).all()

    return [
        {
            "job_id": job_id,
            "job_title": title,
            "is_active": is_active,
            "total_applications": total_applications
        }
        for job_id, title, is_active, total_applications in results
    ]