FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy scraper and app
COPY scraper/ /app/scraper/
COPY app/ /app/app/

# Create data directory
RUN mkdir -p /app/scraper/data/images

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
