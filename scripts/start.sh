#!/bin/bash
set -euxo pipefail

echo "--- Running database migrations ---"
alembic upgrade head
echo "--- Database migrations complete ---"

echo "--- Starting web server ---"
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-5201}"
