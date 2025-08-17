# OCI Vosk Speech-to-Text API Service Deployment

This directory contains all the necessary files for deploying this Vosk Speech-to-Text API service to Oracle Cloud Infrastructure (OCI) using one-click deployment.

## Files

### Dockerfile
- Container configuration for running the API service
- Installs all required dependencies including ffmpeg for audio processing

### main.tf
- Terraform configuration for OCI infrastructure deployment
- Creates VM instance with proper security rules
- Sets up networking and resource management

### variables.tf
- Terraform variables for deployment parameters:
  - VM shape and configuration
  - Network settings
  - API key for authentication

## Deployment Process

1. Package all files into a zip archive
2. Upload to OCI Resource Manager
3. Configure deployment parameters (VM shape, API key)
4. Deploy using the OCI Console

## Requirements

- OCI Account with Free Tier resources
- API key for authentication
- ZIP file containing all source code, Dockerfile, and Terraform files

## Configuration

Environment variables can be set during deployment:
- API_KEY: Authentication key for API access
- MODEL_PATH: Path to Vosk model files
- INPUT_DIR: Directory for uploaded audio files
- OUTPUT_DIR: Directory for transcription results