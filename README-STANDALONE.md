# AI Post Report - Standalone Version

A simplified standalone version of the AI Post Report feature that transcribes audio recordings and automatically fills training report forms using OpenAI's Whisper and GPT-4 APIs.

## Files Overview

### Frontend
- `index.html` - Complete standalone HTML page with embedded CSS and Bootstrap
- `ai-post-report-standalone.js` - JavaScript module for handling audio upload and AI processing

### Backend
- `backend/main.py` - FastAPI server with OpenAI integration
- `requirements-standalone.txt` - Python dependencies for deployment

## Quick Deployment

### Option 1: Frontend Only (Static Hosting)
For testing the UI without AI functionality:
1. Upload `index.html` to any static hosting service (Netlify, Vercel, GitHub Pages)
2. The form will work but AI processing will be disabled

### Option 2: Full Stack Deployment

#### Backend (Render.com or similar)
1. Create a new web service on Render.com
2. Connect your GitHub repo
3. Set build command: `pip install -r requirements-standalone.txt`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `OPENAI_API_KEY=your_openai_api_key`

#### Frontend
1. Update the `apiBaseUrl` in `ai-post-report-standalone.js` to your backend URL
2. Upload `index.html` and `ai-post-report-standalone.js` to static hosting

## Local Development

1. Install Python dependencies:
```bash
pip install -r requirements-standalone.txt
```

2. Create `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```

3. Start backend:
```bash
uvicorn backend.main:app --reload --port 8000
```

4. Open `index.html` in a web browser

## Features

- **Audio Upload**: Supports MP3, WAV, M4A, AAC files up to 50MB
- **AI Transcription**: Uses OpenAI Whisper API for accurate speech-to-text
- **Intelligent Field Mapping**: Uses GPT-4 to extract and organize content into report fields
- **Real-time Progress**: Visual progress indicators during processing
- **Form Integration**: Automatically populates training report form fields
- **Responsive Design**: Works on desktop and mobile devices

## Environment Variables

- `OPENAI_API_KEY` - Required for AI functionality
- `PORT` - Server port (default: 8000 for local, set by hosting service)

## API Endpoint

- `POST /api/post-report/audio` - Upload audio file and receive extracted report data

## Browser Compatibility

- Modern browsers with JavaScript enabled
- File API support for audio uploads
- Fetch API support for server communication
