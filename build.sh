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

# Install protobuf first (since it's a core dependency)
pip install protobuf==3.20.3

# Install numpy first (since it's a core dependency)
pip install numpy==1.23.5

# Install Google packages first
pip install google-api-core==2.24.1
pip install google-auth==2.31.0
pip install google-auth-httplib2==0.2.0
pip install google-auth-oauthlib==1.2.1
pip install google-generativeai==0.8.4

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