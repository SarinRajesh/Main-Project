#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Set environment variables
export DJANGO_SETTINGS_MODULE=ElegantDecor.settings
export PYTHONUNBUFFERED=1

# Start Gunicorn with optimized settings
gunicorn ElegantDecor.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --worker-class gthread 