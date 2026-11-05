from tests.test_recruiter import create_user_and_login


def test_candidate_dashboard(client):
    token = create_user_and_login(
        client,
        "dashboard_candidate@test.com",
        "candidate"
    )

    response = client.get(
        "/api/v1/candidate/dashboard",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "candidate"
    assert data["user"] == "Test Recruiter"
    assert data["message"] == "Welcome to Candidate Dashboard"


def test_recruiter_cannot_access_candidate_dashboard(client):
    token = create_user_and_login(
        client,
        "dashboard_recruiter@test.com",
        "recruiter"
    )

    response = client.get(
        "/api/v1/candidate/dashboard",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_candidate_dashboard_without_token(client):
    response = client.get(
        "/api/v1/candidate/dashboard"
    )

    assert response.status_code == 401

def test_candidate_can_view_own_applications(client):
    recruiter_token = create_user_and_login(
        client,
        "job_recruiter@test.com",
        "recruiter"
    )

    candidate_token = create_user_and_login(
        client,
        "my_application_candidate@test.com",
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
            "cover_letter": "I am interested in this position."
        }
    )

    assert application_response.status_code == 201

    # Candidate views own applications
    response = client.get(
        "/api/v1/applications/my-applications",
        headers=candidate_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["job_id"] == job_id
    assert data[0]["status"] == "applied"

def test_candidate_can_view_application_details(client):
    recruiter_token = create_user_and_login(
        client,
        "details_recruiter@test.com",
        "recruiter"
    )

    candidate_token = create_user_and_login(
        client,
        "details_candidate@test.com",
        "candidate"
    )

    recruiter_headers = {
        "Authorization": f"Bearer {recruiter_token}"
    }

    candidate_headers = {
        "Authorization": f"Bearer {candidate_token}"
    }

    job_response = client.post(
        "/api/v1/jobs/",
        headers=recruiter_headers,
        json={
            "title": "Python Developer",
            "description": "We need a Python backend developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    assert job_response.status_code == 201

    application_response = client.post(
        "/api/v1/applications/",
        headers=candidate_headers,
        json={
            "job_id": job_response.json()["id"],
            "cover_letter": "I am interested in this role."
        }
    )

    assert application_response.status_code == 201

    application_id = application_response.json()["id"]

    response = client.get(
        f"/api/v1/applications/my-applications/{application_id}",
        headers=candidate_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == application_id
    assert response.json()["status"] == "applied"

def test_candidate_cannot_view_other_candidate_application(client):
    recruiter_token = create_user_and_login(
        client,
        "other_recruiter@test.com",
        "recruiter"
    )

    candidate1_token = create_user_and_login(
        client,
        "candidate1@test.com",
        "candidate"
    )

    candidate2_token = create_user_and_login(
        client,
        "candidate2@test.com",
        "candidate"
    )

    recruiter_headers = {
        "Authorization": f"Bearer {recruiter_token}"
    }

    candidate1_headers = {
        "Authorization": f"Bearer {candidate1_token}"
    }

    candidate2_headers = {
        "Authorization": f"Bearer {candidate2_token}"
    }

    job_response = client.post(
        "/api/v1/jobs/",
        headers=recruiter_headers,
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    assert job_response.status_code == 201

    application_response = client.post(
        "/api/v1/applications/",
        headers=candidate1_headers,
        json={
            "job_id": job_response.json()["id"],
            "cover_letter": "I am interested in this job."
        }
    )

    assert application_response.status_code == 201

    application_id = application_response.json()["id"]

    response = client.get(
        f"/api/v1/applications/my-applications/{application_id}",
        headers=candidate2_headers
    )

    assert response.status_code == 404

def test_candidate_application_details(client):
    recruiter_token = create_user_and_login(
        client,
        "stats_recruiter@test.com",
        "recruiter"
    )

    candidate_token = create_user_and_login(
        client,
        "stats_candidate@test.com",
        "candidate"
    )

    recruiter_headers = {
        "Authorization": f"Bearer {recruiter_token}"
    }

    candidate_headers = {
        "Authorization": f"Bearer {candidate_token}"
    }

    job_response = client.post(
        "/api/v1/jobs/",
        headers=recruiter_headers,
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    assert job_response.status_code == 201

    application_response = client.post(
        "/api/v1/applications/",
        headers=candidate_headers,
        json={
            "job_id": job_response.json()["id"],
            "cover_letter": "I am interested in this position."
        }
    )

    assert application_response.status_code == 201

    response = client.get(
        "/api/v1/applications/my-applications/stats",
        headers=candidate_headers
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["total_applications"] == 1
    assert data["applied"] == 1
    assert data["reviewing"] == 0
    assert data["shortlisted"] == 0
    assert data["rejected"] == 0
    assert data["hired"] == 0