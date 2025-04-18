import json
import shutil
from pathlib import Path
from fastapi import UploadFile

from src.shinki_zemi_asr.config import AUDIO_DIR, TRANSCRIPTION_DIR

def save_uploaded_file(file: UploadFile, file_name: str) -> Path:
    """Save an uploaded file to the audio directory."""
    file_path = AUDIO_DIR / file_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def save_transcription(audio_file_path: str, transcript_data: list) -> Path:
    """Save transcription data to a JSON file."""
    transcription_path = TRANSCRIPTION_DIR / f"{Path(audio_file_path).stem}.json"
    
    with open(transcription_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=2)
    
    return transcription_path

def read_transcription(audio_file_path: str) -> str:
    """Read transcription data from a JSON file."""
    transcript_path = TRANSCRIPTION_DIR / f"{Path(audio_file_path).stem}.json"
    
    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    return text

def convert_tuple_to_list(obj):
    """Convert nested tuples to lists for JSON serialization."""
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, list):
        return [convert_tuple_to_list(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convert_tuple_to_list(v) for k, v in obj.items()}
    return obj