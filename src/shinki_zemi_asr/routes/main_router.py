from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from src.shinki_zemi_asr.config import TEMPLATES_DIR, AppState, TRANSCRIPTION_DIR
from src.shinki_zemi_asr.models.schemas import PathData
from src.shinki_zemi_asr.database.csv_operations import read_data_file, add_recording_data
from src.shinki_zemi_asr.utils.file_operations import save_uploaded_file, read_transcription, format_transcript
from src.shinki_zemi_asr.services.transcriber import process_audio_file
from src.shinki_zemi_asr.utils.output_to_wiki import output_to_wiki


router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    """Render the homepage with data from the CSV file."""
    data_content = read_data_file()
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "data_content": data_content, 
            "status": AppState.STATUS
        }
    )

@router.post("/upload-recording", response_class=JSONResponse)
async def upload_recording(
    presenter_name: str = Form(...),
    date: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    audio_file: UploadFile = File(...),
):
    """Upload a recording file and add its metadata to the database."""
    try:
        if audio_file.filename is None:
            raise HTTPException(status_code=400, detail="No file_name provided in uploaded audio file")
        
        # Save the uploaded file
        file_path = save_uploaded_file(audio_file, audio_file.filename)
        
        # Add recording data to the database
        add_recording_data(presenter_name, date, start_time, end_time, str(file_path))
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Recording uploaded successfully",
                "file_path": str(file_path)
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error uploading recording: {str(e)}"}
        )

@router.post("/start-processing", response_class=JSONResponse)
async def start_processing(data: PathData, background_tasks: BackgroundTasks):
    """Start processing an audio file in the background."""
    background_tasks.add_task(process_audio_file, audio_file_path=data.process_path)
    
    return JSONResponse(
        status_code=200,
        content={
            "message": "Started Processing Successfully",
            "process_path": data.process_path
        }
    )

@router.get("/get-transcript")
async def get_transcript(audio_file_path: str):
    """Get the transcription for a processed audio file."""
    try:
        transcript_text = read_transcription(audio_file_path)
        return transcript_text
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Transcript for {audio_file_path} not found"
        )

@router.get("/post-transcript")
async def post_transcript(audio_file_path: str):
    """Post transcription to Lab Wiki for processed audio file path."""
    try:
        transcript_text = read_transcription(audio_file_path)
        formatted_transcript = format_transcript(transcript_text)

        transcript_path = TRANSCRIPTION_DIR / f"{Path(audio_file_path).stem}.json"

        output_to_wiki(formatted_transcript, str(transcript_path))
        return formatted_transcript
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Transcript for {audio_file_path} not found"
        )

