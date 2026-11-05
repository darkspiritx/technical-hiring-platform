def create_user_and_login(client, email, role):
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Recruiter",
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


def test_recruiter_dashboard(client):
    token = create_user_and_login(
        client,
        "recruiter@test.com",
        "recruiter"
    )

    response = client.get(
        "/api/v1/recruiter/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["role"] == "recruiter"
    assert response.json()["message"] == "Welcome to Recruiter Dashboard"


def test_candidate_cannot_access_recruiter_dashboard(client):
    token = create_user_and_login(
        client,
        "candidate@test.com",
        "candidate"
    )

    response = client.get(
        "/api/v1/recruiter/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_recruiter_dashboard_without_token(client):
    response = client.get("/api/v1/recruiter/dashboard")

    assert response.status_code == 401

def test_recruiter_dashboard_stats(client):
    token = create_user_and_login(
        client,
        "stats_recruiter@test.com",
        "recruiter"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create first active job
    client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    # Create second active job
    client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "FastAPI Developer",
            "description": "Looking for a FastAPI developer.",
            "location": "Prayagraj",
            "employment_type": "internship",
            "experience_level": "junior",
            "salary_min": 10000,
            "salary_max": 20000
        }
    )

    response = client.get(
        "/api/v1/recruiter/dashboard/stats",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_jobs"] == 2
    assert data["active_jobs"] == 2
    assert data["inactive_jobs"] == 0
    assert data["total_applications"] == 0
    assert data["application_statistics"]["applied"] == 0

def test_recruiter_recent_applications(client):
    recruiter_token = create_user_and_login(
        client,
        "recent_recruiter@test.com",
        "recruiter"
    )

    candidate_token = create_user_and_login(
        client,
        "recent_candidate@test.com",
        "candidate"
    )

    recruiter_headers = {
        "Authorization": f"Bearer {recruiter_token}"
    }

    candidate_headers = {
        "Authorization": f"Bearer {candidate_token}"
    }

    # Recruiter creates a job
    job_response = client.post(
        "/api/v1/jobs/",
        headers=recruiter_headers,
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    assert job_response.status_code == 201

    job_id = job_response.json()["id"]

    # Candidate applies for the job
    application_response = client.post(
        "/api/v1/applications/",
        headers=candidate_headers,
        json={
            "job_id": job_id,
            "cover_letter": "I am interested in this Python role."
        }
    )

    assert application_response.status_code == 201

    # Recruiter checks recent applications
    response = client.get(
        "/api/v1/recruiter/dashboard/recent-applications",
        headers=recruiter_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["job_id"] == job_id
    assert data[0]["job_title"] == "Python Backend Developer"
    assert data[0]["status"] == "applied"

def test_recruiter_job_performance(client):
    token = create_user_and_login(
        client,
        "performance_recruiter@test.com",
        "recruiter"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    job_response = client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "FastAPI Backend Developer",
            "description": "Looking for an experienced FastAPI developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "junior",
            "salary_min": 20000,
            "salary_max": 40000
        }
    )

    assert job_response.status_code == 201

    response = client.get(
        "/api/v1/recruiter/dashboard/job-performance",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["job_title"] == "FastAPI Backend Developer"
    assert data[0]["is_active"] is True
    assert data[0]["total_applications"] == 0