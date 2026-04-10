#!/usr/bin/env bash
set -o errexit

# Install C++ compiler and CMake for dlib
apt-get update && apt-get install -y cmake g++

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate