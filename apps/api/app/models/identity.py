"""Email and Phone identity models."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.types import GUID, StringArray


class EmailIdentity(Base):
    __tablename__ = "email_identities"
    __table_args__ = (
        Index("ix_email_identities_org_agent", "org_id", "agent_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("agents.id"), nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("orgs.id"), nullable=False)
    address: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    domain_verified: Mapped[bool] = mapped_column(default=False)
    provider: Mapped[str] = mapped_column(Text, default="mailgun")
    provider_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="provisioning")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="email_identities")


class PhoneIdentity(Base):
    __tablename__ = "phone_identities"
    __table_args__ = (
        Index("ix_phone_identities_org_agent", "org_id", "agent_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("agents.id"), nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("orgs.id"), nullable=False)
    number: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    country: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(Text, default="twilio")
    provider_sid: Mapped[str | None] = mapped_column(Text)
    capabilities: Mapped[list[str]] = mapped_column(StringArray, default=lambda: ["sms"])
    status: Mapped[str] = mapped_column(Text, default="provisioning")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="phone_identities")


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_org_agent", "org_id", "agent_id"),
        Index("ix_messages_org_created", "org_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("orgs.id"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("agents.id"), nullable=False)
    channel: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    identity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    recipient: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    body_text: Mapped[str | None] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    provider_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="received")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
