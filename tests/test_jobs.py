from tests.test_recruiter import create_user_and_login


def test_recruiter_can_create_job(client):
    token = create_user_and_login(
        client,
        "job_create@test.com",
        "recruiter"
    )

    response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {token}"},
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

    assert response.status_code == 201
    assert response.json()["title"] == "Python Backend Developer"


def test_recruiter_can_view_all_active_jobs(client):
    token = create_user_and_login(
        client,
        "job_list@test.com",
        "recruiter"
    )

    client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    response = client.get("/api/v1/jobs/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recruiter_can_view_job_by_id(client):
    token = create_user_and_login(
        client,
        "job_detail@test.com",
        "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "FastAPI Developer",
            "description": "Looking for a FastAPI developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "junior"
        }
    )

    job_id = job_response.json()["id"]

    response = client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_recruiter_can_update_own_job(client):
    token = create_user_and_login(
        client,
        "job_update@test.com",
        "recruiter"
    )

    headers = {"Authorization": f"Bearer {token}"}

    job_response = client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    job_id = job_response.json()["id"]

    response = client.patch(
        f"/api/v1/jobs/{job_id}",
        headers=headers,
        json={"title": "Senior Python Developer"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Senior Python Developer"


def test_recruiter_cannot_update_another_recruiters_job(client):
    recruiter1 = create_user_and_login(
        client, "owner1@test.com", "recruiter"
    )

    recruiter2 = create_user_and_login(
        client, "owner2@test.com", "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter1}"},
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    job_id = job_response.json()["id"]

    response = client.patch(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {recruiter2}"},
        json={"title": "Updated Job"}
    )

    assert response.status_code == 403


def test_recruiter_can_delete_own_job(client):
    token = create_user_and_login(
        client,
        "job_delete@test.com",
        "recruiter"
    )

    headers = {"Authorization": f"Bearer {token}"}

    job_response = client.post(
        "/api/v1/jobs/",
        headers=headers,
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    job_id = job_response.json()["id"]

    response = client.delete(
        f"/api/v1/jobs/{job_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Job deleted successfully"


def test_recruiter_cannot_delete_another_recruiters_job(client):
    recruiter1 = create_user_and_login(
        client, "delete_owner1@test.com", "recruiter"
    )

    recruiter2 = create_user_and_login(
        client, "delete_owner2@test.com", "recruiter"
    )

    job_response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {recruiter1}"},
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    job_id = job_response.json()["id"]

    response = client.delete(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {recruiter2}"}
    )

    assert response.status_code == 403


def test_candidate_cannot_create_job(client):
    token = create_user_and_login(
        client,
        "job_candidate@test.com",
        "candidate"
    )

    response = client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    assert response.status_code == 403


def test_job_creation_without_token(client):
    response = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "location": "Remote",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    assert response.status_code == 401

def test_search_jobs_by_keyword(client):
    token = create_user_and_login(
        client,
        "job_search@test.com",
        "recruiter"
    )

    client.post(
        "/api/v1/jobs/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Python Backend Developer",
            "description": "Looking for a Python backend developer.",
            "location": "Prayagraj",
            "employment_type": "full-time",
            "experience_level": "fresher"
        }
    )

    response = client.get(
        "/api/v1/jobs/search?keyword=Python"
    )
    

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Backend Developer"