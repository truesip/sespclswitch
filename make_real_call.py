#!/usr/bin/env python3
"""
Script to make a real phone call using the Voice Call API
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def make_real_call(to_number, from_number, message):
    """Make a real phone call"""
    print(f"Making real call from {from_number} to {to_number}")
    print(f"Message: {message}")
    print("-" * 50)
    
    try:
        payload = {
            "ToNumber": to_number,
            "FromNumber": from_number,
            "Text": message
        }
        
        print("Sending API request...")
        response = requests.post(
            f"{BASE_URL}/voice/call",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Call initiated successfully!")
            print(f"Call ID: {result.get('call_id')}")
            print(f"Timestamp: {result.get('timestamp')}")
            print(f"Success: {result.get('success')}")
            
            # Check call status
            if result.get('call_id'):
                print("\nChecking call status...")
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/voice/status/{result['call_id']}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Call Status: {status_data.get('status')}")
                    
            return True
        else:
            print("❌ Call failed!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Voice Call API - Real Call Test")
    print("=" * 50)
    
    # Test call configuration
    # Using a test number for demonstration
    TO_NUMBER = "+15551234567"  # Test number - replace with actual number for real calls
    FROM_NUMBER = "12156"      # Using the configured SIP username
    MESSAGE = "Hello! This is a test call from the Voice Call API. This message is being generated using text-to-speech technology. Thank you for testing our system."
    
    print("📞 Making test call...")
    print(f"TO_NUMBER: {TO_NUMBER}")
    print(f"FROM_NUMBER: {FROM_NUMBER}")
    
    # Make the actual call
    success = make_real_call(TO_NUMBER, FROM_NUMBER, MESSAGE)
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
