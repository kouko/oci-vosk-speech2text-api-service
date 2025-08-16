# OCI Vosk Speech-to-Text API Service

This project provides a deployable Vosk-based Speech-to-Text (STT) API service for Oracle Cloud Infrastructure (OCI).

## Quick Deploy

For one-click deployment to OCI:
1. Build the deployment package using GitHub Actions
2. Download the generated zip file from GitHub Releases
3. Upload to OCI Resource Manager:
   ```
   https://console.us-phoenix-1.oraclecloud.com/resourcemanager/stacks/create?region=home&zipUrl=https://github.com/YOUR_USERNAME/oci-vosk-speech2text-api-service/releases/download/v1/vosk-stt-api-deployment.zip
   ```

## Project Structure
- `api/` - Source code for the Vosk STT API service
- `deploy/` - Infrastructure as Code (Terraform/OCI Resource Manager) for deployment
- `config/` - Configuration files
- `.github/workflows/` - CI/CD workflows
- `.github/copilot-instructions.md` - Copilot instructions

## Usage
Instructions for local development, deployment, and API usage will be provided soon.