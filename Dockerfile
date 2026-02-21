# ============================================================
# AgentID — Multi-stage Dockerfile
# Stages: frontend-build → backend → production
# ============================================================

# --- Stage 1: Frontend build (Next.js) ---
FROM node:20-alpine AS frontend-build
WORKDIR /app/web

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Backend base ---
FROM python:3.12-slim AS backend-base
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/pyproject.toml ./
RUN pip install --no-cache-dir .

COPY apps/api/ ./
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

# --- Stage 3: Production ---
FROM python:3.12-slim AS production
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app && adduser --system --ingroup app app

COPY --from=backend-base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin
COPY --from=backend-base /app /app
COPY --from=frontend-build /app/web/.next /app/static/frontend/.next
COPY --from=frontend-build /app/web/public /app/static/frontend/public

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
