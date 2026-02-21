#!/usr/bin/env bash
# AgentID — One-command local development
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "🚀 AgentID — Starting local development stack..."

# Create .env from example if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env from .env.example — edit with your keys"
fi

# Start everything
docker compose up --build -d

echo ""
echo "✅ AgentID is running!"
echo "   API:       http://localhost:8000"
echo "   Dashboard: http://localhost:3000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Postgres:  localhost:5432"
echo "   Redis:     localhost:6379"
echo ""
echo "📋 Useful commands:"
echo "   docker compose logs -f api     # API logs"
echo "   docker compose logs -f worker  # Worker logs"
echo "   docker compose down            # Stop all"
echo "   ./scripts/migrate.sh 'msg'     # Create migration"
