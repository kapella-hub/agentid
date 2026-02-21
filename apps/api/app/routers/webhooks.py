"""Webhook endpoint management."""

import secrets
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.models.webhook import WebhookEndpoint
from app.schemas import WebhookCreate, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse, status_code=201)
async def create_webhook(req: WebhookCreate, auth: Auth, db: DB):
    endpoint = WebhookEndpoint(
        org_id=auth["org_id"],
        url=req.url,
        events=req.events,
        signing_secret=secrets.token_urlsafe(32),
    )
    db.add(endpoint)
    await db.flush()
    return endpoint


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(auth: Auth, db: DB):
    result = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.org_id == auth["org_id"])
    )
    return result.scalars().all()


@router.delete("/{webhook_id}", status_code=204)
async def delete_webhook(webhook_id: UUID, auth: Auth, db: DB):
    endpoint = await db.get(WebhookEndpoint, webhook_id)
    if not endpoint or endpoint.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await db.delete(endpoint)
