from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
AUDIO_DIR = BASE_DIR / "Audio"
TRANSCRIPTION_DIR = BASE_DIR / "Transcription"

DATA_FILE = BASE_DIR / "data.csv"

#うまくいっていないのでutils/output_to_wiki.pyにBASE_URLを直接書いている
#BASE_URL = "http://133.15.57.8/api"

class AppState:
    STATUS = "idle"
