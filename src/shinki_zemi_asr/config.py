from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
AUDIO_DIR = BASE_DIR / "Audio"
TRANSCRIPTION_DIR = BASE_DIR / "Transcription"

DATA_FILE = BASE_DIR / "data.csv"

class AppState:
    STATUS = "idle"
