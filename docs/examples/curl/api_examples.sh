#!/bin/bash

# AgentID cURL Examples - Complete API Reference
# 
# Comprehensive examples for all AgentID API endpoints.

set -e

API_BASE="https://api.agentid.io"
API_KEY="${AGENTID_API_KEY}"

# ============================================================================
# AGENTS
# ============================================================================

echo "=== AGENTS ==="

# Create agent
curl -X POST "$API_BASE/v1/agents" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyAgent",
    "description": "Example agent",
    "policies": {
      "max_outbound_messages_per_day": 1000
    }
  }'

# List agents
curl -X GET "$API_BASE/v1/agents?limit=20&offset=0" \
  -H "Authorization: Bearer $API_KEY"

# Get agent
curl -X GET "$API_BASE/v1/agents/{agent_id}" \
  -H "Authorization: Bearer $API_KEY"

# Update agent
curl -X PATCH "$API_BASE/v1/agents/{agent_id}" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "UpdatedAgentName",
    "policies": {
      "max_outbound_messages_per_day": 2000
    }
  }'

# Delete agent
curl -X DELETE "$API_BASE/v1/agents/{agent_id}" \
  -H "Authorization: Bearer $API_KEY"

# Create agent token
curl -X POST "$API_BASE/v1/agents/{agent_id}/tokens" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": ["messages:read", "secrets:read"],
    "expires_in": 3600
  }'

# ============================================================================
# EMAIL IDENTITIES
# ============================================================================

echo -e "\n=== EMAIL IDENTITIES ==="

# Create email on agentid.io domain
curl -X POST "$API_BASE/v1/agents/{agent_id}/email" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "agentid.io",
    "prefix": "my-agent",
    "webhook_url": "https://your-app.com/webhooks/email"
  }'

# Add custom domain
curl -X POST "$API_BASE/v1/domains" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "agents.example.com",
    "org_id": "org_abc123"
  }'

# Create email on custom domain
curl -X POST "$API_BASE/v1/agents/{agent_id}/email" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "agents.example.com",
    "prefix": "support"
  }'

# List email identities
curl -X GET "$API_BASE/v1/agents/{agent_id}/email" \
  -H "Authorization: Bearer $API_KEY"

# Revoke email identity
curl -X DELETE "$API_BASE/v1/agents/{agent_id}/email/{email_id}" \
  -H "Authorization: Bearer $API_KEY"

# ============================================================================
# PHONE IDENTITIES
# ============================================================================

echo -e "\n=== PHONE IDENTITIES ==="

# Create phone number
curl -X POST "$API_BASE/v1/agents/{agent_id}/phone" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "US",
    "area_code": "415",
    "capabilities": ["sms"],
    "webhook_url": "https://your-app.com/webhooks/sms"
  }'

# List phone identities
curl -X GET "$API_BASE/v1/agents/{agent_id}/phone" \
  -H "Authorization: Bearer $API_KEY"

# Revoke phone identity
curl -X DELETE "$API_BASE/v1/agents/{agent_id}/phone/{phone_id}" \
  -H "Authorization: Bearer $API_KEY"

# ============================================================================
# MESSAGES
# ============================================================================

echo -e "\n=== MESSAGES ==="

# List email messages
curl -X GET "$API_BASE/v1/messages/email?agent_id={agent_id}&limit=20" \
  -H "Authorization: Bearer $API_KEY"

# Get email message
curl -X GET "$API_BASE/v1/messages/email/{message_id}" \
  -H "Authorization: Bearer $API_KEY"

# Send email
curl -X POST "$API_BASE/v1/messages/email/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "email_id": "email_123",
    "to": "recipient@example.com",
    "subject": "Hello from AgentID",
    "body_plain": "This is the plain text body",
    "body_html": "<p>This is the <strong>HTML</strong> body</p>"
  }'

# Send email with attachment
curl -X POST "$API_BASE/v1/messages/email/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "email_id": "email_123",
    "to": "recipient@example.com",
    "subject": "With attachment",
    "body_plain": "See attached file",
    "attachments": [
      {
        "filename": "document.pdf",
        "content_type": "application/pdf",
        "data": "base64-encoded-content..."
      }
    ]
  }'

# List SMS messages
curl -X GET "$API_BASE/v1/messages/sms?agent_id={agent_id}&limit=20" \
  -H "Authorization: Bearer $API_KEY"

# Send SMS
curl -X POST "$API_BASE/v1/messages/sms/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "phone_id": "phone_789",
    "to": "+14085551234",
    "body": "Hello from AgentID!"
  }'

# ============================================================================
# SECRETS
# ============================================================================

echo -e "\n=== SECRETS ==="

# Create secret
curl -X POST "$API_BASE/v1/secrets" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "name": "api_key",
    "value": "sk-secret-value",
    "description": "API key for external service",
    "rotation_policy": {
      "enabled": true,
      "interval_days": 90
    }
  }'

# List secrets
curl -X GET "$API_BASE/v1/secrets?agent_id={agent_id}" \
  -H "Authorization: Bearer $API_KEY"

# Get secret value (requires secrets:read scope)
curl -X GET "$API_BASE/v1/secrets/{secret_id}/value" \
  -H "Authorization: Bearer $API_KEY"

# Update secret
curl -X PATCH "$API_BASE/v1/secrets/{secret_id}" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "new-secret-value",
    "description": "Updated API key"
  }'

# Rotate secret
curl -X POST "$API_BASE/v1/secrets/{secret_id}/rotate" \
  -H "Authorization: Bearer $API_KEY"

# Delete secret
curl -X DELETE "$API_BASE/v1/secrets/{secret_id}" \
  -H "Authorization: Bearer $API_KEY"

# ============================================================================
# WEBHOOKS
# ============================================================================

echo -e "\n=== WEBHOOKS ==="

# Create webhook
curl -X POST "$API_BASE/v1/webhooks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/agentid",
    "events": ["email.received", "sms.received", "secret.rotated"],
    "agent_id": "agent_xyz",
    "description": "Main webhook endpoint"
  }'

# List webhooks
curl -X GET "$API_BASE/v1/webhooks?agent_id={agent_id}" \
  -H "Authorization: Bearer $API_KEY"

# Delete webhook
curl -X DELETE "$API_BASE/v1/webhooks/{webhook_id}" \
  -H "Authorization: Bearer $API_KEY"

# ============================================================================
# PAYMENTS
# ============================================================================

echo -e "\n=== PAYMENTS ==="

# Create Stripe Connect onboarding
curl -X POST "$API_BASE/v1/payments/connect/onboard" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_abc123",
    "return_url": "https://dashboard.example.com/settings/payments",
    "refresh_url": "https://dashboard.example.com/settings/payments/refresh"
  }'

# Create charge
curl -X POST "$API_BASE/v1/payments/charges" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_xyz",
    "amount": 2500,
    "currency": "usd",
    "description": "Premium support session",
    "customer_email": "customer@example.com"
  }'

# List charges
curl -X GET "$API_BASE/v1/payments/charges?agent_id={agent_id}&limit=20" \
  -H "Authorization: Bearer $API_KEY"

# ============================================================================
# AUDIT LOGS
# ============================================================================

echo -e "\n=== AUDIT LOGS ==="

# List audit events
curl -X GET "$API_BASE/v1/audit?limit=100&offset=0" \
  -H "Authorization: Bearer $API_KEY"

# Filter by agent
curl -X GET "$API_BASE/v1/audit?agent_id={agent_id}&limit=100" \
  -H "Authorization: Bearer $API_KEY"

# Filter by event type
curl -X GET "$API_BASE/v1/audit?event_type=secret.accessed&limit=100" \
  -H "Authorization: Bearer $API_KEY"

# Export audit logs
curl -X POST "$API_BASE/v1/audit/export" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "json",
    "since": "2026-01-01T00:00:00Z",
    "until": "2026-02-20T23:59:59Z",
    "filters": {
      "agent_id": "agent_xyz"
    }
  }'

# Check export status
curl -X GET "$API_BASE/v1/audit/export/{export_id}" \
  -H "Authorization: Bearer $API_KEY"

echo -e "\n✓ Complete API examples finished"
