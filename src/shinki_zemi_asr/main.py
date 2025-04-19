import os
from fastapi import FastAPI

from src.shinki_zemi_asr.config import AUDIO_DIR, TRANSCRIPTION_DIR
from src.shinki_zemi_asr.database.csv_operations import initialize_data_file
from src.shinki_zemi_asr.routes.main_router import router as recording_router

# Create required directories
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

# Initialize the data file if it doesn't exist
initialize_data_file()

# Create FastAPI application
app = FastAPI(title="Audio Transcription Service")

# Include routers
app.include_router(recording_router)

