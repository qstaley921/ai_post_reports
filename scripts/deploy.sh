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
git commit -m "v2.6.0: Project reorganization + comprehensive documentation

- Reorganized project structure into logical directories:
  * frontend/ - All frontend files (HTML, JS, server)
  * backend/ - API server and uploads
  * scripts/ - Build, deploy, and start scripts  
  * config/ - Render deployment configuration
  * docs/ - Documentation files
  * reference/ - TCAL reference materials
- Updated comprehensive README with setup instructions
- Enhanced .env.example with proper configuration
- Fixed file paths in Render configuration
- Maintained all existing functionality
- Added M4A audio format support with pydub conversion
- Visual progress improvements with checkmark icons

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
