# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vosk-based Speech-to-Text (STT) API service designed for deployment on Oracle Cloud Infrastructure (OCI). The service provides REST APIs for audio file transcription with asynchronous task processing.

## Core Architecture

### API Structure (FastAPI-based)
- **api/main.py**: FastAPI application with endpoints `/transcribe`, `/tasks/{id}`, `/models`, `/health`
- **api/auth.py**: API key authentication middleware
- **api/tasks.py**: Task management with file-based storage in `data/tasks/`
- **api/stt.py**: Vosk speech recognition engine integration
- **api/models.py**: Language and model size configuration
- **api/config.py**: Environment variable and configuration management
- **api/utils.py**: Utility functions for file handling and error processing

### Task Processing Flow
1. Files uploaded to `/transcribe` endpoint with language/model_size parameters
2. Unique task ID generated, stored as JSON in `data/tasks/{task_id}.json`
3. Task status progression: `queued` → `processing` → `done`/`failed`
4. Input files stored in `data/input/`, output results in `data/output/`
5. Client polls `/tasks/{id}` endpoint for status and results

### File-based Storage Structure
```
data/
├── input/     # Uploaded audio/video files
├── output/    # Transcription results (text/VTT format)
└── tasks/     # Task metadata JSON files
```

## Development Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
pytest tests/test_stt.py -v
pytest tests/test_tasks.py -v

# Run with coverage
pytest tests/ -v --cov=api
```

### Code Quality
```bash
# Linting
flake8 api/ tests/

# Code formatting (if black is installed)
black api/ tests/
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Access API documentation
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Docker Development
```bash
# Build image
docker build -t vosk-stt-api .

# Run container
docker run -p 8000:8000 -v $(pwd)/data:/app/data vosk-stt-api
```

## Deployment

### OCI Deployment via GitHub Actions
- Triggered on push to `main` branch
- Creates deployment zip with all necessary files
- Uploads to GitHub Releases for OCI Resource Manager
- One-click deployment URL format:
  ```
  https://console.us-phoenix-1.oraclecloud.com/resourcemanager/stacks/create?region=home&zipUrl=GITHUB_RELEASE_ZIP_URL
  ```

### Manual Deployment
```bash
# Build and package for OCI
docker build -t vosk-stt-api .
zip -r deployment.zip api deploy tests requirements.txt *.md
```

## Key Dependencies
- **FastAPI 0.104.1**: Web framework
- **uvicorn 0.24.0**: ASGI server
- **vosk 0.3.44**: Speech recognition engine
- **pydub 0.25.1**: Audio file processing
- **ffmpeg-python 0.2.0**: Video/audio conversion
- **python-dotenv 1.0.0**: Environment configuration

## Model Management

### Supported Models
- **Chinese (zh)**: 
  - Small: vosk-model-small-cn-0.22 (42MB)
  - Large: vosk-model-cn-0.22 (1.3GB)
- **English (en)**: 
  - Small: vosk-model-small-en-us-0.15 (40MB)
  - Large: vosk-model-en-us-0.22 (1.8GB)
- **Japanese (ja)**: 
  - Small: vosk-model-small-ja-0.22 (48MB)
  - Large: vosk-model-ja-0.22 (1GB)

### Local Development Model Download
```bash
# Download specific language model
python scripts/download_models.py --language ja
python scripts/download_models.py --language en
python scripts/download_models.py --language zh

# Download all models
python scripts/download_models.py --all

# Custom models directory
python scripts/download_models.py --language ja --models-dir /custom/path
```

### Docker Deployment
Models are automatically downloaded during container startup via `/app/download_models.sh`

## Important Configuration
- API authentication uses `x-api-key` header
- Supports audio formats: wav, mp3
- Supports video formats: mp4, mov (audio track extracted)
- Model sizes: small, large
- Task storage: JSON files in filesystem (not database)

## GitHub Workflows
- **ci.yml**: Tests, linting on PR/push
- **deploy-oci.yml**: Build Docker image, create deployment package, release to GitHub

## API Key Management
- API keys stored in config files
- Authentication required for all endpoints except `/health`
- Use environment variables for production API key configuration

## Error Handling Patterns
- All API responses include `status` and `error` fields
- HTTP status codes: 200 (success), 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- Task failures stored in task JSON with error details

## Testing Strategy
- API endpoint testing with FastAPI TestClient
- Task processing unit tests
- Authentication/authorization testing
- File upload and processing integration tests