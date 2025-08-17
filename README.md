# OCI Vosk Speech-to-Text API Service

This project provides a deployable Vosk-based Speech-to-Text (STT) API service for Oracle Cloud Infrastructure (OCI).

## Quick Deploy

### 🚀 One-Click Deployment to OCI

[![Deploy to Oracle Cloud](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://console.us-phoenix-1.oraclecloud.com/resourcemanager/stacks/create?region=home&zipUrl=https://github.com/kouko/oci-vosk-speech2text-api-service/releases/latest/download/vosk-stt-api-deployment.zip)

**Required Setup:**
1. OCI Account (Free Tier supported! 🆓)
2. SSH key pair for secure access  
3. Choose your secure API key (16+ characters)

> **Note**: This project is designed for personal use with HTTP API. Suitable for development, learning, and testing purposes.

**Deployment Process:**
1. 🖱️ Click the "Deploy to Oracle Cloud" button above
2. 🔑 Sign in to your OCI account (if not already signed in)
3. 📋 Fill out the deployment form:
   - **Compartment**: Select your target compartment
   - **Availability Domain**: Choose any available AD
   - **SSH Public Key**: Paste your public SSH key
   - **API Key**: Enter a secure API key (16+ characters)
   - **Instance Shape**: Choose VM shape 
     - 🆓 **Free Tier**: A1.Flex (2 OCPU/8GB) or E2.1.Micro (1 OCPU/1GB)
     - 💰 **Paid**: E3.Flex, E4.Flex for better performance
   - **Network**: Keep "Create New VCN" checked (recommended)
4. 🚀 Click "Create" to start deployment
5. ⏳ Wait 5-10 minutes for complete setup
6. 🎉 Access your API at the provided endpoint!

**After Deployment:**
- ✅ VM instance with proper security settings
- ✅ Vosk models automatically downloaded
- ✅ STT API service running on port 8000
- ✅ API documentation available at `/docs`
- ✅ Complete usage instructions provided

### Manual Deployment Steps (Alternative)
If you prefer manual deployment:
1. Download the latest release from [GitHub Releases](https://github.com/kouko/oci-vosk-speech2text-api-service/releases)
2. Upload ZIP to OCI Resource Manager
3. Configure parameters and deploy

## 🎯 Quick Usage Examples

After deployment, your API will be available at `http://YOUR_INSTANCE_IP:8000`

### Basic API Calls

```bash
# Health check
curl http://YOUR_INSTANCE_IP:8000/health

# Get supported languages and models
curl -H "x-api-key: YOUR_API_KEY" http://YOUR_INSTANCE_IP:8000/models

# Transcribe audio file
curl -X POST \
     -H "x-api-key: YOUR_API_KEY" \
     -F "file=@audio.wav" \
     -F "language=en" \
     -F "model_size=small" \
     http://YOUR_INSTANCE_IP:8000/transcribe
```

### Supported Features

- 🌍 **Languages**: Chinese (zh), English (en), Japanese (ja)
- 📏 **Model Sizes**: small (faster), large (more accurate)
- 🔄 **Processing**: Sync and async modes
- 📄 **Output Formats**: JSON, VTT subtitles
- 🎵 **Audio Formats**: WAV, MP3, MP4, FLAC, AAC

## 📂 Project Structure

- `api/` - Source code for the Vosk STT API service
- `deploy/` - Infrastructure as Code (Terraform/OCI Resource Manager) for deployment
- `tests/` - Automated test suite
- `.github/workflows/` - CI/CD workflows for automated deployment
- `models/` - Vosk model files (auto-downloaded)
- `data/` - Runtime data directories

## 🔧 Development & Customization

For local development and customization, see the detailed documentation in each directory.