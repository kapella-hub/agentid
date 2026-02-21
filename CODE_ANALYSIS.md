# AgentID — Codebase Analysis

> Analysis of the AgentID repository at v0.1.0 (MVP)

---

## 1. Project Overview

**AgentID** is an **Identity-as-a-Service (IDaaS) platform for AI agents**. It gives AI agents real-world identities — email addresses, phone numbers, encrypted credential storage, and payment capabilities — accessible through a REST API. The platform is multi-tenant, with organizations managing multiple agents, each with their own communication identities and secrets.

**Target users:** Developers building AI agent systems who need their agents to send/receive emails, SMS, store API keys securely, and process payments.

---

## 2. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend API** | FastAPI (Python) | Python 3.12, FastAPI ≥0.115 |
| **ORM** | SQLAlchemy (async) | ≥2.0.30 |
| **Database** | PostgreSQL | 16 |
| **Cache / Queue** | Redis + Celery | Redis 7, Celery 5.4 |
| **Frontend** | Next.js (React) | 14 (App Router) |
| **Styling** | Tailwind CSS | via `tailwind.config.ts` |
| **Email Provider** | Mailgun | REST API |
| **Phone Provider** | Twilio | REST API |
| **Payments** | Stripe Connect | ≥10.0 |
| **Encryption** | `cryptography` (AES-256-GCM) | ≥43.0 |
| **Auth** | JWT (python-jose) + Argon2id (passlib) | HS256 |
| **Testing** | pytest + pytest-asyncio + SQLite in-memory | pytest ≥8.0 |
| **Linting** | ruff | ≥0.8 |
| **CI/CD** | GitHub Actions | 3 jobs (backend, frontend, security) |
| **Deployment** | Docker + Railway | Multi-stage Dockerfile |

---

## 3. Architecture

### 3.1 Pattern: Modular Monolith

The backend is a single FastAPI application with clear internal module boundaries:

```
apps/api/app/
├── core/       → Shared infrastructure (config, DB, auth, encryption)
├── models/     → SQLAlchemy ORM models (6 modules, 12 models)
├── routers/    → HTTP endpoint handlers (9 modules)
├── services/   → Business logic (4 modules)
├── schemas.py  → Pydantic request/response models
└── tasks/      → Celery async tasks (placeholder)
```

Each domain (agents, email, phone, vault, webhooks, audit) has its own model file, router, and optionally a service layer. This structure supports future extraction into microservices.

### 3.2 Request Lifecycle

```
Client → FastAPI Router → Auth Dependency → Service Layer → SQLAlchemy → PostgreSQL
                                                 ↓
                                          External Provider (Mailgun/Twilio/Stripe)
```

1. Every request passes through `get_current_auth()` which resolves the bearer token into an auth context dict containing `type`, `org_id`, and role/scope information.
2. All queries are scoped by `org_id` for tenant isolation.
3. Mutating operations trigger `audit_service.log_event()` for audit logging.
4. Database sessions auto-commit on success, rollback on exception (via the `get_db` generator dependency).

### 3.3 Authentication Flow

Three credential types, resolved in order by `deps.py:get_current_auth()`:

| Priority | Type | Detection | Returns |
|----------|------|-----------|---------|
| 1 | **User JWT** | Valid JWT with `type: "user"` | `{type, org_id, user_id, role}` |
| 2 | **Agent Token** | Valid JWT with `type: "agent"` | `{type, org_id, agent_id, scopes}` |
| 3 | **Org API Key** | SHA-256 hash matches `api_keys` table | `{type, org_id, scopes}` |

### 3.4 Data Model

```
orgs (tenant root)
 ├── users (human operators)
 ├── api_keys (server-to-server auth)
 ├── agents
 │    ├── agent_tokens
 │    ├── email_identities
 │    ├── phone_identities
 │    └── messages (email + SMS, inbound + outbound)
 ├── secrets (encrypted credentials)
 │    └── data_encryption_keys (per-org DEK)
 ├── webhook_endpoints
 │    └── webhook_deliveries
 └── audit_events (append-only log)
```

---

## 4. Module-by-Module Analysis

### 4.1 Core Infrastructure

**`core/config.py`** — Pydantic `BaseSettings` with `AGENTID_` env prefix. Covers database, Redis, JWT, Mailgun, Twilio, Stripe, vault encryption, and rate limiting. Clean and well-organized.

**`core/database.py`** — Async SQLAlchemy engine with session factory. The `get_db()` dependency yields a session that auto-commits/rollbacks. Simple and correct for the modular monolith pattern.

**`core/security.py`** — Password hashing (Argon2id with strong parameters), API key generation (`agid_live_` prefix + 32-byte random), and JWT creation/decoding. All operations are synchronous which is appropriate for their nature.

**`core/encryption.py`** — Envelope encryption implementation using AES-256-GCM. The master key is loaded from config (base64-encoded env var) with a dev fallback. DEK generation, wrapping, unwrapping, and secret encrypt/decrypt are cleanly separated.

**`core/deps.py`** — FastAPI dependency injection for auth (`Auth`) and database sessions (`DB`). The `get_current_auth()` function resolves bearer tokens through a JWT-first, then API-key-fallback strategy. `require_scope()` is a factory that returns scope-checking dependencies.

**`core/types.py`** — Custom SQLAlchemy type decorators for UUID (`GUID`) and string arrays (`StringArray`) that work on both PostgreSQL and SQLite. Enables the test suite to use SQLite while production runs PostgreSQL.

### 4.2 Models (ORM Layer)

6 model files define 12 SQLAlchemy ORM classes. All use:
- UUID primary keys via the custom `GUID` type
- `server_default=func.now()` for timestamps
- Appropriate foreign keys and relationships
- `mapped_column` with `Mapped[]` type hints (modern SQLAlchemy 2.0 style)

**Notable:** The `metadata` column on `Agent` and `AuditEvent` is aliased as `metadata_` to avoid collision with SQLAlchemy's `MetaData`. The `config` column on identities uses `JSON` type for flexible provider-specific data.

### 4.3 Routers (API Layer)

9 router modules mount under `/v1` (except `hooks` which receives provider callbacks at root level):

| Router | Prefix | Endpoints |
|--------|--------|-----------|
| `auth` | `/v1` | POST register, login; GET org; CRUD api-keys |
| `agents` | `/v1/agents` | Full CRUD + token issuance |
| `email` | `/v1/agents/{id}/email` | Provision, list, deprovision |
| `phone` | `/v1/agents/{id}/phone` | Provision, list, deprovision |
| `messages` | `/v1/messages` | List, get, send (email/SMS) |
| `vault` | `/v1/secrets` | CRUD with encryption |
| `webhooks` | `/v1/webhooks` | CRUD for webhook endpoints |
| `audit` | `/v1/audit` | Query audit log |
| `hooks` | `/hooks` | Mailgun/Twilio inbound callbacks |

All endpoints consistently use:
- `Auth` dependency for authentication
- `DB` dependency for database access
- Pydantic schemas for request/response validation
- HTTP status codes (201 for creation, 204 for deletion, 4xx for errors)

### 4.4 Services (Business Logic)

**`vault_service.py`** — Implements the envelope encryption flow:
1. `_get_or_create_dek()`: Retrieves or creates a per-org DEK
2. `create_secret()`: Encrypts a value and stores it
3. `read_secret()`: Decrypts a stored secret
4. `rotate_secret()`: Re-encrypts with a new value, increments version

**`email_service.py`** — `MailgunClient` wraps the Mailgun REST API for route creation (inbound forwarding), route deletion, and email sending. `provision_email()` creates the identity record and Mailgun route atomically.

**`phone_service.py`** — `TwilioClient` wraps Twilio's REST API for number search/purchase, release, and SMS sending. `provision_phone()` purchases a number and creates the identity record.

**`audit_service.py`** — Single `log_event()` function creates `AuditEvent` records. Minimal but effective.

### 4.5 Frontend

Next.js 14 with App Router, providing a single-page dashboard with 5 panels:
- **AgentList**: Browse and select agents
- **IdentityManager**: Manage email/phone identities per agent
- **CredentialVault**: View and manage encrypted secrets
- **ApiKeyManager**: Create and revoke API keys
- **UsageBilling**: Usage metrics and billing info

The `ApiClient` class in `lib/api-client.ts` provides typed methods for all backend endpoints with automatic auth header injection.

### 4.6 Testing

5 test files using pytest-asyncio with SQLite in-memory:

| Test File | What It Tests | Assertions |
|-----------|--------------|------------|
| `test_auth.py` | Registration, login, duplicate detection | HTTP status codes, token presence |
| `test_agents.py` | Agent CRUD lifecycle, token issuance | Status codes, response payloads |
| `test_vault.py` | Secret create/read/rotate/delete | Encryption roundtrip, versioning |
| `test_encryption.py` | DEK wrap/unwrap, secret encrypt/decrypt | Byte-level correctness |
| `test_security.py` | Password hashing, API key gen, JWT | Cryptographic properties |

The `conftest.py` creates an in-memory SQLite database, overrides the `get_db` dependency, and provides an `AsyncClient` fixture for HTTP testing.

---

## 5. Identified Issues

### 5.1 Security Issues

| # | Severity | Location | Issue | Impact |
|---|----------|----------|-------|--------|
| S1 | **High** | `routers/hooks.py` | No webhook signature validation on Mailgun/Twilio inbound endpoints | Anyone can forge inbound emails/SMS by POSTing to `/hooks/mailgun/inbound` or `/hooks/twilio/sms` |
| S2 | **Medium** | `core/config.py` | JWT uses HS256, architecture doc specifies ES256 | HS256 is a shared-secret algorithm; ES256 (asymmetric) is more secure for distributed verification |
| S3 | **Medium** | `core/config.py:21` | Default JWT secret is `"CHANGE-ME-IN-PRODUCTION"` | Risk of deploying with the default secret if env var is not set |
| S4 | **Low** | `core/encryption.py:20` | Dev fallback master key is deterministic (`agentid-dev-master-key-00000000!`) | Predictable encryption in development; documented and acceptable for dev only |

### 5.2 Correctness Issues

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| C1 | **High** | `Dockerfile:10` | References `apps/web/` but frontend code lives in `frontend/` — Docker build will fail for frontend stage |
| C2 | **High** | `docker-compose.yml:81-90` | Web service mounts `./apps/web:/app` but frontend is at `./frontend/` |
| C3 | **High** | `.github/workflows/ci.yml:48-51` | CI references `apps/api/requirements.txt` and `requirements-dev.txt` which don't exist; only `pyproject.toml` is present |
| C4 | **Medium** | `frontend/lib/api-client.ts` | Several API paths don't match backend routes (e.g., `/messages/email` vs `/messages?channel=email`, `/identities/email/{id}` vs `/agents/{id}/email/{eid}`) |
| C5 | **Medium** | `.env.example` vs `core/config.py` | Env var naming mismatch — `.env.example` uses `JWT_SECRET` but config expects `AGENTID_JWT_SECRET_KEY` (due to `env_prefix: "AGENTID_"`) |

### 5.3 Missing Implementations

| # | Description | Evidence |
|---|-------------|---------|
| M1 | **Rate limiting** — config field exists (`rate_limit_per_minute`), no middleware implements it | `core/config.py:44`, no middleware in `main.py` |
| M2 | **Celery tasks** — `tasks/__init__.py` is empty; email/phone provisioning runs synchronously in request handlers | `tasks/__init__.py` is a blank placeholder |
| M3 | **MFA/TOTP** — `User.mfa_enabled` field exists, no TOTP generation/verification endpoints | `models/auth.py:37`, no `/auth/mfa/*` routes |
| M4 | **Cursor-based pagination** — `PaginatedResponse` schema exists, no endpoint uses it | `schemas.py:207-210`, list endpoints return bare lists |
| M5 | **`secret_access_log`** — table defined in architecture, model not implemented | SQL in ARCHITECTURE.md, no model or writes |
| M6 | **Webhook delivery dispatch** — `WebhookDelivery` model exists, no dispatcher sends events to registered webhook URLs | `models/webhook.py:25-36`, no dispatch logic |
| M7 | **Payments/Stripe Connect** — No router or service for payment endpoints | ARCHITECTURE.md defines endpoints, no implementation |

### 5.4 Code Quality Observations

| # | Location | Observation |
|---|----------|------------|
| Q1 | `routers/hooks.py:22` | Creates its own `async_session_factory()` session instead of using the `DB` dependency, bypassing the standard transaction/rollback pattern |
| Q2 | `routers/auth.py:119` | Inline import of `datetime` inside `revoke_api_key()` — should be at module top |
| Q3 | `services/phone_service.py:26,56,67` | `httpx` imported inside methods instead of at module top |
| Q4 | `models/agent.py:22` | `metadata_` alias pattern works but is inconsistent — some models use it, others don't need it |
| Q5 | `OPS.md:187-201` | Documents `packages/sdk-ts/` and `packages/sdk-py/` directories that don't exist yet |

---

## 6. Test Coverage Assessment

### What's Tested
- Auth flow (register + login) — happy path and error cases
- Agent CRUD — full lifecycle including soft-delete
- Agent token issuance — creation and scope verification
- Vault secrets — create, read (decrypt), rotate (version bump), delete
- Encryption primitives — DEK wrap/unwrap roundtrip, secret encrypt/decrypt
- Security utilities — password hashing, API key generation, JWT encode/decode

### What's Not Tested
- Email provisioning / Mailgun integration
- Phone provisioning / Twilio integration
- Message sending and receiving
- Webhook endpoint management
- Audit log queries
- Inbound webhook handlers (Mailgun/Twilio callbacks)
- API key authentication flow (only JWT tested)
- Scope-based authorization
- Error handling edge cases (e.g., provider failures)
- Frontend components

---

## 7. Strengths

1. **Clean separation of concerns** — Routers handle HTTP, services handle business logic, models handle persistence. Each domain is isolated.

2. **Proper envelope encryption** — The vault uses industry-standard AES-256-GCM with per-org DEKs, designed for easy KMS migration.

3. **Consistent audit logging** — Every mutating operation calls `log_event()`, creating a comprehensive audit trail.

4. **Multi-tenant isolation** — Every query includes `org_id` scoping. No cross-tenant data access is possible through the API layer.

5. **Portable test infrastructure** — Custom `GUID` and `StringArray` types enable fast SQLite-based tests while running PostgreSQL in production.

6. **Dev-mode fallbacks** — Email and phone provisioning work without provider API keys, assigning fake identities for local development.

7. **Well-documented architecture** — `ARCHITECTURE.md` (787 lines) provides thorough coverage of the system design, database schema, API contracts, security model, and scaling strategy.

8. **Modern Python patterns** — Uses Python 3.12 features (union types `X | None`), SQLAlchemy 2.0 mapped columns, Pydantic v2 models, and `Annotated` type aliases for dependency injection.

---

## 8. Recommendations

### Immediate (blocking for production)
1. **Add webhook signature validation** to `hooks.py` — verify Mailgun/Twilio signatures before processing
2. **Fix path mismatches** — align Dockerfile, docker-compose.yml, and CI config with actual directory structure
3. **Fix `.env.example`** — align variable names with the `AGENTID_` prefix expected by Pydantic settings
4. **Generate `requirements.txt`** from `pyproject.toml` or update CI to use `pip install .`

### Short-term (before beta)
5. Add rate limiting middleware (Redis-based token bucket)
6. Implement cursor-based pagination for all list endpoints
7. Align frontend `ApiClient` routes with actual backend endpoints
8. Add tests for email/phone provisioning with mocked providers
9. Add tests for inbound webhook handlers
10. Move `hooks.py` to use the standard `DB` dependency

### Medium-term (production hardening)
11. Implement Celery tasks for async provisioning
12. Add webhook delivery dispatcher
13. Implement MFA/TOTP for dashboard vault access
14. Switch JWT algorithm from HS256 to ES256
15. Add `secret_access_log` model and writes
16. Implement Stripe Connect payment endpoints
