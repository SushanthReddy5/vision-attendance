/**
 * Vision Attendance — Demo Mode
 * When the real backend is unreachable, this intercepts all fetch() calls
 * and returns realistic mock data so the demo looks fully functional.
 */

// Auto-set login session — demo always starts logged in
sessionStorage.setItem('va_logged_in', '1');

const DEMO_STUDENTS = [
  { id:1, name:'Arjun Sharma',    roll_no:'CS21001', department:'Computer Science', section:'A', email:'arjun@college.edu',    phone:'9876543210', photo_path:null },
  { id:2, name:'Priya Reddy',     roll_no:'CS21002', department:'Computer Science', section:'A', email:'priya@college.edu',    phone:'9876543211', photo_path:null },
  { id:3, name:'Rahul Mehta',     roll_no:'EC21001', department:'Electronics',      section:'B', email:'rahul@college.edu',    phone:'9876543212', photo_path:null },
  { id:4, name:'Sneha Patel',     roll_no:'ME21001', department:'Mechanical',       section:'A', email:'sneha@college.edu',    phone:'9876543213', photo_path:null },
  { id:5, name:'Vikram Singh',    roll_no:'CS21003', department:'Computer Science', section:'B', email:'vikram@college.edu',   phone:'9876543214', photo_path:null },
  { id:6, name:'Ananya Das',      roll_no:'EC21002', department:'Electronics',      section:'A', email:'ananya@college.edu',   phone:'9876543215', photo_path:null },
  { id:7, name:'Karthik Nair',    roll_no:'CS21004', department:'Computer Science', section:'A', email:'karthik@college.edu',  phone:'9876543216', photo_path:null },
  { id:8, name:'Divya Iyer',      roll_no:'ME21002', department:'Mechanical',       section:'B', email:'divya@college.edu',    phone:'9876543217', photo_path:null },
  { id:9, name:'Rohan Gupta',     roll_no:'CS21005', department:'Computer Science', section:'B', email:'rohan@college.edu',    phone:'9876543218', photo_path:null },
  { id:10,name:'Lakshmi Krishnan',roll_no:'EC21003', department:'Electronics',      section:'A', email:'lakshmi@college.edu',  phone:'9876543219', photo_path:null },
];

const today = new Date();
const fmt = d => d.toISOString().slice(0,10);

const DEMO_ATTENDANCE = [
  { id:1, name:'Arjun Sharma',    roll_no:'CS21001', department:'Computer Science', status:'Present', confidence:94.2, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 8,12).toISOString() },
  { id:2, name:'Priya Reddy',     roll_no:'CS21002', department:'Computer Science', status:'Present', confidence:91.5, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 8,25).toISOString() },
  { id:3, name:'Rahul Mehta',     roll_no:'EC21001', department:'Electronics',      status:'Present', confidence:88.7, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 8,43).toISOString() },
  { id:4, name:'Vikram Singh',    roll_no:'CS21003', department:'Computer Science', status:'Present', confidence:96.1, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9, 5).toISOString() },
  { id:5, name:'Ananya Das',      roll_no:'EC21002', department:'Electronics',      status:'Present', confidence:89.3, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9,18).toISOString() },
  { id:6, name:'Karthik Nair',    roll_no:'CS21004', department:'Computer Science', status:'Present', confidence:92.8, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9,30).toISOString() },
  { id:7, name:'Lakshmi Krishnan',roll_no:'EC21003', department:'Electronics',      status:'Present', confidence:87.4, timestamp: new Date(today.getFullYear(), today.getMonth(), today.getDate(), 9,47).toISOString() },
];

const DEMO_TREND = Array.from({length:7}, (_,i) => {
  const d = new Date(); d.setDate(d.getDate() - (6-i));
  return { day: fmt(d), present_count: 5 + Math.floor(Math.random()*4) };
});

const DEMO_API = {
  '/admin/login':    () => ({ message:'Login successful', name:'Admin', role:'System Administrator' }),
  '/admin/profile':  () => ({ id:1, username:'admin', email:'admin@vision.local', name:'Admin', role:'System Administrator', created_at:'2026-01-01T00:00:00' }),
  '/students':       () => DEMO_STUDENTS,
  '/students/search':q => DEMO_STUDENTS.filter(s =>
    s.name.toLowerCase().includes(q) || s.roll_no.toLowerCase().includes(q) ||
    s.department.toLowerCase().includes(q)),
  '/attendance/today': () => DEMO_ATTENDANCE,
  '/dashboard/stats':  () => ({
    total_students: DEMO_STUDENTS.length,
    present_today: DEMO_ATTENDANCE.length,
    absent_today: DEMO_STUDENTS.length - DEMO_ATTENDANCE.length,
    average_attendance_pct: Math.round((DEMO_ATTENDANCE.length / DEMO_STUDENTS.length) * 100),
  }),
  '/reports/stats': () => ({
    total_students: DEMO_STUDENTS.length,
    present_today: DEMO_ATTENDANCE.length,
    absent_today: DEMO_STUDENTS.length - DEMO_ATTENDANCE.length,
    avg_confidence: 91.4,
    absence_rate: Math.round(((DEMO_STUDENTS.length - DEMO_ATTENDANCE.length) / DEMO_STUDENTS.length) * 100),
    by_department: [
      { department:'Computer Science', pct:80, present:4, total:5 },
      { department:'Electronics',      pct:75, present:3, total:4 },
      { department:'Mechanical',       pct:50, present:1, total:2 },
    ],
    absentees: DEMO_STUDENTS.filter(s => !DEMO_ATTENDANCE.find(a => a.roll_no === s.roll_no))
      .map(s => ({...s, absences: Math.floor(Math.random()*5)})),
  }),
  '/reports/trend':  () => ({ trend: DEMO_TREND, total_students: DEMO_STUDENTS.length }),
  '/recognize':      () => {
    const picks = [
      { matched:true,  newly_marked:true,  student:{ name:'Arjun Sharma',    roll_no:'CS21001', department:'Computer Science', confidence:94.2 }},
      { matched:true,  newly_marked:false, student:{ name:'Priya Reddy',     roll_no:'CS21002', department:'Computer Science', confidence:91.5 }},
      { matched:false, message:'Face not recognized' },
      { matched:true,  newly_marked:true,  student:{ name:'Vikram Singh',    roll_no:'CS21003', department:'Computer Science', confidence:96.1 }},
    ];
    return picks[Math.floor(Math.random() * picks.length)];
  },
};

let _demoActive = false;
let _backendChecked = false;

async function _checkBackend(url) {
  if (_backendChecked) return _demoActive;
  try {
    const ctrl = new AbortController();
    const timeout = setTimeout(() => ctrl.abort(), 3000);
    const base = url.split('/').slice(0,3).join('/');
    await fetch(base + '/docs', { signal: ctrl.signal, mode:'no-cors' });
    clearTimeout(timeout);
    _demoActive = false;
  } catch {
    _demoActive = true;
  }
  _backendChecked = true;
  if (_demoActive) _showDemoBanner();
  return _demoActive;
}

function _showDemoBanner() {
  if (document.getElementById('demo-banner')) return;
  const b = document.createElement('div');
  b.id = 'demo-banner';
  b.style.cssText = `
    position:fixed;top:0;left:0;right:0;z-index:99999;
    background:linear-gradient(90deg,#1a58b7,#3d72d2);
    color:#fff;text-align:center;padding:8px 16px;
    font-family:Inter,sans-serif;font-size:13px;font-weight:600;
    display:flex;align-items:center;justify-content:center;gap:8px;
    box-shadow:0 2px 12px rgba(0,0,0,0.2);
  `;
  b.innerHTML = `
    <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.05em;">DEMO MODE</span>
    Running with sample data — backend not connected.
    <a href="https://github.com/SushanthReddy5/vision-attendance#readme"
       target="_blank"
       style="color:#aec6ff;text-decoration:underline;margin-left:4px;">Deploy your own →</a>
  `;
  document.body.prepend(b);
  // Push page content down
  document.body.style.paddingTop = '40px';
}

function _mockResponse(data) {
  return {
    ok: true, status: 200,
    json: async () => JSON.parse(JSON.stringify(data)),
    text: async () => JSON.stringify(data),
  };
}

function _demoFetch(url, opts = {}) {
  const path = new URL(url, location.href).pathname;
  const params = new URL(url, location.href).searchParams;

  // Login — always succeed in demo
  if (path.endsWith('/admin/login')) {
    sessionStorage.setItem('va_logged_in','1');
    return Promise.resolve(_mockResponse(DEMO_API['/admin/login']()));
  }
  if (path.endsWith('/admin/profile') && (!opts.method || opts.method==='GET'))
    return Promise.resolve(_mockResponse(DEMO_API['/admin/profile']()));
  if (path.endsWith('/admin/profile') && opts.method==='PUT')
    return Promise.resolve(_mockResponse({ message:'Profile updated (demo)' }));
  if (path.endsWith('/admin/change-password'))
    return Promise.resolve(_mockResponse({ message:'Password changed (demo)' }));
  if (path.endsWith('/students') && (!opts.method || opts.method==='GET'))
    return Promise.resolve(_mockResponse(DEMO_API['/students']()));
  if (path.endsWith('/students') && opts.method==='POST')
    return Promise.resolve(_mockResponse({ message:'Student registered (demo)', id:99, angles_captured:1 }));
  if (path.includes('/students/search'))
    return Promise.resolve(_mockResponse(DEMO_API['/students/search'](params.get('q')||'')));
  if (path.includes('/students/') && opts.method==='PUT')
    return Promise.resolve(_mockResponse({ message:'Student updated (demo)' }));
  if (path.includes('/students/') && opts.method==='DELETE')
    return Promise.resolve(_mockResponse({ message:'Student deleted (demo)' }));
  if (path.endsWith('/recognize'))
    return Promise.resolve(_mockResponse(DEMO_API['/recognize']()));
  if (path.endsWith('/attendance/today'))
    return Promise.resolve(_mockResponse(DEMO_API['/attendance/today']()));
  if (path.endsWith('/dashboard/stats'))
    return Promise.resolve(_mockResponse(DEMO_API['/dashboard/stats']()));
  if (path.endsWith('/reports/stats'))
    return Promise.resolve(_mockResponse(DEMO_API['/reports/stats']()));
  if (path.endsWith('/reports/trend'))
    return Promise.resolve(_mockResponse(DEMO_API['/reports/trend']()));

  return Promise.resolve(_mockResponse({ message:'Demo response' }));
}

// Patch global fetch to intercept API calls
const _originalFetch = window.fetch.bind(window);
window.fetch = async function(url, opts = {}) {
  if (typeof url !== 'string' || !url.includes(API_BASE_URL.replace('http://localhost:8000',''))) {
    // Non-API call (CDNs, fonts etc) — check if it's an API URL
    if (typeof url === 'string' && (
      url.startsWith('http://localhost:8000') ||
      url.startsWith(API_BASE_URL)
    )) {
      const isDemo = await _checkBackend(url);
      if (isDemo) return _demoFetch(url, opts);
    }
    return _originalFetch(url, opts);
  }
  const isDemo = await _checkBackend(url);
  if (isDemo) return _demoFetch(url, opts);
  return _originalFetch(url, opts);
};

// Also handle login page — auto-detect and mock
window._demoLogin = async function() {
  _demoActive = true;
  _backendChecked = true;
  sessionStorage.setItem('va_logged_in','1');
};
