# Agri-LLaVA backend — FastAPI service.
#
# This image is CPU-only and intentionally does NOT include torch/transformers.
# In "remote" inference mode (the recommended production setup), this service
# only forwards requests to a separate GPU-hosted model service — see
# docs/deployment.md for that service's own (GPU-based) Dockerfile.
#
# If you later run INFERENCE_MODE=local (model loaded in this same process),
# you must switch the base image to a CUDA-enabled one and add torch/transformers
# /peft/bitsandbytes/accelerate to requirements.txt — do not attempt that on this
# slim image.
#
# backend/ is self-contained (backend/knowledge/crop_diseases.json is a synced
# copy of the repo-root knowledge/ file — see app/core/config.py), so this can
# build from either the repo root or backend/ as context. Building from the
# repo root keeps the command consistent with other tooling:
#   docker build -f backend/Dockerfile -t agri-llava-backend .

FROM python:3.11-slim

WORKDIR /app

# System deps needed by Pillow for image format support
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY backend/knowledge ./knowledge

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
