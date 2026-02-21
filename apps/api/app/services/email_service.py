"""Email provisioning service — Mailgun integration."""

from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.identity import EmailIdentity


class MailgunClient:
    """Thin wrapper around the Mailgun API."""

    def __init__(self):
        self.api_key = settings.mailgun_api_key
        self.base_url = settings.mailgun_base_url
        self.domain = settings.mailgun_domain

    async def create_route(self, address: str, webhook_url: str) -> str:
        """Create a Mailgun route that forwards inbound mail to our webhook."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/routes",
                auth=("api", self.api_key),
                data={
                    "priority": 0,
                    "description": f"AgentID route for {address}",
                    "expression": f'match_recipient("{address}")',
                    "action": [f"forward('{webhook_url}')", "stop()"],
                },
            )
            resp.raise_for_status()
            return resp.json()["route"]["id"]

    async def delete_route(self, route_id: str) -> None:
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/routes/{route_id}",
                auth=("api", self.api_key),
            )
            resp.raise_for_status()

    async def send_email(
        self, from_addr: str, to: str, subject: str, body: str, html: str | None = None
    ) -> str:
        data: dict = {
            "from": from_addr,
            "to": [to],
            "subject": subject,
            "text": body,
        }
        if html:
            data["html"] = html
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/{self.domain}/messages",
                auth=("api", self.api_key),
                data=data,
            )
            resp.raise_for_status()
            return resp.json().get("id", "")


mailgun = MailgunClient()


async def provision_email(
    db: AsyncSession,
    org_id: UUID,
    agent_id: UUID,
    local_part: str,
    domain: str | None = None,
) -> EmailIdentity:
    """Provision an email identity for an agent."""
    domain = domain or settings.mailgun_domain
    address = f"{local_part}@{domain}"

    # Check uniqueness
    existing = await db.execute(select(EmailIdentity).where(EmailIdentity.address == address))
    if existing.scalar_one_or_none():
        raise ValueError(f"Address {address} already provisioned")

    identity = EmailIdentity(
        org_id=org_id,
        agent_id=agent_id,
        address=address,
        domain=domain,
        domain_verified=(domain == settings.mailgun_domain),
        status="provisioning",
    )
    db.add(identity)
    await db.flush()

    # Provision with Mailgun (skip if no API key configured)
    if settings.mailgun_api_key:
        webhook_url = f"https://api.agentid.io/hooks/mailgun/inbound"
        try:
            route_id = await mailgun.create_route(address, webhook_url)
            identity.provider_id = route_id
            identity.status = "active"
        except Exception:
            identity.status = "failed"
    else:
        identity.status = "active"  # dev mode

    return identity


async def deprovision_email(db: AsyncSession, identity: EmailIdentity) -> None:
    if identity.provider_id and settings.mailgun_api_key:
        try:
            await mailgun.delete_route(identity.provider_id)
        except Exception:
            pass
    identity.status = "deleted"
