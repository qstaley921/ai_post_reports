# AI Post Report Integration (Scaffold)

This repository contains an exported HTML snapshot of a TCal Training Post-OST Report page plus a newly added "AI Post Report" section scaffold (in `tcal_post_report_page/example.html`). The new section (inside the existing Training Post-OST collapsible area) provides:

- Audio upload button (currently only simulates processing steps)
- Progress step indicators: Uploading, Transcribing, Organizing, Pasting
- Simulated progress bar & status messaging

## Current State
Pure front-end placeholder only. Selecting an audio file triggers a timed simulation that marks each step complete and updates a progress bar. No network calls or real transcription yet.

## Planned Architecture
1. User uploads audio.
2. Front-end sends `FormData` with audio blob to backend endpoint `/api/post-report/audio`.
3. Backend:
   - Stores file (temp storage / S3)
   - Runs Whisper (OpenAI API or local whisper.cpp) to get transcript
   - Sends transcript to custom GPT prompt that returns JSON keyed by report section IDs.
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
5. Front-end iterates keys, injects text into matching `textarea#<id>` fields.
6. Display completion + allow user edits before final manual submit (existing form post).

## IDs / Field Mapping Extracted
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

## Next Implementation Steps
- Add lightweight JS module to perform real upload & injection.
- Introduce a backend (Node/Express or Python FastAPI) with two endpoints: upload+process, status/poll (optional for long jobs).
- Decide on transcription provider (OpenAI Whisper API vs. local model).
- Craft GPT prompt & response schema; add validation.
- Error handling & retry UI states.
- Security: size/type validation, auth token if needed.

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
