#!/usr/bin/env python3
"""
SIP Diagnostics Script
Tests various aspects of SIP configuration and connectivity
"""

import requests
import json
import subprocess
import socket
import time

def test_network_connectivity():
    """Test network connectivity to SIP server"""
    try:
        print("Testing network connectivity to SIP server...")
        
        # Test DNS resolution
        import socket
        sip_server = "sip.truesip.net"
        sip_port = 5060
        
        # Resolve hostname
        try:
            ip = socket.gethostbyname(sip_server)
            print(f"✅ DNS resolution successful: {sip_server} -> {ip}")
        except socket.gaierror as e:
            print(f"❌ DNS resolution failed: {e}")
            return False
        
        # Test TCP connectivity
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((sip_server, sip_port))
            sock.close()
            
            if result == 0:
                print(f"✅ TCP connectivity successful: {sip_server}:{sip_port}")
                return True
            else:
                print(f"❌ TCP connectivity failed: {sip_server}:{sip_port}")
                return False
        except Exception as e:
            print(f"❌ TCP connectivity test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Network connectivity test failed: {e}")
        return False

def test_sip_registration_direct():
    """Test SIP registration using direct SIP commands"""
    try:
        print("\nTesting SIP registration...")
        
        # Create a simple SIP registration test
        sip_message = f"""REGISTER sip:sip.truesip.net SIP/2.0
Via: SIP/2.0/UDP 192.168.1.100:5060;branch=z9hG4bK-test
To: <sip:12156@sip.truesip.net>
From: <sip:12156@sip.truesip.net>;tag=test123
Call-ID: test-call-id@192.168.1.100
CSeq: 1 REGISTER
Contact: <sip:12156@192.168.1.100:5060>
Content-Length: 0

"""
        
        # Send UDP packet to SIP server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        try:
            sock.sendto(sip_message.encode(), ("sip.truesip.net", 5060))
            response, addr = sock.recvfrom(1024)
            
            response_str = response.decode()
            print(f"SIP Server Response: {response_str[:200]}...")
            
            if "401 Unauthorized" in response_str:
                print("✅ SIP server responding (authentication required)")
                return True
            elif "200 OK" in response_str:
                print("✅ SIP registration successful")
                return True
            else:
                print(f"❌ Unexpected SIP response: {response_str[:100]}")
                return False
                
        except socket.timeout:
            print("❌ SIP server not responding (timeout)")
            return False
        except Exception as e:
            print(f"❌ SIP registration test failed: {e}")
            return False
        finally:
            sock.close()
            
    except Exception as e:
        print(f"❌ SIP registration test failed: {e}")
        return False

def test_api_with_valid_number():
    """Test API call with a potentially valid number"""
    try:
        print("\nTesting API with different phone numbers...")
        
        # Test with various number formats
        test_numbers = [
            "+18005551234",  # Toll-free number
            "+12125551234",  # NYC area code
            "+15551234567",  # Generic test number
            "18005551234",   # Without +
            "5551234567"     # Local format
        ]
        
        for number in test_numbers:
            print(f"\nTesting number: {number}")
            
            payload = {
                "ToNumber": number,
                "FromNumber": "12156",
                "Text": "Test call"
            }
            
            try:
                response = requests.post(
                    "http://167.172.135.7:5000/voice/call",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 202:
                    result = response.json()
                    call_id = result.get('call_id')
                    print(f"✅ Call queued successfully: {call_id}")
                    
                    # Check status after a few seconds
                    time.sleep(5)
                    status_response = requests.get(
                        f"http://167.172.135.7:5000/voice/status/{call_id}"
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Status: {status_data.get('status')}")
                        if status_data.get('error_message'):
                            print(f"Error: {status_data.get('error_message')}")
                        
                        if status_data.get('status') == 'completed':
                            print(f"✅ Call completed successfully with {number}")
                            return True
                        
                else:
                    print(f"❌ API call failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ API test failed for {number}: {e}")
                
        return False
        
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        return False

def suggest_fixes():
    """Suggest potential fixes for common SIP issues"""
    print("\n" + "="*50)
    print("SUGGESTED FIXES FOR SIP ISSUES:")
    print("="*50)
    
    print("\n1. **Check SIP Credentials:**")
    print("   - Verify username: 12156")
    print("   - Verify password: 1C36na9C")
    print("   - Contact TrueSIP support to confirm account status")
    
    print("\n2. **Install/Configure PJSUA:**")
    print("   - Install PJSUA on the server: apt-get install pjsua")
    print("   - Verify PJSUA is in PATH: which pjsua")
    print("   - Test PJSUA manually: pjsua --version")
    
    print("\n3. **Network Configuration:**")
    print("   - Check firewall settings for SIP ports (5060-5090)")
    print("   - Ensure UDP traffic is allowed")
    print("   - Verify server can reach sip.truesip.net:5060")
    
    print("\n4. **Phone Number Issues:**")
    print("   - Use real phone numbers for testing")
    print("   - Ensure proper number formatting (+1XXXXXXXXXX)")
    print("   - Check if destination numbers are valid/reachable")
    
    print("\n5. **Audio Issues:**")
    print("   - Ensure audio files are properly converted")
    print("   - Check WAV file format (8kHz, mono, 16-bit)")
    print("   - Verify audio codecs are supported")
    
    print("\n6. **Server Configuration:**")
    print("   - Check environment variables in Docker container")
    print("   - Verify Celery workers are running")
    print("   - Check system resources (CPU, memory)")

if __name__ == "__main__":
    print("SIP DIAGNOSTICS TOOL")
    print("="*50)
    
    # Run diagnostic tests
    results = []
    
    # Test 1: Network connectivity
    results.append(("Network Connectivity", test_network_connectivity()))
    
    # Test 2: SIP registration
    results.append(("SIP Registration", test_sip_registration_direct()))
    
    # Test 3: API with different numbers
    results.append(("API Testing", test_api_with_valid_number()))
    
    # Display results
    print("\n" + "="*50)
    print("DIAGNOSTIC RESULTS:")
    print("="*50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Suggest fixes
    suggest_fixes()
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    
    if all(result[1] for result in results):
        print("✅ All tests passed! The system should be working correctly.")
    else:
        print("❌ Some tests failed. Please address the issues above.")
        print("💡 Focus on fixing the failed tests first.")
        print("📞 Contact TrueSIP support if credentials are the issue.")
