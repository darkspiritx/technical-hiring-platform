def test_get_my_profile(client):
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

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Profile Candidate"
    assert response.json()["email"] == "profile@test.com"
    assert "password_hash" not in response.json()


def test_get_my_profile_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_get_my_profile_invalid_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid_token"
        }
    )

    assert response.status_code == 401