# AgentID

**Identity infrastructure for AI agents.**

AgentID provides programmatic identity primitives—email, phone numbers, credential vaults, and payment rails—so your autonomous agents can interact with the real world without manual provisioning or compliance headaches.

## Why AgentID?

Building autonomous agents that interact with real-world services requires identity primitives humans take for granted:

- **Email addresses** for account creation and verification
- **Phone numbers** for SMS/voice verification
- **Secure credential storage** for API keys and secrets
- **Payment capabilities** to transact on behalf of users

Manually provisioning these is slow, fragile, and non-compliant at scale. AgentID solves this with a developer-first API.

## Core Features

### 🔐 Identity Provisioning
- **Email identities**: `agent@agentid.io` or custom domains with full SPF/DKIM/DMARC support
- **Virtual phone numbers**: SMS-capable numbers with region selection
- **Inbound routing**: Webhooks + polling API for messages
- **Outbound capabilities**: Send email/SMS with policy-based limits

### 🗝️ Credential Vault
- **Encrypted at rest**: KMS-backed envelope encryption per organization
- **Scoped access tokens**: Time-limited, capability-restricted agent tokens
- **Automatic rotation**: Scheduled rotation for supported providers
- **Audit trails**: Immutable logs for every secret access

### 💳 Payment Delegation
- **Stripe Connect integration**: Let agents create charges/invoices
- **Compliance-first**: Clear merchant-of-record separation
- **Revenue sharing**: Transparent 2% platform fee model

### 📊 Governance & Observability
- **Admin dashboard**: Manage agents, view messages, control access
- **Policy controls**: Rate limits, geo restrictions, approval workflows
- **Audit logs**: Complete compliance reporting and export
- **Instant revocation**: Disable identities in one click

## Quick Start

### Installation

```bash
# Node.js
npm install @agentid/sdk

# Python
pip install agentid
```

### 30-Second Example

```python
from agentid import AgentID

# Initialize with your API key
client = AgentID(api_key="agid_live_...")

# Create an agent
agent = client.agents.create(
    name="CustomerSupportBot",
    description="Handles customer inquiries"
)

# Provision email identity
email = client.identities.create_email(
    agent_id=agent.id,
    domain="agentid.io"  # or your custom domain
)

print(f"Agent email: {email.address}")
# => agent-abc123@agentid.io

# Set up webhook for inbound messages
client.webhooks.create(
    events=["email.received"],
    url="https://your-app.com/webhooks/agentid",
    agent_id=agent.id
)

# Retrieve messages via API
messages = client.messages.list_email(agent_id=agent.id, limit=10)
for msg in messages:
    print(f"From: {msg.from_address}, Subject: {msg.subject}")
```

### Authentication

AgentID uses API keys for authentication. Get yours from the [dashboard](https://dashboard.agentid.io):

```bash
# Set as environment variable
export AGENTID_API_KEY="agid_live_..."
```

**Security best practice**: Store API keys in your credential vault, not in code.

## Use Cases

### 🤖 Autonomous Agents
Your agent needs to sign up for a SaaS tool to complete a task:
1. Provision an email identity
2. Receive verification email via webhook
3. Extract verification link
4. Complete signup flow

### 🏢 Multi-Tenant Agent Platforms
Managing 100+ agent instances for different clients:
1. Create organization per client
2. Provision agent identities per use case
3. Enforce per-agent rate limits and policies
4. Provide audit logs for compliance

### 💬 Customer Support Bots
Agent needs to send SMS reminders:
1. Provision phone number
2. Store customer preferences in vault
3. Send SMS via outbound API
4. Handle opt-outs via inbound webhook

### 💰 Payment-Enabled Assistants
Agent needs to process customer payments:
1. Complete Stripe Connect onboarding
2. Generate scoped payment token for agent
3. Agent creates charges with policy limits
4. Platform earns 2% fee automatically

## Architecture

AgentID is built on a **zero-trust, policy-first** architecture:

```
┌─────────────┐
│ Your Agent  │
└──────┬──────┘
       │ API Call
       ▼
┌─────────────────────┐
│   AgentID API       │
│  (FastAPI/Python)   │
└──────┬──────────────┘
       │
       ├─► Mailgun/SendGrid (Email)
       ├─► Twilio (SMS)
       ├─► KMS (Encryption)
       ├─► Stripe Connect (Payments)
       └─► PostgreSQL + Redis
```

All secrets are encrypted with per-organization data keys wrapped by KMS. Webhooks are signed and retried with exponential backoff.

## Key Concepts

### Organizations
The top-level billing and governance entity. All agents belong to an org.

### Agents
A logical identity representing one autonomous agent. Each agent can have multiple identity bundles.

### Identity Bundles
A collection of identity primitives (email + phone + secrets) bound to one agent.

### Scoped Tokens
Short-lived API tokens with restricted capabilities (e.g., "read messages only" or "send SMS only").

### Policies
Rules governing what agents can do: rate limits, geographic restrictions, approval workflows.

## Documentation

- **[API Reference](./API_DOCS.md)**: Complete endpoint documentation
- **[Integration Guide](./INTEGRATION_GUIDE.md)**: Step-by-step integration patterns
- **[Security Model](./SECURITY.md)**: Encryption, compliance, and security controls
- **[Contributing](./CONTRIBUTING.md)**: How to contribute to AgentID
- **[Examples](./examples/)**: Code examples in Python, Node.js, and cURL

## Pricing

### Starter Plan
**$10/agent/month**
- 1 email identity
- 1 phone number
- Unlimited secrets in vault
- 1,000 inbound messages/month
- 500 outbound messages/month
- Standard support

### Professional Plan
**$50/agent/month**
- Everything in Starter
- Custom domains (verified)
- 10,000 inbound messages/month
- 5,000 outbound messages/month
- Social account setup assistance ($50 one-time)
- Priority support

### Enterprise
**Custom pricing**
- SSO/SAML integration
- SCIM provisioning
- Dedicated infrastructure
- SLAs and DPA
- Volume discounts
- White-label options

**Payment processing**: 2% platform fee on all transactions processed through AgentID payment delegation.

## Support

- **Documentation**: [docs.agentid.io](https://docs.agentid.io)
- **API Status**: [status.agentid.io](https://status.agentid.io)
- **Community**: [Discord](https://discord.gg/agentid)
- **Email**: support@agentid.io
- **Enterprise**: enterprise@agentid.io

## Compliance

AgentID is built with compliance in mind:

- **SOC 2 Type II** (in progress)
- **GDPR** compliant data handling
- **CCPA** compliance
- **KYC/KYB** for high-risk operations
- **Audit logs** for all sensitive operations

See [SECURITY.md](./SECURITY.md) for detailed security and compliance information.

## License

Proprietary. See [Terms of Service](https://agentid.io/terms).

---

**Ready to give your agents real-world identities?**  
[Get started](https://dashboard.agentid.io/signup) • [Read the docs](./API_DOCS.md) • [View examples](./examples/)
