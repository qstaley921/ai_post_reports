from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
import urllib.request
import urllib.parse
import json
from typing import Dict, Any
import logging
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Post Report API", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# OpenAI API endpoints
OPENAI_TRANSCRIPTION_URL = "https://api.openai.com/v1/audio/transcriptions"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# Check OpenAI API key
if OPENAI_API_KEY and OPENAI_API_KEY.strip():
    print("✅ OpenAI API key loaded successfully")
    api_available = True
else:
    print("❌ OpenAI API key not found in environment variables")
    api_available = False

# Field mapping for the post report form
REPORT_FIELDS = {
    "postost_wins": "WINS/CELEBRATIONS",
    "client_goals": "STAT/GOAL REVIEW", 
    "postost_holdbacks": "BIGGEST BARRIERS OR ISSUES CLIENT IS STRUGGLING WITH",
    "human_capital": "HUMAN CAPITAL",
    "marketing": "MARKETING",
    "space_and_equipment": "SPACE AND EQUIPMENT",
    "clinical_duplication": "CLINICAL DUPLICATION",
    "financial": "FINANCIAL",
    "upcoming_milestones": "UPCOMING MILESTONES",
    "homework_doctor": "HOMEWORK FOR DOCTOR",
    "homework_trainer": "HOMEWORK FOR TRAINER",
    "next_steps": "NEXT STEPS"
}

def format_report_text(report_data: Dict[str, str]) -> Dict[str, str]:
    """Format report text with proper line breaks between numbered items"""
    formatted_data = {}
    
    for key, text in report_data.items():
        if not text or not isinstance(text, str):
            formatted_data[key] = text
            continue
            
        # Split by numbered items ([1], [2], [3], etc.)
        import re
        
        # Find all numbered items in [1], [2], [3] format
        numbered_items = re.split(r'(\[\d+\])', text)
        
        if len(numbered_items) <= 2:
            # No numbered items found, return as-is
            formatted_data[key] = text
        else:
            # Process numbered items
            formatted_parts = []
            current_item = ""
            
            for i, part in enumerate(numbered_items):
                if re.match(r'^\[\d+\]$', part):  # This is a number like "[1]"
                    if current_item.strip():  # Save previous item
                        formatted_parts.append(current_item.strip())
                    current_item = part  # Start new item with the number
                elif part.strip():  # This is content
                    current_item += " " + part.strip()
            
            # Add the last item
            if current_item.strip():
                formatted_parts.append(current_item.strip())
            
            # Join with double line breaks (no HTML tags)
            if formatted_parts:
                formatted_text = '\n\n'.join(formatted_parts)
                formatted_data[key] = formatted_text
            else:
                formatted_data[key] = text
    
    return formatted_data

@app.get("/")
async def root():
    return {"message": "AI Post Report API is running"}

@app.post("/api/post-report/audio")
async def process_audio_upload(file: UploadFile = File(...)):
    """
    Process uploaded audio file:
    1. Validate file
    2. Transcribe with Whisper
    3. Extract report sections with GPT
    4. Return structured data
    """
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file size
        file_size = 0
        temp_file_path = None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file_path = temp_file.name
            
            # Read and save file while checking size
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE_BYTES:
                    temp_file.close()
                    os.unlink(temp_file_path)
                    raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_FILE_SIZE_MB}MB")
                temp_file.write(chunk)
        
        logger.info(f"Processing audio file: {file.filename} ({file_size} bytes)")
        
        # Step 1: Convert audio to MP3 if needed (for OpenAI compatibility)
        audio_file_path = temp_file_path
        converted_file_path = None
        
        # Check if file needs conversion based on extension
        file_extension = Path(file.filename).suffix.lower()
        needs_conversion = file_extension not in ['.mp3', '.wav', '.flac', '.webm']
        
        if needs_conversion or file_extension in ['.m4a', '.aac', '.ogg']:
            logger.info(f"Converting {file_extension} to MP3 for OpenAI compatibility")
            converted_file_path = convert_audio_to_mp3(temp_file_path)
            audio_file_path = converted_file_path
        
        # Step 2: Transcribe audio with Whisper
        transcript = await transcribe_audio(audio_file_path)
        logger.info(f"Transcription completed: {len(transcript)} characters")
        
        # Step 3: Extract report sections with GPT
        report_data = await extract_report_sections(transcript)
        logger.info("Report sections extracted successfully")
        
        # Clean up temp files
        os.unlink(temp_file_path)
        if converted_file_path and os.path.exists(converted_file_path):
            os.unlink(converted_file_path)
        
        return JSONResponse(content={
            "success": True,
            "transcript": transcript,
            "report_data": report_data,
            "message": "Audio processed successfully"
        })
        
    except HTTPException:
        # Clean up temp files if they exist
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if 'converted_file_path' in locals() and converted_file_path and os.path.exists(converted_file_path):
            os.unlink(converted_file_path)
        raise
    except Exception as e:
        # Clean up temp files if they exist
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        if 'converted_file_path' in locals() and converted_file_path and os.path.exists(converted_file_path):
            os.unlink(converted_file_path)
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

def convert_audio_to_mp3(input_path: str) -> str:
    """
    Convert audio file to MP3 format for OpenAI compatibility.
    Returns path to converted MP3 file.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Create temp MP3 file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
            mp3_path = temp_mp3.name
        
        # Export as MP3
        audio.export(mp3_path, format="mp3")
        logger.info(f"Converted audio from {input_path} to MP3: {mp3_path}")
        
        return mp3_path
        
    except CouldntDecodeError as e:
        logger.error(f"Could not decode audio file {input_path}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Unsupported audio format or corrupted file: {str(e)}")
    except Exception as e:
        logger.error(f"Error converting audio {input_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error converting audio: {str(e)}")

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file using OpenAI Whisper API via direct HTTP request"""
    try:
        if not api_available:
            # Demo mode - return sample transcript
            return """
            This is a demo transcription. In a real deployment with an OpenAI API key, 
            this would contain the actual transcription of your uploaded audio file.
            
            Sample training session content:
            - Discussed patient progress and goals
            - Reviewed marketing strategies 
            - Identified equipment needs
            - Planned next steps for the practice
            """
        
        # Use direct HTTP request to OpenAI API with urllib
        import urllib.request
        import urllib.parse
        
        with open(file_path, "rb") as audio_file:
            # Create multipart form data manually
            boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
            
            # Build multipart body
            body = []
            body.append(f"--{boundary}".encode())
            body.append(b'Content-Disposition: form-data; name="model"')
            body.append(b"")
            body.append(b"whisper-1")
            
            body.append(f"--{boundary}".encode())
            body.append(b'Content-Disposition: form-data; name="response_format"')
            body.append(b"")
            body.append(b"text")
            
            body.append(f"--{boundary}".encode())
            body.append(b'Content-Disposition: form-data; name="file"; filename="audio.wav"')
            body.append(b'Content-Type: audio/wav')
            body.append(b"")
            body.append(audio_file.read())
            
            body.append(f"--{boundary}--".encode())
            
            data = b"\r\n".join(body)
            
            # Create request
            req = urllib.request.Request(
                OPENAI_TRANSCRIPTION_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": f"multipart/form-data; boundary={boundary}"
                }
            )
            
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    if response.status == 200:
                        return response.read().decode('utf-8')
                    else:
                        raise Exception(f"OpenAI API error: {response.status}")
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8') if e.fp else str(e)
                raise Exception(f"OpenAI API error: {e.code} - {error_msg}")
                
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

async def extract_report_sections(transcript: str) -> Dict[str, str]:
    """Extract report sections from transcript using GPT"""
    try:
        prompt = f"""
You are an expert at organizing training post-OST reports. Please analyze the following transcript from a training session and extract information for each of the report sections below. If a section is not mentioned in the transcript, return an empty string for that field.

IMPORTANT INSTRUCTIONS:
- Use direct quotes from the transcription whenever possible
- Be as detailed as possible - include all relevant information mentioned
- List each point using markdown numbered format: [1], [2], [3], etc.
- Preserve exact numbers, names, and specific details from the transcript
- Include context and background information when mentioned
- Do not summarize - provide comprehensive, detailed extraction

Transcript:
{transcript}

Please organize the information into these sections and return ONLY a valid JSON object with these exact keys:

{{
    "postost_wins": "WINS/CELEBRATIONS - Notable successes, achievements, improvements, positive outcomes - use [1], [2], [3] format",
    "client_goals": "STAT/GOAL REVIEW - Baseline numbers, goals, targets, metrics, incentives in place - use [1], [2], [3] format",
    "postost_holdbacks": "BIGGEST BARRIERS OR ISSUES CLIENT IS STRUGGLING WITH - Problems, challenges, obstacles, concerns - use [1], [2], [3] format",
    "human_capital": "HUMAN CAPITAL - Staffing levels, team members, capacity, hiring needs - use [1], [2], [3] format",
    "marketing": "MARKETING - Marketing efforts, campaigns, lead generation, promotional activities - use [1], [2], [3] format",
    "space_and_equipment": "SPACE AND EQUIPMENT - Physical space, operatories, equipment, capacity constraints - use [1], [2], [3] format",
    "clinical_duplication": "CLINICAL DUPLICATION - Provider capacity, clinical workflow, scheduling efficiency - use [1], [2], [3] format",
    "financial": "FINANCIAL - Financial status, budget considerations, payment systems - use [1], [2], [3] format",
    "upcoming_milestones": "UPCOMING MILESTONES - Future goals, renewal dates, planned trainings, important dates - use [1], [2], [3] format",
    "homework_doctor": "HOMEWORK FOR DOCTOR - Action items, tasks, commitments for the doctor - use [1], [2], [3] format",
    "homework_trainer": "HOMEWORK FOR TRAINER - Follow-up actions, tasks for the trainer - use [1], [2], [3] format",
    "next_steps": "NEXT STEPS - Future actions, planned activities, implementation steps - use [1], [2], [3] format"
}}

For each field, extract ALL relevant information from the transcript using [1], [2], [3] numbered points. Use direct quotes where applicable and be as comprehensive as possible. If no information is available for a field, use an empty string.
"""

        # Parse the JSON response
        import json
        
        if not api_available:
            # Demo mode - return sample data
            report_data = {
                "postost_wins": "[1] Successfully implemented new patient scheduling system [2] Increased patient satisfaction scores by 15% [3] Team completed advanced training certification",
                "client_goals": "[1] Target: Increase monthly revenue to $50,000 [2] Goal: See 200 patients per month [3] Metric: Achieve 95% appointment adherence rate",
                "postost_holdbacks": "[1] Limited operatory space constraining patient flow [2] Staffing shortage affecting appointment capacity [3] Insurance processing delays impacting cash flow",
                "human_capital": "[1] Current team: 2 hygienists, 1 assistant [2] Need to hire: 1 additional dental assistant [3] Training required: New software system for front desk",
                "marketing": "[1] Social media campaign running on Facebook and Instagram [2] Referral program showing 20% increase in new patients [3] Google Ads campaign needs optimization",
                "space_and_equipment": "[1] 4 operatories currently operational [2] Need new digital X-ray equipment [3] Waiting room renovation planned for next quarter",
                "clinical_duplication": "[1] Provider seeing 25-30 patients per day [2] Hygienist capacity at 8-10 patients per day [3] Same-day emergency slots available",
                "financial": "[1] Monthly overhead: $35,000 [2] Collections rate: 92% [3] Insurance reimbursement average: 85%",
                "upcoming_milestones": "[1] Quarterly review meeting on March 15th [2] New equipment installation scheduled for April [3] Staff training workshop planned for May",
                "homework_doctor": "[1] Review treatment plans for comprehensive cases [2] Follow up with specialist referrals [3] Complete continuing education requirements",
                "homework_trainer": "[1] Schedule follow-up coaching session [2] Provide additional resources for team training [3] Monitor implementation of new protocols",
                "next_steps": "[1] Implement new scheduling protocols [2] Begin recruitment for additional staff [3] Finalize equipment purchase decisions"
            }
        else:
            # Real OpenAI processing with direct HTTP request using urllib
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a professional assistant that extracts structured information from training session transcripts. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            
            # Create request with urllib
            req = urllib.request.Request(
                OPENAI_CHAT_URL,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    if response.status == 200:
                        response_data = json.loads(response.read().decode('utf-8'))
                        report_data = json.loads(response_data["choices"][0]["message"]["content"])
                    else:
                        raise Exception(f"OpenAI API error: {response.status}")
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8') if e.fp else str(e)
                raise Exception(f"OpenAI API error: {e.code} - {error_msg}")
        
        # Validate that all expected keys are present
        for key in REPORT_FIELDS.keys():
            if key not in report_data:
                report_data[key] = ""
        
        # Format the text with proper line breaks and HTML tags
        report_data = format_report_text(report_data)
        
        return report_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response as JSON: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        logger.error(f"GPT extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
