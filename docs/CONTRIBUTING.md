# Contributing to AgentID

Thank you for your interest in contributing to AgentID! This document provides guidelines and instructions for contributing to the AgentID project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:

- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race
- Ethnicity
- Age
- Religion
- Nationality

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations of the Code of Conduct can be reported to conduct@agentid.io. All complaints will be reviewed and investigated promptly and fairly.

---

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [issue tracker](https://github.com/agentid/agentid/issues) to avoid duplicates.

**Good bug reports include:**

- **Clear title**: Summarize the issue in one line
- **Description**: What happened vs. what you expected
- **Reproduction steps**: How to reproduce the issue
- **Environment**: OS, SDK version, runtime version
- **Code samples**: Minimal reproducible example
- **Logs**: Relevant error messages or stack traces

**Example bug report:**

```markdown
## Bug: Email identity provisioning times out

### Description
When provisioning an email identity on a custom domain, the API request times out after 30 seconds.

### Steps to Reproduce
1. Add custom domain via `POST /v1/domains`
2. Verify DNS records
3. Call `POST /v1/agents/{id}/email` with custom domain
4. Request times out after 30s

### Expected Behavior
Email identity should be created within 10 seconds.

### Actual Behavior
Request times out with 504 Gateway Timeout.

### Environment
- SDK: agentid-python v1.0.0
- Python: 3.11.5
- OS: macOS 14.0

### Logs
```
TimeoutError: Request exceeded 30 second timeout
  at /usr/local/lib/python3.11/site-packages/httpx/_client.py:1234
```
```

### Suggesting Features

We welcome feature suggestions! Before submitting:

1. **Search existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with use cases
4. **Consider alternatives** you've evaluated

**Example feature request:**

```markdown
## Feature Request: Agent usage analytics

### Problem
As an agent operator, I need visibility into which agents are consuming the most resources (messages, API calls) to optimize costs.

### Proposed Solution
Add a new endpoint `GET /v1/agents/{id}/analytics` that returns:
- Message count by day/week/month
- API calls by endpoint
- Cost breakdown
- Resource utilization trends

### Use Cases
1. Identify high-volume agents for optimization
2. Budget forecasting
3. Anomaly detection (sudden spikes)

### Alternatives Considered
- Export audit logs and process manually (too slow)
- Third-party analytics (data privacy concerns)

### Additional Context
Similar to AWS Cost Explorer or Stripe Dashboard.
```

### Contributing Code

We welcome code contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** with tests and documentation
4. **Run tests**: `npm test` or `pytest`
5. **Commit with clear messages**: `git commit -m "feat: add agent analytics endpoint"`
6. **Push to your fork**: `git push origin feature/your-feature`
7. **Open a Pull Request** with description and context

### Contributing Documentation

Documentation improvements are highly valued! You can contribute by:

- Fixing typos or clarifying existing docs
- Adding code examples for common patterns
- Writing tutorials or guides
- Translating documentation
- Improving API reference accuracy

---

## Development Setup

### Prerequisites

- **Backend**: Python 3.11+ (FastAPI) or Node.js 18+ (Express)
- **Frontend**: Node.js 18+, React 18+
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Tools**: Docker, Git

### Backend Setup (Python/FastAPI)

```bash
# Clone repository
git clone https://github.com/agentid/agentid.git
cd agentid

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup (Next.js)

```bash
cd apps/web

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### Running with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests
docker-compose exec api pytest
```

### SDK Development

#### Python SDK

```bash
cd packages/sdk-py

# Install in editable mode
pip install -e .

# Run tests
pytest

# Type checking
mypy agentid

# Linting
ruff check .
```

#### TypeScript SDK

```bash
cd packages/sdk-ts

# Install dependencies
npm install

# Build
npm run build

# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with `main`

### PR Title Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add agent analytics endpoint`
- `fix: resolve email provisioning timeout`
- `docs: update API reference for secrets`
- `refactor: simplify webhook signature verification`
- `test: add integration tests for SMS flow`
- `chore: update dependencies`

### PR Description Template

```markdown
## Description
Brief description of the changes.

## Motivation
Why is this change necessary? What problem does it solve?

## Changes
- List of specific changes
- Another change
- etc.

## Testing
How was this tested?
- Unit tests added
- Integration tests run locally
- Manual testing performed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Changelog updated
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs tests and linters
2. **Code review**: Maintainer reviews code quality and design
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: PR is merged to `main`

**Timeline:**
- Initial review: Within 2 business days
- Feedback response: Please respond within 1 week
- Merge: After approval and CI passes

---

## Coding Standards

### Python (Backend)

**Style:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Ruff for linting and formatting

**Example:**

```python
from typing import Optional
from pydantic import BaseModel


class AgentCreate(BaseModel):
    """Schema for creating a new agent."""
    
    name: str
    description: Optional[str] = None
    policies: Optional[dict] = None


async def create_agent(
    agent_data: AgentCreate,
    org_id: str,
    db: Session,
) -> Agent:
    """
    Create a new agent.
    
    Args:
        agent_data: Agent creation data
        org_id: Organization ID
        db: Database session
    
    Returns:
        Created agent instance
    
    Raises:
        ValidationError: If agent_data is invalid
        DatabaseError: If database operation fails
    """
    agent = Agent(
        name=agent_data.name,
        description=agent_data.description,
        org_id=org_id,
    )
    
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    return agent
```

### TypeScript (Frontend & SDK)

**Style:**
- Use TypeScript strict mode
- Prefer functional components (React)
- Use ESLint and Prettier
- Maximum line length: 100 characters

**Example:**

```typescript
interface Agent {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'disabled';
  createdAt: string;
}

interface CreateAgentParams {
  name: string;
  description?: string;
  policies?: Record<string, any>;
}

/**
 * Create a new agent.
 * 
 * @param params - Agent creation parameters
 * @returns Promise resolving to created agent
 * @throws {ValidationError} If parameters are invalid
 * @throws {APIError} If API request fails
 */
export async function createAgent(
  params: CreateAgentParams
): Promise<Agent> {
  const response = await this.request<Agent>({
    method: 'POST',
    path: '/v1/agents',
    body: params,
  });
  
  return response.data;
}
```

### API Design

**RESTful conventions:**
- Use nouns for resources: `/agents`, not `/createAgent`
- HTTP methods: GET (read), POST (create), PATCH (update), DELETE (delete)
- Plural resource names: `/agents`, not `/agent`
- Nested resources: `/agents/{id}/email`
- Query parameters for filtering: `?status=active&limit=20`

**Response format:**

```json
{
  "data": {...},        // or [] for lists
  "error": {...},       // Only present on errors
  "meta": {             // Optional metadata
    "total": 100,
    "has_more": true
  }
}
```

**Error format:**

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid email address",
    "code": "invalid_email",
    "param": "email",
    "request_id": "req_abc123"
  }
}
```

---

## Testing Guidelines

### Unit Tests

**Coverage requirements:**
- Minimum 80% code coverage
- All new features must include tests
- Test edge cases and error conditions

**Example (Python):**

```python
import pytest
from app.services.agents import create_agent
from app.schemas import AgentCreate


@pytest.fixture
def agent_data():
    return AgentCreate(
        name="TestAgent",
        description="Test agent"
    )


async def test_create_agent_success(agent_data, db_session):
    """Test successful agent creation."""
    agent = await create_agent(
        agent_data=agent_data,
        org_id="org_123",
        db=db_session
    )
    
    assert agent.id is not None
    assert agent.name == "TestAgent"
    assert agent.status == "active"


async def test_create_agent_duplicate_name(agent_data, db_session):
    """Test agent creation with duplicate name fails."""
    await create_agent(agent_data, "org_123", db_session)
    
    with pytest.raises(ValidationError) as exc:
        await create_agent(agent_data, "org_123", db_session)
    
    assert "already exists" in str(exc.value)
```

### Integration Tests

Test complete flows across multiple components:

```python
import pytest
from httpx import AsyncClient


@pytest.mark.integration
async def test_agent_email_flow(client: AsyncClient, api_key: str):
    """Test complete agent creation and email provisioning flow."""
    
    # 1. Create agent
    response = await client.post(
        "/v1/agents",
        json={"name": "IntegrationTestAgent"},
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 201
    agent = response.json()["data"]
    
    # 2. Provision email
    response = await client.post(
        f"/v1/agents/{agent['id']}/email",
        json={"domain": "agentid.io"},
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 201
    email = response.json()["data"]
    assert "@agentid.io" in email["address"]
    
    # 3. Send test email
    response = await client.post(
        "/v1/messages/email/send",
        json={
            "agent_id": agent["id"],
            "email_id": email["id"],
            "to": "test@example.com",
            "subject": "Test",
            "body_plain": "Test email"
        },
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 200
    
    # 4. Cleanup
    await client.delete(
        f"/v1/agents/{agent['id']}",
        headers={"Authorization": f"Bearer {api_key}"}
    )
```

### End-to-End Tests

Use Playwright or Cypress for web dashboard:

```typescript
import { test, expect } from '@playwright/test';

test('create agent and provision email', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('[name=email]', 'test@example.com');
  await page.fill('[name=password]', 'password');
  await page.click('button[type=submit]');
  
  // Create agent
  await page.click('text=Create Agent');
  await page.fill('[name=name]', 'E2E Test Agent');
  await page.click('button:has-text("Create")');
  
  // Verify agent created
  await expect(page.locator('text=E2E Test Agent')).toBeVisible();
  
  // Provision email
  await page.click('text=Add Email Identity');
  await page.selectOption('[name=domain]', 'agentid.io');
  await page.click('button:has-text("Provision")');
  
  // Verify email provisioned
  await expect(page.locator('text=@agentid.io')).toBeVisible();
});
```

---

## Documentation

### Code Documentation

**Python:**
- Use docstrings (Google style)
- Document all public functions and classes
- Include type hints

**TypeScript:**
- Use JSDoc comments
- Document all exported functions and interfaces
- Include `@param` and `@returns` tags

### API Documentation

API changes require updates to `API_DOCS.md`:

1. Update endpoint descriptions
2. Add request/response examples
3. Document new parameters
4. Update error codes
5. Add code snippets

### Tutorials & Guides

When adding new features, consider writing:

- Quickstart guide
- Step-by-step tutorial
- Best practices document
- Video walkthrough

---

## Community

### Getting Help

- **Discord**: Join our [community Discord](https://discord.gg/agentid)
- **GitHub Discussions**: [github.com/agentid/agentid/discussions](https://github.com/agentid/agentid/discussions)
- **Stack Overflow**: Tag questions with `agentid`
- **Email**: support@agentid.io

### Weekly Office Hours

Join our weekly community calls:

- **When**: Thursdays at 10:00 AM PT
- **Where**: Zoom (link in Discord)
- **Topics**: Feature demos, Q&A, roadmap discussion

### Recognition

Contributors are recognized in:

- [Contributors page](https://agentid.io/contributors)
- Release notes
- Social media shoutouts
- Swag for significant contributions 🎁

---

## License

By contributing to AgentID, you agree that your contributions will be licensed under the same license as the project.

---

## Questions?

If you have questions about contributing, reach out:

- **Discord**: [discord.gg/agentid](https://discord.gg/agentid)
- **Email**: contributors@agentid.io
- **Twitter**: [@agentid](https://twitter.com/agentid)

**Thank you for contributing to AgentID!** 🙏
