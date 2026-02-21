"""Inbound webhook handlers for Mailgun, Twilio, Stripe."""

from fastapi import APIRouter, Request
from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.identity import EmailIdentity, Message, PhoneIdentity

router = APIRouter(prefix="/hooks", tags=["hooks"])


@router.post("/mailgun/inbound")
async def mailgun_inbound(request: Request):
    """Handle inbound email from Mailgun."""
    form = await request.form()
    recipient = form.get("recipient", "")
    sender = form.get("sender", "")
    subject = form.get("subject", "")
    body_text = form.get("body-plain", "")
    body_html = form.get("body-html", "")

    async with async_session_factory() as db:
        result = await db.execute(
            select(EmailIdentity).where(EmailIdentity.address == recipient, EmailIdentity.status == "active")
        )
        identity = result.scalar_one_or_none()
        if not identity:
            return {"status": "ignored", "reason": "unknown recipient"}

        msg = Message(
            org_id=identity.org_id, agent_id=identity.agent_id,
            channel="email", direction="inbound", identity_id=identity.id,
            sender=str(sender), recipient=str(recipient),
            subject=str(subject), body_text=str(body_text), body_html=str(body_html),
            status="received",
        )
        db.add(msg)
        await db.commit()

    return {"status": "ok"}


@router.post("/twilio/sms")
async def twilio_sms(request: Request):
    """Handle inbound SMS from Twilio."""
    form = await request.form()
    to = form.get("To", "")
    from_ = form.get("From", "")
    body = form.get("Body", "")

    async with async_session_factory() as db:
        result = await db.execute(
            select(PhoneIdentity).where(PhoneIdentity.number == to, PhoneIdentity.status == "active")
        )
        identity = result.scalar_one_or_none()
        if not identity:
            return {"status": "ignored"}

        msg = Message(
            org_id=identity.org_id, agent_id=identity.agent_id,
            channel="sms", direction="inbound", identity_id=identity.id,
            sender=str(from_), recipient=str(to), body_text=str(body),
            status="received",
        )
        db.add(msg)
        await db.commit()

    # Return TwiML empty response
    return "<Response></Response>"
