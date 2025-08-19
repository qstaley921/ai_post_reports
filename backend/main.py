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

# Initialize OpenAI client with error handling
openai_client = None
try:
    if OPENAI_API_KEY:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized successfully")
    else:
        print("⚠️  OPENAI_API_KEY not found - demo mode will be used")
except Exception as e:
    print(f"❌ Failed to initialize OpenAI client: {e}")
    print("🔄 Falling back to demo mode")
    openai_client = None

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
        if not openai_client:
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

IMPORTANT INSTRUCTIONS:
- Use direct quotes from the transcription whenever possible
- Be as detailed as possible - include all relevant information mentioned
- List each point using numbered format (1., 2., 3., etc.)
- Preserve exact numbers, names, and specific details from the transcript
- Include context and background information when mentioned
- Do not summarize - provide comprehensive, detailed extraction

Transcript:
{transcript}

Please organize the information into these sections and return ONLY a valid JSON object with these exact keys:

{{
    "postost_wins": "WINS/CELEBRATIONS - Notable successes, achievements, improvements, positive outcomes - use numbered list format",
    "client_goals": "STAT/GOAL REVIEW - Baseline numbers, goals, targets, metrics, incentives in place - use numbered list format",
    "postost_holdbacks": "BIGGEST BARRIERS OR ISSUES CLIENT IS STRUGGLING WITH - Problems, challenges, obstacles, concerns - use numbered list format",
    "human_capital": "HUMAN CAPITAL - Staffing levels, team members, capacity, hiring needs - use numbered list format",
    "marketing": "MARKETING - Marketing efforts, campaigns, lead generation, promotional activities - use numbered list format",
    "space_and_equipment": "SPACE AND EQUIPMENT - Physical space, operatories, equipment, capacity constraints - use numbered list format",
    "clinical_duplication": "CLINICAL DUPLICATION - Provider capacity, clinical workflow, scheduling efficiency - use numbered list format",
    "financial": "FINANCIAL - Financial status, budget considerations, payment systems - use numbered list format",
    "upcoming_milestones": "UPCOMING MILESTONES - Future goals, renewal dates, planned trainings, important dates - use numbered list format",
    "homework_doctor": "HOMEWORK FOR DOCTOR - Action items, tasks, commitments for the doctor - use numbered list format",
    "homework_trainer": "HOMEWORK FOR TRAINER - Follow-up actions, tasks for the trainer - use numbered list format",
    "next_steps": "NEXT STEPS - Future actions, planned activities, implementation steps - use numbered list format"
}}

For each field, extract ALL relevant information from the transcript using numbered points. Use direct quotes where applicable and be as comprehensive as possible. If no information is available for a field, use an empty string.
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
        
        if not openai_client:
            # Demo mode - return sample data
            report_data = {
                "postost_wins": "1. Successfully implemented new patient scheduling system\n2. Increased patient satisfaction scores by 15%\n3. Team completed advanced training certification",
                "client_goals": "1. Target: Increase monthly revenue to $50,000\n2. Goal: See 200 patients per month\n3. Metric: Achieve 95% appointment adherence rate",
                "postost_holdbacks": "1. Limited operatory space constraining patient flow\n2. Staffing shortage affecting appointment capacity\n3. Insurance processing delays impacting cash flow",
                "human_capital": "1. Current team: 2 hygienists, 1 assistant\n2. Need to hire: 1 additional dental assistant\n3. Training required: New software system for front desk",
                "marketing": "1. Social media campaign running on Facebook and Instagram\n2. Referral program showing 20% increase in new patients\n3. Google Ads campaign needs optimization",
                "space_and_equipment": "1. 4 operatories currently operational\n2. Need new digital X-ray equipment\n3. Waiting room renovation planned for next quarter",
                "clinical_duplication": "1. Provider seeing 25-30 patients per day\n2. Hygienist capacity at 8-10 patients per day\n3. Same-day emergency slots available",
                "financial": "1. Monthly overhead: $35,000\n2. Collections rate: 92%\n3. Insurance reimbursement average: 85%",
                "upcoming_milestones": "1. Quarterly review meeting on March 15th\n2. New equipment installation scheduled for April\n3. Staff training workshop planned for May",
                "homework_doctor": "1. Review treatment plans for comprehensive cases\n2. Follow up with specialist referrals\n3. Complete continuing education requirements",
                "homework_trainer": "1. Schedule follow-up coaching session\n2. Provide additional resources for team training\n3. Monitor implementation of new protocols",
                "next_steps": "1. Implement new scheduling protocols\n2. Begin recruitment for additional staff\n3. Finalize equipment purchase decisions"
            }
        else:
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
