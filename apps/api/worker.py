"""Celery worker configuration with task signal hooks.

Signals provide hooks into every stage of the task lifecycle:
- before a task starts (pre-run)
- after a task succeeds or fails (post-run)
- on retries
- on worker startup/shutdown
"""

import logging
import time

from celery import Celery, signals
from celery.app.task import Task

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "agentid",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry policy defaults
    task_default_retry_delay=60,
    task_max_retries=3,
    # Result expiry
    result_expires=3600,
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "app.tasks.maintenance.cleanup_expired_tokens",
            "schedule": 3600.0,  # every hour
        },
        "retry-failed-webhooks": {
            "task": "app.tasks.webhooks.retry_failed_deliveries",
            "schedule": 300.0,  # every 5 minutes
        },
        "check-secret-expiry": {
            "task": "app.tasks.maintenance.check_secret_expiry",
            "schedule": 86400.0,  # daily
        },
    },
)

# Auto-discover tasks in the app.tasks package
celery_app.autodiscover_tasks(["app.tasks"])


# ── Worker lifecycle signals ─────────────────────────────────────────────


@signals.worker_ready.connect
def on_worker_ready(**kwargs):
    """Fired when the Celery worker is fully started and ready to accept tasks."""
    logger.info("Celery worker ready — accepting tasks")


@signals.worker_shutting_down.connect
def on_worker_shutdown(sig, how, exitcode, **kwargs):
    """Fired when the Celery worker begins shutting down."""
    logger.info("Celery worker shutting down (signal=%s, how=%s)", sig, how)


# ── Task lifecycle signals ───────────────────────────────────────────────


@signals.task_prerun.connect
def on_task_prerun(sender: Task, task_id: str, args, kwargs, **kw):
    """Fired immediately before a task function is executed."""
    logger.info(
        "Task starting: %s[%s]",
        sender.name,
        task_id,
        extra={"task_name": sender.name, "task_id": task_id},
    )
    # Stash start time for duration measurement in postrun
    kw_store = getattr(sender, "_agentid_meta", {})
    kw_store[task_id] = {"start_time": time.perf_counter()}
    sender._agentid_meta = kw_store


@signals.task_postrun.connect
def on_task_postrun(sender: Task, task_id: str, retval, state: str, **kw):
    """Fired after a task function returns (success or failure)."""
    meta = getattr(sender, "_agentid_meta", {}).pop(task_id, {})
    duration = (time.perf_counter() - meta["start_time"]) * 1000 if "start_time" in meta else 0

    logger.info(
        "Task finished: %s[%s] state=%s duration=%.1fms",
        sender.name,
        task_id,
        state,
        duration,
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "state": state,
            "duration_ms": round(duration, 1),
        },
    )


@signals.task_failure.connect
def on_task_failure(sender: Task, task_id: str, exception, traceback, **kw):
    """Fired when a task raises an unhandled exception."""
    logger.error(
        "Task failed: %s[%s] error=%s",
        sender.name,
        task_id,
        str(exception),
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        },
        exc_info=True,
    )


@signals.task_retry.connect
def on_task_retry(sender: Task, request, reason, einfo, **kw):
    """Fired when a task is scheduled for retry."""
    logger.warning(
        "Task retrying: %s[%s] reason=%s",
        sender.name,
        request.id,
        reason,
        extra={
            "task_name": sender.name,
            "task_id": request.id,
            "retry_reason": str(reason),
        },
    )


@signals.task_success.connect
def on_task_success(sender: Task, result, **kw):
    """Fired when a task completes successfully."""
    logger.debug("Task succeeded: %s", sender.name)


@signals.task_revoked.connect
def on_task_revoked(sender: Task, request, terminated: bool, signum, expired: bool, **kw):
    """Fired when a task is revoked (cancelled)."""
    logger.warning(
        "Task revoked: %s[%s] terminated=%s expired=%s",
        sender.name if sender else "unknown",
        request.id if request else "unknown",
        terminated,
        expired,
    )
