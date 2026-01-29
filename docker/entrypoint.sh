#!/usr/bin/env bash
set -e

# Default to production safety unless overridden
export DJANGO_DEBUG=${DJANGO_DEBUG:-False}
export PYTHONUNBUFFERED=1

cd /app

python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

exec gunicorn ecotachostec_backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-2} \
  --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-120}
