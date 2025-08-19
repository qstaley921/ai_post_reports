#!/usr/bin/env bash
# Start script for Render.com backend

# Use the PORT environment variable provided by Render, or default to 8000
PORT=${PORT:-8000}

# Start the FastAPI application
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
