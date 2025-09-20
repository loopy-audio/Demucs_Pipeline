#!/usr/bin/env python3
"""
Test client for the stem separation API
"""

import requests
import os
import sys
from pathlib import Path


def test_api_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server")
        print("Make sure the server is running: python app.py")
        return False
    except Exception as e:
        print(f"ERROR: Health check failed: {e}")
        return False


def test_api_info():
    """Test the info endpoint"""
    try:
        response = requests.get("http://localhost:5000/")
        print(f"API Info: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"API Version: {info.get('version')}")
            print(f"Supported formats: {info.get('supported_formats')}")
            print(f"Max file size: {info.get('max_file_size')}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: API info failed: {e}")
        return False


def test_stem_separation(audio_file_path):
    """Test stem separation with an audio file"""
    if not os.path.exists(audio_file_path):
        print(f"ERROR: Audio file not found: {audio_file_path}")
        return False
    
    print(f"Testing stem separation with: {audio_file_path}")
    
    try:
        # Open and send the file
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            
            print("Uploading file and starting separation...")
            response = requests.post(
                "http://localhost:5000/separate", 
                files=files,
                timeout=300  # 5 minute timeout
            )
        
        if response.status_code == 200:
            # Save the returned ZIP file
            output_filename = f"{Path(audio_file_path).stem}_stems.zip"
            
            with open(output_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / (1024 * 1024)  # MB
            print(f"SUCCESS: Stems saved to: {output_filename} ({file_size:.1f} MB)")
            print("The ZIP file contains 4 separated stem files:")
            print("  - bass.mp3 - bass line")
            print("  - drums.mp3 - drum track") 
            print("  - vocals.mp3 - vocal track")
            print("  - other.mp3 - remaining instruments")
            return True
            
        else:
            print(f"ERROR: Separation failed: {response.status_code}")
            try:
                error_info = response.json()
                print(f"Error: {error_info.get('error')}")
                print(f"Message: {error_info.get('message')}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out (separation takes time for large files)")
        return False
    except Exception as e:
        print(f"ERROR: Separation request failed: {e}")
        return False


def main():
    print("Stem Separation API Test Client")
    print("=" * 40)
    
    # Test health endpoint
    print("\n1. Testing API health...")
    if not test_api_health():
        return
    
    # Test info endpoint
    print("\n2. Testing API info...")
    if not test_api_info():
        return
    
    # Test stem separation
    print("\n3. Testing stem separation...")
    
    # Look for an audio file to test with
    test_audio_files = [
        "ed.mp3.mp3",  # Your test file
        "test.mp3",
        "sample.mp3",
        "audio.mp3"
    ]
    
    audio_file = None
    for filename in test_audio_files:
        if os.path.exists(filename):
            audio_file = filename
            break
    
    if audio_file:
        success = test_stem_separation(audio_file)
        if success:
            print("\nAll tests passed!")
        else:
            print("\nStem separation test failed")
    else:
        print("ERROR: No test audio file found")
        print("Available files to test with:")
        for filename in test_audio_files:
            print(f"  - {filename}")
        print("\nTo test separation, place an audio file in the current directory")
        print("and run this script again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Custom audio file provided
        test_stem_separation(sys.argv[1])
    else:
        # Run full test suite
        main()
