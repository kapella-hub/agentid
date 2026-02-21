# AgentID Dashboard

**Identity infrastructure for AI agents** — A clean, developer-friendly dashboard for managing agent identities, credentials, and billing.

## Overview

AgentID Dashboard is a Next.js 14 application that provides a comprehensive interface for:

- **Agent Management**: Create and manage AI agent identities
- **Identity Provisioning**: Email addresses and phone numbers for agents
- **Credential Vault**: Encrypted storage for API keys, passwords, and secrets
- **API Key Management**: Generate and manage organization API keys
- **Usage & Billing**: Monitor usage and track costs

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Runtime**: Node.js 18+

## Features

### 🤖 Agent Management
- Visual agent list with status indicators
- Quick-create workflow
- Agent selection for context-specific views
- Real-time status tracking

### 📧 Identity Manager
- Email address provisioning
- Phone number management
- Inbox/SMS message viewer
- Webhook configuration
- Copy/delete actions with confirmation

### 🔐 Credential Vault
- Encrypted secret storage
- Multiple secret types (API keys, passwords, 2FA seeds, OAuth tokens)
- Show/hide sensitive values
- One-click copy to clipboard
- Expiration tracking

### 🔑 API Key Manager
- Organization-level API keys
- Scope-based permissions
- Key reveal/copy functionality
- Revocation with status tracking
- Expiration management

### 💰 Usage & Billing
- Real-time usage statistics
- Cost breakdown by service
- Billing history
- Payment method management
- Period-based reporting

## Getting Started

### Prerequisites

- Node.js 18 or later
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Environment Variables

Create a `.env.local` file with:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
# NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main dashboard page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── components/
│   ├── Sidebar.tsx           # Navigation sidebar
│   ├── AgentList.tsx         # Agent management
│   ├── IdentityManager.tsx   # Email/phone identities
│   ├── CredentialVault.tsx   # Secret management
│   ├── ApiKeyManager.tsx     # API key management
│   └── UsageBilling.tsx      # Usage & billing view
├── lib/
│   ├── api-client.ts         # API client with typed methods
│   └── utils.ts              # Utility functions
└── public/                   # Static assets
```

## API Integration

The dashboard uses a typed API client (`lib/api-client.ts`) for backend communication:

```typescript
import { api } from '@/lib/api-client';

// Set API key (usually from auth context)
api.setApiKey('your-api-key');

// Use typed endpoints
const agents = await api.agents.list();
const email = await api.identities.email.create(agentId, { domain: 'example.com' });
```

### Available Endpoints

- **Agents**: `list`, `get`, `create`, `delete`
- **Email Identities**: `list`, `create`, `delete`
- **Phone Identities**: `list`, `create`, `delete`
- **Messages**: `email`, `sms`
- **Vault**: `list`, `get`, `create`, `rotate`, `delete`
- **API Keys**: `list`, `create`, `revoke`
- **Billing**: `usage`, `invoices`, `paymentMethod`, `updatePaymentMethod`

## Development

### Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Type checking
npx tsc --noEmit

# Linting (if configured)
npm run lint
```

### Mock Data

Currently, the dashboard uses mock data for demonstration. To connect to a real backend:

1. Update `NEXT_PUBLIC_API_URL` in `.env.local`
2. Implement authentication flow (JWT, OAuth, etc.)
3. Replace mock data in components with API calls using `lib/api-client.ts`

## Design Principles

### B2D (Business-to-Developer) Focus
- **Technical accuracy**: Use proper terminology (E.164, webhooks, scopes)
- **Developer ergonomics**: Copy buttons, monospace fonts for IDs/keys
- **Information density**: Show relevant metadata without clutter
- **Quick actions**: Inline controls for common operations

### Clean UI/UX
- **Consistent spacing**: Tailwind's spacing scale
- **Clear hierarchy**: Typography and color for emphasis
- **Responsive design**: Mobile-first approach
- **Dark mode support**: Respects system preferences
- **Accessible**: Semantic HTML, ARIA labels where needed

### Security-First
- **Masked secrets by default**: Explicit reveal action required
- **Confirmation for destructive actions**: Delete/revoke warnings
- **Scoped permissions**: Clear scope badges on API keys
- **Audit trail awareness**: "Last used" timestamps

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables in Production

Ensure these are set:
- `NEXT_PUBLIC_API_URL`: Your production API endpoint
- Add any authentication/analytics keys as needed

## Customization

### Branding
Update colors in `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        50: '#eff6ff',
        // ... your brand colors
      }
    }
  }
}
```

### Logo
Replace the Bot icon in `components/Sidebar.tsx` with your logo component.

### Features
Add new views by:
1. Creating a component in `components/`
2. Adding navigation item to `Sidebar.tsx`
3. Adding case to `app/page.tsx` render switch

## Contributing

1. Follow the existing code style
2. Use TypeScript strict mode
3. Add types for all API responses
4. Test responsive layouts
5. Ensure dark mode compatibility

## License

MIT License - see LICENSE file for details

## Support

For questions or issues:
- GitHub Issues: [github.com/your-org/agentid](https://github.com/your-org/agentid)
- Documentation: [docs.agentid.io](https://docs.agentid.io)
- Email: support@agentid.io

---

Built with ❤️ for the AI agent ecosystem
