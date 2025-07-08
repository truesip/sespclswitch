"""
Celery Tasks for processing Voice Calls
directly within the Flask Application
"""
from celery_app import celery_app
from models import db, Call
import os
from datetime import datetime
from voice_utils import text_to_speech, prepare_audio_for_sip, execute_sip_call, create_pjsua_command

@celery_app.task(bind=True)
def tts_and_call_task(self, call_id):
    """
    Task to handle Text-to-Speech conversion and SIP call execution
    """
    # Import Flask app for database context
    try:
        from app import app
    except ImportError:
        return 'Error: Flask app not available for database context'
    
    with app.app_context():
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
                "to": call.to_number,
                "from": call.from_number,
                "audio_file": wav_file,
                "sip_server": os.getenv("SIP_TRUNK_IP"),
                "sip_port": os.getenv("SIP_TRUNK_PORT"),
                "username": os.getenv("SIP_USERNAME"),
                "password": os.getenv("SIP_PASSWORD")
            }
            
            # Create PJSUA command and execute call
            pjsua_cmd = create_pjsua_command(call_config, wav_file)
            execute_sip_call(pjsua_cmd, call_config)

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
