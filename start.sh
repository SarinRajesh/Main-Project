#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start Gunicorn with our configuration
gunicorn ElegantDecor.wsgi:application -c gunicorn_config.py 