"""
Voice Call Utility Functions
Separated from app.py to avoid circular imports with tasks.py
"""
import os
import requests
import tempfile
import subprocess
import logging
from pydub import AudioSegment
import base64
from threading import Thread
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configuration from environment variables
SIP_TRUNK_IP = os.getenv("SIP_TRUNK_IP", "sip.truesip.net")
SIP_TRUNK_PORT = os.getenv("SIP_TRUNK_PORT", "5060")
SIP_USERNAME = os.getenv("SIP_USERNAME", "12156")
SIP_PASSWORD = os.getenv("SIP_PASSWORD", "1C36na9C")

# Text-to-Speech Configuration
TTS_SERVICE = os.getenv("TTS_SERVICE", "espeak")
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
        # Use the from_number as the SIP identity for caller ID
        f"--id=sip:{call_config['from']}@{call_config['sip_server']}",
        f"--registrar=sip:{call_config['sip_server']}:{call_config['sip_port']}",
        f"--realm=asterisk",  # Use the exact realm expected by TrueSIP
        f"--username={call_config['username']}",
        f"--password={call_config['password']}",
        # Set contact header with the from number
        f"--contact=sip:{call_config['from']}@{call_config['sip_server']}",
        # Add additional headers for caller ID presentation
        f"--add-header='P-Asserted-Identity: <sip:{call_config['from']}@{call_config['sip_server']}>'",
        f"--add-header='Remote-Party-ID: <sip:{call_config['from']}@{call_config['sip_server']}>'",
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
        # Add custom headers for caller ID presentation
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
