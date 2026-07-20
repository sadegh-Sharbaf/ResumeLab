#!/bin/sh
set -eu

echo "Applying database migrations..."
python manage.py migrate --noinput

if [ "${SEED_DEMO:-1}" = "1" ]; then
  echo "Creating/updating the featured demo resume..."
  python manage.py seed_demo
fi

echo "Starting Gunicorn on port ${PORT:-10000}..."
exec gunicorn PersonalWeb.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile - \
  --error-logfile -
