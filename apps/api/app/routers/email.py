"""Email provisioning endpoints."""

from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.models.identity import EmailIdentity
from app.schemas import EmailIdentityResponse, EmailProvisionRequest
from app.services.audit_service import log_event
from app.services.email_service import deprovision_email, provision_email

router = APIRouter(tags=["email"])


@router.post("/agents/{agent_id}/email", response_model=EmailIdentityResponse, status_code=201)
async def provision_agent_email(agent_id: UUID, req: EmailProvisionRequest, auth: Auth, db: DB):
    try:
        identity = await provision_email(db, auth["org_id"], agent_id, req.local_part, req.domain)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    await log_event(
        db, auth["org_id"], auth["type"], "email.provisioned", "email_identity",
        resource_id=identity.id,
    )
    return identity


@router.get("/agents/{agent_id}/email", response_model=list[EmailIdentityResponse])
async def list_agent_emails(agent_id: UUID, auth: Auth, db: DB):
    result = await db.execute(
        select(EmailIdentity).where(
            EmailIdentity.agent_id == agent_id,
            EmailIdentity.org_id == auth["org_id"],
            EmailIdentity.status != "deleted",
        )
    )
    return result.scalars().all()


@router.delete("/agents/{agent_id}/email/{email_id}", status_code=204)
async def deprovision_agent_email(agent_id: UUID, email_id: UUID, auth: Auth, db: DB):
    identity = await db.get(EmailIdentity, email_id)
    if not identity or identity.org_id != auth["org_id"] or identity.agent_id != agent_id:
        raise HTTPException(status_code=404, detail="Email identity not found")
    await deprovision_email(db, identity)
    await log_event(
        db, auth["org_id"], auth["type"], "email.deprovisioned", "email_identity",
        resource_id=email_id,
    )
