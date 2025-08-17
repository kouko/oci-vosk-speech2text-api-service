"""
Model and language support module
"""
import os
from .config import MODELS_DIR

def get_supported_languages_and_models():
    """
    Get supported languages and model sizes
    """
    languages = []
    models = {}
    
    # Check what language directories exist
    if os.path.exists(MODELS_DIR):
        for lang in os.listdir(MODELS_DIR):
            lang_path = os.path.join(MODELS_DIR, lang)
            if os.path.isdir(lang_path):
                languages.append(lang)
                models[lang] = []
                
                # Check model sizes
                for model_size in os.listdir(lang_path):
                    model_size_path = os.path.join(lang_path, model_size)
                    if os.path.isdir(model_size_path):
                        models[lang].append(model_size)
    
    # Default fallback
    if not languages:
        languages = ["zh", "en", "ja"]
        models = {
            "zh": ["small", "large"],
            "en": ["small", "large"],
            "ja": ["small", "large"]
        }
    
    return {
        "languages": languages,
        "models": models
    }