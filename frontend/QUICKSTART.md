# AgentID Dashboard - Quick Start

Get the dashboard running in 2 minutes.

## Prerequisites
- Node.js 18+ installed
- npm or yarn

## Setup

```bash
# 1. Navigate to the frontend directory
cd /data/.openclaw/workspace/agentid/frontend

# 2. Install dependencies (if not already done)
npm install

# 3. Create environment file
cp .env.example .env.local

# 4. Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

## What You'll See

### Dashboard Features
- **Agent List**: 3 mock agents with different statuses
- **Identity Manager**: Email and phone identities (select an agent first)
- **Credential Vault**: Encrypted secrets and API keys (select an agent first)
- **API Keys**: Organization-level API keys with scopes
- **Usage & Billing**: Current usage stats and cost breakdown

### Current State
- All data is **mocked** for demonstration
- No backend connection required to run
- Fully functional UI with realistic interactions

## Common Actions

### View Different Sections
Click the navigation items in the left sidebar:
- Agents → View all agents, select one
- Identities → Email/phone management (requires agent selection)
- Vault → Secrets management (requires agent selection)
- API Keys → Organization API keys
- Usage & Billing → Usage stats and billing

### Try These Interactions
1. **Select an agent** in Agent List → see how Identities and Vault update
2. **Click "Create Agent"** → see modal (mock only)
3. **Reveal a secret** in Credential Vault → click eye icon
4. **Copy values** → click copy icons on keys/secrets
5. **Toggle dark mode** → change system theme preference

## Connecting to Real Backend

### Step 1: Update Environment
Edit `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Your API URL
```

### Step 2: Update Components
Replace mock data with API calls. Example:

**Before (mock):**
```typescript
const agents = [
  { id: 'agt_1', name: 'customer-support-bot', ... },
];
```

**After (API):**
```typescript
import { api } from '@/lib/api-client';
import { useEffect, useState } from 'react';

const [agents, setAgents] = useState([]);

useEffect(() => {
  api.agents.list().then(setAgents);
}, []);
```

### Step 3: Add Authentication
Install an auth library (e.g., NextAuth.js):
```bash
npm install next-auth
```

Configure and protect routes:
```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';

export const GET = NextAuth({ /* config */ });
export const POST = GET;
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main dashboard page
│   └── layout.tsx        # Root layout
├── components/           # All UI components
├── lib/
│   ├── api-client.ts     # API client (ready to use!)
│   └── utils.ts          # Helper functions
└── .env.local            # Your config (create this)
```

## Customization Quick Wins

### Change Brand Colors
Edit `tailwind.config.ts`:
```typescript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    }
  }
}
```

### Update Logo
Edit `components/Sidebar.tsx`, replace `<Bot />` icon.

### Add New View
1. Create component in `components/MyNewView.tsx`
2. Add nav item in `Sidebar.tsx`
3. Add case in `app/page.tsx` render switch

## Troubleshooting

### Port 3000 already in use?
```bash
# Use different port
npm run dev -- -p 3001
```

### Build failing?
```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

### Types not resolving?
```bash
# Restart TypeScript server in your editor
# VS Code: Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
```

## Production Build

```bash
# Build for production
npm run build

# Test production build locally
npm run start
```

## Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts, set environment variables in Vercel dashboard
```

## Next Steps

- Read [README.md](./README.md) for full documentation
- Check [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) for implementation details
- Explore [lib/api-client.ts](./lib/api-client.ts) for backend integration
- Review components for UI patterns

## Getting Help

- Check component source code (well-commented)
- Review TypeScript types for data structures
- Inspect browser console for errors
- Read Next.js 14 App Router docs

---

**You're all set!** The dashboard is running and ready to connect to your backend.
