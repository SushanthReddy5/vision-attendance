// Vision Attendance - API Configuration
// In development: http://localhost:8000
// In production: set to your Render.com backend URL
const API_BASE_URL = window.VISION_API_URL || 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://vision-attendance-api.onrender.com');
