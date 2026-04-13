#!/bin/bash
set -e

DB_PATH="/app/scraper/data/myl.db"

if [ ! -f "$DB_PATH" ]; then
    echo "No database found. Running scraper..."
    cd /app/scraper
    MYL_DATA_DIR=/app/scraper/data MYL_DB_PATH=$DB_PATH python scraper.py
    echo "Scraper completed."
else
    echo "Database found. Skipping scraper."
fi

echo "Starting server on port ${PORT:-8000}..."
cd /app/app
MYL_DB_PATH=$DB_PATH exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
