from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path
from dotenv import load_dotenv
import openai
from typing import Dict, Any
import logging

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

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
        
        # Step 1: Transcribe audio with Whisper
        transcript = await transcribe_audio(temp_file_path)
        logger.info(f"Transcription completed: {len(transcript)} characters")
        
        # Step 2: Extract report sections with GPT
        report_data = await extract_report_sections(transcript)
        logger.info("Report sections extracted successfully")
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return JSONResponse(content={
            "success": True,
            "transcript": transcript,
            "report_data": report_data,
            "message": "Audio processed successfully"
        })
        
    except HTTPException:
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

async def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file using OpenAI Whisper API"""
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

async def extract_report_sections(transcript: str) -> Dict[str, str]:
    """Extract report sections from transcript using GPT"""
    try:
        prompt = f"""
You are an expert at organizing training post-OST reports. Please analyze the following transcript from a training session and extract information for each of the report sections below. If a section is not mentioned in the transcript, return an empty string for that field.

Transcript:
{transcript}

Please organize the information into these sections and return ONLY a valid JSON object with these exact keys:

{{
    "postost_wins": "WINS/CELEBRATIONS - Notable successes, achievements, improvements, positive outcomes",
    "client_goals": "STAT/GOAL REVIEW - Baseline numbers, goals, targets, metrics, incentives in place",
    "postost_holdbacks": "BIGGEST BARRIERS OR ISSUES CLIENT IS STRUGGLING WITH - Problems, challenges, obstacles, concerns",
    "human_capital": "HUMAN CAPITAL - Staffing levels, team members, capacity, hiring needs",
    "marketing": "MARKETING - Marketing efforts, campaigns, lead generation, promotional activities",
    "space_and_equipment": "SPACE AND EQUIPMENT - Physical space, operatories, equipment, capacity constraints",
    "clinical_duplication": "CLINICAL DUPLICATION - Provider capacity, clinical workflow, scheduling efficiency",
    "financial": "FINANCIAL - Financial status, budget considerations, payment systems",
    "upcoming_milestones": "UPCOMING MILESTONES - Future goals, renewal dates, planned trainings, important dates",
    "homework_doctor": "HOMEWORK FOR DOCTOR - Action items, tasks, commitments for the doctor",
    "homework_trainer": "HOMEWORK FOR TRAINER - Follow-up actions, tasks for the trainer",
    "next_steps": "NEXT STEPS - Future actions, planned activities, implementation steps"
}}

Extract relevant information for each section from the transcript. Be concise but include important details. Return only the JSON object.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional assistant that extracts structured information from training session transcripts. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Parse the JSON response
        import json
        report_data = json.loads(response.choices[0].message.content)
        
        # Validate that all expected keys are present
        for key in REPORT_FIELDS.keys():
            if key not in report_data:
                report_data[key] = ""
        
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
