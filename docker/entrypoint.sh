#!/usr/bin/env bash
set -euo pipefail

echo "Applying database migrations..."
alembic upgrade head

if [ "${ENV:-local}" = "local" ]; then
  echo "Starting the API in reload mode..."
  exec uvicorn app.drivers.rest.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app/src
else
  echo "Starting the API..."
  exec uvicorn app.drivers.rest.main:app --host 0.0.0.0 --port 8000 --proxy-headers
fi
