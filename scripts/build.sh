#!/usr/bin/env bash
# Build script for Render.com

set -e  # Exit on any error

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-standalone.txt

echo "Build completed successfully!"
