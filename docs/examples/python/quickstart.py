"""
AgentID Python SDK - Quickstart Example

This example demonstrates the basic workflow:
1. Create an agent
2. Provision email identity
3. Provision phone identity
4. Store a secret
5. Send a message
"""

import os
from agentid import AgentID

# Initialize client with API key from environment
client = AgentID(api_key=os.environ['AGENTID_API_KEY'])

# 1. Create an agent
print("Creating agent...")
agent = client.agents.create(
    name="QuickstartBot",
    description="Example agent for quickstart guide",
    policies={
        "max_outbound_messages_per_day": 100
    }
)
print(f"✓ Agent created: {agent.id}")

# 2. Provision email identity
print("\nProvisioning email identity...")
email = client.identities.create_email(
    agent_id=agent.id,
    domain="agentid.io",
    webhook_url="https://your-app.com/webhooks/email"
)
print(f"✓ Email provisioned: {email.address}")

# 3. Provision phone identity
print("\nProvisioning phone identity...")
phone = client.identities.create_phone(
    agent_id=agent.id,
    region="US",
    capabilities=["sms"],
    webhook_url="https://your-app.com/webhooks/sms"
)
print(f"✓ Phone provisioned: {phone.number}")

# 4. Store a secret in vault
print("\nStoring secret in vault...")
secret = client.secrets.create(
    agent_id=agent.id,
    name="openai_api_key",
    value="sk-example-key-12345",
    description="OpenAI API key for LLM calls",
    rotation_policy={
        "enabled": True,
        "interval_days": 90
    }
)
print(f"✓ Secret stored: {secret.id}")

# 5. Send an email
print("\nSending test email...")
message = client.messages.send_email(
    agent_id=agent.id,
    email_id=email.id,
    to="test@example.com",
    subject="Hello from AgentID!",
    body_plain="This is a test message from your agent.",
    body_html="<p>This is a <strong>test message</strong> from your agent.</p>"
)
print(f"✓ Email sent: {message.id}")

print("\n🎉 Quickstart complete!")
print(f"\nNext steps:")
print(f"1. Set up webhook handler to receive inbound messages")
print(f"2. Review dashboard at https://dashboard.agentid.io")
print(f"3. Check out examples/python/webhook_handler.py")
