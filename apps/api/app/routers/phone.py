"""Phone provisioning endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.models.identity import PhoneIdentity
from app.schemas import PhoneIdentityResponse, PhoneProvisionRequest
from app.services.audit_service import log_event
from app.services.phone_service import deprovision_phone, provision_phone

router = APIRouter(tags=["phone"])


@router.post("/agents/{agent_id}/phone", response_model=PhoneIdentityResponse, status_code=201)
async def provision_agent_phone(agent_id: UUID, req: PhoneProvisionRequest, auth: Auth, db: DB):
    identity = await provision_phone(db, auth["org_id"], agent_id, req.country, req.capabilities)
    await log_event(
        db, auth["org_id"], auth["type"], "phone.provisioned", "phone_identity",
        resource_id=identity.id,
    )
    return identity


@router.get("/agents/{agent_id}/phone", response_model=list[PhoneIdentityResponse])
async def list_agent_phones(agent_id: UUID, auth: Auth, db: DB):
    result = await db.execute(
        select(PhoneIdentity).where(
            PhoneIdentity.agent_id == agent_id,
            PhoneIdentity.org_id == auth["org_id"],
            PhoneIdentity.status != "deleted",
        )
    )
    return result.scalars().all()


@router.delete("/agents/{agent_id}/phone/{phone_id}", status_code=204)
async def deprovision_agent_phone(agent_id: UUID, phone_id: UUID, auth: Auth, db: DB):
    identity = await db.get(PhoneIdentity, phone_id)
    if not identity or identity.org_id != auth["org_id"] or identity.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Phone identity not found")
    await deprovision_phone(db, identity)
    await log_event(
        db, auth["org_id"], auth["type"], "phone.deprovisioned", "phone_identity",
        resource_id=phone_id,
    )
