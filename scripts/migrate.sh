#!/usr/bin/env bash
# Create a new Alembic migration
set -euo pipefail

MSG="${1:?Usage: ./scripts/migrate.sh 'migration message'}"

docker compose exec api alembic revision --autogenerate -m "$MSG"
echo "✅ Migration created. Review in alembic/versions/"
echo "   Apply: docker compose exec api alembic upgrade head"
