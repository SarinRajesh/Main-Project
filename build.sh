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
pip install protobuf==5.26.1

# Install numpy first (since it's a core dependency)
pip install numpy==1.23.5

# Install grpcio and grpcio-status
pip install grpcio==1.70.0
pip install grpcio-status==1.59.3

# Install tensorflow ecosystem packages in correct order
pip install tensorflow==2.12.0
pip install keras==2.12.0
pip install tensorboard==2.12.3
pip install tensorboard-data-server==0.7.2

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!" 