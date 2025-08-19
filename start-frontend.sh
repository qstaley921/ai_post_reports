#!/bin/bash

# Simple static server for frontend development

echo "🌐 Starting static file server for frontend..."
echo "📁 Serving from: $(pwd)"
echo "🔗 Frontend will be available at: http://localhost:8080"
echo "📄 Open: http://localhost:8080/tcal_post_report_page/example.html"
echo ""
echo "💡 Make sure backend is running on http://localhost:8000"
echo ""

# Use Python's built-in HTTP server
python3 -m http.server 8080
