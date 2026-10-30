import re

path = '/Users/sushanthreddy/vision-attendance/backend/main.py'
with open(path) as f:
    content = f.read()

new_block = '''@app.put("/students/{student_id}")
async def update_student(
    student_id: int,
    name: str = Form(...),
    roll_no: str = Form(...),
    department: str = Form(""),
    section: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    photo: UploadFile = File(None),
):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM students WHERE id = ?", (student_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    cur.execute("SELECT id FROM students WHERE roll_no = ? AND id != ?", (roll_no, student_id))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Roll number {roll_no} is already used by another student.")

    if photo is not None and photo.filename:
        contents = await photo.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid image file")
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_img)
        if len(locations) != 1:
            conn.close()
            raise HTTPException(status_code=400, detail="Photo must contain exactly one clear face.")
        encoding = face_recognition.face_encodings(rgb_img, locations)[0]
        filepath = os.path.join(UPLOAD_DIR, f"{roll_no}_profile.jpg")
        cv2.imwrite(filepath, img)
        cur.execute("""
            UPDATE students SET name=?, roll_no=?, department=?, section=?, email=?, phone=?, photo_path=?, encoding=?
            WHERE id=?
        """, (name, roll_no, department, section, email, phone, filepath, json.dumps(encoding.tolist()), student_id))
    else:
        cur.execute("""
            UPDATE students SET name=?, roll_no=?, department=?, section=?, email=?, phone=?
            WHERE id=?
        """, (name, roll_no, department, section, email, phone, student_id))

    conn.commit()
    conn.close()
    return {"message": "Student updated successfully"}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT photo_path FROM students WHERE id = ?", (student_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    cur.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    if row["photo_path"] and os.path.exists(row["photo_path"]):
        os.remove(row["photo_path"])
    return {"message": "Student deleted successfully"}
'''

start = content.find('@app.put("/students/{student_id}")')
if start == -1:
    print("ABORT: PUT route not found, nothing changed.")
else:
    tail = content[start:]
    if len(re.findall(r'^@app\.', tail, re.M)) != 2:
        print("ABORT: unexpected routes after PUT (expected only PUT and DELETE), nothing changed.")
    else:
        with open(path, 'w') as f:
            f.write(content[:start] + new_block)
        print("PUT and DELETE routes rewritten")
