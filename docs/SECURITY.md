# AgentID Security Model

AgentID is built with a security-first architecture designed to protect your agents' identities and credentials while maintaining compliance with industry standards.

## Table of Contents

- [Security Architecture](#security-architecture)
- [Data Encryption](#data-encryption)
- [Access Control](#access-control)
- [Credential Vault](#credential-vault)
- [Network Security](#network-security)
- [Compliance & Certifications](#compliance--certifications)
- [Incident Response](#incident-response)
- [Security Best Practices](#security-best-practices)
- [Vulnerability Disclosure](#vulnerability-disclosure)

---

## Security Architecture

AgentID follows a **zero-trust, defense-in-depth** security model with multiple layers of protection.

### Security Principles

1. **Least Privilege**: Every API key, token, and agent operates with minimal required permissions
2. **Defense in Depth**: Multiple security layers protect against single point of failure
3. **Encryption Everywhere**: Data encrypted at rest and in transit
4. **Audit Everything**: Complete immutable audit trail for compliance
5. **Fail Secure**: Failures default to denying access, never granting

### Architecture Layers

```
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│  - Input validation                         │
│  - Rate limiting                            │
│  - Business logic                           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Authentication Layer                │
│  - API key validation                       │
│  - Token scoping                            │
│  - MFA for dashboard                        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Authorization Layer                 │
│  - Role-based access control (RBAC)         │
│  - Policy enforcement                       │
│  - Resource-level permissions               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         Data Layer                          │
│  - Encryption at rest (KMS)                 │
│  - Row-level security (RLS)                 │
│  - Audit logging                            │
└─────────────────────────────────────────────┘
```

---

## Data Encryption

### Encryption at Rest

All sensitive data is encrypted at rest using **AES-256** encryption with envelope encryption.

#### Key Hierarchy

```
┌─────────────────────────────────┐
│  Root Key (KMS Master Key)      │
│  - AWS KMS or GCP Cloud KMS     │
│  - Rotated automatically        │
│  - Never leaves KMS             │
└────────────┬────────────────────┘
             │ wraps
┌────────────▼────────────────────┐
│  Organization Data Keys (DEK)   │
│  - One per organization         │
│  - Stored encrypted in DB       │
│  - Rotated every 90 days        │
└────────────┬────────────────────┘
             │ encrypts
┌────────────▼────────────────────┐
│  Sensitive Data                 │
│  - Secrets                      │
│  - Credentials                  │
│  - PII in messages (optional)   │
└─────────────────────────────────┘
```

#### What's Encrypted

| Data Type | Encrypted at Rest | Encrypted in Transit |
|-----------|-------------------|---------------------|
| API Keys | ✅ Yes | ✅ Yes |
| Secrets (vault) | ✅ Yes | ✅ Yes |
| Message bodies | ⚙️ Optional* | ✅ Yes |
| Email addresses | ❌ No** | ✅ Yes |
| Phone numbers | ❌ No** | ✅ Yes |
| Audit logs | ❌ No** | ✅ Yes |

*Message body encryption is configurable per organization.  
**Metadata required for routing and filtering is not encrypted at rest.

### Encryption in Transit

All API communications use **TLS 1.3** (minimum TLS 1.2) with perfect forward secrecy:

- Certificate pinning for mobile SDKs
- HSTS enabled with 1-year max-age
- Webhook deliveries over HTTPS only
- Certificate auto-renewal via Let's Encrypt

### Key Rotation

**Automatic rotation:**
- KMS master keys: Annually (automatic)
- Organization data keys: Every 90 days
- API keys: Manual (recommended every 90 days)
- Webhook signing secrets: Manual

**Rotation process:**
1. New key is generated
2. Data re-encrypted with new key (background job)
3. Old key retained for 30 days for recovery
4. Old key securely destroyed

---

## Access Control

### Authentication Methods

#### 1. Organization API Keys

Long-lived keys for server-to-server communication.

**Format:** `agid_live_...` (48 characters)

**Scopes:**
- Full access to all organization resources
- Create/delete agents
- Manage all identities
- Access all secrets

**Best practices:**
- Store in environment variables or secret manager
- Never commit to version control
- Rotate every 90 days
- One key per environment (dev/staging/prod)

#### 2. Agent Tokens

Short-lived, scoped tokens for individual agents.

**Format:** `agid_agent_...` (48 characters)

**Scopes:**
- `messages:read` - Read inbound messages
- `messages:send` - Send outbound messages
- `secrets:read` - Read secrets
- `secrets:write` - Write secrets
- `identities:read` - View identities
- `identities:manage` - Provision/revoke identities

**Lifetime:** 1 hour (default), max 24 hours

**Best practices:**
- Generate on-demand per agent session
- Use minimal required scopes
- Never store - regenerate as needed
- Automatic expiration

#### 3. Dashboard OAuth

OAuth 2.0 / OIDC for web dashboard access.

**MFA enforcement:**
- Required for all production organizations
- TOTP (Google Authenticator, Authy)
- SMS backup (optional)

### Authorization Model

#### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Owner** | Full access: billing, users, agents, all resources |
| **Admin** | Manage agents, identities, secrets, view audit logs |
| **Developer** | Create agents, provision identities, read secrets |
| **Viewer** | Read-only access to resources and audit logs |

#### Resource-Level Permissions

Fine-grained permissions per resource:

```json
{
  "agent_id": "agent_xyz789",
  "permissions": {
    "users": {
      "user_abc": ["read", "write"],
      "user_def": ["read"]
    },
    "policies": {
      "max_message_rate": 1000,
      "allowed_domains": ["example.com", "trusted.com"]
    }
  }
}
```

### Policy Enforcement

Policies are evaluated on every API request:

1. **Authentication**: Valid API key?
2. **Authorization**: Does key have required scope?
3. **Rate limit**: Within quota?
4. **Policy check**: Complies with org/agent policies?
5. **Action**: Execute or deny

**Example policy:**

```json
{
  "agent_id": "agent_xyz789",
  "policies": {
    "outbound_messages": {
      "max_per_day": 1000,
      "max_per_hour": 100
    },
    "allowed_recipients": {
      "domains": ["example.com"],
      "block_list": ["spam@example.com"]
    },
    "geographic_restrictions": {
      "allowed_regions": ["us", "eu"]
    },
    "approval_required": {
      "payments_over": 10000,
      "identity_provisioning": false
    }
  }
}
```

---

## Credential Vault

The AgentID vault stores sensitive credentials with military-grade security.

### Encryption

**At rest:**
- Secrets encrypted with organization data key
- Data key wrapped by KMS master key
- AES-256-GCM with authenticated encryption

**In transit:**
- TLS 1.3 only
- Certificate pinning in SDKs

### Access Patterns

#### 1. Write Secret

```python
client.secrets.create(
    agent_id="agent_xyz",
    name="api_key",
    value="sk-..."
)
```

**Security flow:**
1. Validate API key and scope (`secrets:write`)
2. Retrieve organization DEK from KMS
3. Encrypt value with DEK
4. Store encrypted value in database
5. Log access in audit trail
6. Return secret ID (never plaintext)

#### 2. Read Secret

```python
secret = client.secrets.get_value("secret_123")
print(secret.value)  # Decrypted
```

**Security flow:**
1. Validate API key and scope (`secrets:read`)
2. Retrieve encrypted value from database
3. Retrieve organization DEK from KMS
4. Decrypt value
5. Log access in audit trail
6. Return plaintext value (one-time)

**Important:** Never cache decrypted secrets. Always fetch fresh from vault.

### Secret Rotation

**Automatic rotation** for supported providers:

- AgentID-managed API keys
- Database credentials
- Webhook signing secrets

**Rotation process:**
1. Generate new credential with provider
2. Store new credential in vault
3. Update all references
4. Revoke old credential after grace period
5. Audit log entry

**Manual rotation:**

```python
client.secrets.rotate("secret_123")
```

---

## Network Security

### API Security

**DDoS Protection:**
- Cloudflare or AWS Shield
- Rate limiting per IP and API key
- Automatic throttling during attacks

**WAF Rules:**
- OWASP Top 10 protection
- SQL injection prevention
- XSS filtering
- Bot detection and blocking

**API Rate Limits:**

| Tier | Requests/min | Burst |
|------|--------------|-------|
| Starter | 60 | 120 |
| Professional | 300 | 600 |
| Enterprise | Custom | Custom |

### Webhook Security

**Signed Webhooks:**

All webhook payloads are signed with HMAC-SHA256:

```
X-AgentID-Signature: t=1708527600,v1=abc123...
```

**Verification:**

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    parts = dict(p.split('=') for p in signature.split(','))
    timestamp = parts['t']
    sig = parts['v1']
    
    # Reject old signatures (replay protection)
    if abs(time.time() - int(timestamp)) > 300:
        return False
    
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(sig, expected)
```

**Delivery Security:**
- Retry with exponential backoff
- Dead letter queue for failures
- IP allowlisting (optional)
- mTLS (enterprise tier)

### Infrastructure Security

**Network Isolation:**
- Private VPC for all services
- No public database access
- Bastion hosts for emergency access
- VPN required for administrative access

**Secrets Management:**
- AWS Secrets Manager or HashiCorp Vault
- No secrets in environment variables (runtime only)
- Automatic secret rotation
- Audit logging for all access

---

## Compliance & Certifications

### Current Compliance

#### SOC 2 Type II (In Progress)

Expected certification: Q3 2026

**Controls:**
- Security
- Availability
- Confidentiality
- Processing Integrity
- Privacy

#### GDPR Compliance

AgentID is GDPR-compliant for EU users:

- **Data minimization**: Only essential data collected
- **Right to access**: API for data export
- **Right to deletion**: Full data deletion upon request
- **Data portability**: Export in JSON format
- **Privacy by design**: Encryption and pseudonymization
- **DPA available**: Data Processing Agreement for customers

**Data retention:**
- Messages: 90 days (configurable)
- Audit logs: 7 years
- Deleted agent data: 30-day soft delete

#### CCPA Compliance

California Consumer Privacy Act compliance:

- **Disclosure**: Transparent data collection practices
- **Opt-out**: Do not sell personal information
- **Data deletion**: Request deletion via API or support
- **Non-discrimination**: No penalties for exercising rights

### Future Certifications (Roadmap)

- **ISO 27001**: Information security management
- **HIPAA**: For healthcare agent use cases
- **PCI DSS Level 1**: Payment card processing
- **FedRAMP**: US government use

### Industry Standards

**Email:**
- SPF, DKIM, DMARC configured for all domains
- CAN-SPAM Act compliance
- GDPR consent mechanisms

**SMS:**
- TCPA compliance (US)
- CTIA best practices
- Opt-in/opt-out management
- A2P registration

**Payments:**
- PCI DSS via Stripe
- Strong Customer Authentication (SCA/3D Secure)
- Anti-money laundering (AML) checks

---

## Incident Response

### Security Incident Process

**Detection → Containment → Investigation → Remediation → Post-Mortem**

#### 1. Detection

**Monitoring:**
- Real-time alerting for anomalies
- Failed authentication attempts
- Unusual API patterns
- Data access violations

**Alerts trigger on:**
- 10+ failed login attempts in 5 minutes
- Secret access from new IP
- Mass data exports
- Webhook signature failures

#### 2. Containment

**Immediate actions:**
- Revoke compromised API keys
- Disable affected agents
- Block suspicious IPs
- Rotate credentials

**Communication:**
- Notify security team (< 5 minutes)
- Notify affected customers (< 2 hours)
- Status page update

#### 3. Investigation

**Forensics:**
- Audit log analysis
- Access pattern review
- Attack vector identification
- Scope assessment

**Timeline:**
- Initial assessment: 1 hour
- Full investigation: 24 hours
- Root cause analysis: 72 hours

#### 4. Remediation

**Short-term:**
- Patch vulnerabilities
- Reset compromised credentials
- Enhanced monitoring

**Long-term:**
- Security control improvements
- Process updates
- Team training

#### 5. Post-Mortem

**Public disclosure:**
- Incident summary (within 7 days)
- Impact assessment
- Remediation steps
- Prevention measures

### Data Breach Response

If personal data is compromised:

1. **Contain the breach** (immediate)
2. **Assess impact** (< 1 hour)
3. **Notify authorities** (< 72 hours, GDPR requirement)
4. **Notify affected users** (< 72 hours)
5. **Provide remediation** (credit monitoring, free tier extension)
6. **Publish post-mortem** (within 14 days)

---

## Security Best Practices

### For Developers

#### 1. API Key Management

**✅ Do:**
```python
# Use environment variables
import os
client = AgentID(api_key=os.environ['AGENTID_API_KEY'])
```

**❌ Don't:**
```python
# Never hardcode keys
client = AgentID(api_key="agid_live_abc123...")  # BAD!
```

#### 2. Use Scoped Tokens

**✅ Do:**
```python
# Minimal scopes for agents
token = client.agents.create_token(
    agent_id="agent_xyz",
    scopes=["messages:read", "secrets:read"],
    expires_in=3600
)
```

**❌ Don't:**
```python
# Don't share org-level API keys with agents
agent.run(api_key=org_api_key)  # BAD!
```

#### 3. Verify Webhooks

**✅ Do:**
```python
if not verify_signature(payload, signature, secret):
    return 401  # Reject invalid signatures
```

**❌ Don't:**
```python
# Process webhooks without verification
event = request.json
process_event(event)  # BAD!
```

#### 4. Implement Rate Limiting

**✅ Do:**
```python
# Respect rate limits
if response.status_code == 429:
    time.sleep(response.headers['Retry-After'])
    retry_request()
```

**❌ Don't:**
```python
# Hammer the API
while True:
    try:
        create_agent()
    except:
        pass  # BAD!
```

#### 5. Log Securely

**✅ Do:**
```python
# Redact sensitive data
logger.info(f"Processed message from {redact_email(sender)}")
```

**❌ Don't:**
```python
# Log plaintext secrets
logger.info(f"Using API key {api_key}")  # BAD!
```

### For Operators

#### 1. Enable MFA

All production accounts must have MFA enabled.

#### 2. Regular Audits

- Review audit logs weekly
- Check for unusual patterns
- Validate user access levels
- Rotate credentials quarterly

#### 3. Network Security

- Use IP allowlists for webhooks (if static IPs available)
- Enable mTLS for webhook delivery (enterprise)
- Firewall API access to known IPs

#### 4. Monitoring

Set up alerts for:
- Failed authentication attempts
- Secret access from new locations
- Unusual message volumes
- Payment failures

#### 5. Incident Response Plan

Document:
- Contact information for security team
- Escalation procedures
- Customer communication templates
- Rollback procedures

---

## Vulnerability Disclosure

AgentID operates a responsible disclosure program.

### Reporting a Vulnerability

**Email:** security@agentid.io  
**PGP Key:** Available at https://agentid.io/.well-known/security.txt

**Include:**
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

### Response Timeline

- **Acknowledgment**: Within 24 hours
- **Initial assessment**: Within 72 hours
- **Status update**: Weekly
- **Fix deployed**: Based on severity
  - Critical: < 24 hours
  - High: < 7 days
  - Medium: < 30 days
  - Low: < 90 days

### Bug Bounty (Coming Soon)

We're launching a bug bounty program in Q3 2026:

- **Critical vulnerabilities**: $5,000 - $10,000
- **High**: $1,000 - $5,000
- **Medium**: $500 - $1,000
- **Low**: $100 - $500

**In scope:**
- API endpoints
- Dashboard web application
- SDKs
- Infrastructure

**Out of scope:**
- Social engineering
- Physical attacks
- DoS/DDoS
- Third-party services

### Hall of Fame

We recognize researchers who responsibly disclose vulnerabilities:
https://agentid.io/security/hall-of-fame

---

## Security Questionnaire

For enterprise customers, we provide detailed security questionnaires covering:

- Infrastructure and architecture
- Data handling and encryption
- Access controls and authentication
- Incident response procedures
- Compliance certifications
- Vendor risk management
- Business continuity planning

**Request:** enterprise@agentid.io

---

## Questions?

- **Security concerns:** security@agentid.io
- **Compliance questions:** compliance@agentid.io
- **Enterprise inquiries:** enterprise@agentid.io
- **General support:** support@agentid.io

---

**Last Updated:** February 2026  
**Security Policy Version:** 1.0
