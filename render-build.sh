#!/usr/bin/env bash
# exit on error
set -o errexit

# Install the underlying Linux PDF Engine
apt-get update && apt-get install -y wkhtmltopdf

# Install your Python packages
pip install -r requirements.txt