# 🎓 Vision Attendance — AI-Powered Face Recognition System

> Smart attendance management using real-time face recognition, built with FastAPI + Vanilla HTML/CSS/JS.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue?style=for-the-badge)](https://sushanthreddy5.github.io/vision-attendance/)
[![Backend](https://img.shields.io/badge/Backend-Render.com-purple?style=for-the-badge)](https://vision-attendance-api.onrender.com/docs)

---

## ✨ Features

- 🔍 **Real-time Face Recognition** — Mark attendance via webcam in seconds
- 👤 **Multi-angle Registration** — Register front, left & right tilt for 98%+ accuracy
- 📊 **Live Dashboard** — Present/absent stats, department analytics
- 📈 **Reports & Trends** — 30-day attendance trend charts
- 🔐 **Admin Auth** — Secure login with SHA-256 hashed passwords
- 📱 **Responsive Design** — Works on desktop & mobile

---

## 🚀 Live Links

| Service | URL |
|---------|-----|
| 🌐 Frontend | https://sushanthreddy5.github.io/vision-attendance/ |
| ⚡ Backend API | https://vision-attendance-api.onrender.com |
| 📚 API Docs | https://vision-attendance-api.onrender.com/docs |

> **Default Login:**  
> Email: `admin@vision.local`  
> Password: `admin123`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| AI/ML | `face_recognition` (dlib) |
| Database | SQLite |
| Frontend | Vanilla HTML + TailwindCSS CDN |
| Hosting | Render.com (backend) + GitHub Pages (frontend) |

---

## 🏃 Run Locally

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
# Simply open frontend/app/index.html in your browser
# Or serve with Python:
cd frontend/app
python -m http.server 3000
# Visit http://localhost:3000
```

---

## 📁 Project Structure

```
vision-attendance/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── database.py      # SQLite setup & helpers
│   ├── requirements.txt # Python deps
│   └── uploads/         # Student photos (git-ignored)
├── frontend/
│   └── app/
│       ├── index.html   # Landing page
│       ├── login.html   # Admin login
│       ├── dashboard.html
│       ├── students.html
│       ├── register.html
│       ├── capture.html # Face recognition
│       ├── reports.html
│       └── config.js    # API URL config
├── render.yaml          # Render.com deployment
└── .gitignore
```

---

## 🔧 Environment Configuration

The frontend auto-detects the environment via [`config.js`](frontend/app/config.js):
- **Local dev** → `http://localhost:8000`
- **Production** → `https://vision-attendance-api.onrender.com`

---

## 📄 License

MIT © 2026 [Sushanth Reddy](https://github.com/SushanthReddy5)

