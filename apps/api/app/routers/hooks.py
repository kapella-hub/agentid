"""Inbound webhook handlers for Mailgun, Twilio, Stripe."""

import hashlib
import hmac
import time

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.identity import EmailIdentity, Message, PhoneIdentity

router = APIRouter(prefix="/hooks", tags=["hooks"])


def _verify_mailgun_signature(token: str, timestamp: str, signature: str) -> bool:
    """Verify Mailgun webhook signature using HMAC-SHA256."""
    if not settings.mailgun_webhook_signing_key:
        return True  # Skip verification in dev mode when no key is configured
    signing_key = settings.mailgun_webhook_signing_key.encode()
    data = f"{timestamp}{token}".encode()
    expected = hmac.new(signing_key, data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _verify_twilio_signature(request: Request, form_data: dict) -> bool:
    """Verify Twilio webhook signature using HMAC-SHA1."""
    if not settings.twilio_auth_token:
        return True  # Skip verification in dev mode when no token is configured
    signature = request.headers.get("X-Twilio-Signature", "")
    if not signature:
        return False

    # Build the validation URL from the request
    url = str(request.url)

    # Sort POST params and append to URL
    param_string = "".join(f"{k}{v}" for k, v in sorted(form_data.items()))
    data = (url + param_string).encode()

    expected = hmac.new(
        settings.twilio_auth_token.encode(), data, hashlib.sha1
    ).digest()

    import base64

    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(expected_b64, signature)


@router.post("/mailgun/inbound")
async def mailgun_inbound(request: Request):
    """Handle inbound email from Mailgun."""
    form = await request.form()

    # Verify Mailgun webhook signature
    token = str(form.get("token", ""))
    timestamp = str(form.get("timestamp", ""))
    signature = str(form.get("signature", ""))
    if not _verify_mailgun_signature(token, timestamp, signature):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    # Reject stale timestamps (> 5 minutes old)
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > 300:
            raise HTTPException(status_code=403, detail="Stale webhook timestamp")
    except ValueError:
        if settings.mailgun_webhook_signing_key:
            raise HTTPException(status_code=403, detail="Invalid timestamp")

    recipient = form.get("recipient", "")
    sender = form.get("sender", "")
    subject = form.get("subject", "")
    body_text = form.get("body-plain", "")
    body_html = form.get("body-html", "")

    async with async_session_factory() as db:
        result = await db.execute(
            select(EmailIdentity).where(
                EmailIdentity.address == recipient, EmailIdentity.status == "active"
            )
        )
        identity = result.scalar_one_or_none()
        if not identity:
            return {"status": "ignored", "reason": "unknown recipient"}

        msg = Message(
            org_id=identity.org_id,
            agent_id=identity.agent_id,
            channel="email",
            direction="inbound",
            identity_id=identity.id,
            sender=str(sender),
            recipient=str(recipient),
            subject=str(subject),
            body_text=str(body_text),
            body_html=str(body_html),
            status="received",
        )
        db.add(msg)
        await db.commit()

    return {"status": "ok"}


@router.post("/twilio/sms")
async def twilio_sms(request: Request):
    """Handle inbound SMS from Twilio."""
    form = await request.form()
    form_data = {k: str(v) for k, v in form.items()}

    # Verify Twilio webhook signature
    if not _verify_twilio_signature(request, form_data):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    to = form_data.get("To", "")
    from_ = form_data.get("From", "")
    body = form_data.get("Body", "")

    async with async_session_factory() as db:
        result = await db.execute(
            select(PhoneIdentity).where(
                PhoneIdentity.number == to, PhoneIdentity.status == "active"
            )
        )
        identity = result.scalar_one_or_none()
        if not identity:
            return {"status": "ignored"}

        msg = Message(
            org_id=identity.org_id,
            agent_id=identity.agent_id,
            channel="sms",
            direction="inbound",
            identity_id=identity.id,
            sender=str(from_),
            recipient=str(to),
            body_text=str(body),
            status="received",
        )
        db.add(msg)
        await db.commit()

    # Return TwiML empty response
    return "<Response></Response>"
