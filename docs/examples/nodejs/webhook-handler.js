/**
 * AgentID Node.js SDK - Webhook Handler Example
 * 
 * This example shows how to:
 * 1. Verify webhook signatures
 * 2. Handle inbound email events
 * 3. Handle inbound SMS events
 * 4. Process events asynchronously with queues
 */

import express from 'express';
import crypto from 'crypto';
import { AgentID } from '@agentid/sdk';
import { Queue, Worker } from 'bullmq';

const app = express();

// Middleware to get raw body (needed for signature verification)
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf.toString('utf8');
  }
}));

// Webhook signing secret (from AgentID dashboard)
const WEBHOOK_SECRET = process.env.AGENTID_WEBHOOK_SECRET;

// Initialize AgentID client
const client = new AgentID({
  apiKey: process.env.AGENTID_API_KEY
});

// Initialize BullMQ for async processing
const webhookQueue = new Queue('webhooks', {
  connection: {
    host: 'localhost',
    port: 6379
  }
});

/**
 * Verify webhook signature to ensure request is from AgentID.
 */
function verifyWebhookSignature(payload, signature) {
  // Parse signature header
  const parts = {};
  signature.split(',').forEach(part => {
    const [key, value] = part.split('=');
    parts[key] = value;
  });

  const timestamp = parts.t;
  const sig = parts.v1;

  if (!timestamp || !sig) {
    return false;
  }

  // Reject signatures older than 5 minutes (replay attack prevention)
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - parseInt(timestamp)) > 300) {
    return false;
  }

  // Compute expected signature
  const expected = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(`${timestamp}.${payload}`)
    .digest('hex');

  // Constant-time comparison to prevent timing attacks
  return crypto.timingSafeEqual(
    Buffer.from(sig),
    Buffer.from(expected)
  );
}

/**
 * Main webhook endpoint
 */
app.post('/webhooks/agentid', async (req, res) => {
  try {
    // Verify signature
    const signature = req.headers['x-agentid-signature'];
    if (!signature || !verifyWebhookSignature(req.rawBody, signature)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    // Parse event
    const event = req.body;

    // Queue for async processing
    await webhookQueue.add('process-event', event);

    // Return immediately (don't block webhook)
    return res.status(200).json({ status: 'ok' });

  } catch (error) {
    console.error('Webhook error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * BullMQ Worker - Process webhook events asynchronously
 */
const worker = new Worker('webhooks', async (job) => {
  const event = job.data;

  try {
    switch (event.type) {
      case 'email.received':
        await handleEmailReceived(event.data);
        break;
      case 'sms.received':
        await handleSmsReceived(event.data);
        break;
      case 'secret.rotated':
        await handleSecretRotated(event.data);
        break;
      case 'payment.charge.succeeded':
        await handlePaymentSucceeded(event.data);
        break;
      default:
        console.log(`Unknown event type: ${event.type}`);
    }
  } catch (error) {
    console.error('Event processing error:', error);
    throw error; // Will trigger retry
  }
}, {
  connection: {
    host: 'localhost',
    port: 6379
  },
  attempts: 3,
  backoff: {
    type: 'exponential',
    delay: 60000 // 1 minute base delay
  }
});

/**
 * Handle inbound email event
 */
async function handleEmailReceived(data) {
  console.log('Processing inbound email...');

  // Retrieve full message
  const message = await client.messages.getEmail(data.message_id);

  console.log(`From: ${message.fromAddress}`);
  console.log(`Subject: ${message.subject}`);
  console.log(`Body: ${message.bodyPlain.substring(0, 100)}...`);

  // Example: Auto-reply to support emails
  if (message.subject.toLowerCase().includes('support')) {
    await client.messages.sendEmail({
      agentId: data.agent_id,
      emailId: data.email_id,
      to: message.fromAddress,
      subject: `Re: ${message.subject}`,
      bodyPlain: 'Thank you for contacting support. We\'ll respond soon!',
      replyTo: message.id
    });
    console.log('✓ Auto-reply sent');
  }
}

/**
 * Handle inbound SMS event
 */
async function handleSmsReceived(data) {
  console.log('Processing inbound SMS...');

  // Retrieve full message
  const message = await client.messages.getSms(data.message_id);

  console.log(`From: ${message.fromNumber}`);
  console.log(`Body: ${message.body}`);

  // Example: Extract 2FA codes
  const codeMatch = message.body.match(/\b(\d{6})\b/);
  if (codeMatch) {
    const code = codeMatch[1];
    console.log(`✓ 2FA code extracted: ${code}`);

    // Store in Redis for agent to retrieve
    // await redis.setex(`2fa:${data.agent_id}`, 300, code);
  }
}

/**
 * Handle secret rotation event
 */
async function handleSecretRotated(data) {
  console.log(`Secret rotated: ${data.secret_id}`);

  // Example: Reload application configuration
  // await config.reloadSecrets();
}

/**
 * Handle successful payment event
 */
async function handlePaymentSucceeded(data) {
  console.log(`Payment succeeded: $${(data.amount / 100).toFixed(2)}`);

  // Example: Send receipt email
  await client.messages.sendEmail({
    agentId: data.agent_id,
    emailId: data.email_id,
    to: data.customer_email,
    subject: 'Payment Receipt',
    bodyPlain: `Thank you! Your payment of $${(data.amount / 100).toFixed(2)} was successful.`
  });
  console.log('✓ Receipt sent');
}

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Webhook handler listening on port ${PORT}`);
  console.log(`📬 Webhook endpoint: http://localhost:${PORT}/webhooks/agentid`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing worker...');
  await worker.close();
  process.exit(0);
});
