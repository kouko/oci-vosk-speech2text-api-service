# Models Directory

This directory contains Vosk speech recognition models for different languages.

## Structure
```
models/
├── en/          # English models
├── ja/          # Japanese models  
├── zh/          # Chinese models
└── README.md    # This file
```

## Usage
- Models are downloaded automatically by the `scripts/download_models.py` script
- Large model files (*.zip, *.tar.gz) are excluded from git tracking
- Only model configuration files are tracked in git

## Note
Model files are large (100MB+) and are excluded from version control via .gitignore