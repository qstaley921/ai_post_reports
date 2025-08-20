# AI Post Report Integration (Scaffold)

This repository contains an exported HTML snapshot of a TCal Training Post-OST Report page plus a newly added "AI Post Report" section scaffold (in `tcal_post_report_page/example.html`). The new section (inside the existing Training Post-OST collapsible area) provides:

- Audio upload button (currently only simulates processing steps)
- Progress step indicators: Uploading, Transcribing, Organizing, Pasting
- Simulated progress bar & status messaging

## Current State
Pure front-end placeholder only. Selecting an audio file triggers a timed simulation that marks each step complete and updates a progress bar. No network calls or real transcription yet.

## Planned Architecture (Python Backend + Vanilla JS Frontend)
1. User uploads audio via vanilla JavaScript file input.
2. Frontend sends `FormData` with audio blob to Python backend endpoint `/api/post-report/audio`.
3. **Python Backend** (FastAPI or Flask):
   - Stores audio file (temp storage or cloud)
   - Uses OpenAI Whisper API or `whisper` Python library for transcription
   - Sends transcript to OpenAI GPT API with custom prompt for report field extraction
   - Returns structured JSON keyed by report section IDs.
4. Backend responds with JSON like:
```json
{
  "postost_wins": "...",
  "client_goals": "...",
  "postost_holdbacks": "...",
  "human_capital": "...",
  "marketing": "...",
  "space_and_equipment": "...",
  "clinical_duplication": "...",
  "financial": "...",
  "upcoming_milestones": "...",
  "homework_doctor": "...",
  "homework_trainer": "...",
  "next_steps": "..."
}
```
5. **Vanilla JavaScript Frontend** iterates response keys, injects text into matching `textarea#<id>` fields.
6. Display completion + allow user edits before final manual submit (existing form post).

## Technology Stack
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Backend**: Python with FastAPI (recommended) or Flask
- **AI Services**: 
  - OpenAI Whisper API for transcription
  - OpenAI GPT API for text organization/extraction
- **Storage**: Temporary file storage (local or cloud)

## Next Implementation Steps (Python Focus)
- Create Python virtual environment and install dependencies (`fastapi`, `openai`, `python-multipart`, etc.)
- Build FastAPI server with `/api/post-report/audio` endpoint
- Implement audio file handling, Whisper transcription, and GPT processing
- Extract inline JavaScript to separate module for real upload & field injection
- Add error handling & validation for audio file types/sizes
- Environment configuration for OpenAI API keys
The HTML already includes field IDs suitable for mapping:
- postost_wins
- client_goals
- postost_holdbacks
- human_capital
- marketing
- space_and_equipment
- clinical_duplication
- financial
- upcoming_milestones
- (Later rows likely include: homework_doctor, homework_trainer, next_steps, etc.)

## IDs / Field Mapping Extracted

## Local Dev Suggestions
Because `example.html` is a static export, you may want to:
1. Serve it via a simple static server (e.g., `python3 -m http.server`).
2. Move inline script into a separate JS file for maintainability.
3. Replace simulation with real fetch calls once backend is ready.

## GitHub Setup
After cloning/initializing locally:
```bash
# Create remote (example)
# gh repo create org/repo-name --public --source=. --push
# or manually on GitHub then:
git remote add origin git@github.com:YOUR_ORG/YOUR_REPO.git
git push -u origin main
```

## License
Internal / Proprietary.

## Dependency Layout (Updated)
We removed the legacy root requirements.txt. Use these instead:
- requirements-backend.txt : FastAPI API + audio + OpenAI integration deps (includes pydub)
- requirements-frontend.txt : Minimal FastAPI server just to serve index.html & JS

runtime.txt was an empty placeholder (Heroku-style Python version pin). Not needed on Render; Python version is controlled via PYTHON_VERSION env var in render.yaml/service settings.

## 🤖 AI Agent Project Standards
See `AI_AGENT_RULES.md` for comprehensive development standards, file structure rules, and deployment guidelines. This ensures consistency and prevents architectural regressions during AI-assisted development.
