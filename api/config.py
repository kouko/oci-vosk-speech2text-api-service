"""
Configuration module for Vosk STT API
"""
import os

# Default configuration values
API_KEY = os.getenv("API_KEY", "your-api-key-here")

# Use local paths for development, Docker paths for production
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.getenv("MODELS_DIR", os.path.join(PROJECT_ROOT, "models"))
INPUT_DIR = os.getenv("INPUT_DIR", os.path.join(PROJECT_ROOT, "data", "input"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(PROJECT_ROOT, "data", "output"))
TASKS_DIR = os.getenv("TASKS_DIR", os.path.join(PROJECT_ROOT, "data", "tasks"))
CONFIG_DIR = os.getenv("CONFIG_DIR", os.path.join(PROJECT_ROOT, "config"))

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Supported languages and models
SUPPORTED_LANGUAGES = ["zh", "en", "ja"]
SUPPORTED_MODEL_SIZES = ["small", "large"]

# File upload limits
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "100")) * 1024 * 1024  # 100MB default
SUPPORTED_FILE_EXTENSIONS = ['.wav', '.mp3', '.mp4', '.mov']

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "3"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "10"))  # seconds

# Task processing
BACKGROUND_TASK_ENABLED = os.getenv("BACKGROUND_TASK_ENABLED", "true").lower() == "true"