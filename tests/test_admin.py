
from fastapi import status

from app.main import app
from app.database.connection import get_db


def create_admin_and_login(client):
    # First create a candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Admin",
            "email": "admin@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    # Access the same SQLite test database used by client
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)

    try:
        from app.models import User

        admin = db.query(User).filter(
            User.email == "admin@test.com"
        ).first()

        admin.role = "admin"
        db.commit()

    finally:
        db_generator.close()

    # Login as admin
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "TestPassword123"
        }
    )

    return response.json()["access_token"]


def create_candidate_and_login(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Candidate",
            "email": "candidate@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "candidate@test.com",
            "password": "TestPassword123"
        }
    )

    return response.json()["access_token"]


def test_admin_dashboard(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "admin"


def create_user_and_login(client, email, role):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": "TestPassword123",
            "role": role
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "TestPassword123"
        }
    )

    return response.json()["access_token"]


def test_candidate_cannot_access_admin_dashboard(client):
    token = create_candidate_and_login(client)

    response = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_dashboard_without_token(client):
    response = client.get("/api/v1/admin/dashboard")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_admin_dashboard_stats(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_users" in data
    assert "total_candidates" in data
    assert "total_recruiters" in data
    assert "total_jobs" in data
    assert "active_jobs" in data
    assert "total_applications" in data

def test_admin_get_all_users(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_admin_deactivate_user(client):
    token = create_admin_and_login(client)

    # Create another candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Another Candidate",
            "email": "another@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    users_response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    user = next(
        user for user in users_response.json()
        if user["email"] == "another@test.com"
    )

    response = client.patch(
        f"/api/v1/admin/users/{user['id']}/status",
        params={"is_active": "false"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False

def test_admin_delete_user(client):
    token = create_admin_and_login(client)

    # Create another candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Delete Candidate",
            "email": "delete@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    users_response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    user = next(
        user for user in users_response.json()
        if user["email"] == "delete@test.com"
    )

    response = client.delete(
        f"/api/v1/admin/users/{user['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

def test_admin_get_user_details(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    user = next(
        user for user in response.json()
        if user["email"] == "admin@test.com"
    )

    detail_response = client.get(
        f"/api/v1/admin/users/{user['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert detail_response.status_code == 200
    assert detail_response.json()["email"] == "admin@test.com"

def test_admin_search_users(client):
    token = create_admin_and_login(client)

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Mohit Test",
            "email": "mohitsearch@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    response = client.get(
        "/api/v1/admin/users/search",
        params={"keyword": "Mohit"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    users = response.json()

    assert len(users) >= 1
    assert any(user["email"] == "mohitsearch@test.com" for user in users)

def test_admin_search_jobs(client):
    token = create_admin_and_login(client)

    # Create recruiter
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Recruiter",
            "email": "recruiter@test.com",
            "password": "TestPassword123",
            "role": "recruiter"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recruiter@test.com",
            "password": "TestPassword123"
        }
    )

    recruiter_token = login_response.json()["access_token"]

    # Create job
    client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer with FastAPI experience.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        },
        headers={"Authorization": f"Bearer {recruiter_token}"}
    )

    response = client.get(
        "/api/v1/admin/jobs/search",
        params={"keyword": "Python"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    jobs = response.json()

    assert len(jobs) >= 1
    assert any(
        job["title"] == "Python Backend Developer"
        for job in jobs
    )

def test_admin_search_applications(client):
    token = create_admin_and_login(client)

    # Create recruiter
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Recruiter",
            "email": "apprecruiter@test.com",
            "password": "TestPassword123",
            "role": "recruiter"
        }
    )

    recruiter_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "apprecruiter@test.com",
            "password": "TestPassword123"
        }
    )

    recruiter_token = recruiter_login.json()["access_token"]

    # Create job
    job_response = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Developer",
            "description": "Python backend developer required for testing.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        },
        headers={"Authorization": f"Bearer {recruiter_token}"}
    )

    job_id = job_response.json()["id"]

    # Create candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Candidate",
            "email": "appcandidate@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    candidate_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "appcandidate@test.com",
            "password": "TestPassword123"
        }
    )

    candidate_token = candidate_login.json()["access_token"]

    # Apply for job,
        
    application_response = client.post(
        "/api/v1/applications/",
        json={"job_id": job_id},
        headers={"Authorization": f"Bearer {candidate_token}"}
    )

    assert application_response.status_code == 201

    # Search application by job ID
    response = client.get(
        "/api/v1/admin/applications/search",
        params={"job_id": job_id},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    applications = response.json()

    assert len(applications) == 1
    assert applications[0]["job_id"] == job_id

def test_admin_search_candidate_profiles(client):
    token = create_admin_and_login(client)

    # Create candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Profile Candidate",
            "email": "profile@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "profile@test.com",
            "password": "TestPassword123"
        }
    )

    candidate_token = login_response.json()["access_token"]

    # Create candidate profile
    profile_response = client.post(
        "/api/v1/candidate/profile/",
        json={
            "headline": "Python Backend Developer",
            "bio": "Interested in backend development",
            "skills": "Python, FastAPI, SQL",
            "education": "BCA",
            "experience": "Fresher"
        },
        headers={"Authorization": f"Bearer {candidate_token}"}
    )

    assert profile_response.status_code in (200, 201)

    # Search candidate profile
    response = client.get(
    "/api/v1/admin/candidate-profiles/search",
    params={"keyword": "FastAPI"},
    headers={"Authorization": f"Bearer {token}"}
)


    assert response.status_code == 200

    profiles = response.json()

    assert len(profiles) >= 1
    assert any(
        "FastAPI" in profile["skills"]
        for profile in profiles
    )

def test_admin_search_notifications(client):
    token = create_admin_and_login(client)

    # Create recruiter
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Notification Recruiter",
            "email": "notification@test.com",
            "password": "TestPassword123",
            "role": "recruiter"
        }
    )

    recruiter_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "notification@test.com",
            "password": "TestPassword123"
        }
    )

    recruiter_token = recruiter_login.json()["access_token"]

    # Create job
    job_response = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Notification Test Job",
            "description": "Backend developer required for notification testing.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        },
        headers={"Authorization": f"Bearer {recruiter_token}"}
    )

    job_id = job_response.json()["id"]

    # Create candidate
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Notification Candidate",
            "email": "notificationcandidate@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    candidate_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "notificationcandidate@test.com",
            "password": "TestPassword123"
        }
    )

    candidate_token = candidate_login.json()["access_token"]

    # Apply for job (this creates a notification)
    application_response = client.post(
        "/api/v1/applications/",
        json={"job_id": job_id},
        headers={"Authorization": f"Bearer {candidate_token}"}
    )

    assert application_response.status_code == 201

    # Search notifications
    response = client.get(
        "/api/v1/admin/notifications/search",
        params={"keyword": "application"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_admin_get_all_jobs(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/jobs",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_get_job_details(client):
    admin_token = create_admin_and_login(client)

    recruiter_token = create_user_and_login(
        client,
        "jobdetails@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    job_id = job_response.json()["id"]

    response = client.get(
        f"/api/v1/admin/jobs/{job_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == job_id

def test_admin_job_employment_distribution(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/jobs/employment-distribution",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_jobs" in data
    assert "distribution" in data
    assert isinstance(data["total_jobs"], int)
    assert isinstance(data["distribution"], list)

def test_admin_job_monthly_trend(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/jobs/monthly-trend",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_admin_update_job_status(client):
    admin_token = create_admin_and_login(client)

    recruiter_token = create_user_and_login(
        client,
        "jobstatus@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    job_id = job_response.json()["id"]

    response = client.patch(
        f"/api/v1/admin/jobs/{job_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"is_active": False}
    )

    assert response.status_code == 200

def test_admin_update_job(client):
    admin_token = create_admin_and_login(client)

    recruiter_token = create_user_and_login(
        client,
        "jobupdate@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    job_id = job_response.json()["id"]

    response = client.patch(
        f"/api/v1/admin/jobs/{job_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Senior Python Developer"
        }
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Senior Python Developer"

def test_admin_delete_job(client):
    admin_token = create_admin_and_login(client)

    recruiter_token = create_user_and_login(
        client,
        "jobdelete@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    job_id = job_response.json()["id"]

    response = client.delete(
        f"/api/v1/admin/jobs/{job_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200

def test_admin_get_all_applications(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/applications",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_application_stats(client):
    token = create_admin_and_login(client)

    response = client.get(
        "/api/v1/admin/applications/stats",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_admin_update_application_status(client):
    admin_token = create_admin_and_login(client)

    recruiter_token = create_user_and_login(
        client,
        "appstatus_recruiter@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter_token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    candidate_token = create_candidate_and_login(client)

    application_response = client.post(
        "/api/v1/applications/",
        headers={"Authorization": f"Bearer {candidate_token}"},
        json={
            "job_id": job_response.json()["id"],
            "cover_letter": "I am interested in this job."
        }
    )

    application_id = application_response.json()["id"]

    response = client.patch(
        f"/api/v1/admin/applications/{application_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "shortlisted"}
    )

    assert response.status_code == 200