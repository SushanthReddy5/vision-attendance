FROM python:3.11-slim

# Runtime libs only — NO cmake, NO build-essential, NO C++ compilation
RUN apt-get update && apt-get install -y \
    libopenblas0 \
    liblapack3 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Step 1: Install dlib-binary FIRST (pre-compiled wheel, ~50MB download, 0 compilation)
# Step 2: face-recognition then sees dlib already satisfied — won't recompile it
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "dlib-binary==19.24.1" && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 10000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
