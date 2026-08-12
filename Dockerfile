FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd \
        --create-home \
        --shell /bin/bash \
        app && \
    chown -R app:app /app

USER app

EXPOSE 9080

# Container healthcheck
HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=20s \
    --retries=3 \
    CMD curl -fsS http://127.0.0.1:9080/ > /dev/null || exit 1

# Production WSGI server
CMD [
    "gunicorn",
    "--bind", "0.0.0.0:9080",
    "--workers", "2",
    "--threads", "4",
    "--timeout", "120",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "mailscout.app:app"
]