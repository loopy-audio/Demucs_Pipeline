#!/usr/bin/env python3
"""
Test script for the stem separator using ed.mp3
"""

import os
import sys
from pathlib import Path
import time

# Import our stem separator
try:
    from stem_separator import separate_stems
except ImportError:
    print("Error: stem_separator.py not found in the same directory")
    sys.exit(1)


def test_separation():
    """Test the stem separation with ed.mp3"""
    
    # Look for ed.mp3.mp3 in current directory
    test_file = Path("ed.mp3.mp3")
    
    if not test_file.exists():
        print("ERROR: Test file 'ed.mp3.mp3' not found in current directory")
        print("Please place ed.mp3.mp3 in the same folder as this script")
        return False
    
    print("Testing stem separation with ed.mp3.mp3")
    print(f"File size: {test_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Create test output directory
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output directory: {output_dir.absolute()}")
    
    # Record start time
    start_time = time.time()
    
    try:
        # Run the separation
        separate_stems(test_file, output_dir)
        
        # Calculate processing time
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"\nProcessing time: {processing_time:.1f} seconds")
        
        # Check if outputs were created
        expected_stems_dir = output_dir / "htdemucs" / "ed.mp3"
        
        if expected_stems_dir.exists():
            stems = list(expected_stems_dir.glob("*.mp3"))
            print(f"\nSUCCESS: Generated {len(stems)} stem files:")
            
            total_size = 0
            for stem in sorted(stems):
                size_mb = stem.stat().st_size / (1024*1024)
                total_size += size_mb
                print(f"   {stem.name} ({size_mb:.1f} MB)")
            
            print(f"\nTotal output size: {total_size:.1f} MB")
            print(f"Output location: {expected_stems_dir.absolute()}")
            
            return True
        else:
            print("ERROR: Expected output directory not found")
            return False
            
    except Exception as e:
        end_time = time.time()
        print(f"\nERROR: Error during separation: {e}")
        print(f"Processing time before error: {end_time - start_time:.1f} seconds")
        return False


def check_requirements():
    """Check if required packages are installed"""
    print("Checking requirements...")
    
    required_packages = ['torch', 'demucs']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"OK: {package} - installed")
        except ImportError:
            print(f"ERROR: {package} - missing")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Install with: pip install torch demucs")
        return False
    
    # Check GPU availability
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"GPU available: {gpu_name}")
        else:
            print("Using CPU (no GPU detected)")
    except:
        print("WARNING: Could not check GPU status")
    
    return True


def main():
    print("Stem Separator Test Suite")
    print("=" * 40)
    
    # Check requirements first
    if not check_requirements():
        print("\nERROR: Requirements check failed")
        return
    
    print("\n" + "=" * 40)
    
    # Run the test
    success = test_separation()
    
    print("\n" + "=" * 40)
    if success:
        print("Test completed successfully!")
        print("\nYou can now play the separated stems:")
        print("   - drums.mp3 - drum track")
        print("   - bass.mp3 - bass line") 
        print("   - vocals.mp3 - vocal track")
        print("   - other.mp3 - remaining instruments")
    else:
        print("ERROR: Test failed")


if __name__ == "__main__":
    main()