"""Tests for auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register
    resp = await client.post("/v1/auth/register", json={
        "org_name": "Test Org",
        "org_slug": "test-org",
        "email": "admin@test.com",
        "password": "securepass123",
    })
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    assert token

    # Login
    resp = await client.post("/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "securepass123",
    })
    assert resp.status_code == 200
    assert resp.json()["access_token"]

    # Get org
    resp = await client.get("/v1/orgs/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["slug"] == "test-org"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/v1/auth/register", json={
        "org_name": "Org1", "org_slug": "org1",
        "email": "dup@test.com", "password": "securepass123",
    })
    resp = await client.post("/v1/auth/register", json={
        "org_name": "Org2", "org_slug": "org2",
        "email": "dup@test.com", "password": "securepass123",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient):
    resp = await client.post("/v1/auth/login", json={
        "email": "nobody@test.com", "password": "wrong",
    })
    assert resp.status_code == 401
