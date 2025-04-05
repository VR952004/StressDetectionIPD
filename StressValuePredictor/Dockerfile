# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory to /code/app
WORKDIR /code/app

# Environment variables to avoid caching & reduce timeouts
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_DEFAULT_TIMEOUT=1000

# (Optional) Install basic build tools in case you need them
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install core Python packages
RUN pip install --no-cache-dir fastapi uvicorn scikit-learn joblib

# Install CPU-only PyTorch, torchvision, and torchaudio from the official CPU index
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install Sentence Transformers
RUN pip install --no-cache-dir sentence-transformers

# Copy the entire 'app' folder contents into the container's /code/app
COPY app/ .

# Expose port 8000 (FastAPI default)
EXPOSE 8002

# Launch the API using Uvicorn
CMD ["uvicorn", "stress_api:app", "--host", "0.0.0.0", "--port", "8002"]