from fastapi.testclient import TestClient
from app.core.config import settings
import uuid

def test_login_access_token(client: TestClient) -> None:
    """
    Test standard login endpoint handling 400 rejection (as no user exists yet in isolated DB).
    Provides testing skeleton blueprint for Auth Flows.
    """
    login_data = {
        "username": "8888888888",
        "password": "wrongpassword"
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    
    auth_token = r.json()
    assert r.status_code == 400
    assert "access_token" not in auth_token
