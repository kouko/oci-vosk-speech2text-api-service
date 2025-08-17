"""
Task management tests for Vosk STT service
"""
import os
import json
import pytest
from api.tasks import create_task, get_task_status, update_task_status
from api.config import TASKS_DIR

def test_create_task():
    """Test creating a new task"""
    task_id = "test-task-123"
    
    # Clean up any existing test task
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    if os.path.exists(task_file):
        os.remove(task_file)
    
    # Create task
    result = create_task(task_id, "/test/input.wav", "zh", "small")
    
    # Verify task was created
    assert result == task_id
    assert os.path.exists(task_file)
    
    # Read and verify task data
    with open(task_file, 'r') as f:
        task_data = json.load(f)
    
    assert task_data["id"] == task_id
    assert task_data["status"] == "queued"
    
    # Clean up
    os.remove(task_file)

def test_get_task_status():
    """Test getting task status"""
    task_id = "test-task-456"
    
    # Clean up any existing test task
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    if os.path.exists(task_file):
        os.remove(task_file)
    
    # Try to get non-existent task
    status = get_task_status(task_id)
    assert status is None
    
    # Create task and verify
    create_task(task_id, "/test/input.wav", "zh", "small")
    status = get_task_status(task_id)
    
    assert status is not None
    assert status["task_id"] == task_id
    assert status["status"] == "queued"
    
    # Clean up
    os.remove(task_file)

def test_update_task_status():
    """Test updating task status"""
    task_id = "test-task-789"
    
    # Clean up any existing test task
    task_file = os.path.join(TASKS_DIR, f"{task_id}.json")
    if os.path.exists(task_file):
        os.remove(task_file)
    
    # Create task
    create_task(task_id, "/test/input.wav", "zh", "small")
    
    # Update status
    result = update_task_status(task_id, "processing", "test result")
    
    assert result is True
    
    # Verify update
    status = get_task_status(task_id)
    assert status["status"] == "processing"
    assert status["result"]["text"] == "test result"
    assert status["result"]["confidence"] == 0.0
    
    # Clean up
    os.remove(task_file)