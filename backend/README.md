# Vision Attendance Backend

This is the FastAPI backend for the Vision-Based Smart Attendance System. It uses OpenCV and the `face_recognition` library to detect and match faces, storing data in SQLite.

## Prerequisites

**Important**: The `face_recognition` library relies on `dlib`, which is a C++ library. You must have CMake and a C++ compiler installed on your system before installing the Python packages.

- **macOS**: `brew install cmake`
- **Linux (Ubuntu/Debian)**: `sudo apt-get install build-essential cmake`
- **Windows**: Install Visual Studio Build Tools with "C++ build tools" and CMake.

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

Start the FastAPI development server using uvicorn:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. You can explore the interactive API documentation at `http://localhost:8000/docs`.
