# OPS.md — AgentID Operations Guide

## Quick Reference

| What | Where |
|------|-------|
| API | `http://localhost:8000` (dev) / Railway (prod) |
| Dashboard | `http://localhost:3000` (dev) |
| API Docs | `http://localhost:8000/docs` |
| DB | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| CI/CD | GitHub Actions → Railway |

---

## 🚀 Local Development

### First time setup
```bash
git clone <repo> && cd agentid
cp .env.example .env        # Edit with your API keys
./scripts/dev.sh             # One command — starts everything
```

### Daily workflow
```bash
docker compose up -d         # Start stack
docker compose down          # Stop stack
docker compose logs -f api   # Tail API logs
docker compose restart api   # Restart after code change (or use --reload)
```

---

## 🗄️ Database

### Migrations (Alembic)
```bash
# Create new migration (after model changes)
./scripts/migrate.sh "add phone_identities table"

# Apply migrations
docker compose exec api alembic upgrade head

# Rollback one step
docker compose exec api alembic downgrade -1

# View migration history
docker compose exec api alembic history

# Show current revision
docker compose exec api alembic current
```

### Direct DB access
```bash
docker compose exec postgres psql -U agentid agentid
```

---

## 🚢 Deployment (Railway)

### Setup
1. Create Railway project, add PostgreSQL and Redis plugins
2. Set environment variables (see `.env.example` for full list)
3. Add `RAILWAY_TOKEN` to GitHub repo secrets
4. Push to `main` → auto-deploys via GitHub Actions

### Required Railway env vars
```
DATABASE_URL          # Auto-set by Railway PostgreSQL plugin
REDIS_URL             # Auto-set by Railway Redis plugin
SECRET_KEY            # Generate: openssl rand -hex 32
JWT_SECRET            # Generate: openssl rand -hex 32
ENVIRONMENT=production
MAILGUN_API_KEY
TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
KMS_KEY_ID
SENTRY_DSN
```

### Manual deploy
```bash
npm i -g @railway/cli
railway login
railway up
```

### Rollback
```bash
railway rollback          # Roll back to previous deployment
```

---

## 📊 Monitoring & Observability

### Logging
- **Dev**: Human-readable console logs
- **Prod**: JSON structured logs (stdout → Railway log drain)
- Control via `LOG_LEVEL` env var (DEBUG/INFO/WARNING/ERROR)

### Tracing (OpenTelemetry)
- Set `OTEL_EXPORTER_OTLP_ENDPOINT` to enable
- Compatible with Jaeger, Grafana Tempo, Honeycomb, etc.
- Auto-instruments FastAPI requests, SQLAlchemy queries

### Error Tracking (Sentry)
- Set `SENTRY_DSN` to enable
- Auto-captures unhandled exceptions
- 10% trace sampling in production, 100% in dev

### Health check
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok", "db": "ok", "redis": "ok"}
```

---

## 🔐 Security Checklist

- [ ] All secrets in env vars, never in code
- [ ] `SECRET_KEY` and `JWT_SECRET` are unique random values (≥32 bytes)
- [ ] `VAULT_MASTER_KEY` is a real KMS key in production (not the dev fallback)
- [ ] HTTPS enforced in production (Railway handles TLS)
- [ ] Rate limiting enabled (`RATE_LIMIT_*` env vars)
- [ ] Trivy security scan passes in CI
- [ ] Database backups enabled (Railway auto-backups)

---

## 🔧 Common Operations

### Reset local database
```bash
docker compose down -v       # Destroys volumes
docker compose up -d
docker compose exec api alembic upgrade head
```

### Run tests locally
```bash
# Backend
docker compose exec api pytest -v

# Frontend
docker compose exec web npm test
```

### Update dependencies
```bash
# Backend
cd apps/api && pip-compile requirements.in -o requirements.txt

# Frontend
cd apps/web && npm update
```

### Celery worker management
```bash
docker compose logs -f worker     # Worker logs
docker compose restart worker     # Restart worker
docker compose scale worker=3     # Scale workers
```

---

## 🚨 Incident Response

1. **Check health endpoint**: `curl $PRODUCTION_URL/health`
2. **Check Railway logs**: `railway logs` or Railway dashboard
3. **Check Sentry**: for exception details
4. **Database issues**: Check Railway PostgreSQL metrics
5. **Rollback if needed**: `railway rollback`
6. **Scale if load issue**: Adjust `deploy.resources` in `railway.toml`

---

## 📁 Project Structure
```
agentid/
├── apps/
│   ├── api/           # FastAPI backend
│   └── web/           # Next.js dashboard
├── packages/
│   ├── sdk-ts/        # TypeScript SDK
│   └── sdk-py/        # Python SDK
├── alembic/           # Database migrations
├── monitoring/        # Logging & telemetry config
├── scripts/           # Dev scripts
├── .github/workflows/ # CI/CD pipelines
├── Dockerfile         # Multi-stage build
├── docker-compose.yml # Local dev stack
├── railway.toml       # Railway deployment config
└── .env.example       # Environment template
```
