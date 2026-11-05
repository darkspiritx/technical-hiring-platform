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

def test_update_my_profile(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Profile Candidate",
            "email": "profileupdate@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "profileupdate@test.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "full_name": "Updated Candidate",
            "phone_number": "9876543210"
        }
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Candidate"
    assert response.json()["phone_number"] == "9876543210"



def test_change_password_success(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Password User",
            "email": "password@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "password@test.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/users/me/change-password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "TestPassword123",
            "new_password": "NewPassword123"
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    # Old password should not work
    old_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "password@test.com",
            "password": "TestPassword123"
        }
    )

    assert old_login.status_code == 401

    # New password should work
    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "password@test.com",
            "password": "NewPassword123"
        }
    )

    assert new_login.status_code == 200

def test_change_password_incorrect_current_password(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Wrong Password User",
            "email": "wrongpassword@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpassword@test.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/users/me/change-password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "WrongPassword123",
            "new_password": "NewPassword123"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect"

def test_change_password_same_password(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Same Password User",
            "email": "samepassword@test.com",
            "password": "TestPassword123",
            "role": "candidate"
        }
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "samepassword@test.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        "/api/v1/users/me/change-password",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "current_password": "TestPassword123",
            "new_password": "TestPassword123"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "New password must be different"