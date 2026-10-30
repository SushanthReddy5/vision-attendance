import re

with open('main.py', 'r') as f:
    content = f.read()

old_func = '''@app.post("/students")
async def register_student(
    name: str = Form(...),
    roll_no: str = Form(...),
    department: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    photo: UploadFile = File(...)
):
    # Read image
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Convert to RGB (face_recognition expects RGB)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect face and compute encoding
    face_locations = face_recognition.face_locations(rgb_img)
    if len(face_locations) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the photo")
    if len(face_locations) > 1:
        raise HTTPException(status_code=400, detail="Multiple faces detected. Please upload a photo with only one face.")
        
    face_encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
    
    # Save the photo
    filename = f"{roll_no}_{photo.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    cv2.imwrite(filepath, img)
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if roll_no already exists
    cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Student with roll number {roll_no} already exists.")
    
    # Serialize encoding to JSON
    encoding_list = face_encoding.tolist()
    encoding_json = json.dumps(encoding_list)
    
    cursor.execute(\'\'\'
        INSERT INTO students (name, roll_no, department, email, phone, photo_path, encoding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    \'\'\', (name, roll_no, department, email, phone, filepath, encoding_json))
    
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"message": "Student registered successfully", "id": student_id}'''

new_func = '''@app.post("/students")
async def register_student(
    name: str = Form(...),
    roll_no: str = Form(...),
    department: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    photo: UploadFile = File(...),
    photo_left: UploadFile = File(None),
    photo_right: UploadFile = File(None)
):
    def decode_and_encode(upload_bytes, label):
        nparr = np.frombuffer(upload_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail=f"Invalid image file ({label})")
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_img)
        if len(face_locations) == 0:
            raise HTTPException(status_code=400, detail=f"No face detected in the {label} photo")
        if len(face_locations) > 1:
            raise HTTPException(status_code=400, detail=f"Multiple faces detected in the {label} photo. Please capture only one face.")
        encoding = face_recognition.face_encodings(rgb_img, face_locations)[0]
        return img, encoding

    # Front photo is required
    front_bytes = await photo.read()
    img, front_encoding = decode_and_encode(front_bytes, "front")
    encodings = [front_encoding]

    # Left/right tilt photos are optional but improve accuracy if provided
    if photo_left is not None:
        left_bytes = await photo_left.read()
        if left_bytes:
            _, left_encoding = decode_and_encode(left_bytes, "left tilt")
            encodings.append(left_encoding)

    if photo_right is not None:
        right_bytes = await photo_right.read()
        if right_bytes:
            _, right_encoding = decode_and_encode(right_bytes, "right tilt")
            encodings.append(right_encoding)

    # Average all captured angles into a single robust encoding
    final_encoding = np.mean(encodings, axis=0)

    # Save the front photo as the reference image
    filename = f"{roll_no}_{photo.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    cv2.imwrite(filepath, img)

    # Save to database
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Student with roll number {roll_no} already exists.")

    encoding_list = final_encoding.tolist()
    encoding_json = json.dumps(encoding_list)

    cursor.execute(\'\'\'
        INSERT INTO students (name, roll_no, department, email, phone, photo_path, encoding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    \'\'\', (name, roll_no, department, email, phone, filepath, encoding_json))

    student_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"message": "Student registered successfully", "id": student_id, "angles_captured": len(encodings)}'''

if old_func not in content:
    print("⚠️  ZERO MATCHES — old function text not found exactly. Aborting, no changes made.")
else:
    content = content.replace(old_func, new_func)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ /students endpoint upgraded to multi-angle averaging")
