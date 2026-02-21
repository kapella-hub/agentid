"""Credential vault endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.models.vault import Secret
from app.schemas import SecretCreate, SecretResponse, SecretUpdate, SecretValueResponse
from app.services.audit_service import log_event
from app.services.vault_service import create_secret, read_secret, rotate_secret

router = APIRouter(prefix="/secrets", tags=["vault"])


@router.post("", response_model=SecretResponse, status_code=201)
async def create_secret_endpoint(req: SecretCreate, auth: Auth, db: DB):
    secret = await create_secret(db, auth["org_id"], req.name, req.value, req.agent_id, req.description)
    await log_event(
        db, auth["org_id"], auth["type"], "secret.created", "secret", resource_id=secret.id,
    )
    return secret


@router.get("", response_model=list[SecretResponse])
async def list_secrets(auth: Auth, db: DB, agent_id: UUID | None = None):
    q = select(Secret).where(Secret.org_id == auth["org_id"])
    if agent_id:
        q = q.where(Secret.agent_id == agent_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{secret_id}", response_model=SecretValueResponse)
async def get_secret(secret_id: UUID, auth: Auth, db: DB):
    secret = await db.get(Secret, secret_id)
    if not secret or secret.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Secret not found")

    # Scope check for agent tokens
    if auth["type"] == "agent" and secret.agent_id != auth.get("agent_id"):
        raise HTTPException(status_code=403, detail="Agent cannot access this secret")

    value = await read_secret(db, secret)
    await log_event(
        db, auth["org_id"], auth["type"], "secret.read", "secret", resource_id=secret.id,
    )
    return SecretValueResponse(
        id=secret.id, org_id=secret.org_id, agent_id=secret.agent_id,
        name=secret.name, description=secret.description, version=secret.version,
        created_at=secret.created_at, value=value,
    )


@router.put("/{secret_id}", response_model=SecretResponse)
async def update_secret(secret_id: UUID, req: SecretUpdate, auth: Auth, db: DB):
    secret = await db.get(Secret, secret_id)
    if not secret or secret.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Secret not found")
    secret = await rotate_secret(db, secret, req.value)
    await log_event(
        db, auth["org_id"], auth["type"], "secret.rotated", "secret", resource_id=secret.id,
    )
    return secret


@router.delete("/{secret_id}", status_code=204)
async def delete_secret(secret_id: UUID, auth: Auth, db: DB):
    secret = await db.get(Secret, secret_id)
    if not secret or secret.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Secret not found")
    await db.delete(secret)
    await log_event(
        db, auth["org_id"], auth["type"], "secret.deleted", "secret", resource_id=secret_id,
    )
