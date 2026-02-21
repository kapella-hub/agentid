# AgentID API Reference

**Base URL**: `https://api.agentid.io`  
**API Version**: `v1`  
**Authentication**: Bearer token (API key)

## Table of Contents

- [Authentication](#authentication)
- [Core Resources](#core-resources)
  - [Organizations](#organizations)
  - [Agents](#agents)
  - [Email Identities](#email-identities)
  - [Phone Identities](#phone-identities)
  - [Messages](#messages)
  - [Secrets](#secrets)
  - [Webhooks](#webhooks)
  - [Payments](#payments)
  - [Audit Logs](#audit-logs)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Webhooks](#webhook-events)
- [SDKs](#sdks)

---

## Authentication

All API requests require authentication via API key in the `Authorization` header:

```bash
curl https://api.agentid.io/v1/agents \
  -H "Authorization: Bearer agid_live_..."
```

### API Key Types

| Type | Prefix | Scope | Use Case |
|------|--------|-------|----------|
| Organization | `agid_live_` | Full org access | Server-to-server |
| Test | `agid_test_` | Test mode only | Development |
| Agent Token | `agid_agent_` | Single agent, scoped | Agent runtime |

### Creating Agent Tokens

Agent tokens are short-lived and capability-scoped:

```bash
POST /v1/agents/{agent_id}/tokens
```

**Request Body:**
```json
{
  "scopes": ["messages:read", "secrets:read"],
  "expires_in": 3600
}
```

**Response:**
```json
{
  "token": "agid_agent_abc123...",
  "expires_at": "2026-02-21T12:00:00Z",
  "scopes": ["messages:read", "secrets:read"]
}
```

**Available Scopes:**
- `messages:read` - Read inbound messages
- `messages:send` - Send outbound messages
- `secrets:read` - Read secrets from vault
- `secrets:write` - Write/update secrets
- `identities:read` - View identity details
- `identities:manage` - Provision/revoke identities

---

## Core Resources

### Organizations

Organizations are the top-level entity for billing and governance.

#### Get Organization

```
GET /v1/orgs/{org_id}
```

**Response:**
```json
{
  "id": "org_abc123",
  "name": "Acme AI Labs",
  "billing_email": "billing@acme.ai",
  "created_at": "2026-01-15T08:00:00Z",
  "plan": "professional",
  "status": "active",
  "settings": {
    "default_webhook_url": "https://acme.ai/webhooks",
    "require_mfa": true,
    "allowed_regions": ["us", "eu"]
  }
}
```

#### Update Organization

```
PATCH /v1/orgs/{org_id}
```

**Request Body:**
```json
{
  "name": "Acme AI Labs Inc.",
  "settings": {
    "require_mfa": true
  }
}
```

---

### Agents

Agents represent individual autonomous agents within your organization.

#### Create Agent

```
POST /v1/agents
```

**Request Body:**
```json
{
  "name": "CustomerSupportBot",
  "description": "Handles tier-1 customer support inquiries",
  "metadata": {
    "team": "support",
    "version": "2.1"
  },
  "policies": {
    "max_outbound_messages_per_day": 1000,
    "allowed_regions": ["us"]
  }
}
```

**Response:**
```json
{
  "id": "agent_xyz789",
  "org_id": "org_abc123",
  "name": "CustomerSupportBot",
  "description": "Handles tier-1 customer support inquiries",
  "status": "active",
  "created_at": "2026-02-20T10:00:00Z",
  "metadata": {
    "team": "support",
    "version": "2.1"
  },
  "policies": {
    "max_outbound_messages_per_day": 1000,
    "allowed_regions": ["us"]
  }
}
```

#### List Agents

```
GET /v1/agents?limit=20&offset=0&status=active
```

**Query Parameters:**
- `limit` (integer, default: 20, max: 100) - Number of results
- `offset` (integer, default: 0) - Pagination offset
- `status` (string) - Filter by status: `active`, `disabled`, `archived`

**Response:**
```json
{
  "data": [
    {
      "id": "agent_xyz789",
      "name": "CustomerSupportBot",
      "status": "active",
      "created_at": "2026-02-20T10:00:00Z"
    }
  ],
  "has_more": false,
  "total": 1
}
```

#### Get Agent

```
GET /v1/agents/{agent_id}
```

#### Update Agent

```
PATCH /v1/agents/{agent_id}
```

**Request Body:**
```json
{
  "name": "CustomerSupportBot v2",
  "policies": {
    "max_outbound_messages_per_day": 2000
  }
}
```

#### Delete Agent

```
DELETE /v1/agents/{agent_id}
```

**Note**: This soft-deletes the agent. All identities are revoked but audit logs are retained.

---

### Email Identities

Email identities provide inbox capabilities for agents.

#### Create Email Identity

```
POST /v1/agents/{agent_id}/email
```

**Request Body:**
```json
{
  "domain": "agentid.io",
  "prefix": "support-bot",
  "webhook_url": "https://acme.ai/webhooks/email",
  "forward_to": "monitor@acme.ai"
}
```

**Response:**
```json
{
  "id": "email_123",
  "agent_id": "agent_xyz789",
  "address": "support-bot@agentid.io",
  "domain": "agentid.io",
  "status": "active",
  "created_at": "2026-02-20T10:05:00Z",
  "webhook_url": "https://acme.ai/webhooks/email",
  "forward_to": "monitor@acme.ai",
  "dkim_verified": true,
  "spf_verified": true
}
```

#### Create Email on Custom Domain

First, add and verify your domain:

```
POST /v1/domains
```

**Request Body:**
```json
{
  "domain": "agents.acme.ai",
  "org_id": "org_abc123"
}
```

**Response:**
```json
{
  "id": "domain_456",
  "domain": "agents.acme.ai",
  "status": "pending_verification",
  "dns_records": [
    {
      "type": "TXT",
      "name": "@",
      "value": "agentid-verification=abc123..."
    },
    {
      "type": "MX",
      "name": "@",
      "value": "10 inbound.agentid.io"
    },
    {
      "type": "TXT",
      "name": "@",
      "value": "v=spf1 include:_spf.agentid.io ~all"
    },
    {
      "type": "TXT",
      "name": "agentid._domainkey",
      "value": "v=DKIM1; k=rsa; p=MIGfMA0GCS..."
    }
  ]
}
```

After DNS verification (typically 5-10 minutes):

```
POST /v1/agents/{agent_id}/email
```

**Request Body:**
```json
{
  "domain": "agents.acme.ai",
  "prefix": "support"
}
```

#### List Email Identities

```
GET /v1/agents/{agent_id}/email
```

#### Revoke Email Identity

```
DELETE /v1/agents/{agent_id}/email/{email_id}
```

---

### Phone Identities

Virtual phone numbers for SMS (and future voice) capabilities.

#### Create Phone Identity

```
POST /v1/agents/{agent_id}/phone
```

**Request Body:**
```json
{
  "region": "US",
  "area_code": "415",
  "capabilities": ["sms"],
  "webhook_url": "https://acme.ai/webhooks/sms"
}
```

**Response:**
```json
{
  "id": "phone_789",
  "agent_id": "agent_xyz789",
  "number": "+14155551234",
  "region": "US",
  "capabilities": ["sms"],
  "status": "active",
  "created_at": "2026-02-20T10:10:00Z",
  "webhook_url": "https://acme.ai/webhooks/sms"
}
```

#### List Phone Identities

```
GET /v1/agents/{agent_id}/phone
```

#### Revoke Phone Identity

```
DELETE /v1/agents/{agent_id}/phone/{phone_id}
```

---

### Messages

Retrieve inbound and send outbound messages.

#### List Email Messages

```
GET /v1/messages/email?agent_id={agent_id}&limit=20&offset=0
```

**Query Parameters:**
- `agent_id` (required) - Filter by agent
- `email_id` (optional) - Filter by specific email identity
- `from` (optional) - Filter by sender address
- `subject` (optional) - Filter by subject (partial match)
- `since` (optional) - ISO timestamp, messages after this time
- `until` (optional) - ISO timestamp, messages before this time
- `limit` (integer, default: 20, max: 100)
- `offset` (integer, default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "msg_email_001",
      "email_id": "email_123",
      "agent_id": "agent_xyz789",
      "from": "customer@example.com",
      "to": "support-bot@agentid.io",
      "subject": "Help with my order",
      "body_plain": "I need help tracking order #12345...",
      "body_html": "<p>I need help tracking order #12345...</p>",
      "received_at": "2026-02-20T11:30:00Z",
      "attachments": [
        {
          "filename": "receipt.pdf",
          "content_type": "application/pdf",
          "size": 45231,
          "url": "https://files.agentid.io/temp/abc123..."
        }
      ],
      "headers": {
        "message-id": "<abc@example.com>",
        "in-reply-to": null
      }
    }
  ],
  "has_more": false,
  "total": 1
}
```

#### Get Single Email Message

```
GET /v1/messages/email/{message_id}
```

#### Send Email

```
POST /v1/messages/email/send
```

**Request Body:**
```json
{
  "agent_id": "agent_xyz789",
  "email_id": "email_123",
  "to": "customer@example.com",
  "subject": "Re: Help with my order",
  "body_plain": "Your order #12345 is on its way!",
  "body_html": "<p>Your order <strong>#12345</strong> is on its way!</p>",
  "reply_to": "msg_email_001",
  "attachments": [
    {
      "filename": "tracking.pdf",
      "content_type": "application/pdf",
      "data": "base64-encoded-content..."
    }
  ]
}
```

**Response:**
```json
{
  "id": "msg_email_002",
  "status": "sent",
  "sent_at": "2026-02-20T11:35:00Z"
}
```

#### List SMS Messages

```
GET /v1/messages/sms?agent_id={agent_id}&limit=20&offset=0
```

**Query Parameters:** Same pattern as email messages.

**Response:**
```json
{
  "data": [
    {
      "id": "msg_sms_001",
      "phone_id": "phone_789",
      "agent_id": "agent_xyz789",
      "from": "+14085551234",
      "to": "+14155551234",
      "body": "What's my order status?",
      "received_at": "2026-02-20T12:00:00Z",
      "direction": "inbound"
    }
  ],
  "has_more": false,
  "total": 1
}
```

#### Send SMS

```
POST /v1/messages/sms/send
```

**Request Body:**
```json
{
  "agent_id": "agent_xyz789",
  "phone_id": "phone_789",
  "to": "+14085551234",
  "body": "Your order #12345 shipped! Track here: https://track.me/abc"
}
```

**Response:**
```json
{
  "id": "msg_sms_002",
  "status": "sent",
  "sent_at": "2026-02-20T12:01:00Z"
}
```

---

### Secrets

Encrypted credential vault for API keys, tokens, and sensitive data.

#### Create Secret

```
POST /v1/secrets
```

**Request Body:**
```json
{
  "agent_id": "agent_xyz789",
  "name": "openai_api_key",
  "value": "sk-...",
  "description": "OpenAI API key for customer support responses",
  "rotation_policy": {
    "enabled": true,
    "interval_days": 90
  },
  "metadata": {
    "provider": "openai",
    "environment": "production"
  }
}
```

**Response:**
```json
{
  "id": "secret_456",
  "agent_id": "agent_xyz789",
  "name": "openai_api_key",
  "description": "OpenAI API key for customer support responses",
  "created_at": "2026-02-20T10:15:00Z",
  "updated_at": "2026-02-20T10:15:00Z",
  "rotation_policy": {
    "enabled": true,
    "interval_days": 90,
    "next_rotation": "2026-05-21T10:15:00Z"
  },
  "metadata": {
    "provider": "openai",
    "environment": "production"
  }
}
```

**Note**: The plaintext `value` is never returned after creation.

#### List Secrets

```
GET /v1/secrets?agent_id={agent_id}
```

**Response:**
```json
{
  "data": [
    {
      "id": "secret_456",
      "agent_id": "agent_xyz789",
      "name": "openai_api_key",
      "description": "OpenAI API key for customer support responses",
      "created_at": "2026-02-20T10:15:00Z",
      "updated_at": "2026-02-20T10:15:00Z"
    }
  ],
  "has_more": false,
  "total": 1
}
```

#### Get Secret (Retrieve Value)

```
GET /v1/secrets/{secret_id}/value
```

**Requires `secrets:read` scope.**

**Response:**
```json
{
  "id": "secret_456",
  "name": "openai_api_key",
  "value": "sk-...",
  "retrieved_at": "2026-02-20T13:00:00Z"
}
```

**Security note**: This operation is logged in audit logs. Use agent tokens with `secrets:read` scope to minimize exposure.

#### Update Secret

```
PATCH /v1/secrets/{secret_id}
```

**Request Body:**
```json
{
  "value": "sk-new...",
  "description": "Rotated OpenAI key"
}
```

#### Rotate Secret

```
POST /v1/secrets/{secret_id}/rotate
```

For secrets where AgentID manages the provider relationship, this will automatically rotate the credential.

**Response:**
```json
{
  "id": "secret_456",
  "rotated_at": "2026-02-20T13:05:00Z",
  "next_rotation": "2026-05-21T13:05:00Z"
}
```

#### Delete Secret

```
DELETE /v1/secrets/{secret_id}
```

---

### Webhooks

Register endpoints to receive real-time events.

#### Create Webhook

```
POST /v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://acme.ai/webhooks/agentid",
  "events": ["email.received", "sms.received", "secret.rotated"],
  "agent_id": "agent_xyz789",
  "secret": "whsec_...",
  "description": "Main webhook for CustomerSupportBot"
}
```

**Response:**
```json
{
  "id": "webhook_123",
  "url": "https://acme.ai/webhooks/agentid",
  "events": ["email.received", "sms.received", "secret.rotated"],
  "agent_id": "agent_xyz789",
  "status": "active",
  "created_at": "2026-02-20T10:20:00Z",
  "signing_secret": "whsec_abc123..."
}
```

#### List Webhooks

```
GET /v1/webhooks?agent_id={agent_id}
```

#### Delete Webhook

```
DELETE /v1/webhooks/{webhook_id}
```

#### Webhook Delivery Format

All webhooks are delivered as `POST` requests with a signature in the `X-AgentID-Signature` header:

```
POST /your/webhook/url
X-AgentID-Signature: t=1708527600,v1=abc123...
Content-Type: application/json

{
  "id": "evt_abc123",
  "type": "email.received",
  "created_at": "2026-02-20T11:30:00Z",
  "data": {
    "message_id": "msg_email_001",
    "email_id": "email_123",
    "agent_id": "agent_xyz789",
    "from": "customer@example.com",
    "subject": "Help with my order",
    "received_at": "2026-02-20T11:30:00Z"
  }
}
```

**Verifying Webhooks:**

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    parts = dict(p.split('=') for p in signature.split(','))
    timestamp = parts['t']
    sig = parts['v1']
    
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(sig, expected)
```

---

### Payments

Stripe Connect integration for agent payment capabilities.

#### Create Connect Onboarding

```
POST /v1/payments/connect/onboard
```

**Request Body:**
```json
{
  "org_id": "org_abc123",
  "return_url": "https://dashboard.acme.ai/settings/payments",
  "refresh_url": "https://dashboard.acme.ai/settings/payments/refresh"
}
```

**Response:**
```json
{
  "url": "https://connect.stripe.com/setup/s/abc123...",
  "expires_at": "2026-02-20T14:00:00Z"
}
```

#### Create Charge (Agent-Initiated)

```
POST /v1/payments/charges
```

**Request Body:**
```json
{
  "agent_id": "agent_xyz789",
  "amount": 2500,
  "currency": "usd",
  "description": "Premium customer support session",
  "customer_email": "customer@example.com",
  "metadata": {
    "session_id": "session_123",
    "customer_id": "cust_456"
  }
}
```

**Response:**
```json
{
  "id": "charge_789",
  "amount": 2500,
  "currency": "usd",
  "status": "succeeded",
  "application_fee": 50,
  "net_amount": 2450,
  "created_at": "2026-02-20T13:30:00Z"
}
```

**Note**: AgentID automatically collects a 2% platform fee (`application_fee`).

#### List Charges

```
GET /v1/payments/charges?agent_id={agent_id}&limit=20
```

---

### Audit Logs

Immutable audit trail for compliance and security.

#### List Audit Events

```
GET /v1/audit?limit=100&offset=0
```

**Query Parameters:**
- `agent_id` (optional) - Filter by agent
- `user_id` (optional) - Filter by user
- `event_type` (optional) - Filter by event type
- `since` (optional) - ISO timestamp
- `until` (optional) - ISO timestamp
- `limit` (integer, default: 100, max: 1000)
- `offset` (integer, default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "audit_001",
      "org_id": "org_abc123",
      "agent_id": "agent_xyz789",
      "user_id": "user_456",
      "event_type": "secret.accessed",
      "resource_id": "secret_456",
      "resource_type": "secret",
      "action": "read",
      "ip_address": "203.0.113.42",
      "user_agent": "agentid-sdk-python/1.0.0",
      "timestamp": "2026-02-20T13:00:00Z",
      "metadata": {
        "secret_name": "openai_api_key",
        "scope": "secrets:read"
      }
    }
  ],
  "has_more": false,
  "total": 1
}
```

#### Export Audit Logs

```
POST /v1/audit/export
```

**Request Body:**
```json
{
  "format": "json",
  "since": "2026-01-01T00:00:00Z",
  "until": "2026-02-20T23:59:59Z",
  "filters": {
    "agent_id": "agent_xyz789"
  }
}
```

**Response:**
```json
{
  "export_id": "export_123",
  "status": "processing",
  "estimated_completion": "2026-02-20T14:00:00Z"
}
```

Check status:

```
GET /v1/audit/export/{export_id}
```

When complete:

```json
{
  "export_id": "export_123",
  "status": "completed",
  "url": "https://exports.agentid.io/...",
  "expires_at": "2026-02-27T14:00:00Z"
}
```

---

## Error Handling

AgentID uses conventional HTTP response codes and returns errors in a consistent format.

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 403 | Forbidden - Valid key but insufficient permissions |
| 404 | Not Found |
| 409 | Conflict - Resource already exists |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Error Response Format

```json
{
  "error": {
    "type": "invalid_request",
    "message": "Agent not found",
    "code": "agent_not_found",
    "param": "agent_id",
    "request_id": "req_abc123"
  }
}
```

**Error Types:**
- `invalid_request` - Bad parameters or malformed request
- `authentication_error` - Invalid or missing API key
- `authorization_error` - Insufficient permissions
- `rate_limit_error` - Too many requests
- `resource_not_found` - Resource doesn't exist
- `resource_conflict` - Resource already exists
- `provider_error` - Upstream provider (Twilio, Mailgun) error
- `api_error` - Internal server error

---

## Rate Limits

AgentID enforces rate limits to ensure platform stability.

### Default Limits

| Plan | Requests/minute | Burst |
|------|----------------|-------|
| Starter | 60 | 120 |
| Professional | 300 | 600 |
| Enterprise | Custom | Custom |

### Rate Limit Headers

Every API response includes rate limit information:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1708527660
```

### Handling Rate Limits

When you exceed the rate limit, you'll receive a 429 response:

```json
{
  "error": {
    "type": "rate_limit_error",
    "message": "Rate limit exceeded. Retry after 30 seconds.",
    "retry_after": 30
  }
}
```

**Best practices:**
- Implement exponential backoff
- Cache responses when possible
- Use webhooks instead of polling
- Batch requests when available

---

## Webhook Events

Complete list of webhook event types:

### Email Events
- `email.received` - Inbound email received
- `email.sent` - Outbound email sent successfully
- `email.bounced` - Email delivery failed
- `email.identity.created` - New email identity provisioned
- `email.identity.revoked` - Email identity revoked

### SMS Events
- `sms.received` - Inbound SMS received
- `sms.sent` - Outbound SMS sent successfully
- `sms.failed` - SMS delivery failed
- `sms.identity.created` - New phone identity provisioned
- `sms.identity.revoked` - Phone identity revoked

### Secret Events
- `secret.created` - New secret stored
- `secret.accessed` - Secret value retrieved
- `secret.updated` - Secret value updated
- `secret.rotated` - Secret automatically rotated
- `secret.deleted` - Secret deleted

### Agent Events
- `agent.created` - New agent created
- `agent.updated` - Agent settings modified
- `agent.disabled` - Agent disabled
- `agent.deleted` - Agent deleted

### Payment Events
- `payment.charge.succeeded` - Charge processed successfully
- `payment.charge.failed` - Charge failed
- `payment.refund.created` - Refund issued

---

## SDKs

Official SDKs handle authentication, retries, and type safety.

### TypeScript/Node.js

```bash
npm install @agentid/sdk
```

```typescript
import { AgentID } from '@agentid/sdk';

const client = new AgentID({
  apiKey: process.env.AGENTID_API_KEY
});

// Create agent
const agent = await client.agents.create({
  name: 'CustomerSupportBot'
});

// Provision email
const email = await client.identities.createEmail({
  agentId: agent.id,
  domain: 'agentid.io'
});
```

### Python

```bash
pip install agentid
```

```python
from agentid import AgentID

client = AgentID(api_key=os.environ['AGENTID_API_KEY'])

# Create agent
agent = client.agents.create(
    name='CustomerSupportBot'
)

# Provision email
email = client.identities.create_email(
    agent_id=agent.id,
    domain='agentid.io'
)
```

---

## Pagination

List endpoints support cursor-based pagination:

```
GET /v1/agents?limit=20&offset=0
```

**Response:**
```json
{
  "data": [...],
  "has_more": true,
  "total": 156
}
```

To fetch the next page:

```
GET /v1/agents?limit=20&offset=20
```

---

## Idempotency

Idempotency keys prevent duplicate operations. Include an `Idempotency-Key` header:

```bash
curl -X POST https://api.agentid.io/v1/agents \
  -H "Authorization: Bearer agid_live_..." \
  -H "Idempotency-Key: unique-key-123" \
  -d '{"name": "CustomerSupportBot"}'
```

If the request is retried with the same key within 24 hours, the original response is returned.

---

## Support

- **Issues**: Report bugs at [github.com/agentid/sdk](https://github.com/agentid/sdk/issues)
- **API Status**: [status.agentid.io](https://status.agentid.io)
- **Community**: [Discord](https://discord.gg/agentid)
- **Email**: support@agentid.io

---

**Last Updated**: February 2026 | **API Version**: v1.0
