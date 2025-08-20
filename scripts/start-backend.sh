#!/bin/bash

# Development startup script for AI Post Report backend

echo "🚀 Starting AI Post Report Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please copy .env.example to .env and add your OpenAI API key"
    cp .env.example .env
    echo "📝 Created .env file from example. Please edit it with your API key."
    exit 1
fi

# Create uploads directory
mkdir -p uploads

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📁 Upload directory: ./uploads"
echo "🎵 Ready to process audio files!"
echo ""

cd backend && python main.py
