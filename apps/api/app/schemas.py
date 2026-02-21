"""Pydantic request/response schemas."""

from datetime import datetime
from uuid import UUID

from enum import Enum
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, EmailStr, Field


# ---- Auth ----

class RegisterRequest(BaseModel):
    org_name: str = Field(min_length=1, max_length=100)
    org_slug: str = Field(min_length=1, max_length=50, pattern=r"^[a-z0-9\-]+$")
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Org ----

class OrgResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Agent ----

class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    metadata: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    metadata: dict | None = None


class AgentResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentTokenCreate(BaseModel):
    scopes: list[str] = Field(default_factory=list)


class AgentTokenResponse(BaseModel):
    id: UUID
    token: str | None = None  # Only on creation
    scopes: list[str]
    expires_at: datetime

    model_config = {"from_attributes": True}


# ---- Email ----

class EmailProvisionRequest(BaseModel):
    local_part: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9\.\-_]+$")
    domain: str | None = None


class EmailIdentityResponse(BaseModel):
    id: UUID
    agent_id: UUID
    address: str
    domain: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Phone ----

class PhoneProvisionRequest(BaseModel):
    country: str = Field(default="US", min_length=2, max_length=2)
    capabilities: list[str] = Field(default_factory=lambda: ["sms"])


class PhoneIdentityResponse(BaseModel):
    id: UUID
    agent_id: UUID
    number: str
    country: str
    capabilities: list[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Messages ----

class MessageResponse(BaseModel):
    id: UUID
    agent_id: UUID
    channel: str
    direction: str
    sender: str
    recipient: str
    subject: str | None
    body_text: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    agent_id: UUID
    channel: Literal["email", "sms"]
    to: str
    subject: str | None = None
    body: str = Field(min_length=1)


# ---- Vault ----

class SecretCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    value: str
    agent_id: UUID | None = None
    description: str | None = None


class SecretResponse(BaseModel):
    id: UUID
    org_id: UUID
    agent_id: UUID | None
    name: str
    description: str | None
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SecretValueResponse(SecretResponse):
    value: str


class SecretUpdate(BaseModel):
    value: str


# ---- Webhook ----

class WebhookCreate(BaseModel):
    url: AnyHttpUrl
    events: list[str] = Field(min_length=1)


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    events: list[str]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- API Keys ----

class ApiKeyCreate(BaseModel):
    name: str
    scopes: list[str] = Field(default_factory=list)


class ApiKeyResponse(BaseModel):
    id: UUID
    key_prefix: str
    name: str
    scopes: list[str]
    created_at: datetime
    key: str | None = None  # Only on creation

    model_config = {"from_attributes": True}


# ---- Pagination ----

class PaginatedResponse(BaseModel):
    data: list
    has_more: bool = False
    cursor: str | None = None


# ---- Errors ----

class ErrorDetail(BaseModel):
    code: str
    message: str
    param: str | None = None
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
