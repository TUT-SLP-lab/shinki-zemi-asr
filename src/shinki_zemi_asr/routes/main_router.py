from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import select

from src.shinki_zemi_asr.config import TEMPLATES_DIR, AppState, TRANSCRIPTION_DIR
from src.shinki_zemi_asr.utils.file_operations import save_uploaded_file, read_transcription, format_transcript
from src.shinki_zemi_asr.services.transcriber import process_audio_file
from src.shinki_zemi_asr.utils.output_to_wiki import output_to_wiki
from src.shinki_zemi_asr.database import SessionDep
from src.shinki_zemi_asr.models.schemas import  ASRRecording,  ASRRecordingCreate,  ProcessRecordingRequest

router = APIRouter()

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", response_class=HTMLResponse)
async def get_root(request: Request, session: SessionDep):
    """Render the homepage with data from the CSV file."""
    data_content = list(session.exec(select(ASRRecording)).all())

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
    session: SessionDep,
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
        asr_create = ASRRecordingCreate(
                presenter_name=presenter_name,
                recording_date=date,
                start_time=start_time,
                end_time=end_time,
                file_path=str(file_path),
            )
        asr_recording = ASRRecording.model_validate(asr_create)
        session.add(asr_recording)
        session.commit()
        session.refresh(asr_recording)

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
async def start_processing(data: ProcessRecordingRequest, background_tasks: BackgroundTasks, session : SessionDep):
    """Start processing an audio file in the background."""
    recording = session.get(ASRRecording, data.recording_id)

    if not recording:
        raise HTTPException(
            status_code=404,
            detail=f"Recording with ID {data.recording_id} not found"
        )

    background_tasks.add_task(process_audio_file, recording_id=recording.id)

    recording.is_processed = True
    session.commit()

    return JSONResponse(
        status_code=200,
        content={
            "message": "Started Processing Successfully",
            "recording_id": data.recording_id
        }
    )

@router.get("/get-transcript", response_class=JSONResponse)
async def get_transcript(recording_id: int, session: SessionDep):
    """Get the transcription for a processed audio file."""
    recording = session.get(ASRRecording, recording_id)
    if not recording:
        raise HTTPException(
            status_code=404,
            detail=f"Recording with ID {recording_id} not found"
        )
    if not recording.is_processed:
        raise HTTPException(
            status_code=400,
            detail=f"Recording with ID {recording_id} has not been processed yet"
        )

    try:
        transcript_text = read_transcription(recording.file_path)
        return JSONResponse(
            status_code=200,
            content={
                "transcript": transcript_text,
            }
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Transcript for {recording.file_path} not found"
        )

@router.get("/post-transcript")
async def post_transcript(recording_id: int, session: SessionDep):
    """Post transcription to Lab Wiki for processed audio file path."""
    recording = session.get(ASRRecording, recording_id)
    if not recording:
        raise HTTPException(
            status_code=404,
            detail=f"Recording with ID {recording_id} not found"
        )
    if not recording.is_processed:
        raise HTTPException(
            status_code=400,
            detail=f"Recording with ID {recording_id} has not been processed yet"
        )

    transcript_text = read_transcription(recording.file_path)
    formatted_transcript = format_transcript(transcript_text)

    transcript_path = TRANSCRIPTION_DIR / f"{Path(recording.file_path).stem}.json"

    output_to_wiki(formatted_transcript, str(transcript_path))
    return formatted_transcript
