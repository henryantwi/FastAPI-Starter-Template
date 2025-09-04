#!/bin/bash

set -e

# Apply database migrations
echo "Applying database migrations..."
/app/.venv/bin/alembic upgrade head

# Create superuser (non-blocking - continue even if it fails)
echo "Creating superuser..."
if /app/.venv/bin/python scripts/create_superuser.py; then
    echo "✓ Superuser setup completed"
else
    echo "⚠ Warning: Superuser creation failed, but continuing with server startup..."
fi

# Start FastAPI server
echo "Starting server..."
/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
