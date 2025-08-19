# Render.com Deployment Guide

## 🚀 Deploy AI Post Report to Render.com

### Step 1: Deploy Backend (Python API)

1. **Go to [Render.com](https://render.com)** and sign up/login
2. **Connect your GitHub** repository: `https://github.com/qstaley921/ai_post_reports`
3. **Create a new Web Service**:
   - **Name**: `ai-post-report-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Auto-Deploy**: `Yes`

4. **Add Environment Variables**:
   - **OPENAI_API_KEY**: `your_openai_api_key_here`
   - **PYTHON_VERSION**: `3.13.6`

5. **Deploy** - It will take 2-3 minutes

### Step 2: Deploy Frontend (Static Site)

1. **Create a new Static Site**:
   - **Name**: `ai-post-report-frontend`
   - **Build Command**: `echo "No build needed"`
   - **Publish Directory**: `.` (root)

2. **Update Backend URL**:
   - Once backend is deployed, note the URL (e.g., `https://ai-post-report-backend.onrender.com`)
   - The JavaScript will auto-detect this URL

### Step 3: Test the Application

Your app will be live at:
- **Frontend**: `https://ai-post-report-frontend.onrender.com`
- **Backend API**: `https://ai-post-report-backend.onrender.com`

## 🎯 Features After Deployment

✅ **Real OpenAI Whisper** transcription  
✅ **Real GPT-4** content organization  
✅ **Public access** for anyone to use  
✅ **Automatic scaling** on Render.com  
✅ **HTTPS security** included  

## 💰 Cost

- **Free Tier**: 750 hours/month (enough for testing)
- **Paid Tier**: $7/month for backend, frontend is free
- **OpenAI Usage**: Pay per API call (typically $0.10-0.30 per hour of audio)

## 🔧 Environment Variables Needed

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `OPENAI_API_KEY` | Your API key | [OpenAI Platform](https://platform.openai.com/api-keys) |

## ⚡ Quick Deploy Option

Use the `render.yaml` file in this repository for one-click deployment:

1. Fork this repository
2. Connect to Render.com
3. Use "Deploy from Repository" option
4. Add your OpenAI API key
5. Deploy!

## 🎯 What Users Will Get

- Upload audio files up to 50MB
- Real AI transcription and content organization
- Automatic form population with numbered, detailed points
- Professional interface with progress tracking
- No installation required - just visit the URL
