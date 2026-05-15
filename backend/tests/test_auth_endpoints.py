from app.models import RefreshToken, User
from app.utils.auth import create_access_token, hash_password


def test_login_success_returns_access_and_refresh_tokens(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["expires_in"] == 1800
    assert payload["access_token"]
    assert payload["refresh_token"]


def test_login_fails_with_invalid_password(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Wrong123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_fails_for_disabled_user(client, db):
    disabled_user = User(
        username="disabled",
        email="disabled@example.com",
        full_name="Disabled User",
        role="user",
        is_active=False,
        hashed_password=hash_password("Admin123!"),
    )
    db.add(disabled_user)
    db.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "disabled", "password": "Admin123!"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is disabled"

def test_register_creates_user_for_admin(client, admin_token_headers):
    response = client.post(
        "/api/auth/register",
        headers=admin_token_headers,
        json={
            "username": "new_user",
            "email": "new_user@example.com",
            "full_name": "New User",
            "role": "user",
            "password": "NewUser123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "new_user"
    assert response.json()["role"] == "user"


def test_register_rejects_duplicate_username(client, admin_user, admin_token_headers):
    response = client.post(
        "/api/auth/register",
        headers=admin_token_headers,
        json={
            "username": "admin",
            "email": "another@example.com",
            "full_name": "Another User",
            "role": "user",
            "password": "Another123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_register_rejects_non_admin(client, user_token_headers):
    response = client.post(
        "/api/auth/register",
        headers=user_token_headers,
        json={
            "username": "forbidden_user",
            "email": "forbidden@example.com",
            "full_name": "Forbidden User",
            "role": "user",
            "password": "Forbidden123!",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_me_returns_current_user(client, admin_token_headers):
    response = client.get("/api/auth/me", headers=admin_token_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "admin"


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_refresh_rotates_token_and_revokes_old_one(client, admin_user, db):
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    old_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert refresh_response.status_code == 200
    payload = refresh_response.json()
    assert payload["refresh_token"] != old_refresh_token

    old_db_token = db.query(RefreshToken).filter(RefreshToken.user_id == admin_user.id).order_by(RefreshToken.id.asc()).first()
    assert old_db_token.revoked_at is not None
    assert old_db_token.replaced_by_token_id is not None


def test_refresh_rejects_reused_rotated_token(client, admin_user, db):
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    old_refresh_token = login_response.json()["refresh_token"]

    first_refresh = client.post("/api/auth/refresh", json={"refresh_token": old_refresh_token})
    assert first_refresh.status_code == 200

    second_refresh = client.post("/api/auth/refresh", json={"refresh_token": old_refresh_token})
    assert second_refresh.status_code == 401
    assert second_refresh.json()["detail"] == "Refresh token has already been rotated or revoked"

    active_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == admin_user.id,
        RefreshToken.revoked_at.is_(None),
    ).all()
    assert active_tokens == []


def test_logout_revokes_refresh_token(client, admin_token_headers, db):
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "Admin123!"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/auth/logout",
        headers=admin_token_headers,
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

    db_token = db.query(RefreshToken).first()
    assert db_token.revoked_at is not None


def test_logout_without_token_still_succeeds(client, admin_token_headers):
    response = client.post(
        "/api/auth/logout",
        headers=admin_token_headers,
        json={},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_admin_endpoint_rejects_missing_bearer_token(client):
    response = client.get("/api/users/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header is missing. Please provide a Bearer token."


def test_admin_endpoint_rejects_invalid_token(client):
    response = client.get(
        "/api/users/",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_admin_endpoint_rejects_non_admin_user(client, user_token_headers):
    response = client.get("/api/users/", headers=user_token_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_admin_endpoint_accepts_admin_user(client, admin_token_headers):
    response = client.get("/api/users/", headers=admin_token_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_me_accepts_directly_created_access_token(client, admin_user):
    token = create_access_token({"sub": "admin", "user_id": admin_user.id, "role": "admin"})

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == admin_user.id