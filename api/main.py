"""
Main API entry point for Vosk Speech-to-Text service
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import uuid
from datetime import datetime
from .auth import verify_api_key
from .tasks import create_task, get_task_status, start_background_task
from .stt import process_audio_file
from .models import get_supported_languages_and_models
from .utils import validate_uploaded_file, validate_language_and_model
from .config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, INPUT_DIR

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Vosk STT API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_error_response(error_message: str):
    """Create standardized error response"""
    return {"status": "failed", "error": error_message, "data": None}

def create_success_response(data: dict):
    """Create standardized success response"""
    return {"status": "success", "error": None, "data": data}

@app.post("/transcribe")
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_WINDOW} seconds")
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form(...),
    model_size: str = Form("small"),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload audio file and submit STT task
    """
    try:
        # Validate file
        file_validation = validate_uploaded_file(file)
        if not file_validation["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=create_error_response(file_validation["error"])
            )
        
        # Validate language and model parameters
        param_validation = validate_language_and_model(language, model_size)
        if not param_validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(param_validation["error"])
            )
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Save uploaded file
        input_file_path = os.path.join(INPUT_DIR, f"{task_id}_{file.filename}")
        
        with open(input_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create task record
        create_task(task_id, input_file_path, language, model_size)
        
        # Start background processing
        start_background_task(task_id, input_file_path, language, model_size)
        
        return create_success_response({
            "task_id": task_id,
            "status": "queued"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=create_error_response(f"Internal server error: {str(e)}")
        )

@app.get("/tasks/{task_id}")
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_WINDOW} seconds")
async def get_task(
    request: Request,
    task_id: str,
    output_format: str = Query("text", pattern="^(text|subtitle|vtt)$"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get task status and result
    """
    try:
        # Check task status
        status = get_task_status(task_id, output_format)
        
        if not status:
            raise HTTPException(
                status_code=404, 
                detail=create_error_response("Task not found")
            )
        
        # Add status wrapper for consistency
        if status.get("status") == "failed":
            return create_error_response(status.get("error", "Unknown error"))
        else:
            return create_success_response(status)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(f"Internal server error: {str(e)}")
        )

@app.get("/models")
@limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_WINDOW} seconds")
async def get_models(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get supported languages and models
    """
    try:
        models_data = get_supported_languages_and_models()
        # Convert to TDD specified format
        tdd_format = {
            "languages": models_data["languages"],
            "model_sizes": ["small", "large"]
        }
        return create_success_response(tdd_format)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=create_error_response(f"Failed to get models: {str(e)}")
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint - no authentication required
    """
    return {"status": "ok"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    from fastapi.responses import JSONResponse
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=create_error_response(exc.detail))

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Rate limit exception handler"""
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=429, content=create_error_response(f"Rate limit exceeded: {exc.detail}"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)