# AgentID Integration Guide

This guide walks through common integration patterns for building autonomous agents with AgentID.

## Table of Contents

- [Getting Started](#getting-started)
- [Common Patterns](#common-patterns)
  - [Email Verification Flow](#email-verification-flow)
  - [SMS Two-Factor Authentication](#sms-two-factor-authentication)
  - [Credential Management](#credential-management)
  - [Multi-Agent Orchestration](#multi-agent-orchestration)
- [Webhook Integration](#webhook-integration)
- [Error Handling & Retries](#error-handling--retries)
- [Testing Strategies](#testing-strategies)
- [Production Checklist](#production-checklist)

---

## Getting Started

### 1. Install SDK

```bash
# Node.js
npm install @agentid/sdk

# Python
pip install agentid
```

### 2. Initialize Client

```python
from agentid import AgentID
import os

client = AgentID(
    api_key=os.environ['AGENTID_API_KEY'],
    timeout=30  # Request timeout in seconds
)
```

### 3. Create Your First Agent

```python
# Create agent
agent = client.agents.create(
    name="MyFirstAgent",
    description="Experimental agent for learning AgentID",
    policies={
        "max_outbound_messages_per_day": 100
    }
)

print(f"Agent ID: {agent.id}")
```

### 4. Provision Email Identity

```python
# Provision email on agentid.io domain
email = client.identities.create_email(
    agent_id=agent.id,
    domain="agentid.io",
    webhook_url="https://your-app.com/webhooks/agentid"
)

print(f"Email address: {email.address}")
```

### 5. Set Up Webhook Handler

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

WEBHOOK_SECRET = "whsec_..."  # From AgentID dashboard

@app.route('/webhooks/agentid', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-AgentID-Signature')
    if not verify_signature(request.data, signature, WEBHOOK_SECRET):
        return jsonify({"error": "Invalid signature"}), 401
    
    event = request.json
    
    if event['type'] == 'email.received':
        handle_email(event['data'])
    elif event['type'] == 'sms.received':
        handle_sms(event['data'])
    
    return jsonify({"status": "ok"}), 200

def verify_signature(payload, signature, secret):
    parts = dict(p.split('=') for p in signature.split(','))
    timestamp = parts['t']
    sig = parts['v1']
    
    expected = hmac.new(
        secret.encode(),
        f"{timestamp}.{payload.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(sig, expected)
```

---

## Common Patterns

### Email Verification Flow

Many services require email verification. Here's how your agent can handle this autonomously.

#### Complete Example

```python
import re
from agentid import AgentID
from time import sleep

class EmailVerificationHandler:
    def __init__(self, agent_id, email_address):
        self.client = AgentID()
        self.agent_id = agent_id
        self.email_address = email_address
    
    def wait_for_verification_email(self, from_domain, timeout=300):
        """
        Poll for verification email and extract link.
        
        Args:
            from_domain: Expected sender domain (e.g., "example.com")
            timeout: Maximum seconds to wait
        
        Returns:
            Verification link or None
        """
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            messages = self.client.messages.list_email(
                agent_id=self.agent_id,
                limit=10
            )
            
            for msg in messages.data:
                if from_domain in msg.from_address:
                    # Extract verification link
                    link = self._extract_verification_link(msg.body_plain)
                    if link:
                        return link
            
            sleep(5)  # Poll every 5 seconds
        
        return None
    
    def _extract_verification_link(self, body):
        """Extract verification URL from email body."""
        # Common patterns
        patterns = [
            r'https?://[^\s]+/verify[^\s]*',
            r'https?://[^\s]+/confirm[^\s]*',
            r'https?://[^\s]+/activate[^\s]*'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return match.group(0)
        
        return None

# Usage
handler = EmailVerificationHandler(
    agent_id="agent_xyz789",
    email_address="agent@agentid.io"
)

# Sign up for service
signup_service(email=handler.email_address)

# Wait for verification email
verification_link = handler.wait_for_verification_email(
    from_domain="example.com",
    timeout=300
)

if verification_link:
    # Click verification link
    requests.get(verification_link)
    print("Email verified successfully!")
else:
    print("Verification email not received")
```

#### Webhook-Based Approach (Recommended)

Instead of polling, use webhooks for real-time notifications:

```python
from flask import Flask, request, jsonify
from queue import Queue
import re

app = Flask(__name__)
verification_queue = Queue()

@app.route('/webhooks/agentid', methods=['POST'])
def webhook_handler():
    event = request.json
    
    if event['type'] == 'email.received':
        data = event['data']
        
        # Check if this is a verification email
        if 'verify' in data['subject'].lower():
            # Extract link
            message = client.messages.get_email(data['message_id'])
            link = extract_verification_link(message.body_plain)
            
            if link:
                verification_queue.put(link)
    
    return jsonify({"status": "ok"}), 200

def extract_verification_link(body):
    patterns = [
        r'https?://[^\s]+/verify[^\s]*',
        r'https?://[^\s]+/confirm[^\s]*'
    ]
    for pattern in patterns:
        match = re.search(pattern, body)
        if match:
            return match.group(0)
    return None

# In your agent code
def signup_with_verification(email, service_url):
    # Trigger signup
    signup_response = requests.post(service_url, json={"email": email})
    
    # Wait for webhook to receive verification link
    verification_link = verification_queue.get(timeout=300)
    
    # Complete verification
    requests.get(verification_link)
    
    return True
```

---

### SMS Two-Factor Authentication

Handle SMS-based 2FA for service logins.

```python
import re
from agentid import AgentID

class SMSTwoFactorHandler:
    def __init__(self, agent_id, phone_number):
        self.client = AgentID()
        self.agent_id = agent_id
        self.phone_number = phone_number
    
    def wait_for_2fa_code(self, timeout=120):
        """
        Wait for 2FA code via SMS.
        
        Returns:
            6-digit code or None
        """
        import time
        start = time.time()
        
        # Get baseline message count
        messages = self.client.messages.list_sms(
            agent_id=self.agent_id,
            limit=1
        )
        last_message_time = messages.data[0].received_at if messages.data else None
        
        while time.time() - start < timeout:
            messages = self.client.messages.list_sms(
                agent_id=self.agent_id,
                since=last_message_time,
                limit=5
            )
            
            for msg in messages.data:
                code = self._extract_2fa_code(msg.body)
                if code:
                    return code
            
            time.sleep(3)
        
        return None
    
    def _extract_2fa_code(self, body):
        """Extract 6-digit code from SMS body."""
        # Common patterns: "Your code is 123456" or "Code: 123456"
        patterns = [
            r'\b(\d{6})\b',
            r'code[:\s]+(\d{6})',
            r'verification[:\s]+(\d{6})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

# Usage
handler = SMSTwoFactorHandler(
    agent_id="agent_xyz789",
    phone_number="+14155551234"
)

# Login and trigger 2FA
login_response = requests.post(
    "https://example.com/login",
    json={"username": "agent@agentid.io", "password": "..."}
)

# Wait for 2FA code
code = handler.wait_for_2fa_code(timeout=120)

if code:
    # Submit 2FA code
    verify_response = requests.post(
        "https://example.com/verify-2fa",
        json={"code": code}
    )
    print("2FA verification successful!")
else:
    print("2FA code not received")
```

---

### Credential Management

Store and retrieve secrets securely.

```python
from agentid import AgentID

class CredentialManager:
    def __init__(self, agent_id):
        self.client = AgentID()
        self.agent_id = agent_id
    
    def store_credential(self, service_name, credential_data):
        """
        Store credentials for a service.
        
        Args:
            service_name: Identifier for the service (e.g., "openai")
            credential_data: Dict with credential fields
        
        Returns:
            Secret ID
        """
        # Convert dict to JSON string for storage
        import json
        value = json.dumps(credential_data)
        
        secret = self.client.secrets.create(
            agent_id=self.agent_id,
            name=f"{service_name}_credentials",
            value=value,
            description=f"Credentials for {service_name}",
            rotation_policy={
                "enabled": True,
                "interval_days": 90
            },
            metadata={
                "service": service_name,
                "created_by": "agent"
            }
        )
        
        return secret.id
    
    def get_credential(self, service_name):
        """Retrieve credentials for a service."""
        # List secrets for this agent
        secrets = self.client.secrets.list(agent_id=self.agent_id)
        
        # Find matching secret
        for secret in secrets.data:
            if secret.name == f"{service_name}_credentials":
                # Retrieve actual value
                secret_value = self.client.secrets.get_value(secret.id)
                
                # Parse JSON
                import json
                return json.loads(secret_value.value)
        
        return None
    
    def rotate_credential(self, service_name, new_credential_data):
        """Update stored credentials."""
        secrets = self.client.secrets.list(agent_id=self.agent_id)
        
        for secret in secrets.data:
            if secret.name == f"{service_name}_credentials":
                import json
                new_value = json.dumps(new_credential_data)
                
                self.client.secrets.update(
                    secret_id=secret.id,
                    value=new_value
                )
                
                return True
        
        return False

# Usage
manager = CredentialManager(agent_id="agent_xyz789")

# Store OpenAI credentials
manager.store_credential("openai", {
    "api_key": "sk-...",
    "organization_id": "org-..."
})

# Retrieve credentials when needed
creds = manager.get_credential("openai")
openai.api_key = creds["api_key"]

# Rotate credentials
manager.rotate_credential("openai", {
    "api_key": "sk-new...",
    "organization_id": "org-..."
})
```

---

### Multi-Agent Orchestration

Manage multiple agents with different roles.

```python
from agentid import AgentID
from typing import List, Dict

class AgentOrchestrator:
    def __init__(self):
        self.client = AgentID()
        self.agents = {}
    
    def provision_agent(self, role, capabilities):
        """
        Provision an agent with specific capabilities.
        
        Args:
            role: Agent role (e.g., "customer_support", "data_collector")
            capabilities: List of capabilities (e.g., ["email", "sms", "phone"])
        
        Returns:
            Agent details with provisioned identities
        """
        # Create agent
        agent = self.client.agents.create(
            name=f"{role}_agent",
            description=f"Agent for {role} tasks",
            policies=self._get_policies_for_role(role)
        )
        
        # Provision identities based on capabilities
        identities = {}
        
        if "email" in capabilities:
            email = self.client.identities.create_email(
                agent_id=agent.id,
                domain="agentid.io",
                webhook_url=f"https://your-app.com/webhooks/{role}/email"
            )
            identities['email'] = email.address
        
        if "phone" in capabilities:
            phone = self.client.identities.create_phone(
                agent_id=agent.id,
                region="US",
                capabilities=["sms"],
                webhook_url=f"https://your-app.com/webhooks/{role}/sms"
            )
            identities['phone'] = phone.number
        
        # Store agent info
        self.agents[role] = {
            "agent_id": agent.id,
            "identities": identities
        }
        
        return self.agents[role]
    
    def _get_policies_for_role(self, role):
        """Define policies based on agent role."""
        policies = {
            "customer_support": {
                "max_outbound_messages_per_day": 5000,
                "allowed_regions": ["us", "eu"]
            },
            "data_collector": {
                "max_outbound_messages_per_day": 100,
                "allowed_regions": ["us"]
            },
            "payment_processor": {
                "max_outbound_messages_per_day": 1000,
                "allowed_regions": ["us"],
                "require_approval_for_charges": True
            }
        }
        
        return policies.get(role, {})
    
    def get_agent_for_role(self, role):
        """Retrieve agent details for a specific role."""
        return self.agents.get(role)
    
    def scale_role(self, role, count):
        """Provision multiple agents for the same role."""
        agents = []
        
        for i in range(count):
            agent_info = self.provision_agent(
                role=f"{role}_{i}",
                capabilities=["email", "phone"]
            )
            agents.append(agent_info)
        
        return agents

# Usage
orchestrator = AgentOrchestrator()

# Provision specialized agents
support_agent = orchestrator.provision_agent(
    role="customer_support",
    capabilities=["email", "sms"]
)

collector_agent = orchestrator.provision_agent(
    role="data_collector",
    capabilities=["email"]
)

payment_agent = orchestrator.provision_agent(
    role="payment_processor",
    capabilities=["email"]
)

# Scale horizontally
support_fleet = orchestrator.scale_role("customer_support", count=5)

print(f"Provisioned {len(support_fleet)} customer support agents")
```

---

## Webhook Integration

### Best Practices

1. **Always verify webhook signatures**
2. **Return 200 immediately, process asynchronously**
3. **Implement idempotency** (deduplicate events)
4. **Monitor webhook failures**

### Production Webhook Handler

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from redis import Redis
from celery import Celery

app = Flask(__name__)
redis = Redis()
celery = Celery('tasks', broker='redis://localhost:6379')

WEBHOOK_SECRET = "whsec_..."

@app.route('/webhooks/agentid', methods=['POST'])
def webhook_handler():
    # 1. Verify signature
    signature = request.headers.get('X-AgentID-Signature')
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    event = request.json
    event_id = event['id']
    
    # 2. Check for duplicate (idempotency)
    if redis.exists(f"event:{event_id}"):
        return jsonify({"status": "ok", "cached": True}), 200
    
    # 3. Mark as processed (24h TTL)
    redis.setex(f"event:{event_id}", 86400, "1")
    
    # 4. Queue for async processing
    process_webhook_event.delay(event)
    
    # 5. Return immediately
    return jsonify({"status": "ok"}), 200

@celery.task(bind=True, max_retries=3)
def process_webhook_event(self, event):
    """Process webhook event asynchronously with retries."""
    try:
        event_type = event['type']
        
        handlers = {
            'email.received': handle_email_received,
            'sms.received': handle_sms_received,
            'secret.rotated': handle_secret_rotated,
            'payment.charge.succeeded': handle_payment_succeeded
        }
        
        handler = handlers.get(event_type)
        if handler:
            handler(event['data'])
        
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

def handle_email_received(data):
    """Process inbound email."""
    agent_id = data['agent_id']
    message_id = data['message_id']
    
    # Retrieve full message
    client = AgentID()
    message = client.messages.get_email(message_id)
    
    # Process based on your logic
    print(f"Processing email from {message.from_address}")
    # ... your business logic ...

def verify_signature(payload, signature):
    """Verify webhook signature."""
    parts = dict(p.split('=') for p in signature.split(','))
    timestamp = parts['t']
    sig = parts['v1']
    
    # Verify timestamp is recent (prevent replay attacks)
    import time
    if abs(time.time() - int(timestamp)) > 300:  # 5 minutes
        return False
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        f"{timestamp}.{payload.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(sig, expected)
```

---

## Error Handling & Retries

### Exponential Backoff

```python
import time
from agentid import AgentID
from agentid.exceptions import RateLimitError, APIError

def create_agent_with_retry(client, max_retries=3):
    """Create agent with exponential backoff."""
    for attempt in range(max_retries):
        try:
            agent = client.agents.create(
                name="RetryAgent",
                description="Agent created with retry logic"
            )
            return agent
            
        except RateLimitError as e:
            # Rate limited - wait and retry
            wait_time = e.retry_after or (2 ** attempt)
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except APIError as e:
            # Server error - retry with exponential backoff
            if e.status_code >= 500 and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Server error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
    raise Exception("Max retries exceeded")
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        self.failures = 0
        self.state = 'closed'
    
    def on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = 'open'

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)
client = AgentID()

try:
    agent = breaker.call(client.agents.create, name="TestAgent")
except Exception as e:
    print(f"Failed to create agent: {e}")
```

---

## Testing Strategies

### Unit Testing with Mocks

```python
import unittest
from unittest.mock import Mock, patch
from agentid import AgentID

class TestAgentIntegration(unittest.TestCase):
    def setUp(self):
        self.client = AgentID(api_key="agid_test_123")
    
    @patch('agentid.resources.agents.Agents.create')
    def test_agent_creation(self, mock_create):
        # Mock response
        mock_create.return_value = Mock(
            id="agent_test_123",
            name="TestAgent",
            status="active"
        )
        
        # Test
        agent = self.client.agents.create(name="TestAgent")
        
        # Assert
        self.assertEqual(agent.id, "agent_test_123")
        self.assertEqual(agent.name, "TestAgent")
        mock_create.assert_called_once()
    
    @patch('agentid.resources.identities.Identities.create_email')
    def test_email_provisioning(self, mock_create_email):
        # Mock response
        mock_create_email.return_value = Mock(
            id="email_123",
            address="test@agentid.io",
            status="active"
        )
        
        # Test
        email = self.client.identities.create_email(
            agent_id="agent_test_123",
            domain="agentid.io"
        )
        
        # Assert
        self.assertEqual(email.address, "test@agentid.io")

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import os
from agentid import AgentID

# Use test API keys
client = AgentID(api_key=os.environ['AGENTID_TEST_API_KEY'])

def test_full_email_flow():
    """Test complete email provisioning and messaging flow."""
    # 1. Create agent
    agent = client.agents.create(
        name="IntegrationTestAgent",
        description="Testing email flow"
    )
    assert agent.id is not None
    
    # 2. Provision email
    email = client.identities.create_email(
        agent_id=agent.id,
        domain="agentid.io"
    )
    assert "@agentid.io" in email.address
    
    # 3. Send test email
    client.messages.send_email(
        agent_id=agent.id,
        email_id=email.id,
        to="test@example.com",
        subject="Integration Test",
        body_plain="This is a test"
    )
    
    # 4. Cleanup
    client.agents.delete(agent.id)
    
    print("✅ Integration test passed")

if __name__ == '__main__':
    test_full_email_flow()
```

---

## Production Checklist

### Pre-Launch

- [ ] **API Key Security**
  - Store in environment variables or secret manager
  - Never commit to version control
  - Rotate regularly (90 days)
  - Use agent tokens with minimal scopes

- [ ] **Webhook Configuration**
  - Implement signature verification
  - Handle idempotency (deduplicate events)
  - Process asynchronously with queue
  - Monitor webhook failures and DLQ

- [ ] **Error Handling**
  - Implement exponential backoff for retries
  - Add circuit breaker for upstream failures
  - Log all errors with context
  - Set up alerting for critical failures

- [ ] **Rate Limiting**
  - Respect rate limit headers
  - Implement client-side rate limiting
  - Use webhooks instead of polling
  - Cache responses where possible

- [ ] **Monitoring**
  - Track API latency and error rates
  - Monitor webhook delivery success
  - Alert on message delivery failures
  - Dashboard for agent health metrics

### Security

- [ ] **Compliance**
  - Review Acceptable Use Policy
  - Implement content filtering for outbound messages
  - Log all sensitive operations
  - Regular audit log reviews

- [ ] **Secret Management**
  - Enable automatic rotation where possible
  - Use scoped tokens for agents
  - Implement MFA for dashboard access
  - Regular security audits

### Scaling

- [ ] **Architecture**
  - Horizontal scaling for webhook handlers
  - Load balancing
  - Database connection pooling
  - Redis for caching and queues

- [ ] **Performance**
  - Batch API calls where possible
  - Use pagination for large result sets
  - Cache frequently accessed data
  - Optimize webhook processing

---

## Next Steps

- Explore [API Reference](./API_DOCS.md) for complete endpoint documentation
- Review [Security Model](./SECURITY.md) for compliance requirements
- Check out [Code Examples](./examples/) for language-specific patterns
- Join [Community Discord](https://discord.gg/agentid) for support

---

**Questions?** Email support@agentid.io or visit [docs.agentid.io](https://docs.agentid.io)
