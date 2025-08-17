FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY tests/ ./tests/

# Create directories for data, models, and config
RUN mkdir -p /app/data/input /app/data/output /app/data/tasks /app/models /app/config

# Create model download script
RUN echo '#!/bin/bash\n\
echo "Downloading Vosk models..."\n\
mkdir -p /app/models/zh/small /app/models/zh/large /app/models/en/small /app/models/en/large /app/models/ja/small /app/models/ja/large\n\
\n\
# Download Chinese small model\n\
if [ ! -f "/app/models/zh/small/mfcc.conf" ]; then\n\
    echo "Downloading Chinese small model..."\n\
    cd /app/models/zh/small\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-small-cn-0.22/* .\n\
    rm -rf vosk-model-small-cn-0.22 model.zip\n\
fi\n\
\n\
# Download Chinese large model\n\
if [ ! -f "/app/models/zh/large/mfcc.conf" ]; then\n\
    echo "Downloading Chinese large model..."\n\
    cd /app/models/zh/large\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-cn-0.22/* .\n\
    rm -rf vosk-model-cn-0.22 model.zip\n\
fi\n\
\n\
# Download English small model\n\
if [ ! -f "/app/models/en/small/mfcc.conf" ]; then\n\
    echo "Downloading English small model..."\n\
    cd /app/models/en/small\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-small-en-us-0.15/* .\n\
    rm -rf vosk-model-small-en-us-0.15 model.zip\n\
fi\n\
\n\
# Download English large model\n\
if [ ! -f "/app/models/en/large/mfcc.conf" ]; then\n\
    echo "Downloading English large model..."\n\
    cd /app/models/en/large\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-en-us-0.22/* .\n\
    rm -rf vosk-model-en-us-0.22 model.zip\n\
fi\n\
\n\
# Download Japanese small model\n\
if [ ! -f "/app/models/ja/small/mfcc.conf" ]; then\n\
    echo "Downloading Japanese small model..."\n\
    cd /app/models/ja/small\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-small-ja-0.22/* .\n\
    rm -rf vosk-model-small-ja-0.22 model.zip\n\
fi\n\
\n\
# Download Japanese large model\n\
if [ ! -f "/app/models/ja/large/mfcc.conf" ]; then\n\
    echo "Downloading Japanese large model..."\n\
    cd /app/models/ja/large\n\
    wget -q "https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip" -O model.zip\n\
    unzip -q model.zip\n\
    mv vosk-model-ja-0.22/* .\n\
    rm -rf vosk-model-ja-0.22 model.zip\n\
fi\n\
\n\
echo "Models downloaded successfully"\n\
' > /app/download_models.sh && chmod +x /app/download_models.sh

# Set environment variables
ENV API_KEY=please-set-secure-api-key
ENV MODELS_DIR=/app/models
ENV INPUT_DIR=/app/data/input
ENV OUTPUT_DIR=/app/data/output
ENV TASKS_DIR=/app/data/tasks
ENV CONFIG_DIR=/app/config
ENV BACKGROUND_TASK_ENABLED=true
ENV MAX_FILE_SIZE=100
ENV RATE_LIMIT_REQUESTS=3
ENV RATE_LIMIT_WINDOW=10

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Vosk STT API service..."\n\
\n\
# Download models if they dont exist\n\
/app/download_models.sh\n\
\n\
# Start the application\n\
exec uvicorn api.main:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]