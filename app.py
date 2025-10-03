#!/usr/bin/env python3
"""
Flask API server for audio stem separation
"""

import os
import tempfile
import shutil
import zipfile
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import uuid

# Import our stem separator
from stem_separator import separate_stems

app = Flask(__name__)

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max file size
ALLOWED_EXTENSIONS = {"mp3", "wav", "flac", "m4a", "ogg"}
UPLOAD_FOLDER = "temp_uploads"
OUTPUT_FOLDER = "temp_outputs"

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_temp_files(temp_dir):
    """Clean up temporary files"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up {temp_dir}: {e}")


@app.route("/", methods=["GET"])
def home():
    """API information endpoint"""
    return jsonify(
        {
            "message": "Audio Stem Separation API",
            "version": "1.0",
            "endpoints": {
                "/separate": "POST - Upload audio file for stem separation",
                "/health": "GET - Health check",
            },
            "supported_formats": list(ALLOWED_EXTENSIONS),
            "max_file_size": "100MB",
        }
    )


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Stem separation API is running"})


@app.route("/separate", methods=["POST"])
def separate_audio():
    """
    Separate audio file into stems

    Accepts: multipart/form-data with 'audio' file
    Returns: ZIP file containing 8 separated stems (4 MP3 + 4 WAV: bass, drums, vocals, other)
    """
    try:
        # Check if file was uploaded
        if "audio" not in request.files:
            return (
                jsonify(
                    {
                        "error": "No audio file provided",
                        "message": "Please upload an audio file with key 'audio'",
                    }
                ),
                400,
            )

        file = request.files["audio"]

        # Check if file was selected
        if file.filename == "":
            return (
                jsonify(
                    {
                        "error": "No file selected",
                        "message": "Please select an audio file to upload",
                    }
                ),
                400,
            )

        # Check file extension
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": "Invalid file format",
                        "message": f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}",
                        "uploaded_format": (
                            file.filename.rsplit(".", 1)[1].lower()
                            if "." in file.filename
                            else "unknown"
                        ),
                    }
                ),
                400,
            )

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create temporary directories for this session
        session_upload_dir = os.path.join(UPLOAD_FOLDER, session_id)
        session_output_dir = os.path.join(OUTPUT_FOLDER, session_id)
        os.makedirs(session_upload_dir, exist_ok=True)
        os.makedirs(session_output_dir, exist_ok=True)

        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(session_upload_dir, filename)
        file.save(input_path)

        # Get file info
        file_size = os.path.getsize(input_path) / (1024 * 1024)  # Size in MB

        print(f"Processing file: {filename} ({file_size:.1f} MB)")

        # Separate stems
        try:
            separate_stems(input_path, session_output_dir)
        except Exception as e:
            cleanup_temp_files(session_upload_dir)
            cleanup_temp_files(session_output_dir)
            return jsonify({"error": "Stem separation failed", "message": str(e)}), 500

        # Find the separated stems
        stem_dir = Path(session_output_dir) / "htdemucs" / Path(filename).stem

        if not stem_dir.exists():
            cleanup_temp_files(session_upload_dir)
            cleanup_temp_files(session_output_dir)
            return (
                jsonify(
                    {
                        "error": "Separation output not found",
                        "message": "The stem separation process completed but output files were not found",
                    }
                ),
                500,
            )

        # Find stem files (both MP3 and WAV)
        mp3_files = list(stem_dir.glob("*.mp3"))
        wav_files = list(stem_dir.glob("*.wav"))
        stem_files = mp3_files + wav_files

        if len(mp3_files) != 4 or len(wav_files) != 4:
            cleanup_temp_files(session_upload_dir)
            cleanup_temp_files(session_output_dir)
            return (
                jsonify(
                    {
                        "error": "Incomplete separation",
                        "message": f"Expected 4 MP3 and 4 WAV stems, found {len(mp3_files)} MP3 and {len(wav_files)} WAV",
                        "found_mp3_files": [f.name for f in mp3_files],
                        "found_wav_files": [f.name for f in wav_files],
                    }
                ),
                500,
            )

        # Create ZIP file with all stems
        zip_path = os.path.join(session_output_dir, f"{Path(filename).stem}_stems.zip")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for stem_file in stem_files:
                # Add file to zip with just the filename (no directory structure)
                zipf.write(stem_file, stem_file.name)

        # Get ZIP file size
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # Size in MB

        # Clean up input file (keep output for download)
        cleanup_temp_files(session_upload_dir)

        print(
            f"Separation complete: {filename} -> {len(mp3_files)} MP3 + {len(wav_files)} WAV stems ({zip_size:.1f} MB)"
        )

        # Return the ZIP file
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{Path(filename).stem}_stems.zip",
            mimetype="application/zip",
        )

    except Exception as e:
        # Clean up on any error
        if "session_upload_dir" in locals():
            cleanup_temp_files(session_upload_dir)
        if "session_output_dir" in locals():
            cleanup_temp_files(session_output_dir)

        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@app.route("/cleanup", methods=["POST"])
def cleanup_all():
    """Clean up all temporary files (admin endpoint)"""
    try:
        cleanup_temp_files(UPLOAD_FOLDER)
        cleanup_temp_files(OUTPUT_FOLDER)

        # Recreate directories
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        return jsonify({"message": "Cleanup completed successfully"})
    except Exception as e:
        return jsonify({"error": "Cleanup failed", "message": str(e)}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return (
        jsonify({"error": "File too large", "message": "Maximum file size is 100MB"}),
        413,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


if __name__ == "__main__":
    print("Audio Stem Separation API Server")
    print("=" * 40)
    print("Starting Flask server...")
    print("Upload endpoint: POST /separate")
    print("Supported formats:", ", ".join(ALLOWED_EXTENSIONS))
    print("Max file size: 100MB")
    print("=" * 40)

    # Run the Flask app
    app.run(
        host="0.0.0.0",  # Allow external connections
        port=5000,
        debug=True,  # Enable debug mode for development
        threaded=True,  # Handle multiple requests
    )
