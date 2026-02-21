"""SQLAlchemy ORM event listeners — automatic audit trail and lifecycle hooks.

These hooks fire at the ORM level, catching ALL changes regardless of which
router or service initiated them. This provides a safety net of audit coverage
beyond the manual audit_service.log_event() calls.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.core.database import Base

logger = logging.getLogger(__name__)

# Models whose changes should be tracked
_TRACKED_ACTIONS: dict[str, str] = {}  # populated by register_hooks()


def _get_changed_fields(target: Base) -> dict:
    """Return a dict of fields that changed on UPDATE, with old→new values."""
    insp = inspect(target)
    changes = {}
    for attr in insp.attrs:
        hist = attr.history
        if hist.has_changes():
            changes[attr.key] = {
                "old": hist.deleted[0] if hist.deleted else None,
                "new": hist.added[0] if hist.added else None,
            }
    return changes


def _serialize_value(val):
    """Safely serialize a value for logging."""
    if isinstance(val, datetime):
        return val.isoformat()
    if hasattr(val, "hex"):  # UUID
        return str(val)
    return val


def _build_change_log(target: Base, action: str) -> dict:
    """Build a structured change log entry for an ORM event."""
    table = target.__tablename__
    pk = getattr(target, "id", None)
    org_id = getattr(target, "org_id", None)

    entry = {
        "table": table,
        "action": action,
        "id": str(pk) if pk else None,
        "org_id": str(org_id) if org_id else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if action == "update":
        changes = _get_changed_fields(target)
        # Filter out sensitive fields
        sensitive = {"password_hash", "token_hash", "key_hash", "encrypted_value", "encrypted_dek"}
        entry["changes"] = {
            k: {kk: _serialize_value(vv) for kk, vv in v.items()}
            for k, v in changes.items()
            if k not in sensitive
        }

    return entry


# ── Listener callbacks ────────────────────────────────────────────────────


def _after_insert(mapper, connection, target):
    """Log INSERT events."""
    log = _build_change_log(target, "insert")
    logger.info("ORM INSERT on %s id=%s", log["table"], log["id"], extra=log)


def _after_update(mapper, connection, target):
    """Log UPDATE events with changed field details."""
    log = _build_change_log(target, "update")
    if log.get("changes"):
        logger.info("ORM UPDATE on %s id=%s", log["table"], log["id"], extra=log)


def _after_delete(mapper, connection, target):
    """Log DELETE events."""
    log = _build_change_log(target, "delete")
    logger.warning("ORM DELETE on %s id=%s", log["table"], log["id"], extra=log)


# ── Session-level hooks ──────────────────────────────────────────────────


def _after_flush(session: Session, flush_context):
    """Post-flush hook — runs after all pending changes are persisted."""
    if session.new:
        logger.debug("Flush: %d new objects committed", len(session.new))
    if session.dirty:
        logger.debug("Flush: %d dirty objects committed", len(session.dirty))
    if session.deleted:
        logger.debug("Flush: %d objects deleted", len(session.deleted))


# ── Registration ─────────────────────────────────────────────────────────


def register_hooks() -> None:
    """Attach ORM event listeners to all tracked models.

    Call this once at application startup (inside the lifespan hook).
    """
    # Import models here to avoid circular imports
    from app.models.agent import Agent, AgentToken
    from app.models.auth import ApiKey, Org, User
    from app.models.identity import EmailIdentity, Message, PhoneIdentity
    from app.models.vault import DataEncryptionKey, Secret
    from app.models.webhook import WebhookDelivery, WebhookEndpoint

    tracked_models = [
        Org, User, ApiKey,
        Agent, AgentToken,
        EmailIdentity, PhoneIdentity, Message,
        Secret, DataEncryptionKey,
        WebhookEndpoint, WebhookDelivery,
    ]

    for model in tracked_models:
        event.listen(model, "after_insert", _after_insert)
        event.listen(model, "after_update", _after_update)
        event.listen(model, "after_delete", _after_delete)

    # Session-level flush hook
    event.listen(Session, "after_flush", _after_flush)

    logger.info("ORM event hooks registered for %d models", len(tracked_models))
