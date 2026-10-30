#!/bin/bash
ROOT="/Users/sushanthreddy/vision-attendance"
BE="$ROOT/backend"
FE="$ROOT/frontend/app"

echo "=== 1. FILES (backend, frontend) ==="
ls -la "$BE" | grep -v venv
echo; ls -la "$FE"

echo; echo "=== 2. BACKEND SYNTAX ==="
"$BE/venv/bin/python" -m py_compile "$BE/main.py" && echo "main.py OK" || echo "main.py SYNTAX ERROR"
"$BE/venv/bin/python" -m py_compile "$BE/database.py" && echo "database.py OK" || echo "database.py SYNTAX ERROR"

echo; echo "=== 3. ROUTES ==="
grep -nE '^@app\.(get|post|put|delete|patch)' "$BE/main.py"
echo "--- duplicate routes (should be empty) ---"
grep -oE '^@app\.[a-z]+\("[^"]+"' "$BE/main.py" | sort | uniq -d
echo "--- known bug patterns (database. / face_utils / pickle) ---"
grep -nE 'database\.|face_utils|pickle' "$BE/main.py" || echo "none found"

echo; echo "=== 4. DATABASE ==="
cd "$BE" && ./venv/bin/python - <<'PY'
import sqlite3
c = sqlite3.connect("attendance.db")
print("students columns:", [r[1] for r in c.execute("PRAGMA table_info(students)")])
print("students:", c.execute("select count(*) from students").fetchone()[0])
print("attendance rows:", c.execute("select count(*) from attendance").fetchone()[0])
print("encoding storage types:", c.execute("select typeof(encoding), count(*) from students group by 1").fetchall())
print("sections:", c.execute("select section, count(*) from students group by 1").fetchall())
PY

echo; echo "=== 5. FRONTEND: broken links + leftover fake data ==="
for f in "$FE"/*.html; do
  echo "--- $(basename "$f")"
  for l in $(grep -oE 'href="[a-z]+\.html"' "$f" | sort -u | sed 's/href="//;s/"//'); do
    [ -f "$FE/$l" ] || echo "  BROKEN LINK -> $l"
  done
  grep -nE 'Aditi Sharma|Rohan Mehta|Marcus|Cam 04|East Wing|googleusercontent|Live Vision Engine|Catalis Vision Systems|Download CSV|Apply Filters|SETTINGS|Settings' "$f" | cut -c1-100
done

echo; echo "=== 6. STRAY / BACKUP FILES ==="
find "$ROOT" -path "$BE/venv" -prune -o \( -name "*.bak" -o -name "fix_*.py" -o -name "migrate_db.py" \) -print
[ -f "$FE/main.py" ] && echo "STRAY: frontend/app/main.py"
[ -f "$ROOT/reports.html" ] && echo "STRAY: root reports.html"

echo; echo "=== 7. LIVE API (needs uvicorn running) ==="
for p in /dashboard/stats /reports/stats /reports/trend /students /attendance/today; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:8000$p")
  echo "$code  $p"
done
echo "(000 = server not running)"
