# Quantlix inference container — DistilGPT2 text generation
# Runs as K8s Job (one-shot) or HTTP server (local dev)
FROM python:3.12-slim

WORKDIR /app

# Install deps (CPU-only for portability; override with CUDA base for GPU)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY serve.py .

# K8s Job mode: JOB_ID, INPUT, REDIS_URL
# Server mode: no JOB_ID → HTTP on PORT (default 8080)
CMD ["python", "serve.py"]
