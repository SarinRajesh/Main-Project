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

# Install numpy first (since it's a core dependency)
pip install numpy==1.23.5

# Install tensorflow ecosystem packages
pip install tensorflow==2.12.0
pip install keras==2.12.0

# Install other dependencies
pip install -r requirements.txt

# Create staticfiles directory
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!"