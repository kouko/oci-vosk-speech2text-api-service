# Copilot Instructions

This project is a Vosk Speech-to-Text API service for Oracle Cloud Infrastructure (OCI).

Key requirements from the documentation:
1. RESTful API with endpoints: /transcribe, /tasks/{id}, /models, /health
2. Support for multiple languages and model sizes (small/large)
3. Asynchronous task processing with file-based storage
4. One-click deployment via OCI Resource Manager
5. Support for audio and video files (mp3, wav, mp4, mov)
6. API key authentication
7. Docker containerization

Implementation details:
- Uses FastAPI for the web framework
- Uses Vosk for speech recognition
- Uses pydub and ffmpeg for audio processing
- Stores tasks as JSON files in a data directory
- Uses environment variables for configuration
- Implements proper error handling and status management

Please follow the project structure as defined in TDD.md:
- api/ - Main API implementation
- deploy/ - Dockerfile and Terraform files
- config/ - Configuration files
- tests/ - Unit tests

The service should be deployable to OCI Free Tier with minimal configuration.