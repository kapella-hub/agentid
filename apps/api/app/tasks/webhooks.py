"""Webhook delivery tasks — async dispatch with retry and dead-letter handling.

Hooks into the Celery task system to deliver outbound webhooks with:
- HMAC-SHA256 payload signing
- Exponential backoff retries
- Delivery status tracking via WebhookDelivery model
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select, update

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.webhook import WebhookDelivery, WebhookEndpoint

logger = logging.getLogger(__name__)

# Lazy import celery_app to avoid circular imports at module level
_celery_app = None


def _get_celery_app():
    global _celery_app
    if _celery_app is None:
        from worker import celery_app
        _celery_app = celery_app
    return _celery_app


def _sign_payload(payload: str, secret: str) -> str:
    """Create HMAC-SHA256 signature for webhook payload."""
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


async def _deliver_webhook(delivery_id: str, endpoint_url: str, payload: dict, signing_secret: str) -> int:
    """Perform the actual HTTP POST to the webhook endpoint.

    Returns the HTTP status code, or 0 on connection failure.
    """
    body = json.dumps(payload, default=str)
    signature = _sign_payload(body, signing_secret)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            endpoint_url,
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-AgentID-Signature": f"sha256={signature}",
                "X-AgentID-Delivery": delivery_id,
                "User-Agent": "AgentID-Webhook/1.0",
            },
        )
        return response.status_code


# ── Celery tasks ─────────────────────────────────────────────────────────


def dispatch_webhook(endpoint_id: str, event_type: str, payload: dict):
    """Enqueue a webhook delivery.

    This is the main entry point — call this from anywhere in the app
    to trigger an async webhook delivery.
    """
    app = _get_celery_app()
    app.send_task(
        "app.tasks.webhooks._dispatch_webhook_task",
        args=[endpoint_id, event_type, payload],
    )


def _register_tasks():
    """Register Celery tasks. Called during worker startup."""
    app = _get_celery_app()

    @app.task(bind=True, name="app.tasks.webhooks._dispatch_webhook_task", max_retries=5)
    def _dispatch_webhook_task(self, endpoint_id: str, event_type: str, payload: dict):
        """Deliver a webhook to a single endpoint with retry."""
        import asyncio
        asyncio.get_event_loop().run_until_complete(
            _async_dispatch(self, endpoint_id, event_type, payload)
        )

    @app.task(name="app.tasks.webhooks.retry_failed_deliveries")
    def retry_failed_deliveries():
        """Periodic task: retry webhook deliveries that are due for retry."""
        import asyncio
        asyncio.get_event_loop().run_until_complete(_async_retry_failed())


async def _async_dispatch(task, endpoint_id: str, event_type: str, payload: dict):
    """Core delivery logic (async)."""
    async with async_session_factory() as db:
        # Fetch the endpoint
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.id == endpoint_id,
                WebhookEndpoint.status == "active",
            )
        )
        endpoint = result.scalar_one_or_none()
        if not endpoint:
            logger.warning("Webhook endpoint %s not found or inactive", endpoint_id)
            return

        # Create delivery record
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_type=event_type,
            payload=payload,
            status="pending",
        )
        db.add(delivery)
        await db.flush()

        try:
            status_code = await _deliver_webhook(
                str(delivery.id), endpoint.url, payload, endpoint.signing_secret
            )

            delivery.response_status = status_code
            delivery.attempts += 1

            if 200 <= status_code < 300:
                delivery.status = "delivered"
                logger.info(
                    "Webhook delivered: %s → %s (status=%d)",
                    event_type, endpoint.url, status_code,
                )
            else:
                delivery.status = "failed"
                # Schedule retry with exponential backoff
                backoff = 60 * (2 ** delivery.attempts)  # 2m, 4m, 8m, 16m, 32m
                delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff)
                logger.warning(
                    "Webhook failed: %s → %s (status=%d, retry in %ds)",
                    event_type, endpoint.url, status_code, backoff,
                )

        except httpx.HTTPError as exc:
            delivery.attempts += 1
            delivery.status = "failed"
            backoff = 60 * (2 ** delivery.attempts)
            delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=backoff)
            logger.error("Webhook delivery error: %s → %s: %s", event_type, endpoint.url, exc)

        await db.commit()


async def _async_retry_failed():
    """Pick up failed deliveries due for retry and re-dispatch them."""
    now = datetime.now(timezone.utc)
    async with async_session_factory() as db:
        result = await db.execute(
            select(WebhookDelivery).where(
                WebhookDelivery.status == "failed",
                WebhookDelivery.next_retry_at <= now,
                WebhookDelivery.attempts < 5,
            ).limit(100)
        )
        deliveries = result.scalars().all()

        for delivery in deliveries:
            # Re-enqueue each delivery
            dispatch_webhook(
                str(delivery.endpoint_id), delivery.event_type, delivery.payload
            )
            # Mark as pending to prevent double-pickup
            await db.execute(
                update(WebhookDelivery)
                .where(WebhookDelivery.id == delivery.id)
                .values(status="pending")
            )

        if deliveries:
            await db.commit()
            logger.info("Re-queued %d failed webhook deliveries for retry", len(deliveries))
