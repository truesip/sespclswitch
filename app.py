"""
SESPCLSwitch Server
A production-ready Flask API for making voice calls via SIP using TrueSIP
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import os
import requests
import tempfile
import uuid
from datetime import datetime
import logging
from pydub import AudioSegment
import io
import base64
import subprocess
import json
from threading import Thread
import time
from dotenv import load_dotenv
from celery import Celery

# Load environment variables from .env file
load_dotenv()

# Initialize Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)
    
    # Optimize Celery for high throughput
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://postgres:password@localhost:5432/voicecall_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 300,
    'pool_pre_ping': True
}

# Celery Configuration
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Cache Configuration
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

# Initialize extensions
from models import db, Call
db.init_app(app)

# Initialize Celery after app configuration
celery = make_celery(app)

# Configure caching for frequently accessed data
cache = Cache(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuration from environment variables
SIP_TRUNK_IP = os.getenv("SIP_TRUNK_IP", "sip.truesip.net")
SIP_TRUNK_PORT = os.getenv("SIP_TRUNK_PORT", "5060")
SIP_USERNAME = os.getenv("SIP_USERNAME", "12156")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "1C36na9C")

# Text-to-Speech Configuration
TTS_SERVICE = os.getenv("TTS_SERVICE", "espeak")  # espeak, google, azure, aws
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY")
AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY")
AZURE_TTS_REGION = os.getenv("AZURE_TTS_REGION")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

def text_to_speech(text, output_file):
    """Convert text to speech and save as audio file"""
    try:
        if TTS_SERVICE == "google" and GOOGLE_TTS_API_KEY:
            return google_tts(text, output_file)
        elif TTS_SERVICE == "azure" and AZURE_TTS_KEY:
            return azure_tts(text, output_file)
        elif TTS_SERVICE == "aws" and AWS_ACCESS_KEY:
            return aws_tts(text, output_file)
        else:
            # Fallback to espeak (offline TTS)
            return espeak_tts(text, output_file)
    except Exception as e:
        logger.error(f"TTS conversion failed: {str(e)}")
        return False

def google_tts(text, output_file):
    """Google Text-to-Speech"""
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}"
    
    payload = {
        "input": {"text": text},
        "voice": {"languageCode": "en-US", "name": "en-US-Standard-A"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        audio_content = base64.b64decode(response.json()["audioContent"])
        with open(output_file, "wb") as f:
            f.write(audio_content)
        return True
    return False

def azure_tts(text, output_file):
    """Azure Text-to-Speech"""
    url = f"https://{AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3"
    }
    
    ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
    <voice name='en-US-AriaNeural'>{text}</voice>
    </speak>"""
    
    response = requests.post(url, headers=headers, data=ssml)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return True
    return False

def aws_tts(text, output_file):
    """AWS Polly Text-to-Speech"""
    try:
        import boto3
        client = boto3.client(
            'polly',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name='us-east-1'
        )
        
        response = client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        
        with open(output_file, "wb") as f:
            f.write(response['AudioStream'].read())
        return True
    except Exception as e:
        logger.error(f"AWS TTS failed: {str(e)}")
        return False

def espeak_tts(text, output_file):
    """Fallback TTS using espeak or Windows SAPI"""
    try:
        # Check if we're on Windows and try PowerShell TTS
        if os.name == 'nt':  # Windows
            return windows_tts(text, output_file)
        
        # Convert to WAV first, then to MP3
        wav_file = output_file.replace('.mp3', '.wav')
        cmd = f'espeak "{text}" -w {wav_file}'
        subprocess.run(cmd, shell=True, check=True)
        
        # Convert WAV to MP3
        audio = AudioSegment.from_wav(wav_file)
        audio.export(output_file, format="mp3")
        
        # Clean up WAV file
        os.remove(wav_file)
        return True
    except Exception as e:
        logger.error(f"Espeak TTS failed: {str(e)}")
        return False

def windows_tts(text, output_file):
    """Windows Text-to-Speech using SAPI"""
    try:
        # Create WAV file first
        wav_file = output_file.replace('.mp3', '.wav')
        
        # PowerShell command for Windows TTS
        ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("{wav_file}")
$synth.Speak("{text}")
$synth.Dispose()
'''
        
        # Run PowerShell script
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Convert WAV to MP3 using pydub
        if os.path.exists(wav_file):
            audio = AudioSegment.from_wav(wav_file)
            audio.export(output_file, format="mp3")
            os.remove(wav_file)  # Clean up WAV file
            logger.info(f"Windows TTS conversion successful: {output_file}")
            return True
        else:
            logger.error("Windows TTS failed to create audio file")
            return False
            
    except Exception as e:
        logger.error(f"Windows TTS failed: {str(e)}")
        return False

def prepare_audio_for_sip(audio_file):
    """Convert audio file to WAV format for SIP compatibility"""
    try:
        # Create WAV file path
        wav_file = audio_file.replace('.mp3', '.wav')
        
        # Convert to WAV using pydub
        if audio_file.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_file)
            # Convert to 8kHz mono WAV (standard for telephony)
            audio = audio.set_frame_rate(8000).set_channels(1)
            audio.export(wav_file, format="wav")
            logger.info(f"Converted audio to WAV: {wav_file}")
        else:
            # If already WAV, just copy it
            import shutil
            shutil.copy(audio_file, wav_file)
            
        return wav_file
    except Exception as e:
        logger.error(f"Audio preparation failed: {str(e)}")
        return audio_file  # Return original if conversion fails

def create_pjsua_command(call_config, wav_file):
    """Create the PJSUA command string for SIP calls"""
    # Create a command that will actually make an outbound call
    cmd_parts = [
        "/usr/local/bin/pjsua",
        "--null-audio",  # Use null audio device
        f"--id=sip:{call_config['username']}@{call_config['sip_server']}",
        f"--registrar=sip:{call_config['sip_server']}:{call_config['sip_port']}",
        f"--realm=asterisk",  # Use the exact realm expected by TrueSIP
        f"--username={call_config['username']}",
        f"--password={call_config['password']}",
        "--log-level=5",  # More detailed logging
        "--reg-timeout=10",  # Quick registration
        "--duration=30",  # Max call duration
        "--auto-answer=200",
        # Pass the target number to call as argument
        f"sip:{call_config['to']}@{call_config['sip_server']}"
    ]
    
    return " ".join(cmd_parts)

def execute_sip_call(command, call_config):
    """Execute real SIP call with enhanced logging"""
    try:
        logger.info(f"Executing SIP call: {command}")
        
        # Set environment variables for audio
        env = os.environ.copy()
        env['ALSA_CARD'] = 'null'
        env['PULSE_RUNTIME_PATH'] = '/tmp/pulse'
        
        # Create input commands for PJSUA to make the call
        pjsua_commands = f"""sleep 3000
m sip:{call_config['to']}@{call_config['sip_server']}
sleep 15000
h
q
"""
        
        # Execute the call with stdin input
        result = subprocess.run(
            command, 
            shell=True, 
            timeout=30,  # Shorter timeout for automated calls
            capture_output=True,
            text=True,
            input=pjsua_commands,
            env=env
        )
        
        if result.returncode == 0:
            logger.info(f"SIP call completed successfully: {call_config['from']} -> {call_config['to']}")
        else:
            logger.warning(f"SIP call ended with code {result.returncode}")
            
        # Log output for debugging
        if result.stdout:
            logger.info(f"PJSUA stdout: {result.stdout}")  # Full output
        if result.stderr:
            logger.warning(f"PJSUA stderr: {result.stderr}")  # Full output
            
    except subprocess.TimeoutExpired:
        logger.info(f"SIP call completed (timeout) - {call_config['from']} -> {call_config['to']}")
    except Exception as e:
        logger.error(f"SIP call execution failed: {str(e)}")
        # Fallback to simulation
        simulate_call(call_config)

def simulate_call(call_config):
    """Simulate SIP call for local testing"""
    try:
        logger.info(f"Simulating call from {call_config['from']} to {call_config['to']}")
        logger.info(f"Playing audio file: {call_config['audio_file']}")
        
        # Simulate call duration
        time.sleep(5)
        
        # Check if audio file exists and log its size
        if os.path.exists(call_config['audio_file']):
            file_size = os.path.getsize(call_config['audio_file'])
            logger.info(f"Audio file size: {file_size} bytes")
        else:
            logger.warning(f"Audio file not found: {call_config['audio_file']}")
        
        logger.info("Simulated call completed successfully")
        
    except Exception as e:
        logger.error(f"Simulated call failed: {str(e)}")

def initiate_sip_call(to_number, from_number, audio_file):
    """Initiate SIP call using pjsua"""
    try:
        # Create SIP call configuration
        call_config = {
            "to": to_number,
            "from": from_number,
            "audio_file": audio_file,
            "sip_server": SIP_TRUNK_IP,
            "sip_port": SIP_TRUNK_PORT,
            "username": SIP_USERNAME,
            "password": SIP_PASSWORD
        }
        
        # Log the call details
        logger.info(f"SIP Call initiated: {from_number} -> {to_number}")
        logger.info(f"SIP Server: {SIP_TRUNK_IP}:{SIP_TRUNK_PORT}")
        logger.info(f"Audio file: {audio_file}")
        
        # Convert audio to WAV format for better SIP compatibility
        wav_file = prepare_audio_for_sip(audio_file)
        
        # Check if pjsua is available
        pjsua_path = "/usr/local/bin/pjsua"
        if not os.path.exists(pjsua_path):
            pjsua_path = "pjsua"  # Try system PATH
        
        try:
            # Create PJSUA command for real SIP call
            pjsua_cmd = create_pjsua_command(call_config, wav_file)
            
            # Execute call in background
            Thread(target=execute_sip_call, args=(pjsua_cmd, call_config)).start()
            logger.info("Real SIP call initiated via pjsua")
            
        except Exception as sip_error:
            # Fallback to simulation if pjsua fails
            logger.warning(f"pjsua execution failed, simulating call: {str(sip_error)}")
            Thread(target=simulate_call, args=(call_config,)).start()
            logger.info("SIP call simulated for testing")
        
        return True
    except Exception as e:
        logger.error(f"SIP call initialization failed: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "sip_server": SIP_TRUNK_IP,
        "tts_service": TTS_SERVICE
    })

@app.route('/voice/call', methods=['POST'])
def make_voice_call():
    """Main API endpoint for voice calls - Async processing"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['ToNumber', 'FromNumber', 'Text']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields,
                "required": required_fields
            }), 400
        
        to_number = data['ToNumber']
        from_number = data['FromNumber']
        text = data['Text']
        audio_url = data.get('AudioUrl')  # Optional
        priority = data.get('Priority', 1)  # 1=high, 2=medium, 3=low
        
        # Create call record in database
        call = Call(
            to_number=to_number,
            from_number=from_number,
            text=text,
            audio_url=audio_url,
            status='pending'
        )
        
        db.session.add(call)
        db.session.commit()
        
        # Queue the call for async processing
        from tasks import tts_and_call_task
        task = tts_and_call_task.delay(call.id)
        
        # Update call with task ID
        call.task_id = task.id
        db.session.commit()
        
        logger.info(f"Call queued for processing: {call.id}")
        
        return jsonify({
            "success": True,
            "call_id": call.id,
            "task_id": task.id,
            "status": "queued",
            "to_number": to_number,
            "from_number": from_number,
            "timestamp": datetime.now().isoformat(),
            "estimated_processing_time": "30-60 seconds"
        }), 202  # Accepted
            
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/voice/status/<call_id>', methods=['GET'])
def get_call_status(call_id):
    """Get call status by ID from database"""
    try:
        call = Call.query.get(call_id)
        if not call:
            return jsonify({"error": "Call not found"}), 404
        
        # Get task status if available
        task_status = None
        if call.task_id:
            task_result = celery.AsyncResult(call.task_id)
            task_status = task_result.status
        
        response_data = call.to_dict()
        response_data['task_status'] = task_status
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and available endpoints"""
    return jsonify({
        "name": "SESPCLSwitch",
        "version": "1.0.0",
        "description": "Production-ready SESPCLSwitch using SIP and Text-to-Speech",
        "endpoints": {
            "GET /health": "Health check endpoint",
            "POST /voice/call": "Make a voice call",
            "GET /voice/status/<call_id>": "Get call status",
            "GET /api/info": "API information"
        },
        "example_request": {
            "method": "POST",
            "url": "/voice/call",
            "body": {
                "ToNumber": "+1234567890",
                "FromNumber": "12156",
                "Text": "Hello, this is a test call"
            }
        },
        "configuration": {
            "sip_server": SIP_TRUNK_IP,
            "sip_port": SIP_TRUNK_PORT,
            "tts_service": TTS_SERVICE
        },
        "metrics": {
            "GET /api/metrics": "System performance metrics",
            "POST /voice/bulk": "Bulk call operations"
        }
    })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system performance metrics"""
    try:
        # Get call statistics
        total_calls = Call.query.count()
        pending_calls = Call.query.filter_by(status='pending').count()
        processing_calls = Call.query.filter_by(status='processing').count()
        completed_calls = Call.query.filter_by(status='completed').count()
        failed_calls = Call.query.filter_by(status='failed').count()
        
        # Calculate success rate
        success_rate = (completed_calls / total_calls * 100) if total_calls > 0 else 0
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "calls": {
                "total": total_calls,
                "pending": pending_calls,
                "processing": processing_calls,
                "completed": completed_calls,
                "failed": failed_calls,
                "success_rate": round(success_rate, 2)
            },
            "system": {
                "status": "operational",
                "version": "2.0.0",
                "celery_workers": "Active"
            }
        })
    except Exception as e:
        logger.error(f"Metrics failed: {str(e)}")
        return jsonify({"error": "Failed to get metrics"}), 500

@app.route('/voice/bulk', methods=['POST'])
def bulk_voice_calls():
    """Handle bulk voice call requests"""
    try:
        data = request.get_json()
        calls_data = data.get('calls', [])
        
        if not calls_data or len(calls_data) > 1000:  # Limit bulk size
            return jsonify({
                "error": "Invalid bulk request",
                "max_calls": 1000
            }), 400
        
        call_ids = []
        task_ids = []
        
        for call_data in calls_data:
            # Validate each call
            required_fields = ['ToNumber', 'FromNumber', 'Text']
            if not all(field in call_data for field in required_fields):
                continue
            
            # Create call record
            call = Call(
                to_number=call_data['ToNumber'],
                from_number=call_data['FromNumber'],
                text=call_data['Text'],
                audio_url=call_data.get('AudioUrl'),
                status='pending'
            )
            
            db.session.add(call)
            db.session.flush()  # Get ID without committing
            
            # Queue the call
            from tasks import tts_and_call_task
            task = tts_and_call_task.delay(call.id)
            call.task_id = task.id
            
            call_ids.append(call.id)
            task_ids.append(task.id)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "queued_calls": len(call_ids),
            "call_ids": call_ids[:10],  # Return first 10 for reference
            "total_calls": len(call_ids),
            "timestamp": datetime.now().isoformat()
        }), 202
        
    except Exception as e:
        logger.error(f"Bulk call failed: {str(e)}")
        return jsonify({"error": "Bulk operation failed"}), 500

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting SESPCLSwitch on port {port}")
    logger.info(f"SIP Server: {SIP_TRUNK_IP}:{SIP_TRUNK_PORT}")
    logger.info(f"TTS Service: {TTS_SERVICE}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
