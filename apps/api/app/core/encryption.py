"""Envelope encryption for the credential vault.

MVP: Uses a local master key (AGENTID_VAULT_MASTER_KEY) instead of KMS.
Production should swap to AWS KMS / GCP KMS via the same interface.
"""

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _get_master_key() -> bytes:
    """Return the 32-byte master key (from base64 env var or derive a dev key)."""
    if settings.vault_master_key:
        return base64.b64decode(settings.vault_master_key)
    # Dev fallback — deterministic but not secure
    return b"agentid-dev-master-key-00000000!"[:32]


def generate_dek() -> bytes:
    """Generate a 256-bit data encryption key."""
    return os.urandom(32)


def wrap_dek(dek: bytes) -> bytes:
    """Encrypt DEK with the master key (envelope wrap)."""
    mk = _get_master_key()
    aesgcm = AESGCM(mk)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, dek, None)
    return nonce + ct  # 12-byte nonce || ciphertext+tag


def unwrap_dek(wrapped: bytes) -> bytes:
    """Decrypt DEK with the master key."""
    mk = _get_master_key()
    aesgcm = AESGCM(mk)
    nonce, ct = wrapped[:12], wrapped[12:]
    return aesgcm.decrypt(nonce, ct, None)


def encrypt_secret(plaintext: str, dek: bytes) -> bytes:
    """Encrypt a secret value with a DEK using AES-256-GCM."""
    aesgcm = AESGCM(dek)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ct


def decrypt_secret(ciphertext: bytes, dek: bytes) -> str:
    """Decrypt a secret value."""
    aesgcm = AESGCM(dek)
    nonce, ct = ciphertext[:12], ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, None).decode()
