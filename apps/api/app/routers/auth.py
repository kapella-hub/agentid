"""Auth endpoints: register, login, API keys."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.models.auth import ApiKey, Org, User
from app.schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    LoginRequest,
    OrgResponse,
    RegisterRequest,
    TokenResponse,
)
from app.services.audit_service import log_event

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: DB):
    # Check uniqueness
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    existing_org = await db.execute(select(Org).where(Org.slug == req.org_slug))
    if existing_org.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Org slug already taken")

    org = Org(name=req.org_name, slug=req.org_slug)
    db.add(org)
    await db.flush()

    user = User(
        org_id=org.id,
        email=req.email,
        password_hash=hash_password(req.password),
        role="owner",
    )
    db.add(user)
    await db.flush()

    await log_event(db, org.id, "user", "org.created", "org", actor_id=user.id, resource_id=org.id)

    token = create_access_token({"sub": str(user.id), "type": "user"})
    return TokenResponse(access_token=token)


@router.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: DB):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "type": "user"})
    return TokenResponse(access_token=token)


@router.get("/orgs/me", response_model=OrgResponse)
async def get_current_org(auth: Auth, db: DB):
    org = await db.get(Org, auth["org_id"])
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    return org


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=201)
async def create_api_key(req: ApiKeyCreate, auth: Auth, db: DB):
    raw_key, key_hash, key_prefix = generate_api_key()
    api_key = ApiKey(
        org_id=auth["org_id"],
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=req.name,
        scopes=req.scopes,
    )
    db.add(api_key)
    await db.flush()

    await log_event(
        db, auth["org_id"], auth["type"], "api_key.created", "api_key",
        resource_id=api_key.id,
    )

    return ApiKeyResponse(
        id=api_key.id,
        key_prefix=api_key.key_prefix,
        name=api_key.name,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        key=raw_key,
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(auth: Auth, db: DB):
    result = await db.execute(
        select(ApiKey).where(ApiKey.org_id == auth["org_id"], ApiKey.revoked_at.is_(None))
    )
    return result.scalars().all()


@router.delete("/api-keys/{key_id}", status_code=204)
async def revoke_api_key(key_id: UUID, auth: Auth, db: DB):
    api_key = await db.get(ApiKey, key_id)
    if not api_key or api_key.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked_at = datetime.now(timezone.utc)
    await log_event(
        db, auth["org_id"], auth["type"], "api_key.revoked", "api_key", resource_id=key_id,
    )
