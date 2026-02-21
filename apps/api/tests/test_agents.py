"""Tests for agent CRUD."""

import pytest
from httpx import AsyncClient


async def _register(client: AsyncClient, slug: str = "test-agents") -> str:
    resp = await client.post("/v1/auth/register", json={
        "org_name": "Test", "org_slug": slug,
        "email": f"{slug}@test.com", "password": "securepass123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_agent_crud(client: AsyncClient):
    token = await _register(client, "agent-crud")
    h = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post("/v1/agents", json={"name": "my-bot", "description": "A test bot"}, headers=h)
    assert resp.status_code == 201
    agent_id = resp.json()["id"]

    # List
    resp = await client.get("/v1/agents", headers=h)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Get
    resp = await client.get(f"/v1/agents/{agent_id}", headers=h)
    assert resp.status_code == 200
    assert resp.json()["name"] == "my-bot"

    # Update
    resp = await client.patch(f"/v1/agents/{agent_id}", json={"description": "updated"}, headers=h)
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated"

    # Delete
    resp = await client.delete(f"/v1/agents/{agent_id}", headers=h)
    assert resp.status_code == 204

    # Verify deleted
    resp = await client.get("/v1/agents", headers=h)
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_agent_token(client: AsyncClient):
    token = await _register(client, "agent-token")
    h = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/v1/agents", json={"name": "token-bot"}, headers=h)
    agent_id = resp.json()["id"]

    resp = await client.post(f"/v1/agents/{agent_id}/tokens", json={"scopes": ["messages:read"]}, headers=h)
    assert resp.status_code == 201
    assert resp.json()["token"]
    assert resp.json()["scopes"] == ["messages:read"]
