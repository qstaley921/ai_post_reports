#!/bin/bash

# Development script for AI Post Report frontend

echo "🌐 Starting AI Post Report Frontend..."
echo "📁 Serving from: $(pwd)"
echo "🔗 Frontend will be available at: http://localhost:8080"
echo "📄 Open: http://localhost:8080/"
echo ""
echo "💡 Make sure backend is running on http://localhost:8000"
echo ""

# Use Python's built-in HTTP server from project root
python3 -m http.server 8080
