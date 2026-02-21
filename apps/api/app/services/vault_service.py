"""Credential vault service with envelope encryption."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_secret, encrypt_secret, generate_dek, unwrap_dek, wrap_dek
from app.models.vault import DataEncryptionKey, Secret


async def _get_or_create_dek(db: AsyncSession, org_id: UUID) -> tuple[DataEncryptionKey, bytes]:
    """Get the active DEK for an org, or create one."""
    result = await db.execute(
        select(DataEncryptionKey).where(
            DataEncryptionKey.org_id == org_id,
            DataEncryptionKey.status == "active",
        )
    )
    dek_row = result.scalar_one_or_none()

    if dek_row:
        dek = unwrap_dek(dek_row.encrypted_dek)
        return dek_row, dek

    # Create new DEK
    raw_dek = generate_dek()
    wrapped = wrap_dek(raw_dek)
    dek_row = DataEncryptionKey(org_id=org_id, encrypted_dek=wrapped)
    db.add(dek_row)
    await db.flush()
    return dek_row, raw_dek


async def create_secret(
    db: AsyncSession,
    org_id: UUID,
    name: str,
    value: str,
    agent_id: UUID | None = None,
    description: str | None = None,
) -> Secret:
    dek_row, dek = await _get_or_create_dek(db, org_id)
    encrypted = encrypt_secret(value, dek)

    secret = Secret(
        org_id=org_id,
        agent_id=agent_id,
        name=name,
        description=description,
        encrypted_value=encrypted,
        dek_id=dek_row.id,
    )
    db.add(secret)
    await db.flush()
    return secret


async def read_secret(db: AsyncSession, secret: Secret) -> str:
    dek_row = await db.get(DataEncryptionKey, secret.dek_id)
    if not dek_row:
        raise ValueError("DEK not found")
    dek = unwrap_dek(dek_row.encrypted_dek)
    return decrypt_secret(secret.encrypted_value, dek)


async def rotate_secret(db: AsyncSession, secret: Secret, new_value: str) -> Secret:
    dek_row, dek = await _get_or_create_dek(db, secret.org_id)
    secret.encrypted_value = encrypt_secret(new_value, dek)
    secret.dek_id = dek_row.id
    secret.version += 1
    await db.flush()
    return secret
