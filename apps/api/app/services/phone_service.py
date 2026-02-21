"""Virtual phone provisioning service — Twilio integration."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.identity import PhoneIdentity


class TwilioClient:
    """Thin async wrapper around Twilio REST API (uses httpx to stay async)."""

    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"

    @property
    def _auth(self):
        return (self.account_sid, self.auth_token)

    async def buy_number(self, country: str, capabilities: list[str]) -> dict:
        import httpx

        # Search for available number
        async with httpx.AsyncClient() as client:
            search_resp = await client.get(
                f"{self.base_url}/AvailablePhoneNumbers/{country}/Local.json",
                auth=self._auth,
                params={"SmsEnabled": "true" if "sms" in capabilities else "false", "PageSize": 1},
            )
            search_resp.raise_for_status()
            numbers = search_resp.json().get("available_phone_numbers", [])
            if not numbers:
                raise ValueError(f"No numbers available in {country}")

            phone_number = numbers[0]["phone_number"]

            # Purchase
            buy_resp = await client.post(
                f"{self.base_url}/IncomingPhoneNumbers.json",
                auth=self._auth,
                data={
                    "PhoneNumber": phone_number,
                    "SmsUrl": "https://api.agentid.io/hooks/twilio/sms",
                    "SmsMethod": "POST",
                },
            )
            buy_resp.raise_for_status()
            data = buy_resp.json()
            return {"number": data["phone_number"], "sid": data["sid"]}

    async def release_number(self, sid: str) -> None:
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self.base_url}/IncomingPhoneNumbers/{sid}.json",
                auth=self._auth,
            )
            resp.raise_for_status()

    async def send_sms(self, from_number: str, to: str, body: str) -> str:
        import httpx

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/Messages.json",
                auth=self._auth,
                data={"From": from_number, "To": to, "Body": body},
            )
            resp.raise_for_status()
            return resp.json().get("sid", "")


twilio_client = TwilioClient()


async def provision_phone(
    db: AsyncSession,
    org_id: UUID,
    agent_id: UUID,
    country: str = "US",
    capabilities: list[str] | None = None,
) -> PhoneIdentity:
    capabilities = capabilities or ["sms"]

    identity = PhoneIdentity(
        org_id=org_id,
        agent_id=agent_id,
        number="pending",
        country=country,
        capabilities=capabilities,
        status="provisioning",
    )
    db.add(identity)
    await db.flush()

    if settings.twilio_account_sid:
        try:
            result = await twilio_client.buy_number(country, capabilities)
            identity.number = result["number"]
            identity.provider_sid = result["sid"]
            identity.status = "active"
        except Exception as e:
            identity.status = "failed"
            identity.config = {"error": str(e)}
    else:
        # Dev mode — assign a fake number
        identity.number = f"+1555000{str(identity.id)[:4]}"
        identity.status = "active"

    return identity


async def deprovision_phone(db: AsyncSession, identity: PhoneIdentity) -> None:
    if identity.provider_sid and settings.twilio_account_sid:
        try:
            await twilio_client.release_number(identity.provider_sid)
        except Exception:
            pass
    identity.status = "deleted"
