#!/usr/bin/env python3
"""
Test script for Voice Call API
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_info():
    """Test API info endpoint"""
    print("\nTesting /api/info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/info")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_voice_call():
    """Test voice call endpoint"""
    print("\nTesting /voice/call endpoint...")
    try:
        payload = {
            "ToNumber": "+1234567890",
            "FromNumber": "12156",
            "Text": "Hello, this is a test call from the Voice Call API"
        }
        
        response = requests.post(
            f"{BASE_URL}/voice/call",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_call_status():
    """Test call status endpoint"""
    print("\nTesting /voice/status endpoint...")
    try:
        test_call_id = "test-123-456"
        response = requests.get(f"{BASE_URL}/voice/status/{test_call_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Voice Call API Test Suite")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    tests = [
        ("Health Check", test_health),
        ("API Info", test_api_info),
        ("Voice Call", test_voice_call),
        ("Call Status", test_call_status)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * 20)
        success = test_func()
        results.append((test_name, success))
        
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
