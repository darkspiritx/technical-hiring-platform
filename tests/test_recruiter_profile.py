from tests.test_recruiter import create_user_and_login


def test_recruiter_can_create_profile(client):

    token = create_user_and_login(
        client,
        "recruiter_profile_create@test.com",
        "recruiter"
    )

    response = client.post(
        "/api/v1/recruiter/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "company_name": "Tech Solutions",
            "company_description": "Software development company",
            "designation": "HR Manager",
            "company_website": "https://example.com",
            "company_location": "Prayagraj"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["company_name"] == "Tech Solutions"
    assert data["designation"] == "HR Manager"
    assert data["company_location"] == "Prayagraj"


def test_recruiter_can_view_own_profile(client):

    token = create_user_and_login(
        client,
        "recruiter_profile_view@test.com",
        "recruiter"
    )

    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/recruiter/profile",
        headers=headers,
        json={"company_name": "My Company"}
    )

    response = client.get(
        "/api/v1/recruiter/profile",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "My Company"


def test_recruiter_can_update_profile(client):

    token = create_user_and_login(
        client,
        "recruiter_profile_update@test.com",
        "recruiter"
    )

    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/recruiter/profile",
        headers=headers,
        json={
            "company_name": "Old Company",
            "designation": "HR"
        }
    )

    response = client.patch(
        "/api/v1/recruiter/profile",
        headers=headers,
        json={
            "company_name": "Updated Company",
            "designation": "Senior HR Manager"
        }
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "Updated Company"
    assert response.json()["designation"] == "Senior HR Manager"


def test_recruiter_cannot_create_duplicate_profile(client):

    token = create_user_and_login(
        client,
        "recruiter_profile_duplicate@test.com",
        "recruiter"
    )

    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/recruiter/profile",
        headers=headers,
        json={"company_name": "First Company"}
    )

    response = client.post(
        "/api/v1/recruiter/profile",
        headers=headers,
        json={"company_name": "Second Company"}
    )

    assert response.status_code == 409


def test_recruiter_profile_not_found(client):

    token = create_user_and_login(
        client,
        "recruiter_profile_missing@test.com",
        "recruiter"
    )

    response = client.get(
        "/api/v1/recruiter/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


def test_candidate_cannot_access_recruiter_profile(client):

    token = create_user_and_login(
        client,
        "candidate_access_recruiter_profile@test.com",
        "candidate"
    )

    response = client.get(
        "/api/v1/recruiter/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_recruiter_profile_without_token(client):

    response = client.get(
        "/api/v1/recruiter/profile"
    )

    assert response.status_code == 401