# Docker Usage Guide

This guide explains how to use the Audio Stem Separation API with Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### Option 1: Using Docker Directly

1. **Build the Docker image**:
   ```bash
   docker build -t audio-stem-separator .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 audio-stem-separator
   ```

3. **Access the API** at `http://localhost:5000`

### Option 2: Using Docker Compose (Recommended)

1. **Start the service**:
   ```bash
   docker-compose up
   ```

2. **Run in detached mode** (background):
   ```bash
   docker-compose up -d
   ```

3. **Stop the service**:
   ```bash
   docker-compose down
   ```

## Testing the API

Once the container is running, test it:

```bash
# Health check
curl http://localhost:5000/health

# Upload and separate an audio file
curl -X POST -F "audio=@creep.mp3" http://localhost:5000/separate -o stems.zip
```

## Configuration

### Custom Port

To run on a different port (e.g., 8080):

```bash
docker run -p 8080:5000 audio-stem-separator
```

Or modify `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"
```

### Persistent Storage

The `docker-compose.yml` already includes volume mounts for persistent storage. If you want to add them to a plain Docker run command:

```bash
docker run -p 5000:5000 \
  -v $(pwd)/temp_uploads:/app/temp_uploads \
  -v $(pwd)/temp_outputs:/app/temp_outputs \
  audio-stem-separator
```

## Advanced Usage

### View Logs

```bash
# Using Docker
docker logs <container-id>

# Using Docker Compose
docker-compose logs -f
```

### Run in Interactive Mode

```bash
docker run -it --rm -p 5000:5000 audio-stem-separator bash
```

### Execute Commands Inside Container

```bash
docker exec -it <container-id> bash
```

### Rebuild After Changes

```bash
docker-compose up --build
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```bash
# Find and stop the process
docker ps
docker stop <container-id>

# Or use a different port
docker run -p 5001:5000 audio-stem-separator
```

### Container Won't Start

Check logs for errors:
```bash
docker logs <container-id>
```

### Out of Memory

If you encounter memory issues:

1. Allocate more RAM to Docker (Docker Desktop settings)
2. Reduce batch sizes in processing
3. Use the cleanup endpoint: `POST http://localhost:5000/cleanup`

## Building for Production

For production deployment, you may want to:

1. Remove `debug=True` from `app.py`
2. Use a production WSGI server (e.g., gunicorn)
3. Add health checks and restart policies
4. Use environment-specific configurations

Example production Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install gunicorn
RUN pip install gunicorn

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Deployment

### Docker Hub

1. Tag and push your image:
   ```bash
   docker tag audio-stem-separator yourusername/audio-stem-separator:latest
   docker push yourusername/audio-stem-separator:latest
   ```

2. Pull and run on your server:
   ```bash
   docker pull yourusername/audio-stem-separator:latest
   docker run -p 5000:5000 yourusername/audio-stem-separator:latest
   ```

### Cloud Platforms

The containerized application can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku (with container support)

Consult each platform's documentation for deployment steps.
