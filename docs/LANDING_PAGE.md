# AgentID Landing Page Copy

Marketing copy and content for the AgentID landing page.

---

## Hero Section

### Headline
**Give Your AI Agents Real-World Identities**

### Subheadline
Provision email addresses, phone numbers, and payment capabilities for your autonomous agents in minutes. Focus on building intelligence, not infrastructure.

### CTA Buttons
- **Primary:** Get Started Free
- **Secondary:** View Documentation

### Hero Visual Description
Split-screen design:
- **Left:** Floating code snippet showing simple agent provisioning
- **Right:** Visual of email inbox + phone number + payment card materializing from code

---

## Problem Section

### Headline
**Building Autonomous Agents Shouldn't Require Manual Infrastructure**

### Problem Cards

#### Card 1: Manual Provisioning
**Icon:** 🕐  
**Title:** Hours of Setup  
**Copy:** Creating email accounts, buying phone numbers, and managing credentials for each agent wastes valuable development time.

#### Card 2: Fragile Systems
**Icon:** 🔥  
**Title:** Brittle Workflows  
**Copy:** Hardcoded credentials, manual verification flows, and scattered identity management break when scaled.

#### Card 3: Compliance Nightmares
**Icon:** ⚖️  
**Title:** Legal Exposure  
**Copy:** Ad-hoc identity solutions create compliance risks with GDPR, CAN-SPAM, TCPA, and payment regulations.

#### Card 4: No Governance
**Icon:** 🎯  
**Title:** Zero Visibility  
**Copy:** Without audit trails and policy controls, you're flying blind on what your agents are doing.

---

## Solution Section

### Headline
**Identity Infrastructure for AI Agents**

### Subheadline
AgentID provides programmatic access to identity primitives your agents need—secured, governed, and compliant by default.

### Feature Blocks

#### Feature 1: Email Identities
**Icon:** 📧  
**Title:** Agent Email Addresses  
**Copy:** Provision `agent@agentid.io` addresses or use your custom domain. Receive verification emails via webhook, send outbound messages with SPF/DKIM/DMARC.

**Code Snippet:**
```python
email = client.identities.create_email(
    agent_id="agent_xyz",
    domain="agentid.io"
)
# => agent-abc123@agentid.io
```

#### Feature 2: Virtual Phone Numbers
**Icon:** 📱  
**Title:** SMS-Capable Numbers  
**Copy:** Get virtual phone numbers in 50+ countries. Handle SMS verification flows autonomously. Receive inbound messages in real-time.

**Code Snippet:**
```python
phone = client.identities.create_phone(
    agent_id="agent_xyz",
    region="US"
)
# => +1 (415) 555-1234
```

#### Feature 3: Credential Vault
**Icon:** 🔐  
**Title:** Encrypted Secret Storage  
**Copy:** Store API keys, tokens, and credentials with KMS-backed encryption. Automatic rotation. Scoped access tokens. Complete audit trails.

**Code Snippet:**
```python
client.secrets.create(
    agent_id="agent_xyz",
    name="openai_key",
    value="sk-..."
)
```

#### Feature 4: Payment Capabilities
**Icon:** 💳  
**Title:** Agent Payment Rails  
**Copy:** Let agents process payments via Stripe Connect. Platform takes 2% fee. Full PCI compliance. No merchant-of-record complexity.

**Code Snippet:**
```python
charge = client.payments.create_charge(
    agent_id="agent_xyz",
    amount=2500,
    currency="usd"
)
```

---

## How It Works Section

### Headline
**From Zero to Autonomous in 3 Steps**

### Step 1
**Icon:** 🤖  
**Title:** Create an Agent  
**Copy:** Define your agent's identity and policies in one API call.

```python
agent = client.agents.create(
    name="CustomerSupportBot",
    policies={"max_messages_per_day": 1000}
)
```

### Step 2
**Icon:** ⚡  
**Title:** Provision Identities  
**Copy:** Add email, phone, and secrets in seconds. Webhook delivers inbound messages instantly.

```python
email = client.identities.create_email(agent_id=agent.id)
phone = client.identities.create_phone(agent_id=agent.id)
```

### Step 3
**Icon:** 🚀  
**Title:** Deploy & Monitor  
**Copy:** Your agent operates autonomously. Dashboard provides full visibility and control.

---

## Use Cases Section

### Headline
**Built for Modern AI Applications**

### Use Case 1: Customer Support Bots
**Scenario:** AI agent handles tier-1 support inquiries via email and SMS.

**Before AgentID:** 
- Shared support@ inbox creates confusion
- Manual SMS forwarding from personal numbers
- No audit trail for compliance

**After AgentID:**
- Dedicated email per agent instance
- Direct SMS routing via webhooks
- Complete audit logs for GDPR

**Result:** 10x faster customer response time, zero manual routing.

### Use Case 2: Data Collection Agents
**Scenario:** Agents sign up for competitor websites to collect pricing data.

**Before AgentID:**
- Manual account creation with throwaway emails
- SMS verification requires human intervention
- Credentials stored in spreadsheets

**After AgentID:**
- Automated email provisioning per target
- SMS codes received via webhook
- Encrypted credential vault

**Result:** Fully autonomous competitive intelligence at scale.

### Use Case 3: Payment-Enabled Assistants
**Scenario:** Personal AI assistant books services and makes purchases on behalf of user.

**Before AgentID:**
- User must input card for every transaction
- No payment limits or controls
- Liability unclear

**After AgentID:**
- Scoped payment capabilities with limits
- User approves high-value transactions
- Platform handles compliance

**Result:** True autonomous commerce with user-defined guardrails.

---

## Social Proof Section

### Headline
**Trusted by AI-First Teams**

### Testimonial 1
**Company:** Synthia AI  
**Role:** CTO  
**Quote:** "AgentID cut our agent deployment time from hours to minutes. The credential vault alone saved us from multiple security incidents."  
**Logo:** [Synthia AI Logo]

### Testimonial 2
**Company:** AutoFlow Studios  
**Role:** Founder  
**Quote:** "Managing 200+ autonomous agents was a nightmare until AgentID. Now we have complete visibility and control from one dashboard."  
**Logo:** [AutoFlow Logo]

### Testimonial 3
**Company:** AgentOps  
**Role:** Head of Engineering  
**Quote:** "The compliance features are a game-changer. We onboarded enterprise clients 3x faster because AgentID handles GDPR, SOC 2, and audit logs out of the box."  
**Logo:** [AgentOps Logo]

### Stats Row
- **50,000+ Agents** deployed
- **10M+ Messages** processed monthly
- **99.99% Uptime** SLA
- **<60s** average provisioning time

---

## Pricing Section

### Headline
**Transparent Pricing for Every Scale**

### Starter Plan
**$10/agent/month**

✅ 1 email identity  
✅ 1 phone number  
✅ Unlimited secrets  
✅ 1,000 inbound messages/mo  
✅ 500 outbound messages/mo  
✅ Standard support  
✅ 7-day audit log retention  

**CTA:** Start Free Trial

### Professional Plan
**$50/agent/month**

Everything in Starter, plus:

✅ Custom domains  
✅ 10,000 inbound messages/mo  
✅ 5,000 outbound messages/mo  
✅ Social account setup ($50 one-time)  
✅ Priority support  
✅ 90-day audit log retention  
✅ Advanced policies  

**CTA:** Start Free Trial

### Enterprise Plan
**Custom Pricing**

Everything in Professional, plus:

✅ SSO/SAML integration  
✅ SCIM provisioning  
✅ Dedicated infrastructure  
✅ Custom SLAs & DPA  
✅ Volume discounts  
✅ White-label options  
✅ 7-year audit log retention  
✅ Dedicated support  

**CTA:** Contact Sales

### Payment Processing
**2% platform fee** on all transactions processed through AgentID payment delegation.

### Add-Ons
- **Extra messages:** $0.01/message over quota
- **Additional phone numbers:** $2/number/month
- **Custom integrations:** Contact sales

---

## Security & Compliance Section

### Headline
**Enterprise-Grade Security, Out of the Box**

### Security Badges Row
🔒 **SOC 2 Type II** (in progress)  
🛡️ **GDPR Compliant**  
✅ **CCPA Compliant**  
🔐 **AES-256 Encryption**

### Key Security Features

#### Encryption Everywhere
All data encrypted at rest (KMS) and in transit (TLS 1.3). Secrets never stored in plaintext.

#### Zero-Trust Architecture
Scoped access tokens, policy-based controls, MFA for admins. Least privilege by default.

#### Complete Audit Trail
Immutable audit logs for every action. Export for compliance reporting. GDPR data request support.

#### Proactive Monitoring
Real-time anomaly detection. Automatic credential rotation. 24/7 security operations.

**CTA:** Read Security Documentation

---

## Developer Experience Section

### Headline
**APIs Developers Love**

### Feature Highlights

#### 🎨 Intuitive SDKs
```python
# Python
pip install agentid

# TypeScript
npm install @agentid/sdk
```

Type-safe, fully documented, with IntelliSense support.

#### 📚 Comprehensive Docs
Complete API reference, integration guides, and real-world examples.

#### ⚡ Instant Webhooks
Real-time event delivery with retry logic and signature verification.

#### 🧪 Test Mode
Full-featured sandbox environment with test API keys. No credit card required.

#### 🔍 Built-in Debugging
Request IDs, detailed error messages, and comprehensive logging.

#### 🎛️ Admin Dashboard
Manage agents, view messages, control access—no code required.

---

## FAQ Section

### Headline
**Frequently Asked Questions**

#### Q: How does AgentID handle email/SMS abuse prevention?
A: We enforce strict rate limits, implement content policies, require KYC/KYB for higher tiers, and monitor for spam patterns. Organizations violating our Acceptable Use Policy are suspended immediately.

#### Q: Can I use my own domain for agent emails?
A: Yes! Professional and Enterprise plans support custom domains. Simply verify DNS records (SPF, DKIM, DMARC) and provision agent emails on your domain.

#### Q: What happens if I exceed my message quota?
A: Overages are billed at $0.01/message. You can set hard limits in the dashboard to prevent unexpected charges.

#### Q: Is AgentID GDPR/CCPA compliant?
A: Yes. AgentID provides data export, deletion, and retention controls. We offer Data Processing Agreements (DPA) for enterprise customers.

#### Q: Can agents access secrets from other agents?
A: No. Secrets are scoped to specific agents with strict access controls. Only authorized API keys with correct scopes can retrieve secret values.

#### Q: What's your uptime SLA?
A: We maintain 99.9% uptime for Professional plans and 99.99% for Enterprise. Full status at status.agentid.io.

#### Q: Do you support social account provisioning?
A: We offer assisted social account setup (X, Discord, Telegram) as a one-time service. Fully automated provisioning is coming Q3 2026.

#### Q: What payment methods do you accept?
A: All major credit cards via Stripe. Enterprise customers can pay via invoice (NET 30).

#### Q: Can I white-label AgentID for my customers?
A: Yes! White-label options are available on Enterprise plans. Contact sales for details.

#### Q: How do I migrate existing agents to AgentID?
A: We provide migration guides and support for bulk agent imports. Contact support@agentid.io for assistance.

---

## Final CTA Section

### Headline
**Ready to Give Your Agents Real-World Capabilities?**

### Subheadline
Join 1,000+ developers building the next generation of autonomous AI agents.

### CTA Buttons
- **Primary:** Start Free Trial (no credit card required)
- **Secondary:** Schedule a Demo

### Trust Indicators
✅ Free 14-day trial  
✅ No credit card required  
✅ Cancel anytime  
✅ Full feature access  

---

## Footer

### Product
- Features
- Pricing
- Documentation
- API Reference
- Status Page
- Changelog

### Use Cases
- Customer Support Bots
- Data Collection Agents
- Payment Assistants
- Multi-Agent Platforms

### Resources
- Documentation
- API Reference
- Integration Guides
- Code Examples
- Blog
- Community Discord

### Company
- About Us
- Careers
- Brand Assets
- Contact
- Privacy Policy
- Terms of Service
- Acceptable Use Policy

### Security & Compliance
- Security Model
- SOC 2 Report
- GDPR Compliance
- Vulnerability Disclosure
- Bug Bounty

### Contact
- Email: support@agentid.io
- Enterprise: enterprise@agentid.io
- Twitter: @agentid
- GitHub: github.com/agentid
- Discord: discord.gg/agentid

---

## Meta Tags (SEO)

**Title:** AgentID - Identity Infrastructure for AI Agents  
**Description:** Give your AI agents email addresses, phone numbers, and payment capabilities. Provision identities in minutes with enterprise-grade security and compliance.  
**Keywords:** AI agents, autonomous agents, agent identity, email API, phone number API, credential vault, agent infrastructure, LLM agents

**Open Graph:**
- **og:title:** AgentID - Identity Infrastructure for AI Agents
- **og:description:** Provision email, phone, and payment capabilities for your autonomous agents in minutes.
- **og:image:** [Hero Image URL]
- **og:url:** https://agentid.io

**Twitter Card:**
- **twitter:card:** summary_large_image
- **twitter:title:** AgentID - Identity Infrastructure for AI Agents
- **twitter:description:** Give your AI agents real-world identities—email, phone, payments—secured and compliant.
- **twitter:image:** [Hero Image URL]

---

**Ready to launch?** This copy is designed to convert developer traffic into sign-ups by emphasizing speed, security, and simplicity.
