#!/usr/bin/env python3
"""
Simple audio stem separator using Facebook Demucs
"""

import os
import sys
from pathlib import Path
import torch
from demucs.separate import main as demucs_main


def separate_stems(audio_file, output_dir=None):
    """
    Separate audio file into stems using Demucs
    
    Args:
        audio_file: Path to audio file (mp3, wav, etc.)
        output_dir: Where to save stems (optional)
    """
    audio_file = Path(audio_file)
    
    if not audio_file.exists():
        print(f"File not found: {audio_file}")
        return
    
    # Set output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = audio_file.parent / "separated"
    
    output_path.mkdir(exist_ok=True)
    
    print(f"Separating: {audio_file.name}")
    print(f"Output: {output_path}")
    
    # Build demucs command arguments
    args = [
        str(audio_file),
        "-o", str(output_path),
        "--mp3",  # Output as MP3
        "--mp3-bitrate", "320"
    ]
    
    # Add GPU support if available
    if torch.cuda.is_available():
        args.extend(["-d", "cuda"])
        print("Using GPU acceleration")
    else:
        print("Using CPU")
    
    # Run demucs separation
    try:
        # Temporarily replace sys.argv for demucs
        original_argv = sys.argv
        sys.argv = ["demucs"] + args
        
        demucs_main()
        
        sys.argv = original_argv
        
        print("Separation complete!")
        
        # Show output files
        stem_dir = output_path / "htdemucs" / audio_file.stem
        if stem_dir.exists():
            stems = list(stem_dir.glob("*.mp3"))
            print(f"\nGenerated {len(stems)} stems:")
            for stem in stems:
                print(f"  {stem.name}")
        
    except Exception as e:
        sys.argv = original_argv
        print(f"Error: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python stem_separator.py <audio_file> [output_dir]")
        print("Example: python stem_separator.py song.mp3")
        return
    
    audio_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    separate_stems(audio_file, output_dir)


if __name__ == "__main__":
    main()