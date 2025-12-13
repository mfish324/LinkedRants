#!/bin/bash
echo "Running migrations..."
python manage.py migrate --noinput
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn linkedrants.wsgi:application --bind 0.0.0.0:${PORT:-8000} --log-level debug
