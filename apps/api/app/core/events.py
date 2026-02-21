"""Application event bus — lightweight pub/sub for decoupled hook integration.

Usage:
    from app.core.events import event_bus

    # Subscribe a handler
    @event_bus.on("agent.created")
    async def on_agent_created(data: dict):
        ...

    # Emit an event
    await event_bus.emit("agent.created", {"agent_id": ..., "org_id": ...})
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


class EventBus:
    """Async event bus with ordered handler execution and error isolation."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[Handler]] = defaultdict(list)
        self._wildcard_listeners: list[Handler] = []

    def on(self, event: str) -> Callable[[Handler], Handler]:
        """Decorator to subscribe a handler to an event type."""
        def decorator(fn: Handler) -> Handler:
            self._listeners[event].append(fn)
            return fn
        return decorator

    def on_all(self, fn: Handler) -> Handler:
        """Subscribe a handler to ALL events (wildcard)."""
        self._wildcard_listeners.append(fn)
        return fn

    def subscribe(self, event: str, handler: Handler) -> None:
        """Imperatively subscribe a handler to an event type."""
        self._listeners[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler) -> None:
        """Remove a handler from an event type."""
        self._listeners[event] = [h for h in self._listeners[event] if h is not handler]

    async def emit(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Emit an event to all subscribed handlers.

        Handlers run sequentially. Errors in one handler do not prevent
        subsequent handlers from executing.
        """
        payload = data or {}
        payload.setdefault("_event", event)

        handlers = list(self._listeners.get(event, [])) + list(self._wildcard_listeners)

        # Also fire prefix-wildcard: "agent.*" listeners get "agent.created"
        prefix = event.rsplit(".", 1)[0] + ".*" if "." in event else None
        if prefix and prefix in self._listeners:
            handlers.extend(self._listeners[prefix])

        for handler in handlers:
            try:
                await handler(payload)
            except Exception:
                logger.exception("Event handler %s failed for event %r", handler.__name__, event)

    async def emit_background(self, event: str, data: dict[str, Any] | None = None) -> None:
        """Fire-and-forget: emit event without blocking the caller."""
        asyncio.create_task(self.emit(event, data))

    @property
    def registered_events(self) -> list[str]:
        """List all event types that have at least one handler."""
        return sorted(self._listeners.keys())


# Singleton instance
event_bus = EventBus()
