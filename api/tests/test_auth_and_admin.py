import uuid

from fastapi.testclient import TestClient


def test_signup_and_login_flow(client: TestClient):
    unique_email = f"testuser-{uuid.uuid4().hex[:8]}@example.com"
    signup_payload = {
        "fullname": "Test User",
        "email": unique_email,
        "password": "strongpassword123",
    }

    signup_response = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201, signup_response.text
    assert signup_response.json()["success"] is True

    sign_in_response = client.post(
        "/api/v1/auth/signin",
        json={"email": signup_payload["email"], "password": signup_payload["password"]},
    )
    assert sign_in_response.status_code == 200, sign_in_response.text


def test_admin_login_uses_settings_credentials(client: TestClient):
    from setting import settings

    response = client.post(
        "/api/v1/auth/signin",
        json={"email": settings.ONYX_ADMIN_EMAIL, "password": settings.ONYX_ADMIN_PASS},
    )

    assert response.status_code == 200, response.text
