"""Audit log query endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.models.audit import AuditEvent
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEventResponse(BaseModel):
    id: UUID
    org_id: UUID
    actor_type: str
    actor_id: UUID | None
    action: str
    resource_type: str
    resource_id: UUID | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[AuditEventResponse])
async def list_audit_events(
    auth: Auth,
    db: DB,
    action: str | None = None,
    resource_type: str | None = None,
    limit: int = Query(default=50, le=200),
):
    q = select(AuditEvent).where(AuditEvent.org_id == auth["org_id"])
    if action:
        q = q.where(AuditEvent.action == action)
    if resource_type:
        q = q.where(AuditEvent.resource_type == resource_type)
    q = q.order_by(AuditEvent.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()
