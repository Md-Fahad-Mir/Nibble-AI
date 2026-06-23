###############################################################################
# Nibble AI — receipt-OCR service (FastAPI + Tesseract). Internal-only:
# reached by the backend over the compose network at http://ai:8001; never
# published to the host or exposed through nginx.
###############################################################################
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# OCR + OpenCV runtime libs. tesseract-ocr is the engine; libgl1 + libglib2.0-0
# are REQUIRED by opencv-python (without them `import cv2` fails at runtime).
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code:
#   offline.py — Tesseract engine (default, no API key, no network)
#   code.py    — GPT-4V alternative (available but NOT wired into the API;
#                enabling it requires editing receipt_api.py + OPENAI_API_KEY)
COPY receipt_api.py offline.py code.py ./

# Unprivileged runtime user (fixed uid/gid; no home, no login shell).
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin app
USER app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8001/health').status==200 else 1)" || exit 1

# No --reload in the image; multiple workers for CPU-bound OCR.
CMD ["python", "-m", "uvicorn", "receipt_api:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]
