#!/bin/bash

# AI Post Report Deployment Script
echo "🚀 Deploying AI Post Report updates..."

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "❌ Error: Not in the AI Post Report directory"
    exit 1
fi

# Add all changes
git add .

# Get current timestamp
timestamp=$(date "+%Y-%m-%d %H:%M:%S")

# Commit with descriptive message
git commit -m "v2.5.0: Visual progress improvements + M4A audio format support

- Fixed analyze step activation in progress tracking
- Added checkmark icons for completed progress steps  
- Updated active step colors (white instead of dark green)
- Added pydub for M4A/AAC/OGG to MP3 audio conversion
- Enhanced error handling for unsupported audio formats
- Updated to version 2.5.0 with timestamp

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
