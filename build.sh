#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies first
pip install wheel setuptools

# Install tensorflow and keras first
pip install tensorflow==2.12.0
pip install keras==2.12.0

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!" 