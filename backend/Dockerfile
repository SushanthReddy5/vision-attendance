FROM python:3.11-slim

# Runtime libs only — NO cmake, NO build-essential, NO C++ compilation
RUN apt-get update && apt-get install -y \
    libopenblas0 \
    liblapack3 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces runs as non-root user 1000
RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .

# Install dlib-binary FIRST (pre-compiled wheel, 0 C++ compilation)
# face-recognition then sees dlib already satisfied — skips compilation
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "dlib-binary==19.24.1" && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads && chown -R appuser:appuser /app

USER appuser

# HF Spaces uses port 7860
EXPOSE 7860
CMD uvicorn main:app --host 0.0.0.0 --port 7860
