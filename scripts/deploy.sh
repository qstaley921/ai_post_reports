#!/bin/bash

# AI Post Report Deployment Script
echo "🚀 Deploying AI Post Report updates..."

# Check if we're in the right directory (look for README.md and backend directory)
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Not in the AI Post Report root directory"
    echo "Please run from the project root directory"
    exit 1
fi

# Add all changes
git add .

# Get current timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Commit with descriptive message
git commit -m "v2.7.3: Complete Kill Robot fix - stop all async operations

- Made simulateDelay abort-aware to stop progress simulation immediately
- Added abort checks in simulateUploadProgress loop to prevent continued updates
- Enhanced demo function with proper try-catch and abort handling
- Progress bar now stops immediately when Kill Robot is clicked
- Prevented async operations from continuing after abort
- Robot revenge messages no longer get overridden by delayed error messages
- Complete termination of all progress simulation and status updates

Deployment: $timestamp"

# Push to GitHub (triggers Render auto-deploy)
git push origin main

echo "✅ Changes pushed to GitHub"
echo "⏱️  Render will auto-deploy in ~2-3 minutes"
echo "🌐 Frontend: https://ai-post-report-frontend.onrender.com"  
echo "🔧 Backend: https://ai-post-reports.onrender.com"
echo ""
echo "📋 Changes deployed:"
echo "   • Visual progress improvements"
echo "   • M4A audio format support"  
echo "   • Enhanced user experience"
