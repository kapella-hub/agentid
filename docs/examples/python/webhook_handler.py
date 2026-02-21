"""
AgentID Python SDK - Webhook Handler Example

This example shows how to:
1. Verify webhook signatures
2. Handle inbound email events
3. Handle inbound SMS events
4. Process events asynchronously with retries
"""

import hmac
import hashlib
import time
from flask import Flask, request, jsonify
from celery import Celery
from agentid import AgentID

app = Flask(__name__)

# Initialize Celery for async processing
celery = Celery(
    'webhook_tasks',
    broker='redis://localhost:6379',
    backend='redis://localhost:6379'
)

# Webhook signing secret (from AgentID dashboard)
WEBHOOK_SECRET = "whsec_your_secret_here"

# Initialize AgentID client
client = AgentID()


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """
    Verify webhook signature to ensure request is from AgentID.
    
    Args:
        payload: Raw request body
        signature: X-AgentID-Signature header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    # Parse signature header
    parts = dict(p.split('=') for p in signature.split(','))
    timestamp = parts.get('t')
    sig = parts.get('v1')
    
    if not timestamp or not sig:
        return False
    
    # Reject signatures older than 5 minutes (replay attack prevention)
    if abs(time.time() - int(timestamp)) > 300:
        return False
    
    # Compute expected signature
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        f"{timestamp}.{payload.decode()}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(sig, expected)


@app.route('/webhooks/agentid', methods=['POST'])
def webhook_handler():
    """
    Main webhook endpoint.
    
    This endpoint:
    1. Verifies webhook signature
    2. Returns 200 immediately
    3. Queues event for async processing
    """
    # Verify signature
    signature = request.headers.get('X-AgentID-Signature')
    if not signature or not verify_webhook_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse event
    event = request.json
    
    # Queue for async processing
    process_webhook_event.delay(event)
    
    # Return immediately (don't block webhook)
    return jsonify({"status": "ok"}), 200


@celery.task(bind=True, max_retries=3)
def process_webhook_event(self, event):
    """
    Process webhook event asynchronously with retries.
    
    Args:
        event: Webhook event payload
    """
    try:
        event_type = event['type']
        
        # Route to appropriate handler
        if event_type == 'email.received':
            handle_email_received(event['data'])
        elif event_type == 'sms.received':
            handle_sms_received(event['data'])
        elif event_type == 'secret.rotated':
            handle_secret_rotated(event['data'])
        elif event_type == 'payment.charge.succeeded':
            handle_payment_succeeded(event['data'])
        else:
            print(f"Unknown event type: {event_type}")
            
    except Exception as exc:
        # Retry with exponential backoff
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)


def handle_email_received(data):
    """
    Handle inbound email event.
    
    Args:
        data: Email event data
    """
    print(f"Processing inbound email...")
    
    # Retrieve full message
    message = client.messages.get_email(data['message_id'])
    
    print(f"From: {message.from_address}")
    print(f"Subject: {message.subject}")
    print(f"Body: {message.body_plain[:100]}...")
    
    # Example: Auto-reply to emails
    if "support" in message.subject.lower():
        client.messages.send_email(
            agent_id=data['agent_id'],
            email_id=data['email_id'],
            to=message.from_address,
            subject=f"Re: {message.subject}",
            body_plain="Thank you for contacting support. We'll respond soon!",
            reply_to=message.id
        )
        print("✓ Auto-reply sent")


def handle_sms_received(data):
    """
    Handle inbound SMS event.
    
    Args:
        data: SMS event data
    """
    print(f"Processing inbound SMS...")
    
    # Retrieve full message
    message = client.messages.get_sms(data['message_id'])
    
    print(f"From: {message.from_number}")
    print(f"Body: {message.body}")
    
    # Example: Extract 2FA codes
    import re
    code_match = re.search(r'\b(\d{6})\b', message.body)
    if code_match:
        code = code_match.group(1)
        print(f"✓ 2FA code extracted: {code}")
        
        # Store in Redis or database for agent to retrieve
        # redis_client.setex(f"2fa:{data['agent_id']}", 300, code)


def handle_secret_rotated(data):
    """
    Handle secret rotation event.
    
    Args:
        data: Secret rotation event data
    """
    print(f"Secret rotated: {data['secret_id']}")
    
    # Example: Update application configuration
    # config.reload_secrets()


def handle_payment_succeeded(data):
    """
    Handle successful payment event.
    
    Args:
        data: Payment event data
    """
    print(f"Payment succeeded: ${data['amount']/100:.2f}")
    
    # Example: Send receipt email
    client.messages.send_email(
        agent_id=data['agent_id'],
        email_id=data['email_id'],
        to=data['customer_email'],
        subject="Payment Receipt",
        body_plain=f"Thank you! Your payment of ${data['amount']/100:.2f} was successful."
    )
    print("✓ Receipt sent")


if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
