"""Message retrieval and sending endpoints."""

import logging
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.core.pagination import apply_cursor, encode_cursor
from app.models.identity import EmailIdentity, Message, PhoneIdentity
from app.schemas import MessageResponse, PaginatedResponse, SendMessageRequest
from app.services.email_service import mailgun
from app.services.phone_service import twilio_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("", response_model=PaginatedResponse)
async def list_messages(
    auth: Auth,
    db: DB,
    agent_id: UUID | None = None,
    channel: Literal["email", "sms"] | None = None,
    direction: Literal["inbound", "outbound"] | None = None,
    limit: int = Query(default=50, le=100),
    cursor: str | None = None,
):
    q = select(Message).where(Message.org_id == auth["org_id"])
    if agent_id:
        q = q.where(Message.agent_id == agent_id)
    if channel:
        q = q.where(Message.channel == channel)
    if direction:
        q = q.where(Message.direction == direction)
    q = apply_cursor(q, cursor, Message.id, limit)
    result = await db.execute(q)
    items = list(result.scalars().all())

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return PaginatedResponse(
        data=[MessageResponse.model_validate(m) for m in items],
        has_more=has_more,
        cursor=encode_cursor(items[-1].id) if items else None,
    )


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: UUID, auth: Auth, db: DB):
    msg = await db.get(Message, message_id)
    if not msg or msg.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


@router.post("/send", response_model=MessageResponse, status_code=201)
async def send_message(req: SendMessageRequest, auth: Auth, db: DB):
    if req.channel == "email":
        # Find email identity for this agent
        result = await db.execute(
            select(EmailIdentity).where(
                EmailIdentity.agent_id == req.agent_id,
                EmailIdentity.org_id == auth["org_id"],
                EmailIdentity.status == "active",
            )
        )
        identity = result.scalars().first()
        if not identity:
            raise HTTPException(status_code=400, detail="No active email identity for agent")

        try:
            provider_id = await mailgun.send_email(identity.address, req.to, req.subject or "", req.body)
            msg_status = "delivered"
        except Exception as e:
            logger.error("Failed to send email via Mailgun: %s", e)
            provider_id = None
            msg_status = "failed"

        msg = Message(
            org_id=auth["org_id"], agent_id=req.agent_id, channel="email",
            direction="outbound", identity_id=identity.id,
            sender=identity.address, recipient=req.to,
            subject=req.subject, body_text=req.body,
            provider_id=provider_id, status=msg_status,
        )
    elif req.channel == "sms":
        result = await db.execute(
            select(PhoneIdentity).where(
                PhoneIdentity.agent_id == req.agent_id,
                PhoneIdentity.org_id == auth["org_id"],
                PhoneIdentity.status == "active",
            )
        )
        identity = result.scalars().first()
        if not identity:
            raise HTTPException(status_code=400, detail="No active phone identity for agent")

        try:
            provider_id = await twilio_client.send_sms(identity.number, req.to, req.body)
            msg_status = "delivered"
        except Exception as e:
            logger.error("Failed to send SMS via Twilio: %s", e)
            provider_id = None
            msg_status = "failed"

        msg = Message(
            org_id=auth["org_id"], agent_id=req.agent_id, channel="sms",
            direction="outbound", identity_id=identity.id,
            sender=identity.number, recipient=req.to,
            body_text=req.body, provider_id=provider_id, status=msg_status,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid channel")

    db.add(msg)
    await db.flush()
    return msg
