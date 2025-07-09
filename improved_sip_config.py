#!/usr/bin/env python3
"""
Improved SIP Configuration for Voice Call API
This script provides better SIP handling with proper error detection
"""

import subprocess
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_improved_pjsua_command(call_config, wav_file):
    """Create improved PJSUA command with better error handling"""
    
    # Try different PJSUA paths
    pjsua_paths = [
        "/usr/local/bin/pjsua",
        "/usr/bin/pjsua", 
        "pjsua",
        "/opt/pjproject/bin/pjsua"
    ]
    
    pjsua_cmd = None
    for path in pjsua_paths:
        try:
            result = subprocess.run([path, "--version"], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode == 0:
                pjsua_cmd = path
                break
        except:
            continue
    
    if not pjsua_cmd:
        raise Exception("PJSUA not found in system PATH")
    
    # Create improved command with better SIP parameters
    cmd_parts = [
        pjsua_cmd,
        "--null-audio",
        "--no-vad",  # Disable voice activity detection
        "--ec-tail=0",  # Disable echo cancellation
        "--quality=4",  # Set audio quality
        f"--id=sip:{call_config['username']}@{call_config['sip_server']}",
        f"--registrar=sip:{call_config['sip_server']}:{call_config['sip_port']}",
        f"--realm={call_config['sip_server']}",
        f"--username={call_config['username']}",
        f"--password={call_config['password']}",
        f"--proxy=sip:{call_config['sip_server']}:{call_config['sip_port']}",
        "--reg-timeout=300",  # Longer registration timeout
        "--duration=60",  # Longer call duration
        "--auto-answer=200",
        "--log-level=4",
        "--app-log-level=4",
        f"--play-file={wav_file}",  # Play audio file during call
        f"sip:{call_config['to']}@{call_config['sip_server']}"
    ]
    
    return " ".join(cmd_parts)

def test_sip_registration(call_config):
    """Test SIP registration before making calls"""
    try:
        # Test registration only
        test_cmd = [
            "pjsua",
            "--null-audio",
            f"--id=sip:{call_config['username']}@{call_config['sip_server']}",
            f"--registrar=sip:{call_config['sip_server']}:{call_config['sip_port']}",
            f"--username={call_config['username']}",
            f"--password={call_config['password']}",
            "--duration=5",
            "--auto-quit"
        ]
        
        result = subprocess.run(test_cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if "Registration successful" in result.stdout:
            logger.info("SIP registration successful")
            return True
        else:
            logger.error(f"SIP registration failed: {result.stdout}")
            return False
            
    except Exception as e:
        logger.error(f"SIP registration test failed: {str(e)}")
        return False

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove any non-digit characters except +
    import re
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Check if it's a valid format
    if cleaned.startswith('+1') and len(cleaned) == 12:
        return cleaned
    elif cleaned.startswith('1') and len(cleaned) == 11:
        return '+' + cleaned
    elif len(cleaned) == 10:
        return '+1' + cleaned
    else:
        raise ValueError(f"Invalid phone number format: {phone_number}")

# Test configuration
if __name__ == "__main__":
    test_config = {
        'username': '12156',
        'password': '1C36na9C',
        'sip_server': 'sip.truesip.net',
        'sip_port': '5060',
        'to': '+15551234567',
        'from': '12156'
    }
    
    print("Testing SIP configuration...")
    if test_sip_registration(test_config):
        print("✅ SIP registration test passed")
    else:
        print("❌ SIP registration test failed")
        
    try:
        validated_number = validate_phone_number(test_config['to'])
        print(f"✅ Phone number validation passed: {validated_number}")
    except ValueError as e:
        print(f"❌ Phone number validation failed: {e}")
