"""
API tests for Vosk STT service
"""
import pytest
import os
import tempfile

# Set API key BEFORE importing any app modules
TEST_API_KEY = "test-api-key-123"
os.environ["API_KEY"] = TEST_API_KEY

# Import app after setting environment variables
from api.main import app
from starlette.testclient import TestClient

client = TestClient(app)

def get_test_headers():
    """Get headers with test API key"""
    return {"x-api-key": TEST_API_KEY}

def get_bearer_headers():
    """Get headers with Bearer token"""
    return {"Authorization": f"Bearer {TEST_API_KEY}"}

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_models_with_api_key():
    """Test models endpoint with valid API key"""
    response = client.get("/models", headers=get_test_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["error"] is None
    assert "data" in data
    assert "languages" in data["data"]
    assert "model_sizes" in data["data"]

def test_get_models_with_bearer_token():
    """Test models endpoint with Bearer token"""
    response = client.get("/models", headers=get_bearer_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_get_models_missing_api_key():
    """Test models endpoint without API key"""
    response = client.get("/models")
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "failed"
    assert "API key is required" in data["error"]

def test_get_models_invalid_api_key():
    """Test models endpoint with invalid API key"""
    response = client.get("/models", headers={"x-api-key": "invalid-key"})
    assert response.status_code == 401
    data = response.json()
    assert data["status"] == "failed"
    assert "Invalid API key" in data["error"]

def test_transcribe_missing_api_key():
    """Test transcribe without API key"""
    response = client.post("/transcribe")
    assert response.status_code == 401

def test_transcribe_missing_file():
    """Test transcribe without file"""
    response = client.post("/transcribe", headers=get_test_headers())
    assert response.status_code == 422  # Validation error

def test_transcribe_with_invalid_file_type():
    """Test transcribe with unsupported file type"""
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(b"test content")
        tmp_file.flush()
        
        with open(tmp_file.name, "rb") as f:
            response = client.post(
                "/transcribe",
                headers=get_test_headers(),
                files={"file": ("test.txt", f, "text/plain")},
                data={"language": "en", "model_size": "small"}
            )
        
        os.unlink(tmp_file.name)
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failed"
    assert "Unsupported file type" in data["error"]

def test_transcribe_with_invalid_language():
    """Test transcribe with unsupported language"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(b"fake wav content")
        tmp_file.flush()
        
        with open(tmp_file.name, "rb") as f:
            response = client.post(
                "/transcribe",
                headers=get_test_headers(),
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "invalid_lang", "model_size": "small"}
            )
        
        os.unlink(tmp_file.name)
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failed"
    assert "Unsupported language" in data["error"]

def test_transcribe_with_invalid_model_size():
    """Test transcribe with unsupported model size"""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp_file.write(b"fake wav content")
        tmp_file.flush()
        
        with open(tmp_file.name, "rb") as f:
            response = client.post(
                "/transcribe",
                headers=get_test_headers(),
                files={"file": ("test.wav", f, "audio/wav")},
                data={"language": "en", "model_size": "invalid_size"}
            )
        
        os.unlink(tmp_file.name)
    
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "failed"
    assert "Unsupported model size" in data["error"]

def test_get_task_not_found():
    """Test getting non-existent task"""
    response = client.get("/tasks/non-existent-id", headers=get_test_headers())
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "failed"
    assert "Task not found" in data["error"]

def test_get_task_with_output_format():
    """Test getting task with different output formats"""
    # Test with text format
    response = client.get(
        "/tasks/non-existent-id?output_format=text", 
        headers=get_test_headers()
    )
    assert response.status_code == 404
    
    # Test with subtitle format
    response = client.get(
        "/tasks/non-existent-id?output_format=subtitle", 
        headers=get_test_headers()
    )
    assert response.status_code == 404
    
    # Test with invalid format
    response = client.get(
        "/tasks/non-existent-id?output_format=invalid", 
        headers=get_test_headers()
    )
    assert response.status_code == 422  # Validation error