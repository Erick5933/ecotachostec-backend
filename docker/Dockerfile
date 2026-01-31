# Multi-stage build for smaller image
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for opencv, pillow, psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libgl1 \
       libglib2.0-0 \
       libjpeg62-turbo \
       zlib1g \
       curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY src/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project
COPY src/ /app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app

USER appuser

# Collect static at build time (safe with WhiteNoise)
# Will not fail if static not configured
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Entrypoint runs migrations and starts gunicorn
COPY docker/entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh && chown appuser:appuser /entrypoint.sh
USER appuser

CMD ["/entrypoint.sh"]
