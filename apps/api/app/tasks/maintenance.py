"""Scheduled maintenance tasks — cleanup, expiry checks, health monitoring.

These tasks run on the Celery beat schedule defined in worker.py.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import delete, select, update

from app.core.database import async_session_factory

logger = logging.getLogger(__name__)


async def _cleanup_expired_tokens_async():
    """Revoke agent tokens and API keys past their expiry date."""
    now = datetime.now(timezone.utc)
    async with async_session_factory() as db:
        from app.models.agent import AgentToken
        from app.models.auth import ApiKey

        # Revoke expired agent tokens
        result = await db.execute(
            update(AgentToken)
            .where(
                AgentToken.expires_at < now,
                AgentToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        expired_tokens = result.rowcount

        # Revoke expired API keys
        result = await db.execute(
            update(ApiKey)
            .where(
                ApiKey.expires_at < now,
                ApiKey.expires_at.is_not(None),
                ApiKey.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        expired_keys = result.rowcount

        await db.commit()

        if expired_tokens or expired_keys:
            logger.info(
                "Cleaned up %d expired tokens, %d expired API keys",
                expired_tokens, expired_keys,
            )


async def _check_secret_expiry_async():
    """Check for secrets approaching or past expiry and log warnings."""
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    warning_window = now + timedelta(days=7)

    async with async_session_factory() as db:
        from app.models.vault import Secret

        # Secrets expiring within 7 days
        result = await db.execute(
            select(Secret).where(
                Secret.expires_at.is_not(None),
                Secret.expires_at <= warning_window,
                Secret.expires_at > now,
            )
        )
        expiring_soon = result.scalars().all()

        for secret in expiring_soon:
            logger.warning(
                "Secret %s (org=%s) expires at %s",
                secret.name,
                secret.org_id,
                secret.expires_at.isoformat(),
            )

        # Already expired
        result = await db.execute(
            select(Secret).where(
                Secret.expires_at.is_not(None),
                Secret.expires_at <= now,
            )
        )
        expired = result.scalars().all()

        if expired:
            logger.error("%d secrets have expired and need rotation", len(expired))

        # Clean up old webhook deliveries (> 30 days)
        from app.models.webhook import WebhookDelivery

        cutoff = now - timedelta(days=30)
        result = await db.execute(
            delete(WebhookDelivery).where(WebhookDelivery.created_at < cutoff)
        )
        if result.rowcount:
            logger.info("Purged %d old webhook deliveries", result.rowcount)
            await db.commit()


def _register_tasks():
    """Register maintenance tasks with Celery."""
    from worker import celery_app
    import asyncio

    @celery_app.task(name="app.tasks.maintenance.cleanup_expired_tokens")
    def cleanup_expired_tokens():
        asyncio.get_event_loop().run_until_complete(_cleanup_expired_tokens_async())

    @celery_app.task(name="app.tasks.maintenance.check_secret_expiry")
    def check_secret_expiry():
        asyncio.get_event_loop().run_until_complete(_check_secret_expiry_async())
