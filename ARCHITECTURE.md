# AgentID — Technical Architecture (v0.1)

> Identity-as-a-Service for AI Agents
> MVP Scope: Phases 1–4 (Email, Phone, Vault, Payments)

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENTS                                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────────────┐  │
│  │ Dashboard │  │ REST API │  │ TS SDK    │  │ Python SDK        │  │
│  │ (Next.js) │  │ Clients  │  │           │  │                   │  │
│  └─────┬─────┘  └────┬─────┘  └─────┬─────┘  └────────┬──────────┘  │
└────────┼──────────────┼──────────────┼─────────────────┼────────────┘
         │              │              │                 │
         ▼              ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API GATEWAY / LOAD BALANCER                   │
│                    (nginx / ALB — TLS termination)                  │
│                    Rate limiting (token bucket per org)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  AUTH SERVICE   │  │  CORE API       │  │  WEBHOOK        │
│  (FastAPI)      │  │  (FastAPI)      │  │  INGRESS        │
│                 │  │                 │  │  (FastAPI)      │
│ - OAuth2/OIDC   │  │ - Orgs/Agents   │  │ - Mailgun cb   │
│ - API key auth  │  │ - Email CRUD    │  │ - Twilio cb    │
│ - Agent tokens  │  │ - Phone CRUD    │  │ - Stripe cb    │
│ - MFA (TOTP)    │  │ - Vault ops     │  │                │
│                 │  │ - Payments      │  │                │
└────────┬────────┘  └────────┬────────┘  └───────┬────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        TASK QUEUE (Redis + Celery)                  │
│                                                                     │
│  Queues:  provisioning | webhooks | vault-rotation | notifications  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
         ┌─────────────┬───────┼───────┬──────────────┐
         ▼             ▼       ▼       ▼              ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────────┐
│ PROVISIONING │ │ WEBHOOK  │ │ VAULT       │ │ PAYMENTS     │
│ WORKERS      │ │ DISPATCH │ │ SERVICE     │ │ SERVICE      │
│              │ │          │ │             │ │              │
│ - Mailgun    │ │ - Retry  │ │ - Envelope  │ │ - Connect    │
│ - Twilio     │ │ - DLQ    │ │   encryption│ │ - Charges    │
│ - DNS verify │ │ - Sign   │ │ - KMS       │ │ - App fees   │
└──────┬───────┘ └────┬─────┘ └──────┬──────┘ └──────┬───────┘
       │              │              │               │
       ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL PROVIDERS                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Mailgun  │  │ Twilio   │  │ AWS KMS  │  │ Stripe   │           │
│  │          │  │          │  │          │  │ Connect  │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                   │
│  ┌──────────────────────┐  ┌──────────────────┐                    │
│  │ PostgreSQL 16        │  │ Redis 7          │                    │
│  │                      │  │                  │                    │
│  │ - Core tables        │  │ - Task queues    │                    │
│  │ - Audit log          │  │ - Rate limits    │                    │
│  │ - Encrypted secrets  │  │ - Session cache  │                    │
│  │ (RLS by org_id)      │  │ - Pub/sub        │                    │
│  └──────────────────────┘  └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow: Inbound Email Example

1. Email arrives at `agent-xyz@agentid.io` → Mailgun receives
2. Mailgun POSTs to **Webhook Ingress** `/hooks/mailgun/inbound`
3. Ingress validates signature, stores message metadata + body in `messages` table
4. Enqueues webhook dispatch job for the agent's registered webhook URL
5. **Webhook Dispatcher** signs payload (HMAC-SHA256), delivers with retries (exponential backoff, 3 attempts)
6. On failure → Dead Letter Queue, surfaced in dashboard

---

## 2. Database Schema (PostgreSQL)

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- TENANCY & AUTH
-- ============================================================

CREATE TABLE orgs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    slug            TEXT UNIQUE NOT NULL,
    plan            TEXT NOT NULL DEFAULT 'starter',  -- starter | growth | enterprise
    stripe_customer_id TEXT,
    settings        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'member',  -- owner | admin | member
    mfa_secret_enc  BYTEA,                           -- TOTP secret, encrypted
    mfa_enabled     BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_org ON users(org_id);

CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    key_hash        TEXT NOT NULL UNIQUE,             -- SHA-256 of the key
    key_prefix      TEXT NOT NULL,                    -- first 8 chars for identification
    name            TEXT NOT NULL,
    scopes          TEXT[] NOT NULL DEFAULT '{}',     -- e.g. {'agents:read','vault:write'}
    expires_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_api_keys_org ON api_keys(org_id);

-- ============================================================
-- AGENTS
-- ============================================================

CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    name            TEXT NOT NULL,
    description     TEXT,
    status          TEXT NOT NULL DEFAULT 'active',   -- active | suspended | deleted
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, name)
);
CREATE INDEX idx_agents_org ON agents(org_id);

CREATE TABLE agent_tokens (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        UUID NOT NULL REFERENCES agents(id),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    token_hash      TEXT NOT NULL UNIQUE,
    scopes          TEXT[] NOT NULL DEFAULT '{}',
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_agent_tokens_agent ON agent_tokens(agent_id);

-- ============================================================
-- EMAIL IDENTITIES
-- ============================================================

CREATE TABLE email_identities (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        UUID NOT NULL REFERENCES agents(id),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    address         TEXT UNIQUE NOT NULL,              -- agent-xyz@agentid.io
    domain          TEXT NOT NULL,                     -- agentid.io or custom
    domain_verified BOOLEAN NOT NULL DEFAULT false,
    provider        TEXT NOT NULL DEFAULT 'mailgun',
    provider_id     TEXT,                              -- Mailgun route/mailbox ID
    status          TEXT NOT NULL DEFAULT 'provisioning', -- provisioning | active | suspended | deleted
    config          JSONB NOT NULL DEFAULT '{}',       -- sending limits, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_email_org ON email_identities(org_id);
CREATE INDEX idx_email_agent ON email_identities(agent_id);
CREATE INDEX idx_email_address ON email_identities(address);

CREATE TABLE email_domains (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    domain          TEXT UNIQUE NOT NULL,
    verification    JSONB NOT NULL DEFAULT '{}',       -- SPF/DKIM/DMARC records + status
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- PHONE IDENTITIES
-- ============================================================

CREATE TABLE phone_identities (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id        UUID NOT NULL REFERENCES agents(id),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    number          TEXT UNIQUE NOT NULL,              -- E.164 format
    country         TEXT NOT NULL,                     -- ISO 3166-1 alpha-2
    provider        TEXT NOT NULL DEFAULT 'twilio',
    provider_sid    TEXT,                              -- Twilio phone number SID
    capabilities    TEXT[] NOT NULL DEFAULT '{sms}',   -- sms | voice
    status          TEXT NOT NULL DEFAULT 'provisioning',
    config          JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_phone_org ON phone_identities(org_id);
CREATE INDEX idx_phone_agent ON phone_identities(agent_id);

-- ============================================================
-- MESSAGES (email + SMS unified)
-- ============================================================

CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    agent_id        UUID NOT NULL REFERENCES agents(id),
    channel         TEXT NOT NULL,                     -- email | sms
    direction       TEXT NOT NULL,                     -- inbound | outbound
    identity_id     UUID NOT NULL,                     -- FK to email_identities or phone_identities
    sender          TEXT NOT NULL,
    recipient       TEXT NOT NULL,
    subject         TEXT,                              -- email only
    body_text       TEXT,
    body_html       TEXT,                              -- email only
    metadata        JSONB NOT NULL DEFAULT '{}',       -- headers, provider metadata
    provider_id     TEXT,                              -- provider message ID
    status          TEXT NOT NULL DEFAULT 'received',  -- received | delivered | failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_messages_agent ON messages(agent_id, created_at DESC);
CREATE INDEX idx_messages_org ON messages(org_id, created_at DESC);
CREATE INDEX idx_messages_channel ON messages(channel, agent_id);

-- ============================================================
-- CREDENTIAL VAULT
-- ============================================================

CREATE TABLE secrets (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    agent_id        UUID REFERENCES agents(id),        -- NULL = org-level secret
    name            TEXT NOT NULL,
    description     TEXT,
    encrypted_value BYTEA NOT NULL,                    -- AES-256-GCM encrypted
    dek_id          UUID NOT NULL REFERENCES data_encryption_keys(id),
    version         INT NOT NULL DEFAULT 1,
    rotation_policy JSONB,                             -- e.g. {"interval_days": 90}
    last_rotated_at TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(org_id, agent_id, name)
);
CREATE INDEX idx_secrets_org ON secrets(org_id);
CREATE INDEX idx_secrets_agent ON secrets(agent_id);

CREATE TABLE data_encryption_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    encrypted_dek   BYTEA NOT NULL,                    -- DEK wrapped by KMS CMK
    kms_key_id      TEXT NOT NULL,                     -- KMS key ARN
    status          TEXT NOT NULL DEFAULT 'active',    -- active | rotating | retired
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE secret_access_log (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    secret_id       UUID NOT NULL REFERENCES secrets(id),
    accessor_type   TEXT NOT NULL,                     -- user | agent_token | api_key
    accessor_id     UUID NOT NULL,
    action          TEXT NOT NULL,                     -- read | write | rotate | delete
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_secret_access_secret ON secret_access_log(secret_id, created_at DESC);

-- ============================================================
-- PAYMENTS (Stripe Connect)
-- ============================================================

CREATE TABLE payment_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES orgs(id) UNIQUE,
    stripe_account_id   TEXT UNIQUE,                   -- acct_xxx (Connected Account)
    onboarding_status   TEXT NOT NULL DEFAULT 'pending', -- pending | onboarding | active | restricted
    capabilities        JSONB NOT NULL DEFAULT '{}',
    application_fee_pct NUMERIC(5,2) NOT NULL DEFAULT 2.00,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE payment_transactions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id              UUID NOT NULL REFERENCES orgs(id),
    agent_id            UUID REFERENCES agents(id),
    stripe_charge_id    TEXT,
    amount_cents        INT NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'usd',
    application_fee     INT,
    status              TEXT NOT NULL,                  -- pending | succeeded | failed | refunded
    metadata            JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_txn_org ON payment_transactions(org_id, created_at DESC);

-- ============================================================
-- WEBHOOKS
-- ============================================================

CREATE TABLE webhook_endpoints (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL REFERENCES orgs(id),
    url             TEXT NOT NULL,
    events          TEXT[] NOT NULL,                    -- e.g. {'email.received','sms.received'}
    signing_secret  TEXT NOT NULL,                      -- HMAC secret
    status          TEXT NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_webhooks_org ON webhook_endpoints(org_id);

CREATE TABLE webhook_deliveries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint_id     UUID NOT NULL REFERENCES webhook_endpoints(id),
    event_type      TEXT NOT NULL,
    payload         JSONB NOT NULL,
    response_status INT,
    attempts        INT NOT NULL DEFAULT 0,
    next_retry_at   TIMESTAMPTZ,
    status          TEXT NOT NULL DEFAULT 'pending',   -- pending | delivered | failed
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_deliveries_status ON webhook_deliveries(status, next_retry_at);

-- ============================================================
-- AUDIT LOG (append-only)
-- ============================================================

CREATE TABLE audit_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id          UUID NOT NULL,
    actor_type      TEXT NOT NULL,                     -- user | api_key | agent_token | system
    actor_id        UUID,
    action          TEXT NOT NULL,                     -- e.g. agent.created, secret.read, email.provisioned
    resource_type   TEXT NOT NULL,
    resource_id     UUID,
    metadata        JSONB NOT NULL DEFAULT '{}',
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_org ON audit_events(org_id, created_at DESC);
CREATE INDEX idx_audit_action ON audit_events(action, created_at DESC);

-- Partition by month for performance
-- CREATE TABLE audit_events_2026_02 PARTITION OF audit_events
--     FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

---

## 3. API Design (FastAPI)

### 3.1 Authentication Model

Three auth mechanisms, resolved by middleware:

| Mechanism | Format | Use Case | Scopes |
|-----------|--------|----------|--------|
| **Org API Key** | `Authorization: Bearer agid_live_xxx` | Server-to-server | Configurable per key |
| **User Session** | HTTP-only cookie (JWT) | Dashboard | Role-based (owner/admin/member) |
| **Agent Token** | `Authorization: Bearer agt_xxx` | Agent runtime | Scoped to single agent + capabilities |

**Token format:**
- Org API keys: `agid_live_` prefix (production) / `agid_test_` (sandbox)
- Agent tokens: `agt_` prefix, JWT with claims `{org_id, agent_id, scopes, exp}`
- All tokens hashed (SHA-256) before storage; raw value shown once at creation

### 3.2 Endpoint Reference

All endpoints prefixed `/v1/`. Request/response bodies are JSON.

#### Auth & Org Management

```
POST   /v1/auth/register            # Create org + first user
POST   /v1/auth/login               # Email + password → session
POST   /v1/auth/mfa/verify          # TOTP verification
POST   /v1/auth/logout              # Invalidate session

GET    /v1/orgs/me                   # Current org details
PATCH  /v1/orgs/me                   # Update org settings

POST   /v1/api-keys                  # Create org API key
GET    /v1/api-keys                  # List keys (prefix only)
DELETE /v1/api-keys/{id}             # Revoke key
```

#### Agents

```
POST   /v1/agents                    # Create agent
GET    /v1/agents                    # List agents (paginated)
GET    /v1/agents/{id}               # Get agent detail
PATCH  /v1/agents/{id}               # Update agent
DELETE /v1/agents/{id}               # Soft-delete (suspends identities)

POST   /v1/agents/{id}/tokens        # Issue scoped agent token
GET    /v1/agents/{id}/tokens        # List active tokens
DELETE /v1/agents/{id}/tokens/{tid}   # Revoke token
```

#### Email Provisioning

```
POST   /v1/agents/{id}/email         # Provision email identity
  Request:  { "local_part": "support-bot", "domain": "agentid.io" }
  Response: { "id": "...", "address": "support-bot@agentid.io", "status": "provisioning" }

GET    /v1/agents/{id}/email          # List email identities for agent
DELETE /v1/agents/{id}/email/{eid}    # Deprovision

POST   /v1/domains                    # Register custom domain
GET    /v1/domains                    # List domains + verification status
GET    /v1/domains/{id}/verify        # Check DNS verification
```

#### Phone Provisioning

```
POST   /v1/agents/{id}/phone         # Provision phone number
  Request:  { "country": "US", "capabilities": ["sms"] }
  Response: { "id": "...", "number": "+1234567890", "status": "provisioning" }

GET    /v1/agents/{id}/phone          # List phone identities
DELETE /v1/agents/{id}/phone/{pid}    # Release number
```

#### Messages

```
GET    /v1/messages                   # List messages (filtered)
  Query:  ?agent_id=...&channel=email|sms&direction=inbound&since=...&limit=50

GET    /v1/messages/{id}              # Get message detail (full body)

POST   /v1/messages/send              # Send outbound (email or SMS)
  Request:  { "agent_id": "...", "channel": "email", "to": "user@example.com",
              "subject": "Hello", "body": "..." }
```

#### Credential Vault

```
POST   /v1/secrets                    # Create secret
  Request:  { "agent_id": "...", "name": "openai_key", "value": "sk-xxx" }
  Response: { "id": "...", "name": "openai_key", "version": 1 }
  # Value is encrypted at rest; never returned after creation

GET    /v1/secrets                    # List secrets (metadata only)
GET    /v1/secrets/{id}               # Get secret value (requires scope: vault:read)
  Response: { "id": "...", "name": "openai_key", "value": "sk-xxx", "version": 1 }
  # Audit logged. Dashboard requires MFA re-confirmation.

PUT    /v1/secrets/{id}               # Update secret value (new version)
POST   /v1/secrets/{id}/rotate        # Trigger rotation
DELETE /v1/secrets/{id}               # Soft-delete secret
```

#### Payments

```
POST   /v1/payments/connect/onboard   # Start Stripe Connect onboarding
  Response: { "url": "https://connect.stripe.com/...", "status": "onboarding" }

GET    /v1/payments/connect/status     # Check onboarding status

POST   /v1/payments/charges            # Create charge via connected account
  Request:  { "agent_id": "...", "amount_cents": 5000, "currency": "usd",
              "description": "...", "metadata": {} }
  # Automatically applies application_fee_amount (2%)
```

#### Webhooks

```
POST   /v1/webhooks                   # Register endpoint
GET    /v1/webhooks                   # List endpoints
PATCH  /v1/webhooks/{id}              # Update endpoint
DELETE /v1/webhooks/{id}              # Remove endpoint
GET    /v1/webhooks/{id}/deliveries   # List recent deliveries + status
```

#### Audit

```
GET    /v1/audit                      # Query audit log
  Query:  ?action=secret.read&since=...&actor_id=...&limit=100
GET    /v1/audit/export               # CSV export (async, returns download URL)
```

### 3.3 Webhook Events

| Event | Trigger |
|-------|---------|
| `email.received` | Inbound email stored |
| `sms.received` | Inbound SMS stored |
| `email.provisioned` | Email identity active |
| `phone.provisioned` | Phone number active |
| `secret.rotated` | Secret version bumped |
| `identity.revoked` | Any identity suspended/deleted |
| `payment.succeeded` | Charge completed |
| `payment.failed` | Charge failed |

**Delivery format:**
```json
{
  "id": "evt_xxx",
  "type": "email.received",
  "created_at": "2026-02-21T12:00:00Z",
  "data": { ... }
}
```
**Signature:** `X-AgentID-Signature: sha256=HMAC(signing_secret, raw_body)`

### 3.4 Error Format

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Agent name already exists in this org",
    "param": "name",
    "request_id": "req_xxx"
  }
}
```

Standard HTTP codes: 400, 401, 403, 404, 409, 422, 429, 500.

### 3.5 Pagination

Cursor-based for all list endpoints:
```
GET /v1/agents?limit=20&cursor=eyJpZCI6Inh4eCJ9
→ { "data": [...], "has_more": true, "cursor": "eyJpZCI6Inl5eSJ9" }
```

### 3.6 Rate Limits

| Tier | Requests/min | Burst |
|------|-------------|-------|
| Starter | 60 | 120 |
| Growth | 300 | 600 |
| Enterprise | Custom | Custom |

Returned in headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

---

## 4. Service Boundaries

### 4.1 Service Map

The MVP is a **modular monolith** — single deployable with clear internal boundaries, ready to split later.

```
apps/api/
├── core/              # Shared: auth middleware, DB session, config, pagination
├── agents/            # Agent CRUD, token issuance
├── email/             # Email provisioning, Mailgun integration
│   ├── routes.py
│   ├── service.py     # Orchestrates Mailgun API calls
│   ├── models.py
│   └── tasks.py       # Celery tasks: provision, deprovision
├── phone/             # Phone provisioning, Twilio integration
│   ├── routes.py
│   ├── service.py
│   ├── models.py
│   └── tasks.py
├── vault/             # Secret management, encryption
│   ├── routes.py
│   ├── service.py     # Encrypt/decrypt via envelope encryption
│   ├── kms.py         # KMS client abstraction
│   └── models.py
├── payments/          # Stripe Connect integration
│   ├── routes.py
│   ├── service.py
│   └── models.py
├── webhooks/          # Webhook registration + dispatch
│   ├── routes.py
│   ├── ingress.py     # Provider callback handlers
│   ├── dispatcher.py  # Celery: sign + deliver + retry
│   └── models.py
├── audit/             # Audit log write + query
└── hooks/             # Incoming provider webhooks (Mailgun, Twilio, Stripe)
    ├── mailgun.py
    ├── twilio.py
    └── stripe.py
```

### 4.2 Provider Abstractions

Each external provider has an adapter interface, enabling swap-out:

```python
class EmailProvider(Protocol):
    async def create_mailbox(self, address: str, domain: str) -> str: ...
    async def delete_mailbox(self, provider_id: str) -> None: ...
    async def send(self, from_addr: str, to: str, subject: str, body: str) -> str: ...

class PhoneProvider(Protocol):
    async def provision_number(self, country: str, capabilities: list[str]) -> ProvisionedNumber: ...
    async def release_number(self, provider_sid: str) -> None: ...
    async def send_sms(self, from_number: str, to: str, body: str) -> str: ...
```

---

## 5. Security Model

### 5.1 Encryption Architecture

```
                    ┌─────────────┐
                    │  AWS KMS    │
                    │  (CMK)      │  ← Customer Master Key (never leaves KMS)
                    └──────┬──────┘
                           │ Wrap/Unwrap
                           ▼
                    ┌─────────────┐
                    │    DEK      │  ← Data Encryption Key (one per org)
                    │ (AES-256)   │  Stored encrypted in `data_encryption_keys`
                    └──────┬──────┘
                           │ Encrypt/Decrypt
                           ▼
                    ┌─────────────┐
                    │  Secrets    │  ← Individual secret values
                    │ (AES-256-  │    Encrypted with DEK using AES-256-GCM
                    │  GCM)      │    Nonce stored alongside ciphertext
                    └─────────────┘
```

**Envelope encryption flow:**
1. On first secret for an org → generate DEK, wrap with KMS, store wrapped DEK
2. To encrypt: unwrap DEK via KMS → AES-256-GCM encrypt → store ciphertext + nonce
3. To decrypt: unwrap DEK via KMS → AES-256-GCM decrypt → return plaintext
4. DEK cached in-memory (60s TTL) to reduce KMS calls

**Key rotation:** Generate new DEK, re-encrypt all org secrets, retire old DEK.

### 5.2 Authentication Security

- **Passwords:** Argon2id (memory=64MB, iterations=3, parallelism=4)
- **API keys:** 32-byte random, SHA-256 hashed before storage
- **Agent tokens:** JWT (ES256), 1-hour default TTL, refresh via API key
- **Sessions:** HTTP-only, Secure, SameSite=Strict cookies; 24h expiry
- **MFA:** TOTP (RFC 6238), required for vault read in dashboard

### 5.3 Transport Security

- TLS 1.3 enforced at load balancer
- Internal service communication over private network (no public exposure)
- Webhook delivery validates provider signatures (Mailgun, Twilio, Stripe)
- Outbound webhook signatures use per-endpoint HMAC-SHA256

### 5.4 Access Control

```
Org Owner ──► Full access to all resources
Org Admin ──► Manage agents, identities, secrets; cannot delete org
Org Member ──► Read-only dashboard; cannot manage secrets
API Key ──► Scoped by explicit permission set
Agent Token ──► Scoped to single agent + allowed operations
```

**Scope grammar:** `resource:action` — e.g. `agents:write`, `vault:read`, `messages:read`, `payments:charge`

### 5.5 Audit & Compliance

- **Every mutating operation** produces an `audit_event` (append-only table)
- Audit entries include: actor, action, resource, IP, timestamp, metadata
- **Secret reads** are additionally logged to `secret_access_log` with accessor details
- Audit log export available as CSV; retention: 2 years minimum
- Dashboard shows real-time audit stream filtered by org

### 5.6 Anti-Abuse Controls

| Control | Implementation |
|---------|---------------|
| Rate limiting | Redis token bucket per org + per-agent |
| Email sending cap | 100/day (starter), 1000/day (growth), configurable |
| SMS sending cap | 50/day (starter), 500/day (growth) |
| Webhook delivery | 3 retries with exponential backoff (10s, 60s, 300s) then DLQ |
| Provisioning throttle | Max 10 identities/org (starter), 100 (growth) |
| Content scanning | Outbound email/SMS checked against basic spam patterns |

---

## 6. Scalability Considerations

### 6.1 MVP Target

- **100 orgs, 1,000 agents, 10,000 messages/day** — single instance is sufficient
- PostgreSQL handles this trivially; Redis for queues adds reliability

### 6.2 Scaling Path

| Component | MVP | Scale Strategy |
|-----------|-----|---------------|
| API | Single FastAPI process (uvicorn, 4 workers) | Horizontal: multiple pods behind LB |
| Database | Single PostgreSQL instance | Read replicas → eventually shard by org_id |
| Task queue | Single Celery worker | Scale workers independently per queue |
| Webhook ingress | Shared with API | Separate deployment for isolation |
| Audit log | Single table | Partition by month; archive to S3 after 6 months |
| Messages | Single table | Partition by month + org_id; archive old messages |
| Vault | In-DB encrypted | No change needed; KMS scales independently |

### 6.3 Infrastructure (MVP)

```
Production:
  - 1x API server (4 vCPU, 8GB) — FastAPI + uvicorn
  - 1x Worker server (2 vCPU, 4GB) — Celery workers
  - 1x PostgreSQL (managed, e.g. RDS db.t4g.medium)
  - 1x Redis (managed, e.g. ElastiCache t4g.small)
  - ALB + ACM for TLS
  - AWS KMS for vault encryption

Staging:
  - Mirrors production at smaller instance sizes
  - Stripe test mode, Twilio test credentials, Mailgun sandbox
```

### 6.4 Deployment

- **Docker** containers, deployed via **ECS Fargate** (or k8s if preferred)
- **Alembic** for DB migrations (run as pre-deploy task)
- **GitHub Actions** CI/CD: lint → test → build → deploy staging → deploy prod
- Blue-green deploys for zero-downtime

### 6.5 Observability

- **Structured logging** (JSON) → CloudWatch / Datadog
- **OpenTelemetry** traces across API → Queue → Worker → Provider
- **Metrics:** request latency (p50/p95/p99), error rate, queue depth, provisioning time
- **Alerts:** error rate > 5%, queue backlog > 100, provisioning failure rate > 10%

---

## 7. Open Architecture Decisions

| # | Decision | Recommendation | Rationale |
|---|----------|---------------|-----------|
| 1 | Message body storage | Store full bodies, encrypt at rest, 90-day retention default | Agents need message content; let orgs configure retention |
| 2 | Custom domain mailbox access | API-only (no IMAP) for MVP | IMAP adds complexity; API covers agent use cases |
| 3 | Payments merchant model | Platform-only (Stripe Connect) | Avoids MoR liability; revisit if unit economics demand it |
| 4 | KYC/KYB | Stripe Identity for payment orgs; manual review for high tiers | Minimizes build; gates abuse at payment layer |
| 5 | Queue system | Celery + Redis | Python ecosystem alignment with FastAPI; BullMQ if we ever go Node |

---

## 8. Technology Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), React, Tailwind CSS, shadcn/ui |
| API | FastAPI (Python 3.12), Pydantic v2, uvicorn |
| Auth | JWT (ES256) + HTTP-only sessions, Argon2id passwords |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7, Celery 5 |
| Email Provider | Mailgun |
| Phone Provider | Twilio |
| Payments | Stripe Connect |
| Encryption | AWS KMS + AES-256-GCM envelope encryption |
| Infra | Docker, ECS Fargate, RDS, ElastiCache, ALB, ACM |
| CI/CD | GitHub Actions |
| Observability | OpenTelemetry, CloudWatch/Datadog, Sentry |
| IaC | Terraform |
