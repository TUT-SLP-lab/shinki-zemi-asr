from src.shinki_zemi_asr.asr import ASRModel
from src.shinki_zemi_asr.utils.file_operations import convert_tuple_to_list, save_transcription
from src.shinki_zemi_asr.utils.output_to_wiki import output_to_wiki
from src.shinki_zemi_asr.database.csv_operations import update_processing_status
from src.shinki_zemi_asr.config import AppState

def process_audio_file(audio_file_path: str):
    """Process an audio file using the ASR model and save the transcript."""
    print(f"Processing file: {audio_file_path}")
    
    # Update application state
    AppState.STATUS = "processing"
    
    try:
        # Initialize ASR model and transcribe
        asr_model = ASRModel()
        transcript = asr_model.transcribe(audio_file_path)
        
        # Convert transcript data for JSON serialization
        converted_transcript = convert_tuple_to_list(transcript)
        
        # Save transcription to file
        filepath = save_transcription(audio_file_path, converted_transcript)
        
        # Output to wiki
        output_to_wiki(converted_transcript, filepath)

        # Update processing status in the database
        update_processing_status(audio_file_path, True)
        
        print(f"Finished processing: {audio_file_path}")
    except Exception as e:
        print(f"Error processing audio file: {str(e)}")
    finally:
        # Reset application state
        AppState.STATUS = "idle"