# AgentID Dashboard - UI Guide

Visual guide to the dashboard interface and component layout.

## Layout Overview

```
┌─────────────────────────────────────────────────────────────┐
│  ┌────────────┐ ┌──────────────────────────────────────────┐│
│  │            │ │                                          ││
│  │  Sidebar   │ │         Main Content Area               ││
│  │            │ │                                          ││
│  │  (fixed)   │ │         (scrollable)                    ││
│  │            │ │                                          ││
│  └────────────┘ └──────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Sidebar Navigation

**Position**: Left side, fixed width (256px)

**Sections**:
```
┌─────────────────┐
│ 🤖 AgentID      │  ← Logo + Brand
│ Identity infra  │
├─────────────────┤
│ 🤖 Agents       │  ← Active (blue highlight)
│ 📧 Identities   │
│ 🛡️  Vault        │
│ 🔑 API Keys     │
│ 📊 Usage        │
├─────────────────┤
│ [U] user@...    │  ← User info
│ Org: demo-org   │
└─────────────────┘
```

**States**:
- Active item: Blue background, blue text
- Hover: Light gray background
- Default: Gray text

## View 1: Agent List

**Header Section**:
```
┌──────────────────────────────────────────────────┐
│ Agents                      [+ Create Agent]     │
│ Manage your AI agent identities                  │
│ ┌────────────────────────────────────────┐       │
│ │ 🔍 Search agents...                    │       │
│ └────────────────────────────────────────┘       │
└──────────────────────────────────────────────────┘
```

**Agent Cards** (Grid layout):
```
┌────────────────────────────────────────────┐
│ 🤖 customer-support-bot          ✓ Active │
│ ID: agt_1                                  │
│ ✉️  support@agentid.io                     │
│ 📱 +1-555-0123                             │
│ ─────────────────────────────────────────  │
│ Created 2024-02-15    Active 2 minutes ago │
└────────────────────────────────────────────┘
```

**Status Indicators**:
- ✓ Active: Green checkmark
- ⚠ Inactive: Gray alert
- ✗ Error: Red X

## View 2: Identity Manager

**Tab Navigation**:
```
┌───────────────────────────────────────────┐
│ Identity Manager                          │
│ Email addresses, phone numbers, messages  │
│ ─────────────────────────────────────────│
│ [Email] [Phone] [Messages]               │
└───────────────────────────────────────────┘
```

**Email Tab** - Address Cards:
```
┌────────────────────────────────────────────┐
│ support@agentid.io         🔍 📧 🗑️       │
│ Domain: agentid.io         [Verified]     │
│                                            │
│ Inbox count: 47    Last received: 5 min ago│
│ → View inbox                               │
└────────────────────────────────────────────┘
```

**Phone Tab** - Number Cards:
```
┌────────────────────────────────────────────┐
│ +1-555-0123                    🔍 📧 🗑️   │
│ Region: US                                 │
│ [SMS] [Voice]                             │
│                                            │
│ SMS count: 23      Last received: 12 min ago│
│ → View messages                            │
└────────────────────────────────────────────┘
```

**Empty State** (no agent selected):
```
        📧
    No agent selected
    Select an agent from the
    list to manage identities
```

## View 3: Credential Vault

**Security Banner**:
```
┌────────────────────────────────────────────┐
│ 🔒 Encrypted at rest: All secrets are     │
│    encrypted using envelope encryption     │
│    with KMS. Requires MFA for reveal.     │
└────────────────────────────────────────────┘
```

**Secret Cards**:
```
┌────────────────────────────────────────────┐
│ 🔑 OpenAI API Key            [api-key] 🗑️ │
│                                            │
│ [sk_live_1234...xyz]         👁️ 📋      │
│  ─ or ─                                   │
│ [••••••••••••••]             👁️ 📋      │
│                                            │
│ Created: 2024-02-15  Last used: 2 hours ago│
│ Expires: 2024-08-15                        │
└────────────────────────────────────────────┘
```

**Secret Types** (color-coded badges):
- `api-key` → Blue
- `password` → Purple
- `2fa-seed` → Green
- `oauth-token` → Orange

**Actions**:
- 👁️ (eye): Reveal/hide value
- 📋 (copy): Copy to clipboard
- 🗑️ (trash): Delete secret

## View 4: API Key Manager

**Info Banner**:
```
┌────────────────────────────────────────────┐
│ 🔑 API keys provide programmatic access   │
│    to AgentID. Keep them secure and never │
│    commit them to version control.        │
└────────────────────────────────────────────┘
```

**API Key Cards**:
```
┌────────────────────────────────────────────┐
│ Production Server        [✓ Active]    🗑️ │
│                                            │
│ [agid_prod_1234...xyz]   👁️ 📋          │
│                                            │
│ Scopes: [agents:read] [agents:write]      │
│         [identities:read] [identities:write]│
│                                            │
│ Created: 2024-02-15  Last used: 2 min ago  │
│ Expires: 2024-08-15                        │
└────────────────────────────────────────────┘
```

**Revoked Keys** (faded with red border):
```
┌────────────────────────────────────────────┐
│ Old CI/CD Key            [Revoked]         │
│ [agid_ci_xyz...abc]      👁️ 📋          │
│ Scopes: [agents:read]                      │
│ Created: 2024-01-15  Last used: 10 days ago│
└────────────────────────────────────────────┘
```

## View 5: Usage & Billing

**Current Bill Card** (gradient blue):
```
┌────────────────────────────────────────────┐
│ Current billing period          💲         │
│ 2024-02-01 — 2024-02-29                    │
│                                            │
│ $68.40                                     │
│ Estimated charges                          │
└────────────────────────────────────────────┘
```

**Usage Stats Grid** (4 cards):
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Active   │ │Email    │ │SMS      │ │API      │
│Agents   │ │Volume   │ │Volume   │ │Calls    │
│ 📊      │ │ 📧      │ │ 📱      │ │ 📈      │
│                                            │
│   3     │ │ 1,247   │ │  456    │ │ 12,453  │
│$10/mo   │ │messages │ │messages │ │this     │
│         │ │received │ │received │ │period   │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

**Cost Breakdown**:
```
┌────────────────────────────────────────────┐
│ Cost Breakdown                             │
├────────────────────────────────────────────┤
│ 📊 Agents (3 × $10)               $30.00  │
│ 📧 Email (1,247 messages)         $15.60  │
│ 📱 SMS (456 messages)             $22.80  │
│ 🛡️  Vault (8 secrets)              Included│
│ ──────────────────────────────────────────│
│ Total                             $68.40  │
└────────────────────────────────────────────┘
```

**Payment Method**:
```
┌────────────────────────────────────────────┐
│ Payment Method                             │
├────────────────────────────────────────────┤
│ 💳 Visa •••• 4242          [Update]        │
│    Expires 12/2025                         │
└────────────────────────────────────────────┘
```

**Billing History**:
```
┌────────────────────────────────────────────┐
│ Billing History                            │
├────────────────────────────────────────────┤
│ 2024-01-01                        $52.30  │
│ Paid                            Download   │
│ ──────────────────────────────────────────│
│ 2023-12-01                        $45.80  │
│ Paid                            Download   │
└────────────────────────────────────────────┘
```

## Color Scheme

### Light Mode
- Background: White (#ffffff), Light Gray (#f9fafb)
- Text: Dark Gray (#0a0a0a), Medium Gray (#6b7280)
- Primary: Blue (#2563eb)
- Borders: Light Gray (#e5e7eb)

### Dark Mode
- Background: Dark Gray (#0a0a0a), Darker Gray (#1f2937)
- Text: Off-White (#ededed), Light Gray (#9ca3af)
- Primary: Light Blue (#60a5fa)
- Borders: Dark Gray (#374151)

### Status Colors
- Success/Active: Green (#10b981)
- Warning/Inactive: Amber (#f59e0b)
- Error: Red (#ef4444)
- Info: Blue (#3b82f6)

## Typography

- **Headings**: -apple-system, BlinkMacSystemFont, 'Segoe UI'
- **Body**: Same as headings
- **Code/IDs**: Monospace (font-mono)
- **Sizes**:
  - Page title: 2xl (24px)
  - Card title: lg (18px) 
  - Body: base (16px)
  - Small: sm (14px), xs (12px)

## Spacing

- **Section padding**: 24px (p-6)
- **Card padding**: 20px (p-5)
- **Element spacing**: 16px (space-y-4)
- **Tight spacing**: 12px (space-y-3)

## Responsive Breakpoints

- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 1024px (2 columns for grids)
- **Desktop**: > 1024px (full layout)

## Interactive Elements

### Buttons
- **Primary**: Blue background, white text
- **Secondary**: Border, gray text
- **Danger**: Red text on hover

### Hover States
- Cards: Slight border color change
- Buttons: Darker background
- Icons: Color change

### Focus States
- Blue ring on keyboard focus
- Clear outline for accessibility

## Icons

All icons from **Lucide React**:
- Bot, Mail, Phone, Shield, Key, BarChart3
- Plus, Trash2, Eye, EyeOff, Copy, Search
- CheckCircle, XCircle, AlertCircle
- ExternalLink, MessageSquare, TrendingUp
- DollarSign, CreditCard, Lock

Size: 16px (w-4 h-4) or 20px (w-5 h-5)

---

This UI guide describes the visual structure. For screenshots, run `npm run dev` and capture the live interface.
