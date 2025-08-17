"""
Utility functions for Vosk STT API
"""
import os
import json
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException
from .config import MAX_FILE_SIZE, SUPPORTED_FILE_EXTENSIONS

def create_directory_if_not_exists(path: str):
    """
    Create directory if it doesn't exist
    """
    os.makedirs(path, exist_ok=True)

def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes
    """
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0

def validate_file_type(file_name: str) -> bool:
    """
    Validate if file type is supported
    """
    return any(file_name.lower().endswith(ext) for ext in SUPPORTED_FILE_EXTENSIONS)

def validate_uploaded_file(file: UploadFile) -> dict:
    """
    Validate uploaded file for size and type
    Returns validation result with status and error message if any
    """
    # Check if file is provided
    if not file or not file.filename:
        return {
            "valid": False,
            "error": "No file provided"
        }
    
    # Check file extension
    if not validate_file_type(file.filename):
        return {
            "valid": False,
            "error": f"Unsupported file type. Supported formats: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
        }
    
    # Check file size if available
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        return {
            "valid": False,
            "error": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        }
    
    return {"valid": True}

def validate_language_and_model(language: str, model_size: str) -> dict:
    """
    Validate language and model_size parameters
    """
    from .config import SUPPORTED_LANGUAGES, SUPPORTED_MODEL_SIZES
    
    if not language:
        return {
            "valid": False,
            "error": "Language parameter is required"
        }
    
    if language not in SUPPORTED_LANGUAGES:
        return {
            "valid": False,
            "error": f"Unsupported language '{language}'. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
        }
    
    if model_size not in SUPPORTED_MODEL_SIZES:
        return {
            "valid": False,
            "error": f"Unsupported model size '{model_size}'. Supported sizes: {', '.join(SUPPORTED_MODEL_SIZES)}"
        }
    
    return {"valid": True}

def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp to ISO string
    """
    return timestamp.isoformat() if timestamp else None

def seconds_to_vtt_time(seconds: float) -> str:
    """
    Convert seconds to VTT time format (HH:MM:SS.mmm)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def generate_vtt_subtitle(segments: list) -> str:
    """
    Generate VTT subtitle format from segments
    Each segment should have: {'start': float, 'end': float, 'text': str}
    """
    vtt_content = "WEBVTT\n\n"
    
    for i, segment in enumerate(segments):
        start_time = seconds_to_vtt_time(segment['start'])
        end_time = seconds_to_vtt_time(segment['end'])
        text = segment['text'].strip()
        
        if text:  # Only add non-empty segments
            vtt_content += f"{start_time} --> {end_time}\n"
            vtt_content += f"{text}\n\n"
    
    return vtt_content

def read_json_file(file_path: str):
    """
    Safely read JSON file
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def write_json_file(file_path: str, data):
    """
    Safely write JSON file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def cleanup_temp_files(file_paths: list):
    """
    Clean up temporary files
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            pass  # Ignore errors during cleanup