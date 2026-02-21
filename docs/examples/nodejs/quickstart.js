/**
 * AgentID Node.js SDK - Quickstart Example
 * 
 * This example demonstrates the basic workflow:
 * 1. Create an agent
 * 2. Provision email identity
 * 3. Provision phone identity
 * 4. Store a secret
 * 5. Send a message
 */

import { AgentID } from '@agentid/sdk';

// Initialize client with API key from environment
const client = new AgentID({
  apiKey: process.env.AGENTID_API_KEY
});

async function quickstart() {
  try {
    // 1. Create an agent
    console.log('Creating agent...');
    const agent = await client.agents.create({
      name: 'QuickstartBot',
      description: 'Example agent for quickstart guide',
      policies: {
        max_outbound_messages_per_day: 100
      }
    });
    console.log(`✓ Agent created: ${agent.id}`);

    // 2. Provision email identity
    console.log('\nProvisioning email identity...');
    const email = await client.identities.createEmail({
      agentId: agent.id,
      domain: 'agentid.io',
      webhookUrl: 'https://your-app.com/webhooks/email'
    });
    console.log(`✓ Email provisioned: ${email.address}`);

    // 3. Provision phone identity
    console.log('\nProvisioning phone identity...');
    const phone = await client.identities.createPhone({
      agentId: agent.id,
      region: 'US',
      capabilities: ['sms'],
      webhookUrl: 'https://your-app.com/webhooks/sms'
    });
    console.log(`✓ Phone provisioned: ${phone.number}`);

    // 4. Store a secret in vault
    console.log('\nStoring secret in vault...');
    const secret = await client.secrets.create({
      agentId: agent.id,
      name: 'openai_api_key',
      value: 'sk-example-key-12345',
      description: 'OpenAI API key for LLM calls',
      rotationPolicy: {
        enabled: true,
        intervalDays: 90
      }
    });
    console.log(`✓ Secret stored: ${secret.id}`);

    // 5. Send an email
    console.log('\nSending test email...');
    const message = await client.messages.sendEmail({
      agentId: agent.id,
      emailId: email.id,
      to: 'test@example.com',
      subject: 'Hello from AgentID!',
      bodyPlain: 'This is a test message from your agent.',
      bodyHtml: '<p>This is a <strong>test message</strong> from your agent.</p>'
    });
    console.log(`✓ Email sent: ${message.id}`);

    console.log('\n🎉 Quickstart complete!');
    console.log('\nNext steps:');
    console.log('1. Set up webhook handler to receive inbound messages');
    console.log('2. Review dashboard at https://dashboard.agentid.io');
    console.log('3. Check out examples/nodejs/webhook-handler.js');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Run quickstart
quickstart();
