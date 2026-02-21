"""Tests for vault (secrets) endpoints."""

import pytest
from httpx import AsyncClient


async def _setup(client: AsyncClient) -> tuple[str, str]:
    resp = await client.post("/v1/auth/register", json={
        "org_name": "Vault Org", "org_slug": "vault-org",
        "email": "vault@test.com", "password": "securepass123",
    })
    token = resp.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    resp = await client.post("/v1/agents", json={"name": "vault-bot"}, headers=h)
    agent_id = resp.json()["id"]
    return token, agent_id


@pytest.mark.asyncio
async def test_secret_lifecycle(client: AsyncClient):
    token, agent_id = await _setup(client)
    h = {"Authorization": f"Bearer {token}"}

    # Create
    resp = await client.post("/v1/secrets", json={
        "name": "openai_key", "value": "sk-secret123", "agent_id": agent_id,
    }, headers=h)
    assert resp.status_code == 201
    secret_id = resp.json()["id"]
    assert "value" not in resp.json()  # Value not in create response

    # Read
    resp = await client.get(f"/v1/secrets/{secret_id}", headers=h)
    assert resp.status_code == 200
    assert resp.json()["value"] == "sk-secret123"
    assert resp.json()["version"] == 1

    # Update (rotate)
    resp = await client.put(f"/v1/secrets/{secret_id}", json={"value": "sk-new456"}, headers=h)
    assert resp.status_code == 200
    assert resp.json()["version"] == 2

    # Verify new value
    resp = await client.get(f"/v1/secrets/{secret_id}", headers=h)
    assert resp.json()["value"] == "sk-new456"

    # Delete
    resp = await client.delete(f"/v1/secrets/{secret_id}", headers=h)
    assert resp.status_code == 204

    # Verify gone
    resp = await client.get(f"/v1/secrets/{secret_id}", headers=h)
    assert resp.status_code == 404
