"""Rate limiting middleware using in-memory token bucket.

Uses a simple in-memory dict for MVP. Production should swap to Redis-based
rate limiting for multi-process / multi-instance support.
"""

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class _TokenBucket:
    """Simple token bucket rate limiter."""

    def __init__(self, rate: int, per: float = 60.0):
        self.rate = rate  # tokens per interval
        self.per = per  # interval in seconds
        self._buckets: dict[str, tuple[float, float]] = {}

    def allow(self, key: str) -> tuple[bool, int, float]:
        """Check if a request is allowed. Returns (allowed, remaining, reset_at)."""
        now = time.time()
        tokens, last_refill = self._buckets.get(key, (float(self.rate), now))

        # Refill tokens based on elapsed time
        elapsed = now - last_refill
        tokens = min(self.rate, tokens + elapsed * (self.rate / self.per))
        last_refill = now

        if tokens >= 1:
            tokens -= 1
            self._buckets[key] = (tokens, last_refill)
            return True, int(tokens), now + self.per
        else:
            self._buckets[key] = (tokens, last_refill)
            return False, 0, now + (1 - tokens) * (self.per / self.rate)


_bucket = _TokenBucket(rate=settings.rate_limit_per_minute)

# Paths exempt from rate limiting
_EXEMPT_PATHS = {"/health", "/hooks/mailgun/inbound", "/hooks/twilio/sms"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for exempt paths
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        # Use Authorization header hash or client IP as the rate limit key
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            key = f"auth:{hash(auth_header)}"
        else:
            key = f"ip:{request.client.host if request.client else 'unknown'}"

        allowed, remaining, reset_at = _bucket.allow(key)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": "Too many requests. Please retry later.",
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset_at)),
                    "Retry-After": str(int(reset_at - time.time()) + 1),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_at))
        return response
