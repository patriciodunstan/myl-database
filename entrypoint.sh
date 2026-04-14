#!/bin/bash
set -e

echo "Starting MyL Database API..."

# Seed database if empty
echo "Checking if database needs seeding..."
cd /app/app
python -m seed

echo "Starting server on port ${PORT:-8000}..."
DATABASE_URL=$DATABASE_URL exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
