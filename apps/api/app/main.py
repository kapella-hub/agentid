"""AgentID API — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestIdMiddleware, SecurityHeadersMiddleware, TimingMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.routers import agents, audit, auth, email, hooks, messages, phone, vault, webhooks

logger = logging.getLogger(__name__)


# ── Lifespan hooks (startup / shutdown) ──────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hook — runs setup on startup, cleanup on shutdown."""
    # ── Startup ──────────────────────────────────────────────────────────
    from monitoring.logging_config import setup_logging, setup_sentry, setup_telemetry

    setup_logging()
    setup_sentry()
    setup_telemetry()
    logger.info("AgentID API starting up (env=%s)", settings.environment)

    # Register SQLAlchemy ORM event listeners
    from app.core.orm_hooks import register_hooks
    register_hooks()

    # Register application event bus handlers
    from app.core.event_handlers import register_event_handlers
    register_event_handlers()

    logger.info("All hooks registered — application ready")

    yield  # ── Application is running ────────────────────────────────────

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("AgentID API shutting down — cleaning up resources")


# ── Application factory ──────────────────────────────────────────────────


app = FastAPI(
    title=settings.app_name,
    description="Identity-as-a-Service for AI Agents",
    version="0.1.0",
    lifespan=lifespan,
)

# Register exception handlers
register_exception_handlers(app)

# Middleware stack (order matters — outermost first)
# 1. Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# 2. Request ID for distributed tracing
app.add_middleware(RequestIdMiddleware)

# 3. Request timing and access logging
app.add_middleware(TimingMiddleware)

# 4. CORS — allow the frontend dashboard to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Rate limiting
app.add_middleware(RateLimitMiddleware)

# Mount all routers under /v1
for r in [auth.router, agents.router, email.router, phone.router, messages.router, vault.router, webhooks.router, audit.router]:
    app.include_router(r, prefix=settings.api_prefix)

# Hooks are not under /v1 — they receive provider callbacks
app.include_router(hooks.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
