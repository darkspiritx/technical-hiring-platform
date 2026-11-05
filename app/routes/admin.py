from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.core.permissions import require_role
from app.database.connection import get_db

from app.models import (
    User,
    Job,
    Application,
    CandidateProfile,
    Notification
)

from app.schemas.user import AdminUserResponse
from app.schemas.job import JobUpdate, JobResponse
from app.schemas.application import ApplicationStatusUpdate

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "message": "Welcome to Admin Dashboard",
        "user": current_user.full_name,
        "role": current_user.role
    }

@router.get("/dashboard/stats")
def admin_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    total_users = db.query(User).count()

    total_candidates = db.query(User).filter(
        User.role == "candidate"
    ).count()

    total_recruiters = db.query(User).filter(
        User.role == "recruiter"
    ).count()

    total_jobs = db.query(Job).count()

    active_jobs = db.query(Job).filter(
        Job.is_active == True
    ).count()

    total_applications = db.query(Application).count()

    return {
        "total_users": total_users,
        "total_candidates": total_candidates,
        "total_recruiters": total_recruiters,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_applications": total_applications
    }

@router.get(
    "/users",
    response_model=list[AdminUserResponse]
)
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    users = db.query(User).order_by(
        User.created_at.desc()
    ).all()

    return users


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot deactivate their own account"
        )

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return {
        "message": "User status updated successfully",
        "user_id": user.id,
        "is_active": user.is_active
    }

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Admin cannot delete their own account"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }

@router.get("/jobs")
def get_all_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    jobs = db.query(Job).order_by(
        Job.created_at.desc()
    ).all()

    return jobs

@router.patch("/jobs/{job_id}/status")
def update_job_status(
    job_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job.is_active = is_active

    db.commit()
    db.refresh(job)

    return {
        "message": "Job status updated successfully",
        "job_id": job.id,
        "is_active": job.is_active
    }

@router.get("/applications")
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    applications = db.query(Application).order_by(
        Application.created_at.desc()
    ).all()

    return applications

@router.get("/applications/stats")
def get_application_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    total_applications = db.query(Application).count()

    applied = db.query(Application).filter(
        Application.status == "applied"
    ).count()

    reviewing = db.query(Application).filter(
        Application.status == "reviewing"
    ).count()

    shortlisted = db.query(Application).filter(
        Application.status == "shortlisted"
    ).count()

    rejected = db.query(Application).filter(
        Application.status == "rejected"
    ).count()

    hired = db.query(Application).filter(
        Application.status == "hired"
    ).count()

    return {
        "total_applications": total_applications,
        "applied": applied,
        "reviewing": reviewing,
        "shortlisted": shortlisted,
        "rejected": rejected,
        "hired": hired
    }

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }

@router.get("/candidate-profiles")
def get_all_candidate_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    profiles = db.query(CandidateProfile).order_by(
        CandidateProfile.updated_at.desc()
    ).all()

    return profiles

@router.get("/notifications")
def get_all_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    notifications = db.query(Notification).order_by(
        Notification.created_at.desc()
    ).all()

    return notifications

@router.get("/recruiter-stats")
def get_recruiter_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    recruiters = db.query(
        User.id,
        User.full_name,
        User.email,
        func.count(Job.id).label("total_jobs"),
        func.count(Application.id).label("total_applications")
    ).outerjoin(
        Job, Job.recruiter_id == User.id
    ).outerjoin(
        Application, Application.job_id == Job.id
    ).filter(
        User.role == "recruiter"
    ).group_by(
        User.id,
        User.full_name,
        User.email
    ).all()

    return [
        {
            "recruiter_id": recruiter.id,
            "full_name": recruiter.full_name,
            "email": recruiter.email,
            "total_jobs": recruiter.total_jobs,
            "total_applications": recruiter.total_applications
        }
        for recruiter in recruiters
    ]

@router.get("/candidate-stats")
def get_candidate_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    candidates = db.query(
        User.id,
        User.full_name,
        User.email,
        func.count(Application.id).label("total_applications")
    ).outerjoin(
        Application, Application.candidate_id == User.id
    ).filter(
        User.role == "candidate"
    ).group_by(
        User.id,
        User.full_name,
        User.email
    ).all()

    return [
        {
            "candidate_id": candidate.id,
            "full_name": candidate.full_name,
            "email": candidate.email,
            "total_applications": candidate.total_applications
        }
        for candidate in candidates
    ]

@router.get(
    "/users/search",
    response_model=list[AdminUserResponse]
)
def search_users(   
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
        users = db.query(User).filter(
        (User.full_name.ilike(f"%{keyword}%")) |
        (User.email.ilike(f"%{keyword}%"))
    ).order_by(
        User.created_at.desc()
    ).all()

        return users

@router.get("/jobs/search")
def search_jobs(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    jobs = db.query(Job).filter(
        (Job.title.ilike(f"%{keyword}%")) |
        (Job.location.ilike(f"%{keyword}%")) |
        (Job.description.ilike(f"%{keyword}%"))
    ).order_by(
        Job.created_at.desc()
    ).all()

    return jobs

@router.get("/applications/search")
def search_applications(
    candidate_id: int | None = None,
    job_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    query = db.query(Application)

    if candidate_id is not None:
        query = query.filter(
            Application.candidate_id == candidate_id
        )

    if job_id is not None:
        query = query.filter(
            Application.job_id == job_id
        )

    if status is not None:
        query = query.filter(
            Application.status == status
        )

    applications = query.order_by(
        Application.created_at.desc()
    ).all()

    return applications

@router.get("/candidate-profiles/search")
def search_candidate_profiles(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    search_term = f"%{keyword}%"

    profiles = db.query(CandidateProfile).filter(
        or_(
            CandidateProfile.headline.ilike(search_term),
            CandidateProfile.bio.ilike(search_term),
            CandidateProfile.skills.ilike(search_term),
            CandidateProfile.education.ilike(search_term),
            CandidateProfile.experience.ilike(search_term)
        )
    ).order_by(
        CandidateProfile.updated_at.desc()
    ).all()

    return profiles

@router.get("/notifications/search")
def search_notifications(
    keyword: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    search_term = f"%{keyword}%"

    notifications = db.query(Notification).filter(
        or_(
            Notification.title.ilike(search_term),
            Notification.message.ilike(search_term),
            Notification.notification_type.ilike(search_term)
        )
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return notifications

@router.delete("/candidate-profiles/{profile_id}")
def delete_candidate_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == profile_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Candidate profile deleted successfully"
    }

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": "Notification deleted successfully"
    }

@router.patch(
    "/jobs/{job_id}",
    response_model=JobResponse
)
def admin_update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    update_data = job_data.model_dump(exclude_unset=True)

    if (
        "salary_min" in update_data
        and "salary_max" in update_data
    ):
        if update_data["salary_min"] > update_data["salary_max"]:
            raise HTTPException(
                status_code=400,
                detail="Minimum salary cannot exceed maximum salary"
            )

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job

@router.patch("/applications/{application_id}/status")
def admin_update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    old_status = application.status
    new_status = status_data.status

    application.status = new_status

    notification = Notification(
        user_id=application.candidate_id,
        title="Application Status Updated",
        message=(
            f"Your application status has changed "
            f"from {old_status} to {new_status} "
            f"for application ID {application.id}."
        ),
        notification_type="application_status"
    )

    db.add(notification)
    db.commit()
    db.refresh(application)

    return application

@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@router.get("/jobs/{job_id:int}", response_model=JobResponse)
def get_admin_job_details(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.get("/applications/{application_id:int}")
def get_admin_application_details(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application

@router.get("/candidate-profiles/{profile_id}")
def get_admin_candidate_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.id == profile_id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    return profile

@router.get("/notifications/{notification_id}")
def get_admin_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return notification

@router.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return {
        "message": "Application deleted successfully"
    }

@router.get("/applications/status-distribution")
def application_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        Application.status,
        func.count(Application.id).label("total")
    ).group_by(
        Application.status
    ).all()

    total_applications = sum(
        result.total for result in results
    )

    distribution = []

    for result in results:
        percentage = (
            round((result.total / total_applications) * 100, 2)
            if total_applications > 0
            else 0
        )

        distribution.append({
            "status": result.status,
            "total": result.total,
            "percentage": percentage
        })

    return {
        "total_applications": total_applications,
        "distribution": distribution
    }


@router.get("/jobs/employment-distribution")
def jobs_employment_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        Job.employment_type,
        func.count(Job.id).label("total")
    ).group_by(
        Job.employment_type
    ).all()

    total_jobs = sum(result.total for result in results)

    distribution = []

    for result in results:
        percentage = (
            round((result.total / total_jobs) * 100, 2)
            if total_jobs > 0
            else 0
        )

        distribution.append({
            "employment_type": result.employment_type,
            "total": result.total,
            "percentage": percentage
        })

    return {
        "total_jobs": total_jobs,
        "distribution": distribution
    }


@router.get("/jobs/employment-distribution")
def jobs_employment_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        Job.employment_type,
        func.count(Job.id).label("total")
    ).group_by(
        Job.employment_type
    ).all()

    total_jobs = sum(result.total for result in results)

    distribution = []

    for result in results:
        percentage = (
            round((result.total / total_jobs) * 100, 2)
            if total_jobs > 0
            else 0
        )

        distribution.append({
            "employment_type": result.employment_type,
            "total": result.total,
            "percentage": percentage
        })

    return {
        "total_jobs": total_jobs,
        "distribution": distribution
    }

@router.get("/top-recruiters")
def top_recruiters(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        User.id,
        User.full_name,
        User.email,
        func.count(func.distinct(Job.id)).label("total_jobs")
    ).outerjoin(
        Job, Job.recruiter_id == User.id
    ).filter(
        User.role == "recruiter"
    ).group_by(
        User.id,
        User.full_name,
        User.email
    ).order_by(
        func.count(Job.id).desc()
    ).limit(10).all()

    return [
        {
            "recruiter_id": result.id,
            "full_name": result.full_name,
            "email": result.email,
            "total_jobs": result.total_jobs
        }
        for result in results
    ]

@router.get("/top-jobs")
def top_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        Job.id,
        Job.title,
        Job.location,
        func.count(Application.id).label("total_applications")
    ).outerjoin(
        Application, Application.job_id == Job.id
    ).group_by(
        Job.id,
        Job.title,
        Job.location
    ).order_by(
        func.count(Application.id).desc()
    ).limit(10).all()

    return [
        {
            "job_id": result.id,
            "title": result.title,
            "location": result.location,
            "total_applications": result.total_applications
        }
        for result in results
    ]

@router.get("/applications/monthly-trend")
def monthly_application_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        func.to_char(
            func.date_trunc("month", Application.created_at),
            "YYYY-MM"
        ).label("month"),
        func.count(Application.id).label("total_applications")
    ).group_by(
        func.date_trunc("month", Application.created_at)
    ).order_by(
        func.date_trunc("month", Application.created_at)
    ).all()

    return [
        {
            "month": result.month,
            "total_applications": result.total_applications
        }
        for result in results
    ]

@router.get("/jobs/monthly-trend")
def monthly_job_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    results = db.query(
        func.to_char(
            func.date_trunc("month", Job.created_at),
            "YYYY-MM"
        ).label("month"),
        func.count(Job.id).label("total_jobs")
    ).group_by(
        func.date_trunc("month", Job.created_at)
    ).order_by(
        func.date_trunc("month", Job.created_at)
    ).all()

    return [
        {
            "month": result.month,
            "total_jobs": result.total_jobs
        }
        for result in results
    ]



