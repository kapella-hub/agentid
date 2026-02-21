"""FastAPI dependency injection helpers."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token, hash_token
from app.models.auth import ApiKey, Org, User

bearer_scheme = HTTPBearer(auto_error=False)

DB = Annotated[AsyncSession, Depends(get_db)]


async def get_current_auth(
    db: DB,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> dict:
    """Resolve bearer token to an auth context dict.

    Returns {"type": "user"|"api_key"|"agent", "org_id": UUID, ...}
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials

    # Try JWT first
    payload = decode_token(token)
    if payload:
        token_type = payload.get("type", "user")
        if token_type == "agent":
            return {
                "type": "agent",
                "org_id": UUID(payload["org_id"]),
                "agent_id": UUID(payload["sub"]),
                "scopes": payload.get("scopes", []),
            }
        # User JWT
        user = await db.get(User, UUID(payload["sub"]))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"type": "user", "org_id": user.org_id, "user_id": user.id, "role": user.role}

    # Try API key
    token_hash = hash_token(token)
    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == token_hash, ApiKey.revoked_at.is_(None))
    )
    api_key = result.scalar_one_or_none()
    if api_key is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"type": "api_key", "org_id": api_key.org_id, "scopes": list(api_key.scopes or [])}


Auth = Annotated[dict, Depends(get_current_auth)]


def require_scope(scope: str):
    """Dependency that checks the auth context has a required scope."""

    async def _check(auth: Auth) -> dict:
        if auth["type"] == "user":
            return auth  # users have full access via role
        if scope not in auth.get("scopes", []):
            raise HTTPException(status_code=403, detail=f"Missing scope: {scope}")
        return auth

    return _check
