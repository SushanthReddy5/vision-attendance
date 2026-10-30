import os
import cv2
import numpy as np
import face_recognition
import json
from datetime import datetime, date
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database import get_db, hash_password

app = FastAPI(title="Vision Attendance Backend")

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded images as static files so frontend can display them
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def decode_and_encode(upload_bytes: bytes, label: str):
    nparr = np.frombuffer(upload_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail=f"Invalid image file ({label})")
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img)
    if len(face_locations) == 0:
        raise HTTPException(status_code=400, detail=f"No face detected in the {label} photo")
    if len(face_locations) > 1:
        raise HTTPException(status_code=400, detail=f"Multiple faces detected in {label} photo — please capture only one face.")
    encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
    return img, encoding


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/students")
async def register_student(
    name: str = Form(...),
    roll_no: str = Form(...),
    department: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    section: str = Form(""),
    photo: UploadFile = File(...),
    photo_left: UploadFile = File(None),
    photo_right: UploadFile = File(None),
):
    # Front photo is required
    front_bytes = await photo.read()
    img, front_encoding = decode_and_encode(front_bytes, "front")
    encodings = [front_encoding]

    # Save front photo
    safe_roll = roll_no.replace("/", "_").replace("\\", "_")
    front_filename = f"{safe_roll}_front.jpg"
    front_path = os.path.join(UPLOAD_DIR, front_filename)
    cv2.imwrite(front_path, img)

    # Left tilt (optional)
    left_path = None
    if photo_left is not None:
        left_bytes = await photo_left.read()
        if left_bytes:
            left_img, left_encoding = decode_and_encode(left_bytes, "left tilt")
            encodings.append(left_encoding)
            left_filename = f"{safe_roll}_left.jpg"
            left_path = os.path.join(UPLOAD_DIR, left_filename)
            cv2.imwrite(left_path, left_img)

    # Right tilt (optional)
    right_path = None
    if photo_right is not None:
        right_bytes = await photo_right.read()
        if right_bytes:
            right_img, right_encoding = decode_and_encode(right_bytes, "right tilt")
            encodings.append(right_encoding)
            right_filename = f"{safe_roll}_right.jpg"
            right_path = os.path.join(UPLOAD_DIR, right_filename)
            cv2.imwrite(right_path, right_img)

    # Average all angles into a robust single encoding
    final_encoding = np.mean(encodings, axis=0)
    encoding_json = json.dumps(final_encoding.tolist())

    # Save to database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Student with roll number {roll_no} already exists.")

    cursor.execute('''
        INSERT INTO students (name, roll_no, department, section, email, phone, photo_path, photo_left_path, photo_right_path, encoding)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, roll_no, department, section, email, phone, front_path, left_path, right_path, encoding_json))

    student_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "message": "Student registered successfully",
        "id": student_id,
        "angles_captured": len(encodings),
    }


@app.get("/students")
def get_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, department, section, email, phone, photo_path, photo_left_path, photo_right_path FROM students ORDER BY name")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students


@app.get("/students/search")
def search_students(q: str = Query("", description="Search query")):
    """Search students by name, roll_no, department, email — partial, case-insensitive."""
    conn = get_db()
    cursor = conn.cursor()
    term = f"%{q.strip()}%"
    cursor.execute("""
        SELECT id, name, roll_no, department, section, email, phone, photo_path, photo_left_path, photo_right_path
        FROM students
        WHERE name LIKE ? OR roll_no LIKE ? OR department LIKE ? OR email LIKE ? OR section LIKE ?
        ORDER BY name
        LIMIT 20
    """, (term, term, term, term, term))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


@app.put("/students/{student_id}")
async def update_student(
    student_id: int,
    name: str = Form(...),
    roll_no: str = Form(...),
    department: str = Form(""),
    section: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    photo: UploadFile = File(None),
    photo_left: UploadFile = File(None),
    photo_right: UploadFile = File(None),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, encoding, photo_path, photo_left_path, photo_right_path FROM students WHERE id = ?", (student_id,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")

    cur.execute("SELECT id FROM students WHERE roll_no = ? AND id != ?", (roll_no, student_id))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Roll number {roll_no} is already used by another student.")

    safe_roll = roll_no.replace("/", "_").replace("\\", "_")

    # Start with existing encoding list; rebuild from any new photos + keep old base
    existing_encoding = np.array(json.loads(existing["encoding"]))
    new_encoding = existing_encoding  # will be overwritten only if front changes

    front_path = existing["photo_path"]
    left_path = existing["photo_left_path"]
    right_path = existing["photo_right_path"]

    # Collect per-angle encodings for re-averaging if any photo updated
    encodings = []
    updated_any_photo = False

    # Front photo
    if photo is not None and photo.filename:
        front_bytes = await photo.read()
        if front_bytes:
            front_img, front_enc = decode_and_encode(front_bytes, "front")
            front_filename = f"{safe_roll}_front.jpg"
            front_path = os.path.join(UPLOAD_DIR, front_filename)
            cv2.imwrite(front_path, front_img)
            encodings.append(front_enc)
            updated_any_photo = True

    # Left photo
    if photo_left is not None and photo_left.filename:
        left_bytes = await photo_left.read()
        if left_bytes:
            left_img, left_enc = decode_and_encode(left_bytes, "left tilt")
            left_filename = f"{safe_roll}_left.jpg"
            left_path = os.path.join(UPLOAD_DIR, left_filename)
            cv2.imwrite(left_path, left_img)
            encodings.append(left_enc)
            updated_any_photo = True

    # Right photo
    if photo_right is not None and photo_right.filename:
        right_bytes = await photo_right.read()
        if right_bytes:
            right_img, right_enc = decode_and_encode(right_bytes, "right tilt")
            right_filename = f"{safe_roll}_right.jpg"
            right_path = os.path.join(UPLOAD_DIR, right_filename)
            cv2.imwrite(right_path, right_img)
            encodings.append(right_enc)
            updated_any_photo = True

    if updated_any_photo and encodings:
        new_encoding = np.mean(encodings, axis=0)
    else:
        new_encoding = existing_encoding

    encoding_json = json.dumps(new_encoding.tolist())

    cur.execute("""
        UPDATE students
        SET name=?, roll_no=?, department=?, section=?, email=?, phone=?,
            photo_path=?, photo_left_path=?, photo_right_path=?, encoding=?
        WHERE id=?
    """, (name, roll_no, department, section, email, phone,
          front_path, left_path, right_path, encoding_json, student_id))
    conn.commit()
    conn.close()
    return {"message": "Student updated successfully"}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT photo_path, photo_left_path, photo_right_path FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    for path_key in ["photo_path", "photo_left_path", "photo_right_path"]:
        p = row[path_key]
        if p and os.path.exists(p):
            os.remove(p)
    return {"message": "Student deleted successfully"}


# ─────────────────────────────────────────────────────────────────────────────
# RECOGNITION & ATTENDANCE
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/recognize")
async def recognize_face(frame: UploadFile = File(...)):
    contents = await frame.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img)
    if len(face_locations) == 0:
        return {"matched": False, "message": "No face detected"}

    unknown_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roll_no, department, encoding FROM students")
    students = cursor.fetchall()

    if not students:
        conn.close()
        return {"matched": False, "message": "No registered students found"}

    known_encodings = [np.array(json.loads(row["encoding"])) for row in students]
    known_metadata = [dict(row) for row in students]

    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)
    best_match_index = int(np.argmin(face_distances))
    best_distance = face_distances[best_match_index]

    threshold = 0.5
    if best_distance <= threshold:
        match = known_metadata[best_match_index]
        confidence = (1 - best_distance) * 100
        student_id = match["id"]
        today = date.today().isoformat()

        cursor.execute('''
            SELECT id FROM attendance
            WHERE student_id = ? AND date(timestamp) = ?
        ''', (student_id, today))
        already_marked = cursor.fetchone() is not None
        newly_marked = False

        if not already_marked:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO attendance (student_id, timestamp, status, confidence)
                VALUES (?, ?, ?, ?)
            ''', (student_id, now, "Present", float(confidence)))
            conn.commit()
            newly_marked = True

        conn.close()
        return {
            "matched": True,
            "newly_marked": newly_marked,
            "student": {
                "name": match["name"],
                "roll_no": match["roll_no"],
                "department": match["department"],
                "confidence": round(confidence, 2),
            }
        }
    else:
        conn.close()
        return {"matched": False, "message": "Face not recognized"}


@app.get("/attendance/today")
def get_today_attendance():
    conn = get_db()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute('''
        SELECT a.id, a.timestamp, a.status, a.confidence,
               s.name, s.roll_no, s.department
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE date(a.timestamp) = ?
        ORDER BY a.timestamp DESC
    ''', (today,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records


# ─────────────────────────────────────────────────────────────────────────────
# REPORTS & DASHBOARD STATS
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/reports/stats")
def reports_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as c FROM students")
    total = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) as c FROM attendance WHERE date(timestamp) = date('now')")
    present = cur.fetchone()["c"]

    cur.execute("SELECT AVG(confidence) as avg FROM attendance WHERE confidence IS NOT NULL")
    row = cur.fetchone()
    avg_conf = round(row["avg"], 1) if row["avg"] else 0.0

    absent = max(total - present, 0)
    absence_rate = round((absent / total) * 100, 1) if total else 0.0

    cur.execute("""
        SELECT s.department,
               COUNT(DISTINCT a.student_id) as present_count,
               COUNT(DISTINCT s.id) as total_count
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND date(a.timestamp) = date('now')
        GROUP BY s.department
    """)
    dept_rows = cur.fetchall()
    by_dept = []
    for r in dept_rows:
        pct = round((r["present_count"] / r["total_count"]) * 100) if r["total_count"] else 0
        by_dept.append({"department": r["department"] or "Unassigned", "pct": pct,
                        "present": r["present_count"], "total": r["total_count"]})

    cur.execute("""
        SELECT s.id, s.name, s.roll_no, s.department,
               COUNT(a.id) as absences
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
          AND date(a.timestamp) != date('now')
        WHERE s.id NOT IN (
            SELECT student_id FROM attendance WHERE date(timestamp) = date('now')
        )
        GROUP BY s.id
        ORDER BY absences DESC
        LIMIT 10
    """)
    absentees = [dict(r) for r in cur.fetchall()]

    conn.close()
    return {
        "total_students": total,
        "present_today": present,
        "absent_today": absent,
        "avg_confidence": avg_conf,
        "absence_rate": absence_rate,
        "by_department": by_dept,
        "absentees": absentees,
    }


@app.get("/dashboard/stats")
def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM students")
    total_students = cursor.fetchone()["count"]

    today = date.today().isoformat()
    cursor.execute(
        "SELECT COUNT(DISTINCT student_id) as count FROM attendance WHERE date(timestamp) = ? AND status = 'Present'",
        (today,)
    )
    present_today = cursor.fetchone()["count"]
    absent_today = max(total_students - present_today, 0)
    avg_pct = round((present_today / total_students) * 100, 1) if total_students > 0 else 0

    conn.close()
    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "average_attendance_pct": avg_pct,
    }


@app.get("/reports/trend")
def reports_trend():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM students")
    total_students = cur.fetchone()["c"]
    cur.execute("""
        SELECT date(timestamp) as day, COUNT(DISTINCT student_id) as present_count
        FROM attendance
        GROUP BY date(timestamp)
        ORDER BY day DESC
        LIMIT 30
    """)
    rows = [dict(r) for r in cur.fetchall()]
    rows.reverse()
    conn.close()
    return {"trend": rows, "total_students": total_students}



# ─────────────────────────────────────────────────────────────────────────────
# ADMIN PROFILE ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/admin/profile")
def get_admin_profile():
    """Returns the first (and only) admin profile — no password hash exposed."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, name, role, created_at FROM admin_users ORDER BY id LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No admin account found")
    return dict(row)


@app.put("/admin/profile")
async def update_admin_profile(
    name: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM admin_users ORDER BY id LIMIT 1")
    admin = cur.fetchone()
    if not admin:
        conn.close()
        raise HTTPException(status_code=404, detail="No admin account found")

    # Check email uniqueness (against other admins if any)
    cur.execute("SELECT id FROM admin_users WHERE email = ? AND id != ?", (email, admin["id"]))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="That email is already in use.")

    cur.execute(
        "UPDATE admin_users SET name=?, email=?, username=? WHERE id=?",
        (name.strip(), email.strip(), username.strip(), admin["id"])
    )
    conn.commit()
    conn.close()
    return {"message": "Profile updated successfully"}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@app.post("/admin/change-password")
def change_admin_password(body: ChangePasswordRequest):
    if len(body.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM admin_users ORDER BY id LIMIT 1")
    admin = cur.fetchone()
    if not admin:
        conn.close()
        raise HTTPException(status_code=404, detail="No admin account found")

    if hash_password(body.current_password) != admin["password_hash"]:
        conn.close()
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    new_hash = hash_password(body.new_password)
    cur.execute("UPDATE admin_users SET password_hash=? WHERE id=?", (new_hash, admin["id"]))
    conn.commit()
    conn.close()
    return {"message": "Password changed successfully"}


@app.post("/admin/login")
async def admin_login(
    email: str = Form(...),
    password: str = Form(...),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, role FROM admin_users WHERE email = ? AND password_hash = ?",
                (email.strip(), hash_password(password)))
    admin = cur.fetchone()
    conn.close()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"message": "Login successful", "name": admin["name"], "role": admin["role"]}
