import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register user
    reg_payload = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "SecurePassword123!",
        "role": "SALES_REP"
    }
    res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res_reg.status_code == 201
    data_reg = res_reg.json()
    assert data_reg["email"] == "newuser@example.com"
    assert data_reg["role"] == "SALES_REP"

    # 2. Login user
    res_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "newuser@example.com", "password": "SecurePassword123!"}
    )
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get /me user profile
    res_me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    me_data = res_me.json()
    assert me_data["email"] == "newuser@example.com"


@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrongpassword"}
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Incorrect email or password"
