# AgentID Documentation Index

Complete guide to AgentID - identity infrastructure for AI agents.

## 📚 Documentation Structure

### Getting Started

1. **[README.md](./README.md)** - Project overview and quick start
   - What is AgentID?
   - Core features
   - 30-second quickstart
   - Pricing overview

### Core Documentation

2. **[API_DOCS.md](./API_DOCS.md)** - Complete API reference
   - Authentication methods
   - All endpoints with examples
   - Error handling
   - Rate limits
   - Webhook events
   - SDK documentation

3. **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Integration patterns
   - Email verification flows
   - SMS two-factor authentication
   - Credential management
   - Multi-agent orchestration
   - Webhook integration
   - Testing strategies
   - Production checklist

4. **[SECURITY.md](./SECURITY.md)** - Security model and compliance
   - Security architecture
   - Data encryption (at rest and in transit)
   - Access control (RBAC)
   - Credential vault design
   - Compliance certifications (SOC 2, GDPR, CCPA)
   - Incident response
   - Security best practices
   - Vulnerability disclosure

### Contributing

5. **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
   - Code of conduct
   - Bug reports and feature requests
   - Development setup
   - Pull request process
   - Coding standards
   - Testing guidelines

### Marketing

6. **[LANDING_PAGE.md](./LANDING_PAGE.md)** - Landing page copy
   - Hero section
   - Problem/solution messaging
   - Feature descriptions
   - Use cases
   - Testimonials
   - Pricing details
   - FAQ
   - SEO metadata

### Code Examples

7. **[examples/](./examples/)** - Production-ready code
   - **[examples/README.md](./examples/README.md)** - Examples overview
   - **Python examples:**
     - [quickstart.py](./examples/python/quickstart.py)
     - [webhook_handler.py](./examples/python/webhook_handler.py)
     - [email_verification.py](./examples/python/email_verification.py)
   - **Node.js examples:**
     - [quickstart.js](./examples/nodejs/quickstart.js)
     - [webhook-handler.js](./examples/nodejs/webhook-handler.js)
   - **cURL examples:**
     - [quickstart.sh](./examples/curl/quickstart.sh)
     - [api_examples.sh](./examples/curl/api_examples.sh)

---

## 🎯 Quick Navigation by Persona

### For Developers Building Agents

**Start here:**
1. Read [README.md](./README.md) for overview
2. Run [quickstart example](./examples/python/quickstart.py)
3. Implement [webhook handler](./examples/python/webhook_handler.py)
4. Review [Integration Guide](./INTEGRATION_GUIDE.md) for patterns

**Reference:**
- [API Documentation](./API_DOCS.md) for endpoints
- [Security Best Practices](./SECURITY.md#security-best-practices)

### For Technical Writers / Documentarians

**Documentation structure:**
- Main docs: [README](./README.md), [API](./API_DOCS.md), [Integration](./INTEGRATION_GUIDE.md), [Security](./SECURITY.md)
- Code examples: [examples/](./examples/)
- Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md)

**Writing style:**
- Developer-first: clear, concise, code-heavy
- Progressive disclosure: quick start → deep dives
- Real-world examples: production-ready code
- Compliance-aware: security and legal considerations

### For Product/Marketing

**Marketing assets:**
- [Landing page copy](./LANDING_PAGE.md)
  - Hero messaging
  - Feature descriptions
  - Use cases and testimonials
  - Pricing details
  - FAQ
  - SEO metadata

**Technical differentiation:**
- Zero-trust security architecture
- KMS-backed encryption
- Complete audit trail
- Compliance-first (SOC 2, GDPR, CCPA)

### For Security/Compliance Teams

**Security documentation:**
- [SECURITY.md](./SECURITY.md) - Complete security model
  - Architecture layers
  - Encryption (AES-256, TLS 1.3)
  - Key management (KMS, envelope encryption)
  - Access control (RBAC, scoped tokens)
  - Audit logging
  - Incident response
  - Certifications

**Compliance:**
- SOC 2 Type II (in progress)
- GDPR compliant
- CCPA compliant
- Data retention policies
- DPA available

### For Platform Engineers / DevOps

**Integration resources:**
- [Webhook implementation](./INTEGRATION_GUIDE.md#webhook-integration)
- [Error handling patterns](./INTEGRATION_GUIDE.md#error-handling--retries)
- [Production checklist](./INTEGRATION_GUIDE.md#production-checklist)
- [Monitoring best practices](./SECURITY.md#monitoring)

**Infrastructure:**
- RESTful API (FastAPI/Python)
- Postgres + Redis
- KMS for encryption
- Webhooks with retry logic

---

## 📖 Common User Journeys

### Journey 1: First-Time Integration (30 minutes)

1. **Understand AgentID** (5 min)
   - Read [README.md](./README.md) introduction
   - Review core features

2. **Get API key** (2 min)
   - Sign up at dashboard.agentid.io
   - Generate test API key

3. **Run quickstart** (10 min)
   - Install SDK: `pip install agentid`
   - Run [quickstart.py](./examples/python/quickstart.py)
   - See agent, email, phone provisioned

4. **Set up webhooks** (13 min)
   - Run [webhook_handler.py](./examples/python/webhook_handler.py)
   - Test with ngrok: `ngrok http 5000`
   - Send test message and receive webhook

**Result:** Fully functional agent with email/phone identities and webhook integration.

### Journey 2: Production Deployment (2-4 hours)

1. **Security review** (30 min)
   - Read [SECURITY.md](./SECURITY.md)
   - Implement signature verification
   - Set up scoped tokens

2. **Error handling** (30 min)
   - Add exponential backoff
   - Implement circuit breaker
   - Set up monitoring

3. **Webhook production setup** (1 hour)
   - Deploy async queue (Celery/BullMQ)
   - Implement idempotency
   - Add dead letter queue

4. **Testing** (1 hour)
   - Unit tests for SDK calls
   - Integration tests for flows
   - Load testing for webhooks

5. **Go live** (30 min)
   - Switch to production API keys
   - Monitor dashboard
   - Set up alerts

**Reference:** [Production Checklist](./INTEGRATION_GUIDE.md#production-checklist)

### Journey 3: Email Verification Flow (1 hour)

**Goal:** Agent autonomously signs up for a service and completes email verification.

1. **Study pattern** (15 min)
   - Read [email verification example](./examples/python/email_verification.py)
   - Understand polling vs webhook approach

2. **Implement** (30 min)
   - Create agent with email identity
   - Implement verification link extraction
   - Test with sample service

3. **Production hardening** (15 min)
   - Add timeout handling
   - Handle verification failures
   - Log verification attempts

**Code:** [email_verification.py](./examples/python/email_verification.py)

---

## 🔍 Search by Topic

### Authentication
- [API key types](./API_DOCS.md#authentication)
- [Agent tokens](./API_DOCS.md#creating-agent-tokens)
- [Scoped access](./SECURITY.md#authorization-model)

### Email
- [Provision email](./API_DOCS.md#create-email-identity)
- [Custom domains](./API_DOCS.md#create-email-on-custom-domain)
- [Send email](./API_DOCS.md#send-email)
- [Email verification flow](./examples/python/email_verification.py)

### SMS / Phone
- [Provision phone](./API_DOCS.md#create-phone-identity)
- [Send SMS](./API_DOCS.md#send-sms)
- [2FA handling](./INTEGRATION_GUIDE.md#sms-two-factor-authentication)

### Secrets
- [Create secret](./API_DOCS.md#create-secret)
- [Retrieve secret](./API_DOCS.md#get-secret-retrieve-value)
- [Rotation](./API_DOCS.md#rotate-secret)
- [Vault security](./SECURITY.md#credential-vault)

### Webhooks
- [Create webhook](./API_DOCS.md#create-webhook)
- [Verify signatures](./INTEGRATION_GUIDE.md#webhook-integration)
- [Event types](./API_DOCS.md#webhook-events)
- [Production setup](./examples/python/webhook_handler.py)

### Payments
- [Stripe Connect](./API_DOCS.md#create-connect-onboarding)
- [Create charge](./API_DOCS.md#create-charge-agent-initiated)
- [Platform fees](./README.md#pricing)

### Security
- [Encryption](./SECURITY.md#data-encryption)
- [Access control](./SECURITY.md#access-control)
- [Compliance](./SECURITY.md#compliance--certifications)
- [Best practices](./SECURITY.md#security-best-practices)

### Testing
- [Test mode](./examples/README.md#test-mode)
- [Unit testing](./examples/README.md#unit-testing)
- [Integration tests](./CONTRIBUTING.md#integration-tests)

---

## 🆘 Troubleshooting

### Common Issues

**Problem: Webhook signature verification fails**
- **Solution:** Check that you're using raw request body (not parsed JSON)
- **Reference:** [Webhook verification](./INTEGRATION_GUIDE.md#webhook-integration)

**Problem: Rate limit exceeded (429)**
- **Solution:** Implement exponential backoff, respect `Retry-After` header
- **Reference:** [Rate limits](./API_DOCS.md#rate-limits)

**Problem: Email not provisioned (timeout)**
- **Solution:** Check DNS records if using custom domain
- **Reference:** [Custom domains](./API_DOCS.md#create-email-on-custom-domain)

**Problem: Secret retrieval fails (403)**
- **Solution:** Ensure API key has `secrets:read` scope
- **Reference:** [Agent tokens](./API_DOCS.md#creating-agent-tokens)

---

## 📞 Support Channels

- **Documentation**: You're reading it!
- **Community Discord**: [discord.gg/agentid](https://discord.gg/agentid)
- **Email Support**: support@agentid.io
- **GitHub Issues**: [github.com/agentid/sdk/issues](https://github.com/agentid/sdk/issues)
- **Stack Overflow**: Tag `agentid`
- **Status Page**: [status.agentid.io](https://status.agentid.io)

---

## 🚀 Next Steps

**Just starting?**
→ [README.md](./README.md) + [quickstart.py](./examples/python/quickstart.py)

**Building integration?**
→ [Integration Guide](./INTEGRATION_GUIDE.md) + [webhook example](./examples/python/webhook_handler.py)

**Need API reference?**
→ [API Documentation](./API_DOCS.md) + [cURL examples](./examples/curl/api_examples.sh)

**Security/compliance review?**
→ [Security Model](./SECURITY.md)

**Ready to contribute?**
→ [Contributing Guidelines](./CONTRIBUTING.md)

---

**Documentation version:** 1.0  
**Last updated:** February 2026  
**Questions?** support@agentid.io
