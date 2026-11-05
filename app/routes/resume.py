from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import CandidateProfile, User
from app.core.permissions import require_role
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/api/v1/candidate/resume",
    tags=["Candidate Resume"]
)

UPLOAD_DIR = Path("uploads/resumes")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Check PDF extension
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Read file and check size
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 5 MB"
        )

    # Check actual PDF signature
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # Find candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Please create your candidate profile first"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    filename = f"{uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / filename

    # Save file
    try:
        file_path.write_bytes(content)

        # Update database
        profile.resume_path = str(file_path).replace("\\", "/")
        db.commit()
        db.refresh(profile)

    except Exception:
        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Resume upload failed"
        )

    finally:
        await file.close()

    return {
        "message": "Resume uploaded successfully",
        "resume_path": profile.resume_path
    }

@router.get("/download")
def download_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if not profile or not profile.resume_path:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    upload_root = UPLOAD_DIR.resolve()
    file_path = Path(profile.resume_path).resolve()

    # Prevent access outside the resume directory
    if not file_path.is_relative_to(upload_root):
        raise HTTPException(
            status_code=400,
            detail="Invalid resume path"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="my_resume.pdf"
    )