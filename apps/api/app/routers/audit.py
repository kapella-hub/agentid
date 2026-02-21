"""Audit log query endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.core.pagination import apply_cursor, encode_cursor
from app.models.audit import AuditEvent
from app.schemas import PaginatedResponse

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


@router.get("", response_model=PaginatedResponse)
async def list_audit_events(
    auth: Auth,
    db: DB,
    action: str | None = None,
    resource_type: str | None = None,
    limit: int = Query(default=50, le=200),
    cursor: str | None = None,
):
    q = select(AuditEvent).where(AuditEvent.org_id == auth["org_id"])
    if action:
        q = q.where(AuditEvent.action == action)
    if resource_type:
        q = q.where(AuditEvent.resource_type == resource_type)
    q = apply_cursor(q, cursor, AuditEvent.id, limit)
    result = await db.execute(q)
    items = list(result.scalars().all())

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return PaginatedResponse(
        data=[AuditEventResponse.model_validate(e) for e in items],
        has_more=has_more,
        cursor=encode_cursor(items[-1].id) if items else None,
    )
