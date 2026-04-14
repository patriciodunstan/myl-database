FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper first (rarely changes)
COPY scraper/ /app/scraper/

# Create data directory
RUN mkdir -p /app/scraper/data/images

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy app LAST (changes most frequently - avoids cache)
COPY app/ /app/app/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
