"""Authentication & security utilities."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.hash import argon2

from app.core.config import settings

# ---------------------------------------------------------------------------
# Password hashing (Argon2id)
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    return argon2.using(memory_cost=65536, time_cost=3, parallelism=4).hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return argon2.verify(password, hashed)


# ---------------------------------------------------------------------------
# API key generation
# ---------------------------------------------------------------------------


def generate_api_key(prefix: str = "agid_live_") -> tuple[str, str, str]:
    """Return (raw_key, key_hash, key_prefix)."""
    raw = prefix + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    key_prefix = raw[:12]
    return raw, key_hash, key_prefix


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ---------------------------------------------------------------------------
# JWT tokens
# ---------------------------------------------------------------------------


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_agent_token(org_id: str, agent_id: str, scopes: list[str]) -> tuple[str, str]:
    """Return (raw_jwt, token_hash)."""
    token = create_access_token(
        {"sub": agent_id, "org_id": org_id, "scopes": scopes, "type": "agent"},
        timedelta(minutes=settings.agent_token_expire_minutes),
    )
    return token, hash_token(token)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
