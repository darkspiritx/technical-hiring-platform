from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from fastapi import Query
from app.database.connection import get_db
from app.models import Job, User
from app.schemas.job import JobCreate, JobResponse,JobUpdate
from app.core.permissions import require_role


router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs"]
)


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):

    if (
        job_data.salary_min is not None
        and job_data.salary_max is not None
        and job_data.salary_min > job_data.salary_max
    ):
        raise HTTPException(
            status_code=422,
            detail="Minimum salary cannot exceed maximum salary"
        )

    new_job = Job(
        **job_data.model_dump(),
        recruiter_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/", response_model=list[JobResponse])
def get_all_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).filter(
        Job.is_active == True
    ).order_by(Job.created_at.desc()).all()

    return jobs



@router.get("/search", response_model=list[JobResponse])
def search_jobs(
    keyword: str = Query(min_length=2, max_length=100),
    location: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(Job).filter(
        Job.is_active == True
    )

    query = query.filter(
        Job.title.ilike(f"%{keyword}%")
    )

    if location:
        query = query.filter(
            Job.location.ilike(f"%{location}%")
        )

    return query.order_by(Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.is_active == True
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.patch("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only update your own jobs"
        )

    update_data = job_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update"
        )

    new_min = update_data.get("salary_min", job.salary_min)
    new_max = update_data.get("salary_max", job.salary_max)

    if new_min is not None and new_max is not None:
        if new_min > new_max:
            raise HTTPException(
                status_code=400,
                detail="Minimum salary cannot exceed maximum salary"
            )

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("recruiter"))
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    if job.recruiter_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own jobs"
        )

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}