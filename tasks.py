"""
Celery Tasks for processing Voice Calls
directly within the Flask Application
"""
from app import celery, prepare_audio_for_sip, execute_sip_call, text_to_speech
from models import db, Call
import os
from datetime import datetime

@celery.task(bind=True)
def tts_and_call_task(self, call_id):
    """
    Task to handle Text-to-Speech conversion and SIP call execution
    """
    # Fetch call details from the database
    call = Call.query.get(call_id)
    if not call:
        return 'Call not found'

    call.status = 'processing'
    call.started_at = datetime.utcnow()
    db.session.commit()

    try:
        # Create audio file
        temp_dir = os.path.join(os.getcwd(), 'temp_audio')
        os.makedirs(temp_dir, exist_ok=True)
        audio_file_path = os.path.join(temp_dir, f"call_{call_id}.mp3")

        # Convert text to speech
        if not text_to_speech(call.text, audio_file_path):
            raise Exception("Text-to-speech conversion failed")

        # Prepare audio for SIP
        wav_file = prepare_audio_for_sip(audio_file_path)

        # Execute SIP Call
        call_config = {
            "to_number": call.to_number,
            "from_number": call.from_number,
            "audio_file": wav_file,
            "sip_server": os.getenv("SIP_TRUNK_IP"),
            "sip_port": os.getenv("SIP_TRUNK_PORT"),
            "username": os.getenv("SIP_USERNAME"),
            "password": os.getenv("SIP_PASSWORD")
        }
        execute_sip_call(wav_file, call_config)

        call.status = 'completed'
        call.completed_at = datetime.utcnow()
        call.audio_file_path = audio_file_path
        db.session.commit()
        return 'Call completed'

    except Exception as e:
        call.status = 'failed'
        call.error_message = str(e)
        db.session.commit()
        return f"Error: {str(e)}"
