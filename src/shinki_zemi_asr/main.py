from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import csv
import shutil
from pydantic import BaseModel
import json

from pathlib import Path

from src.shinki_zemi_asr.asr import ASRModel

app = FastAPI()

STATUS = "idle"

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

AUDIO_DIR = BASE_DIR / "Audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

TRANSCRIPTION_DIR = BASE_DIR / "Transcription"
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

DATA_FILE = BASE_DIR / "data.csv"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["presenter_name", "date", "start_time", "end_time", "file_path", "is_processed", "is_uploaded",
                         "is_deleted"])

templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    data_content = read_data_file()

    return templates.TemplateResponse(
        request=request, name="index.html", context={"data_content": data_content, "status": STATUS}
    )


def read_data_file() -> list[list[str]]:
    result = []

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader, None)
        for row in csv_reader:
            result.append(row)
    return result


@app.post("/upload-recording", response_class=JSONResponse)
async def upload_recording(
        presenter_name: str = Form(...),
        date: str = Form(...),
        start_time: str = Form(...),
        end_time: str = Form(...),
        audio_file: UploadFile = File(...),
):
    try:
        # file should already be in the format
        # f"{presenter_name}_{date}_{start_time}_{end_time}.wav"

        if audio_file.filename is None:
            raise HTTPException(status_code=400, detail="No file_name provided in uploaded audio file")

        file_path = AUDIO_DIR / audio_file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        with open(DATA_FILE, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([presenter_name, date, start_time, end_time, file_path, False, False, False])

        return JSONResponse(
            status_code=200,
            content={"message": "Recording uploaded successfully",
                     "file_path": str(file_path)
                     }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error uploading recording: {str(e)}"}

        )

class PathData(BaseModel):
    process_path: str


@app.post("/start-processing", response_class=JSONResponse)
async def start_processing(data: PathData, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_path, audio_file_path=data.process_path)
    return JSONResponse(status_code=200,
                        content={
                            "message": "Started Proceessing Successfully",
                            "process_path": data.process_path
                        })


def process_path(audio_file_path: str):
    print(f"Received path: {audio_file_path}")

    STATUS = "processing" # TODO: This is making a new local variable now

    asr_model = ASRModel()
    transcript = asr_model.transcribe(audio_file_path)
    converted_transcript = convert_tuple_to_list(transcript)
    # print(transcript)

    transcription_path = TRANSCRIPTION_DIR / f"{Path(audio_file_path).stem}.json"

    with open(transcription_path, "w", encoding="utf-8") as f:
        json.dump(converted_transcript, f, ensure_ascii=False, indent=2)

    # TODO: Update is_processed status

    print("finished")


    STATUS = "idle"

def convert_tuple_to_list(obj):
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, list):
        return [convert_tuple_to_list(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_tuple_to_list(v) for k, v in obj.items()}
    return obj

@app.get("/get-transcript")
async def get_transcript(audio_file_path : str):
    # TODO: set transcript path in the database
    transcript_path = TRANSCRIPTION_DIR / f"{Path(audio_file_path).stem}.json"
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()

    return text




