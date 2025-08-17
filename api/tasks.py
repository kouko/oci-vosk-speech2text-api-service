"""
Task management module for asynchronous processing
"""
import os
import json
import uuid
import threading
from datetime import datetime
from typing import Optional, Dict
from .config import TASKS_DIR, BACKGROUND_TASK_ENABLED

def create_task(task_id: str, input_file_path: str, language: str, model_size: str):
    """
    Create a new task with initial status
    """
    # Ensure tasks directory exists
    os.makedirs(TASKS_DIR, exist_ok=True)
    
    task_data = {
        "id": task_id,
        "status": "queued",
        "input_file": input_file_path,
        "output_file": None,
        "language": language,
        "model_size": model_size,
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)
    
    return task_id

def get_task_status(task_id: str, output_format: str = "text") -> Optional[Dict]:
    """
    Get status of a specific task with optional output format
    """
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    
    if not os.path.exists(task_file):
        return None
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    
    response = {
        "task_id": task_data["id"],
        "status": task_data["status"],
        "result": None,
        "error": task_data.get("error")
    }
    
    # If task has a result, format it based on output_format
    if task_data.get("result"):
        result_data = task_data["result"]
        
        if output_format == "subtitle" or output_format == "vtt":
            # Generate VTT subtitle
            if isinstance(result_data, dict) and "vtt_segments" in result_data:
                from .utils import generate_vtt_subtitle
                vtt_content = generate_vtt_subtitle(result_data["vtt_segments"])
                response["result"] = {"subtitle": vtt_content}
            else:
                # Fallback for simple text
                response["result"] = {"subtitle": f"WEBVTT\n\n00:00:00.000 --> 00:00:10.000\n{result_data}"}
        else:
            # Default text format
            if isinstance(result_data, dict):
                response["result"] = {
                    "text": result_data.get("text", ""),
                    "confidence": result_data.get("confidence", 0.0)
                }
            else:
                # Backward compatibility
                response["result"] = {"text": str(result_data), "confidence": 0.0}
    
    return response

def update_task_status(task_id: str, status: str, result=None, error=None) -> bool:
    """
    Update task status and result
    """
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    
    if not os.path.exists(task_file):
        return False
    
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return False
    
    task_data["status"] = status
    if result is not None:
        task_data["result"] = result
    if error is not None:
        task_data["error"] = error
    task_data["updated_at"] = datetime.now().isoformat()
    
    try:
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False

def start_background_task(task_id: str, input_file_path: str, language: str, model_size: str):
    """
    Start background processing task
    """
    if not BACKGROUND_TASK_ENABLED:
        return False
    
    def process_task():
        """Background task processing function"""
        try:
            from .stt import process_audio_sync
            process_audio_sync(input_file_path, language, model_size, task_id)
        except Exception as e:
            update_task_status(task_id, "failed", error=str(e))
    
    # Start background thread
    thread = threading.Thread(target=process_task, daemon=True)
    thread.start()
    
    return True

def get_all_tasks() -> list:
    """
    Get all tasks (for debugging/admin purposes)
    """
    if not os.path.exists(TASKS_DIR):
        return []
    
    tasks = []
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith('.json'):
            task_id = filename[:-5]  # Remove .json extension
            task_status = get_task_status(task_id)
            if task_status:
                tasks.append(task_status)
    
    return tasks

def cleanup_old_tasks(days_old: int = 7):
    """
    Clean up tasks older than specified days
    """
    if not os.path.exists(TASKS_DIR):
        return 0
    
    deleted_count = 0
    current_time = datetime.now()
    
    for filename in os.listdir(TASKS_DIR):
        if filename.endswith('.json'):
            task_file = os.path.join(TASKS_DIR, filename)
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    task_data = json.load(f)
                
                created_at = datetime.fromisoformat(task_data['created_at'])
                if (current_time - created_at).days > days_old:
                    os.remove(task_file)
                    deleted_count += 1
            except (json.JSONDecodeError, IOError, KeyError, ValueError):
                # Remove corrupted task files
                os.remove(task_file)
                deleted_count += 1
    
    return deleted_count