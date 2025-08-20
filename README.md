# AI Post Report - Audio-to-Form Processing

A full-stack web application that automatically transcribes audio recordings and extracts structured data for training post-reports using OpenAI's Whisper and GPT-4 APIs.

## ✨ Features

- **Audio Upload**: Supports MP3, M4A, WAV, OGG, and other common audio formats
- **Real-time Progress**: Visual progress tracking with step-by-step feedback
- **AI Processing**: Automatic transcription (Whisper) and content analysis (GPT-4)
- **Form Integration**: Automatically fills form fields with extracted data
- **Professional UI**: Clean, responsive Bootstrap interface
- **Error Handling**: Graceful fallback to demo mode if API unavailable

## 🚀 Live Demo

- **Frontend**: https://ai-post-report-frontend.onrender.com
- **Backend API**: https://ai-post-reports.onrender.com

## 📁 Project Structure

```
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── .gitignore            # Git ignore rules
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── backend/              # FastAPI backend
│   ├── main.py          # Main API server
│   └── uploads/         # Temporary file storage
├── frontend/             # Frontend application
│   ├── index.html       # Main HTML page
│   ├── ai-post-report-standalone.js  # JavaScript logic
│   └── frontend_server.py            # Static file server
├── scripts/              # Utility scripts
│   ├── deploy.sh        # Deployment script
│   ├── start.sh         # Development startup
│   ├── start-backend.sh # Backend only
│   └── start-frontend.sh # Frontend only
├── config/               # Configuration files
│   ├── render.yaml      # Render.com deployment config
│   └── render-frontend.yaml  # Frontend service config
├── docs/                 # Documentation
│   └── RENDER_DEPLOYMENT.md  # Deployment guide
├── reference/            # Reference materials
│   └── tcal_post_report_page/  # Original TCAL page
└── uploads/              # Runtime upload directory
```

```

## 🛠 Technology Stack

- **Frontend**: Vanilla JavaScript, Bootstrap 5, Font Awesome
- **Backend**: FastAPI (Python), direct HTTP calls to OpenAI
- **AI Services**: OpenAI Whisper API (transcription), GPT-4 (analysis)
- **Audio Processing**: pydub for format conversion
- **Deployment**: Render.com (dual service hosting)
- **Development**: Python 3.11+, uvicorn, CORS support

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/qstaley921/ai_post_reports.git
   cd ai_post_reports
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Start both frontend and backend
   ./scripts/start.sh
   
   # Or start individually:
   ./scripts/start-backend.sh   # Backend on port 8000
   ./scripts/start-frontend.sh  # Frontend on port 8080
   ```

5. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000

## 📝 How It Works

1. **Audio Upload**: User selects an audio file (MP3, M4A, WAV, etc.)
2. **Format Conversion**: Backend converts non-MP3 files to MP3 using pydub
3. **Transcription**: Audio sent to OpenAI Whisper API for transcription
4. **Analysis**: Transcript analyzed by GPT-4 to extract structured report data
5. **Form Population**: JavaScript automatically fills form fields with extracted data

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=./uploads
PORT=8000  # For backend (auto-set by Render)
```

### Audio Format Support
- **Supported**: MP3, M4A, WAV, OGG, FLAC, AAC
- **Auto-conversion**: Non-MP3 formats automatically converted
- **Size limit**: 50MB maximum file size

## 🚢 Deployment

### Render.com (Recommended)

The application is configured for automatic deployment on Render.com:

1. **Deploy with one click**: Use the `scripts/deploy.sh` script
2. **Dual service setup**: Separate frontend and backend services
3. **Auto-deploy**: Pushes to main branch trigger automatic deployment

### Manual Deployment

See `docs/RENDER_DEPLOYMENT.md` for detailed deployment instructions.

## 🧪 Development

### Running Tests
```bash
# Backend tests
python -m pytest backend/tests/

# Frontend can be tested manually or with browser automation
```

### Code Structure
- **Backend**: RESTful API with single `/api/post-report/audio` endpoint
- **Frontend**: Progressive enhancement with real-time feedback
- **Error Handling**: Graceful degradation to demo mode

## 📚 API Documentation

### POST /api/post-report/audio

Upload and process audio file for report generation.

**Request:**
- `file`: Audio file (multipart/form-data)

**Response:**
```json
{
  "success": true,
  "transcript": "Full transcription text...",
  "report_data": {
    "postost_wins": "Extracted content...",
    "client_goals": "Extracted content...",
    // ... other report fields
  },
  "message": "Audio processed successfully"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review the reference implementation in `reference/`
3. Create an issue on GitHub
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
