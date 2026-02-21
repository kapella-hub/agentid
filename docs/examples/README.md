# AgentID Code Examples

This directory contains production-ready code examples for integrating AgentID into your autonomous agent applications.

## Quick Links

- **[Python Examples](./python/)** - Python SDK examples with Flask/FastAPI
- **[Node.js Examples](./nodejs/)** - TypeScript/JavaScript SDK examples with Express
- **[cURL Examples](./curl/)** - Raw HTTP API examples for testing

## Getting Started

### Prerequisites

**Python:**
```bash
pip install agentid flask celery redis
```

**Node.js:**
```bash
npm install @agentid/sdk express bullmq
```

**Environment:**
```bash
export AGENTID_API_KEY="agid_live_..."
export AGENTID_WEBHOOK_SECRET="whsec_..."
```

### Quick Start Examples

Start here if you're new to AgentID:

| Language | File | Description |
|----------|------|-------------|
| Python | [quickstart.py](./python/quickstart.py) | Create agent, provision identities, send message |
| Node.js | [quickstart.js](./nodejs/quickstart.js) | Same as Python quickstart |
| cURL | [quickstart.sh](./curl/quickstart.sh) | Bash script demonstrating API calls |

**Run:**
```bash
# Python
python examples/python/quickstart.py

# Node.js
node examples/nodejs/quickstart.js

# cURL
bash examples/curl/quickstart.sh
```

## Example Categories

### 1. Basic Integration

**Webhook Handlers** - Receive real-time events from AgentID

- **Python**: [webhook_handler.py](./python/webhook_handler.py)
  - Flask + Celery for async processing
  - Signature verification
  - Event routing with retries

- **Node.js**: [webhook-handler.js](./nodejs/webhook-handler.js)
  - Express + BullMQ for job queuing
  - Signature verification
  - Exponential backoff

### 2. Common Patterns

**Email Verification Flows** - Autonomous account creation

- **Python**: [email_verification.py](./python/email_verification.py)
  - Poll for verification emails
  - Extract verification links
  - Complete signup flows

**SMS 2FA Handling** - Autonomous two-factor authentication

```python
from agentid import AgentID

class SMSTwoFactorHandler:
    def wait_for_2fa_code(self, timeout=120):
        # Poll for SMS with 2FA code
        # Extract 6-digit code
        # Return code for verification
        pass
```

See [Integration Guide](../INTEGRATION_GUIDE.md) for complete implementation.

### 3. Advanced Use Cases

**Multi-Agent Orchestration** - Manage fleets of agents

```python
orchestrator = AgentOrchestrator()

# Provision specialized agents
support_agent = orchestrator.provision_agent(
    role="customer_support",
    capabilities=["email", "sms"]
)

# Scale horizontally
support_fleet = orchestrator.scale_role("customer_support", count=5)
```

**Credential Management** - Secure secret storage and rotation

```python
manager = CredentialManager(agent_id="agent_xyz")

# Store credentials
manager.store_credential("openai", {
    "api_key": "sk-...",
    "organization_id": "org-..."
})

# Retrieve when needed
creds = manager.get_credential("openai")
```

## Complete API Reference

**cURL Examples** - Every API endpoint with examples

- [api_examples.sh](./curl/api_examples.sh) - Complete API reference in bash
  - Agent CRUD operations
  - Email/phone provisioning
  - Message handling
  - Secret management
  - Webhooks
  - Payments
  - Audit logs

## Testing Your Integration

### Test Mode

Use test API keys for development:

```bash
export AGENTID_API_KEY="agid_test_..."
```

Test mode provides:
- Isolated sandbox environment
- No charges for messages
- Full feature parity with production
- Simulated webhook events

### Webhook Testing

Use tools like [ngrok](https://ngrok.com/) to expose localhost:

```bash
# Start ngrok
ngrok http 5000

# Update webhook URL in AgentID dashboard
https://abc123.ngrok.io/webhooks/agentid

# Run webhook handler
python examples/python/webhook_handler.py
```

### Unit Testing

Mock AgentID SDK for unit tests:

```python
from unittest.mock import Mock, patch

@patch('agentid.resources.agents.Agents.create')
def test_agent_creation(mock_create):
    mock_create.return_value = Mock(id="agent_test_123")
    
    agent = client.agents.create(name="TestAgent")
    
    assert agent.id == "agent_test_123"
```

## Common Patterns

### Error Handling

```python
from agentid import AgentID
from agentid.exceptions import RateLimitError, APIError

try:
    agent = client.agents.create(name="MyAgent")
except RateLimitError as e:
    # Rate limited - wait and retry
    time.sleep(e.retry_after)
except APIError as e:
    # API error - log and alert
    logger.error(f"API error: {e.status_code} - {e.message}")
```

### Retry Logic with Exponential Backoff

```python
import time

def create_agent_with_retry(client, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.agents.create(name="RetryAgent")
        except RateLimitError as e:
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

### Webhook Signature Verification

**Python:**
```python
import hmac
import hashlib

def verify_signature(payload, signature, secret):
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

**Node.js:**
```javascript
import crypto from 'crypto';

function verifySignature(payload, signature, secret) {
  const parts = {};
  signature.split(',').forEach(part => {
    const [key, value] = part.split('=');
    parts[key] = value;
  });

  const expected = crypto
    .createHmac('sha256', secret)
    .update(`${parts.t}.${payload}`)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(parts.v1),
    Buffer.from(expected)
  );
}
```

## Production Checklist

Before deploying to production:

- [ ] **API Keys**
  - Store in environment variables or secret manager
  - Use agent tokens with minimal scopes
  - Rotate regularly (90 days)

- [ ] **Webhook Security**
  - Verify all webhook signatures
  - Process asynchronously with queues
  - Implement idempotency (deduplicate events)

- [ ] **Error Handling**
  - Exponential backoff for retries
  - Circuit breaker for failures
  - Comprehensive logging

- [ ] **Monitoring**
  - Track API latency and error rates
  - Alert on webhook delivery failures
  - Monitor agent health metrics

- [ ] **Compliance**
  - Review Acceptable Use Policy
  - Implement content filtering
  - Regular audit log reviews

## Resources

- **[API Documentation](../API_DOCS.md)** - Complete API reference
- **[Integration Guide](../INTEGRATION_GUIDE.md)** - Step-by-step patterns
- **[Security Model](../SECURITY.md)** - Security best practices
- **[Dashboard](https://dashboard.agentid.io)** - Web UI for management
- **[Status Page](https://status.agentid.io)** - API uptime and incidents

## Support

- **Discord**: [discord.gg/agentid](https://discord.gg/agentid)
- **Email**: support@agentid.io
- **GitHub Issues**: [github.com/agentid/sdk/issues](https://github.com/agentid/sdk/issues)
- **Stack Overflow**: Tag `agentid`

## Contributing

Found an issue or want to improve an example? 

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

**Happy building!** 🚀
