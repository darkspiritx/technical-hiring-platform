from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine

# Import models before create_all
from app.models import (
    User,
    Job,
    Application,
    CandidateProfile,
    Notification,
    RecruiterProfile
)

# Import routers
from app.routes.auth import router as auth_router
from app.routes.user import router as users_router
from app.routes.recruiter import router as recruiter_router
from app.routes.candidate import router as candidate_router
from app.routes.jobs import router as jobs_router
from app.routes import applications
from app.routes import candidate_profile
from app.routes import resume
from app.routes import notifications
from app.routes import admin
from app.routes.recruiter_profile import router as recruiter_profile_router

app = FastAPI(
    title="AI Technical Hiring Platform",
    description="AI-powered technical recruitment and assessment system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(recruiter_router)
app.include_router(candidate_router)
app.include_router(jobs_router)
app.include_router(applications.router)
app.include_router(candidate_profile.router)
app.include_router(resume.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(recruiter_profile_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Technical Hiring Platform",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/api/v1/info")
def platform_info():
    return {
        "project": "Technical Hiring Platform",
        "version": "1.0.0",
        "backend": "FastAPI",
        "database": "PostgreSQL"
    }
@app.get("/health/db")
def database_health():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": "PostgreSQL"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
