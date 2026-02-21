"""Tests for security utilities."""

from app.core.security import (
    create_access_token,
    decode_token,
    generate_api_key,
    hash_password,
    hash_token,
    verify_password,
)


def test_password_hash():
    pw = "my-secure-password"
    hashed = hash_password(pw)
    assert verify_password(pw, hashed)
    assert not verify_password("wrong", hashed)


def test_api_key_generation():
    raw, key_hash, prefix = generate_api_key()
    assert raw.startswith("agid_live_")
    assert len(key_hash) == 64  # SHA-256 hex
    assert prefix == raw[:12]
    assert hash_token(raw) == key_hash


def test_jwt_roundtrip():
    token = create_access_token({"sub": "user-123", "type": "user"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"


def test_jwt_invalid():
    assert decode_token("not-a-valid-token") is None
