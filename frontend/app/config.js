// Vision Attendance - API Configuration
// In development: http://localhost:8000
// In production: Hugging Face Spaces backend
const API_BASE_URL = window.VISION_API_URL ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://sushanthreddy5-vision-attendance-api.hf.space');
