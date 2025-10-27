# Audio Stem Separation API

A Flask API server for separating audio files into individual stems (vocals, drums, bass, other) using Facebook's Demucs library.

## Features

- **REST API**: Simple HTTP API for stem separation
- **High-Quality Separation**: Uses Facebook's state-of-the-art Demucs models
- **Multiple Formats**: Supports MP3, WAV, FLAC, and other common audio formats
- **ZIP Response**: Returns all 4 stems in a convenient ZIP file
- **GPU Acceleration**: Automatic GPU detection and utilization
- **Command Line Tool**: Also includes standalone command-line interface

## Installation

### Docker (Recommended)

1. **Build the Docker image**:
   ```bash
   docker build -t audio-stem-separator .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 audio-stem-separator
   ```

3. **Or use Docker Compose**:
   ```bash
   docker-compose up
   ```

The API will be available at `http://localhost:5000`

### Local Installation

1. **Clone or download this project**
2. **Install Python 3.10+** (recommended: use conda or pyenv)
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Alternative Installation (if you encounter issues)

```bash
# Install PyTorch first (choose appropriate version for your system)
pip install torch torchaudio

# Install Demucs
pip install demucs

# Install other dependencies
pip install librosa soundfile numpy tqdm
```

## Usage

### API Server

1. **Start the API server** (if running locally):
   ```bash
   python app.py
   ```

   Or if using Docker, the API is already running on port 5000.

2. **Upload audio file for separation**:
   ```bash
   curl -X POST -F "audio=@your_song.mp3" http://localhost:5000/separate -o stems.zip
   ```

3. **Test the API**:
   ```bash
   python test_api.py
   ```

### API Endpoints

- **GET /**: API information and supported formats
- **GET /health**: Health check
- **POST /separate**: Upload audio file and get separated stems
- **POST /cleanup**: Clean up temporary files (admin)

### Command Line Tool

```bash
# Separate a single MP3 file
python stem_separator.py input_song.mp3

# Specify output directory  
python stem_separator.py input_song.mp3 output_dir
```

### Advanced Options

```bash
# Force CPU usage
python stem_separator.py input_song.mp3 -d cpu

# Output as MP3 files
python stem_separator.py input_song.mp3 -f mp3

# Batch process with custom output directory
python stem_separator.py ./input_folder -o ./separated_stems -b
```

### Command Line Arguments

- `input`: Input MP3 file or directory
- `-o, --output`: Output directory (default: input_name_stems)
- `-m, --model`: Demucs model to use (default: htdemucs)
- `-d, --device`: Device to use (cpu, cuda, auto)
- `-f, --format`: Output format (wav, mp3, flac)
- `-b, --batch`: Process entire directory

## Available Models

- **htdemucs**: High-quality transformer-based model (default)
- **htdemucs_ft**: Fine-tuned version of htdemucs
- **mdx**: Hybrid transformer model
- **mdx_q**: Quantized version for faster processing

## Output Structure

After processing, you'll get separate files for each stem:

```
song_stems/
├── song_vocals.wav
├── song_drums.wav
├── song_bass.wav
└── song_other.wav
```

## Programmatic Usage

```python
from stem_separator import StemSeparator

# Initialize separator
separator = StemSeparator(model_name="htdemucs", device="auto")

# Separate single file
stem_paths = separator.separate_audio("input.mp3", "output_dir")

# Batch processing
results = separator.batch_separate("input_folder", "output_folder")
```

## Requirements

### Docker
- Docker and Docker Compose installed
- At least 4GB RAM (8GB+ recommended)
- Docker will handle all dependencies automatically

### Local Installation
- Python 3.10+
- PyTorch 1.9+
- CUDA-compatible GPU (recommended for faster processing)
- At least 4GB RAM (8GB+ recommended)

## Performance Tips

1. **Use GPU**: Ensure CUDA is available for faster processing
2. **Batch Processing**: Process multiple files together for efficiency
3. **Model Selection**: 
   - `htdemucs`: Best quality, slower
   - `mdx_q`: Faster processing, slightly lower quality
4. **File Formats**: WAV output is fastest, MP3 requires additional encoding

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:
   - Use `-d cpu` to force CPU processing
   - Try smaller batch sizes

2. **Installation Issues**:
   - Update pip: `pip install --upgrade pip`
   - Install PyTorch separately first
   - Use conda for easier dependency management

3. **Audio Format Issues**:
   - Ensure input files are valid audio
   - Try converting to WAV first

### Getting Help

- Check that all dependencies are properly installed
- Verify Python version (3.10+)
- Test with a small audio file first

## Examples

### Example 1: Basic Separation
```bash
python stem_separator.py my_song.mp3
```

### Example 2: High-Quality Processing
```bash
python stem_separator.py my_song.mp3 -m htdemucs_ft -f wav -o ./high_quality_stems
```

### Example 3: Batch Processing
```bash
python stem_separator.py ./music_collection -b -o ./all_separated_stems
```

## License

This project uses Facebook's Demucs library. Please refer to their license terms for commercial usage.
