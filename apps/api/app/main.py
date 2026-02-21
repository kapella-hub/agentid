"""AgentID API — FastAPI application entry point."""

from fastapi import FastAPI

from app.core.config import settings
from app.routers import agents, audit, auth, email, hooks, messages, phone, vault, webhooks

app = FastAPI(
    title=settings.app_name,
    description="Identity-as-a-Service for AI Agents",
    version="0.1.0",
)

# Mount all routers under /v1
for r in [auth.router, agents.router, email.router, phone.router, messages.router, vault.router, webhooks.router, audit.router]:
    app.include_router(r, prefix=settings.api_prefix)

# Hooks are not under /v1 — they receive provider callbacks
app.include_router(hooks.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
