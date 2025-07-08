"""
Celery Tasks for processing Voice Calls
directly within the Flask Application
"""
from celery_app import celery_app
from models import db, Call
import os
from datetime import datetime
from voice_utils import text_to_speech, prepare_audio_for_sip, execute_sip_call, create_pjsua_command
import logging

# Configure logging
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def tts_and_call_task(self, call_id):
    """
    Task to handle Text-to-Speech conversion and SIP call execution
    """
    logger.info(f"Starting task for call_id: {call_id}")
    
    # Import Flask app for database context from celery_app
    try:
        from celery_app import flask_app as app
    except ImportError as e:
        logger.error(f"Could not import Flask app from celery_app: {e}")
        return 'Error: Flask app not available for database context'
    
    with app.app_context():
        try:
            # Fetch call details from the database
            call = Call.query.get(call_id)
            if not call:
                logger.error(f"Call not found: {call_id}")
                return 'Call not found'

            logger.info(f"Processing call from {call.from_number} to {call.to_number}")
            call.status = 'processing'
            call.started_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Updated call status to processing")

            try:
                # Create audio file
                temp_dir = os.path.join(os.getcwd(), 'temp_audio')
                os.makedirs(temp_dir, exist_ok=True)
                audio_file_path = os.path.join(temp_dir, f"call_{call_id}.mp3")
                logger.info(f"Created temp directory: {temp_dir}")

                # Convert text to speech
                logger.info(f"Starting TTS conversion for text: {call.text[:50]}...")
                if not text_to_speech(call.text, audio_file_path):
                    raise Exception("Text-to-speech conversion failed")
                logger.info(f"TTS conversion successful: {audio_file_path}")

                # Prepare audio for SIP
                logger.info(f"Preparing audio for SIP")
                wav_file = prepare_audio_for_sip(audio_file_path)
                logger.info(f"Audio prepared: {wav_file}")

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
                
                logger.info(f"SIP Config: {call.from_number} -> {call.to_number} via {call_config['sip_server']}")
                
                # Create PJSUA command and execute call
                pjsua_cmd = create_pjsua_command(call_config, wav_file)
                logger.info(f"Executing SIP call with PJSUA")
                execute_sip_call(pjsua_cmd, call_config)
                logger.info(f"SIP call execution completed")

                call.status = 'completed'
                call.completed_at = datetime.utcnow()
                call.audio_file_path = audio_file_path
                db.session.commit()
                logger.info(f"Call {call_id} marked as completed")
                return 'Call completed'

            except Exception as e:
                logger.error(f"Task execution failed for call {call_id}: {str(e)}")
                call.status = 'failed'
                call.error_message = str(e)
                db.session.commit()
                return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Database operation failed for call {call_id}: {str(e)}")
            return f"Database Error: {str(e)}"
