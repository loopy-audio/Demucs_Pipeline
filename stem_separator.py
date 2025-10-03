#!/usr/bin/env python3
"""
Simple audio stem separator using Facebook Demucs
"""

import os
import sys
import shutil
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

    # Run demucs separation twice - once for WAV (default) and once for MP3
    try:
        original_argv = sys.argv

        # Create separate output directories for WAV and MP3
        wav_output_path = output_path / "wav_output"
        mp3_output_path = output_path / "mp3_output"
        wav_output_path.mkdir(exist_ok=True)
        mp3_output_path.mkdir(exist_ok=True)

        # First run: Generate WAV files (default format)
        print("Generating WAV stems...")
        wav_args = [str(audio_file), "-o", str(wav_output_path)]

        # Add GPU support if available
        if torch.cuda.is_available():
            wav_args.extend(["-d", "cuda"])

        sys.argv = ["demucs"] + wav_args
        demucs_main()

        # Second run: Generate MP3 files
        print("Generating MP3 stems...")
        mp3_args = [
            str(audio_file),
            "-o",
            str(mp3_output_path),
            "--mp3",  # Output as MP3
            "--mp3-bitrate",
            "320",
        ]

        # Add GPU support if available
        if torch.cuda.is_available():
            mp3_args.extend(["-d", "cuda"])

        sys.argv = ["demucs"] + mp3_args
        demucs_main()

        sys.argv = original_argv
        print("Separation complete!")

        # Copy files to the main output directory
        wav_stem_dir = wav_output_path / "htdemucs" / audio_file.stem
        mp3_stem_dir = mp3_output_path / "htdemucs" / audio_file.stem
        final_stem_dir = output_path / "htdemucs" / audio_file.stem

        if wav_stem_dir.exists() and mp3_stem_dir.exists():
            # Create final output directory
            final_stem_dir.mkdir(parents=True, exist_ok=True)

            # Copy WAV files
            wav_files = list(wav_stem_dir.glob("*.wav"))
            for wav_file in wav_files:
                shutil.copy2(wav_file, final_stem_dir / wav_file.name)

            # Copy MP3 files
            mp3_files = list(mp3_stem_dir.glob("*.mp3"))
            for mp3_file in mp3_files:
                shutil.copy2(mp3_file, final_stem_dir / mp3_file.name)

            # Clean up temporary directories
            shutil.rmtree(wav_output_path)
            shutil.rmtree(mp3_output_path)

            # Show output files
            mp3_stems = list(final_stem_dir.glob("*.mp3"))
            wav_stems = list(final_stem_dir.glob("*.wav"))
            print(
                f"\nGenerated {len(mp3_stems)} MP3 stems and {len(wav_stems)} WAV stems:"
            )

            # Group by stem type
            stem_types = {}
            for stem in mp3_stems + wav_stems:
                stem_name = stem.stem  # filename without extension
                if stem_name not in stem_types:
                    stem_types[stem_name] = []
                stem_types[stem_name].append(stem.suffix)

            for stem_name, formats in stem_types.items():
                format_str = ", ".join(formats)
                print(f"  {stem_name}: {format_str}")

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
