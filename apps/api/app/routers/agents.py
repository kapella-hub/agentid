"""Agent CRUD + token management."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import DB, Auth
from app.core.security import create_agent_token
from app.models.agent import Agent, AgentToken
from app.schemas import AgentCreate, AgentResponse, AgentTokenCreate, AgentTokenResponse, AgentUpdate
from app.services.audit_service import log_event

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(req: AgentCreate, auth: Auth, db: DB):
    agent = Agent(org_id=auth["org_id"], name=req.name, description=req.description, metadata_=req.metadata)
    db.add(agent)
    try:
        await db.flush()
    except Exception:
        raise HTTPException(status_code=409, detail="Agent name already exists in this org")

    await log_event(db, auth["org_id"], auth["type"], "agent.created", "agent", resource_id=agent.id)
    return agent


@router.get("", response_model=list[AgentResponse])
async def list_agents(auth: Auth, db: DB, limit: int = 50):
    result = await db.execute(
        select(Agent)
        .where(Agent.org_id == auth["org_id"], Agent.status != "deleted")
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: UUID, auth: Auth, db: DB):
    agent = await db.get(Agent, agent_id)
    if not agent or agent.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: UUID, req: AgentUpdate, auth: Auth, db: DB):
    agent = await db.get(Agent, agent_id)
    if not agent or agent.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    for field, value in req.model_dump(exclude_unset=True).items():
        if field == "metadata":
            agent.metadata_ = value
        else:
            setattr(agent, field, value)
    await db.flush()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: UUID, auth: Auth, db: DB):
    agent = await db.get(Agent, agent_id)
    if not agent or agent.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.status = "deleted"
    await log_event(db, auth["org_id"], auth["type"], "agent.deleted", "agent", resource_id=agent.id)


@router.post("/{agent_id}/tokens", response_model=AgentTokenResponse, status_code=201)
async def issue_agent_token(agent_id: UUID, req: AgentTokenCreate, auth: Auth, db: DB):
    agent = await db.get(Agent, agent_id)
    if not agent or agent.org_id != auth["org_id"]:
        raise HTTPException(status_code=404, detail="Agent not found")

    raw_token, token_hash = create_agent_token(str(auth["org_id"]), str(agent_id), req.scopes)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    agent_token = AgentToken(
        agent_id=agent_id,
        org_id=auth["org_id"],
        token_hash=token_hash,
        scopes=req.scopes,
        expires_at=expires_at,
    )
    db.add(agent_token)
    await db.flush()

    return AgentTokenResponse(id=agent_token.id, token=raw_token, scopes=req.scopes, expires_at=expires_at)
