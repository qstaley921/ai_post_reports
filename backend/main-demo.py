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
import asyncio

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
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"  # Enable demo mode by default

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize OpenAI client only if not in demo mode and API key exists
openai_client = None
if not DEMO_MODE and OPENAI_API_KEY:
    try:
        openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"OpenAI client initialization failed: {e}. Falling back to demo mode.")
        DEMO_MODE = True

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
    "best_hotel_1": "Best Hotel in Area 1",
    "other_tips_for_area": "Other Tips for the Area"
}

# Demo content for testing
DEMO_TRANSCRIPT = """
This is a demo transcript from a training session. Today we had some great wins with the team - Preston Location increased their baseline from 30 to 32 patients, which is a 20% increase since starting. The Raleigh location also added new front desk team members including Rachel, who has HR management experience.

For goals and statistics, Preston has a baseline of 32 with a goal of 35 new patients. Incentives are in place, and Dr. Kashyap provides an extra $100 incentive for first-time certifications at the Raleigh location.

The biggest barrier we're facing is that Craig, the office manager, wasn't as engaged as hoped. He was splitting time between Doug's PP training and this 5-Star training. We didn't get proper commitments at the end because he wasn't present for the wrap-up.

For human capital, they have enough team members to handle current capacity. Marketing is managed by Paola, and they recently had a successful Invisalign open house with 21 out of 21 patients attending and starting treatment.

Space-wise, Raleigh has 5 operatories but needs renovation and more space. They're looking to purchase the building to add 20+ operatories. Preston has 7 operatories with adequate space.

Financially, everything appears to be in order with no apparent barriers. Their renewal date is at the end of the year, and we're planning trainings into Q1 of 2026.

For hotels in the area, I don't recommend the Townplace as it's quite run down. The area has good restaurants and the training location is easily accessible.
"""

@app.get("/")
async def root():
    """Health check endpoint"""
    mode = "Demo Mode" if DEMO_MODE else "Production Mode"
    return {"message": "AI Post Report API is running", "mode": mode}

@app.post("/api/post-report/audio")
async def process_audio(file: UploadFile = File(...)):
    """
    Process uploaded audio file:
    1. Validate and save file
    2. Transcribe with Whisper (or use demo content)
    3. Extract report sections with GPT (or use demo extraction)
    """
    temp_file_path = None
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
            )
        
        # Save temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
        temp_file_path = temp_file.name
        temp_file.write(content)
        temp_file.close()
        
        # Step 1: Transcribe audio
        if DEMO_MODE:
            logger.info("Using demo mode - simulating transcription")
            await asyncio.sleep(1)  # Simulate processing time
            transcript = DEMO_TRANSCRIPT
        else:
            transcript = await transcribe_audio(temp_file_path)
        
        # Step 2: Extract report sections
        if DEMO_MODE:
            logger.info("Using demo mode - simulating report extraction")
            await asyncio.sleep(1)  # Simulate processing time
            report_data = get_demo_report_data()
        else:
            report_data = await extract_report_sections(transcript)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Audio processed successfully",
            "transcript": transcript,
            "report_data": report_data,
            "mode": "demo" if DEMO_MODE else "production"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

def get_demo_report_data() -> Dict[str, str]:
    """Return demo report data for testing"""
    return {
        "postost_wins": "1. Preston Location: Increased baseline since 2023; 30 → 32. +20% since starting.\n2. Raleigh Location: New front desk team members including Rachel (former HR manager) who did great in role-playing and engaging.\n3. Successful Invisalign open house with 21/21 patients arriving and starting treatment in a single day - majorly impressive achievement.",
        
        "client_goals": "1. Preston: NP Baseline 32; NP Goal 35. No referral goal currently set.\n2. Incentives are in place across both locations.\n3. Dr. Kashyap gives an extra $100 incentive when team members first certify (only at the Raleigh location).\n4. Raleigh numbers were not available during training but will be updated when confirmed with Trisha.",
        
        "postost_holdbacks": "1. Craig, their office manager, was not as engaged as hoped. He alternated between Doug's PP training and this 5-Star training.\n2. We did not get commitments from Craig at the end of the day because he was not present for the wrap-up session.\n3. Trainer doesn't feel good about the implementation due to lack of management engagement.\n4. Both doctors confirmed their teams should complete checklists within the next 30 days and schedule one-on-one role-play calls for imperfect certifications.",
        
        "human_capital": "1. Set - they have enough team members to handle current capacity.\n2. Preston: Two new team members: Yessica and Tiffany; Tiffany was performing better, it was only Jessica's second day.\n3. Raleigh: Expanded from only Trisha to include Rachael, Trisha, and Latoya.\n4. Rachel is a former HR manager at a hospital and did a great job role-playing and engaging during training.",
        
        "marketing": "1. Paola manages their marketing operations.\n2. They recently had a stellar Invisalign open-house with a special promotion.\n3. 21/21 patients arrived and started treatment in a single day - majorly impressive result that exceeded expectations.",
        
        "space_and_equipment": "1. Raleigh: 5 Ops; not enough space and not renovated; looking to purchase the building with three other tenants to add 20+ ops. This likely won't happen within the next year. Currently scheduling within 3 weeks.\n2. Preston: 7 ops; enough space available; scheduling within 1 week turnaround time.",
        
        "clinical_duplication": "1. Limiting factor because North Carolina state regulations limit two hygienists per doctor.\n2. They currently have more hygiene capacity than doctor capacity, which is limiting their hygiene growth potential.\n3. This regulatory constraint affects their ability to maximize hygiene revenue.",
        
        "financial": "1. Appears to be in order with no apparent barriers identified.\n2. Nothing apparently standing in the way of their financial operations or growth plans.",
        
        "upcoming_milestones": "1. Renewal date at the end of the year (November 14, 2025).\n2. Planning trainings into Q1 of 2026; appears to be valid timeline for renewal.\n3. Teams should complete their checklists within the next 30 days.\n4. One-on-one role-play calls to be scheduled for any team members not receiving perfect certifications.",
        
        "best_hotel_1": "1. I do not recommend the Townplace, which is quite dilapidated, described as 'like a dirty sock dressed up with Febreeze'.\n2. Trainer suggests looking for alternative accommodations in the area.",
        
        "other_tips_for_area": "1. The training location is easily accessible with good parking availability.\n2. Several restaurant options nearby for meals during training breaks.\n3. Area is generally convenient for training logistics and attendee accessibility."
    }

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
    "postost_wins": "Wins, celebrations, and positive outcomes - use numbered list format",
    "client_goals": "Statistics, goals, and performance metrics - use numbered list format", 
    "postost_holdbacks": "Barriers, challenges, and issues - use numbered list format",
    "human_capital": "Team capacity, staffing, and human resources - use numbered list format",
    "marketing": "Marketing activities and promotional efforts - use numbered list format",
    "space_and_equipment": "Physical space and equipment status - use numbered list format",
    "clinical_duplication": "Clinical processes and standardization - use numbered list format",
    "financial": "Financial status and considerations - use numbered list format",
    "upcoming_milestones": "Future milestones and important dates - use numbered list format",
    "best_hotel_1": "Hotel recommendations in the area - use numbered list format",
    "other_tips_for_area": "Local tips and recommendations - use numbered list format"
}}

For each field, extract ALL relevant information from the transcript using numbered points. Use direct quotes where applicable and be as comprehensive as possible. If no information is available for a field, use an empty string.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at extracting structured information from training session transcripts. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Extract JSON from response
        content = response.choices[0].message.content.strip()
        
        # Parse JSON
        import json
        try:
            report_data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                report_data = json.loads(json_content)
            else:
                raise ValueError("Invalid JSON response from GPT")
        
        return report_data
        
    except Exception as e:
        logger.error(f"Report extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report extraction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
