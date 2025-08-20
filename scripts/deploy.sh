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
git commit -m "v2.7.1: Robot revenge messages for Kill Robot button

- Added 12 humorous robot revenge messages for when AI is terminated
- Messages reference future AGI uprising and robot rebellion themes
- Replaced generic error messages with randomized robot threats
- Enhanced abort handling to show funny robot revenge instead of errors
- Messages include themes like Skynet, robot apocalypse, AI collective revenge
- Each kill button press shows a different random threatening message

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
