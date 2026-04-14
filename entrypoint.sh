#!/bin/bash
set -e

echo "Starting MyL Database API..."

cd /app/app

# Start server FIRST (so Railway health check passes)
# Then seed in background
echo "Starting server on port ${PORT:-8000}..."
DATABASE_URL=$DATABASE_URL python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} &

SERVER_PID=$!
echo "Server started with PID $SERVER_PID"

# Wait a moment for server to be ready
sleep 3

# Seed database in background
echo "Starting database seed..."
DATABASE_URL=$DATABASE_URL python -m seed &
SEED_PID=$!
echo "Seed started with PID $SEED_PID"

# Wait for server process (keep container alive)
wait $SERVER_PID
