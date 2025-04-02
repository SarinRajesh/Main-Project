#!/usr/bin/env bash
# exit on error
set -o errexit

# Clean up any existing virtual environment
rm -rf .venv

# Create a new virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies first
pip install numpy==1.24.3
pip install scipy==1.10.1
pip install scikit-learn==1.2.2
pip install gast==0.4.0
pip install keras==2.12.1
pip install tensorflow==2.12.0

# Install other dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate 