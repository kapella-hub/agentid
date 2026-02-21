"""Event bus subscribers — wire application events to concrete actions.

Each handler subscribes to events emitted by routers/services via the event bus
and triggers side effects: webhook dispatch, audit enrichment, notifications, etc.

Register all handlers by calling register_event_handlers() at startup.
"""

import logging
from typing import Any

from app.core.events import event_bus

logger = logging.getLogger(__name__)


# ── Webhook dispatch ─────────────────────────────────────────────────────


@event_bus.on("message.received")
async def dispatch_message_webhook(data: dict[str, Any]) -> None:
    """When an inbound message arrives, fan out to registered webhook endpoints."""
    from app.core.database import async_session_factory
    from app.models.webhook import WebhookEndpoint
    from sqlalchemy import select

    org_id = data.get("org_id")
    channel = data.get("channel", "email")
    event_type = f"{channel}.received"

    async with async_session_factory() as db:
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.org_id == org_id,
                WebhookEndpoint.status == "active",
            )
        )
        endpoints = result.scalars().all()

        for ep in endpoints:
            if event_type in ep.events or "*" in ep.events:
                try:
                    from app.tasks.webhooks import dispatch_webhook
                    dispatch_webhook(str(ep.id), event_type, data)
                except Exception:
                    logger.exception("Failed to enqueue webhook for endpoint %s", ep.id)


# ── Audit enrichment ─────────────────────────────────────────────────────


@event_bus.on("agent.created")
async def audit_agent_created(data: dict[str, Any]) -> None:
    """Log agent creation to the structured audit trail."""
    logger.info(
        "Event: agent.created org=%s agent=%s",
        data.get("org_id"),
        data.get("agent_id"),
    )


@event_bus.on("agent.deleted")
async def audit_agent_deleted(data: dict[str, Any]) -> None:
    logger.info(
        "Event: agent.deleted org=%s agent=%s",
        data.get("org_id"),
        data.get("agent_id"),
    )


@event_bus.on("identity.provisioned")
async def on_identity_provisioned(data: dict[str, Any]) -> None:
    """Trigger post-provisioning hooks: DNS verification, welcome setup, etc."""
    logger.info(
        "Event: identity.provisioned type=%s org=%s",
        data.get("identity_type"),
        data.get("org_id"),
    )


@event_bus.on("identity.deprovisioned")
async def on_identity_deprovisioned(data: dict[str, Any]) -> None:
    logger.info(
        "Event: identity.deprovisioned type=%s org=%s",
        data.get("identity_type"),
        data.get("org_id"),
    )


@event_bus.on("secret.rotated")
async def on_secret_rotated(data: dict[str, Any]) -> None:
    """When a secret is rotated, notify downstream consumers."""
    logger.info(
        "Event: secret.rotated org=%s secret=%s version=%s",
        data.get("org_id"),
        data.get("secret_name"),
        data.get("version"),
    )


@event_bus.on("auth.login")
async def on_auth_login(data: dict[str, Any]) -> None:
    """Track login events for security monitoring."""
    logger.info(
        "Event: auth.login user=%s org=%s ip=%s",
        data.get("user_id"),
        data.get("org_id"),
        data.get("ip_address"),
    )


@event_bus.on("auth.login_failed")
async def on_auth_login_failed(data: dict[str, Any]) -> None:
    """Track failed login attempts for brute-force detection."""
    logger.warning(
        "Event: auth.login_failed email=%s ip=%s",
        data.get("email"),
        data.get("ip_address"),
    )


# ── Wildcard handler for debug logging ───────────────────────────────────


@event_bus.on_all
async def debug_log_all_events(data: dict[str, Any]) -> None:
    """Log every event at DEBUG level for development observability."""
    logger.debug("EventBus → %s", data.get("_event", "unknown"))


# ── Registration ─────────────────────────────────────────────────────────


def register_event_handlers() -> None:
    """All handlers are auto-registered via decorators above.

    This function serves as an explicit import trigger — call it at startup
    to ensure this module is loaded and decorators execute.
    """
    events = event_bus.registered_events
    logger.info("Event handlers registered for %d event types: %s", len(events), events)
