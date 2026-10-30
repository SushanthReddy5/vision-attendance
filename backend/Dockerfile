FROM python:3.11-slim

# System deps for opencv + face_recognition
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dlib-binary first (pre-compiled wheel, NO C++ compilation = no OOM)
# Then install rest of requirements
COPY requirements.txt .
RUN pip install --no-cache-dir dlib-binary && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 10000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}
