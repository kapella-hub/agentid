#!/bin/bash

# AgentID cURL Examples - Quickstart
# 
# This script demonstrates basic AgentID operations using cURL.
# 
# Prerequisites:
# - Set AGENTID_API_KEY environment variable
# - Install jq for JSON parsing: brew install jq

set -e  # Exit on error

# Configuration
API_BASE="https://api.agentid.io"
API_KEY="${AGENTID_API_KEY}"

if [ -z "$API_KEY" ]; then
  echo "❌ Error: AGENTID_API_KEY environment variable not set"
  exit 1
fi

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}AgentID cURL Quickstart${NC}\n"

# 1. Create an agent
echo -e "${GREEN}1. Creating agent...${NC}"
AGENT_RESPONSE=$(curl -s -X POST "$API_BASE/v1/agents" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "QuickstartBot",
    "description": "Example agent for quickstart guide",
    "policies": {
      "max_outbound_messages_per_day": 100
    }
  }')

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.data.id')
echo "✓ Agent created: $AGENT_ID"

# 2. Provision email identity
echo -e "\n${GREEN}2. Provisioning email identity...${NC}"
EMAIL_RESPONSE=$(curl -s -X POST "$API_BASE/v1/agents/$AGENT_ID/email" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "agentid.io",
    "webhook_url": "https://your-app.com/webhooks/email"
  }')

EMAIL_ID=$(echo "$EMAIL_RESPONSE" | jq -r '.data.id')
EMAIL_ADDRESS=$(echo "$EMAIL_RESPONSE" | jq -r '.data.address')
echo "✓ Email provisioned: $EMAIL_ADDRESS"

# 3. Provision phone identity
echo -e "\n${GREEN}3. Provisioning phone identity...${NC}"
PHONE_RESPONSE=$(curl -s -X POST "$API_BASE/v1/agents/$AGENT_ID/phone" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "region": "US",
    "capabilities": ["sms"],
    "webhook_url": "https://your-app.com/webhooks/sms"
  }')

PHONE_ID=$(echo "$PHONE_RESPONSE" | jq -r '.data.id')
PHONE_NUMBER=$(echo "$PHONE_RESPONSE" | jq -r '.data.number')
echo "✓ Phone provisioned: $PHONE_NUMBER"

# 4. Store a secret
echo -e "\n${GREEN}4. Storing secret in vault...${NC}"
SECRET_RESPONSE=$(curl -s -X POST "$API_BASE/v1/secrets" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"name\": \"openai_api_key\",
    \"value\": \"sk-example-key-12345\",
    \"description\": \"OpenAI API key for LLM calls\",
    \"rotation_policy\": {
      \"enabled\": true,
      \"interval_days\": 90
    }
  }")

SECRET_ID=$(echo "$SECRET_RESPONSE" | jq -r '.data.id')
echo "✓ Secret stored: $SECRET_ID"

# 5. Send an email
echo -e "\n${GREEN}5. Sending test email...${NC}"
MESSAGE_RESPONSE=$(curl -s -X POST "$API_BASE/v1/messages/email/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"email_id\": \"$EMAIL_ID\",
    \"to\": \"test@example.com\",
    \"subject\": \"Hello from AgentID!\",
    \"body_plain\": \"This is a test message from your agent.\",
    \"body_html\": \"<p>This is a <strong>test message</strong> from your agent.</p>\"
  }")

MESSAGE_ID=$(echo "$MESSAGE_RESPONSE" | jq -r '.data.id')
echo "✓ Email sent: $MESSAGE_ID"

# Summary
echo -e "\n${BLUE}🎉 Quickstart complete!${NC}\n"
echo "Agent ID:       $AGENT_ID"
echo "Email:          $EMAIL_ADDRESS"
echo "Phone:          $PHONE_NUMBER"
echo "Secret ID:      $SECRET_ID"
echo "Message ID:     $MESSAGE_ID"

echo -e "\nNext steps:"
echo "1. Set up webhook handler to receive inbound messages"
echo "2. Review dashboard at https://dashboard.agentid.io"
echo "3. Check out the API docs at https://docs.agentid.io"
