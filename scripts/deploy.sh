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
git commit -m "v2.7.2: Fix Kill Robot button - complete abort functionality

- Fixed issue where error messages would override robot revenge messages
- Added manual abort flag to prevent error handling from overwriting kill messages
- Kill Robot now properly stops all progress bar updates and intervals
- File input is cleared after abort, allowing immediate re-upload
- Finally block respects manual abort state to prevent button state conflicts
- Robot revenge messages now persist until user starts new upload
- Complete process termination with proper state cleanup

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
