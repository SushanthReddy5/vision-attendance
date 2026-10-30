import re

with open('capture.html', 'r') as f:
    content = f.read()

changes = {}

# 1. Remove "East Wing Entrance - Cam 04" label + divider
content, n = re.subn(
    r'<div class="h-4 w-\[1px\] bg-outline-variant"></div>\s*<h2 class="font-body-md text-on-surface font-semibold">East Wing Entrance - Cam 04</h2>\s*',
    '', content)
changes['camera label removed'] = n

# 2. Remove avatar stack + notification bell in header
content, n = re.subn(
    r'<div class="flex items-center gap-4">\s*<div class="flex -space-x-2">.*?</button>\s*</div>\s*(?=</header>)',
    '', content, flags=re.S)
changes['avatars/bell removed'] = n

# 3. Remove duplicate ATTENDANCE sidebar link
content, n = re.subn(
    r'<a class="flex items-center gap-3 text-on-surface-variant px-4 py-3 mx-2 hover:bg-surface-container-high rounded-lg transition-all duration-200" href="dashboard\.html">\s*'
    r'<span class="material-symbols-outlined">event_available</span>\s*'
    r'<span class="font-label-caps text-label-caps">ATTENDANCE</span>\s*</a>\s*',
    '', content)
changes['attendance nav removed'] = n

# 4. New Scan: button -> link to register.html
content, n = re.subn(
    r'<button class="w-full py-3 bg-on-background text-white rounded-full font-label-caps text-label-caps flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">',
    '<a href="register.html" class="w-full py-3 bg-on-background text-white rounded-full font-label-caps text-label-caps flex items-center justify-center gap-2 hover:opacity-90 transition-opacity">',
    content)
changes['new scan opening tag'] = n

content, n = re.subn(
    r'(<span class="material-symbols-outlined text-sm">add</span>\s*)New Scan\s*</button>',
    r'\1New Scan</a>', content)
changes['new scan closing tag'] = n

# 5. Help Center: href="#" -> href="help.html"
content, n = re.subn(
    r'(<a class="flex items-center gap-3 text-on-surface-variant px-4 py-2 mx-2 hover:bg-surface-container-high rounded-lg transition-all duration-200" href=")#(">\s*<span class="material-symbols-outlined">help</span>)',
    r'\1help.html\2', content)
changes['help center link'] = n

# 6. Replace fake stat cards (412 Present / 28 Pending Review) with real placeholders
content, n = re.subn(
    r'<div class="grid grid-cols-1 gap-4">.*?(?=<!-- Just Marked List -->)',
    '''<div class="grid grid-cols-1 gap-4">
<div class="bg-white p-6 rounded-[24px] shadow-sm border border-outline-variant/20 relative overflow-hidden">
<div class="absolute -right-4 -top-4 w-20 h-20 bg-success-green/5 rounded-full"></div>
<div class="flex items-center justify-between mb-4">
<div class="w-10 h-10 rounded-full bg-success-green/10 flex items-center justify-center">
<span class="material-symbols-outlined text-success-green" style="font-variation-settings: 'FILL' 1;">person_check</span>
</div>
</div>
<p id="cap-present" class="text-3xl font-headline-sm font-bold text-on-surface">--</p>
<p class="text-sm text-on-surface-variant">Present Today</p>
</div>
<div class="bg-white p-6 rounded-[24px] shadow-sm border border-outline-variant/20">
<div class="flex items-center justify-between mb-4">
<div class="w-10 h-10 rounded-full bg-error/10 flex items-center justify-center">
<span class="material-symbols-outlined text-error" style="font-variation-settings: 'FILL' 1;">person_off</span>
</div>
</div>
<p id="cap-absent" class="text-3xl font-headline-sm font-bold text-on-surface">--</p>
<p class="text-sm text-on-surface-variant">Absent Today</p>
</div>
</div>
''', content, flags=re.S)
changes['stat cards replaced'] = n

# 7. Remove bottom fake "Anomaly Detected / CPU GPU Latency" footer bar
content, n = re.subn(
    r'<!-- Live Alerts Footer Area -->.*?(?=</main>)',
    '', content, flags=re.S)
changes['fake footer bar removed'] = n

# 8. Append real data-loading script before </body>
new_script = '''<script>
  (async () => {
    const API_BASE = "http://localhost:8000";
    try {
      const res = await fetch(API_BASE + "/dashboard/stats");
      const data = await res.json();
      document.getElementById('cap-present').textContent = data.present_today;
      document.getElementById('cap-absent').textContent = data.absent_today;
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
    }
    try {
      const res2 = await fetch(API_BASE + "/attendance/today");
      const records = await res2.json();
      const list = document.querySelector('.flex-1.overflow-y-auto');
      if (list) {
        list.innerHTML = '';
        if (records.length === 0) {
          list.innerHTML = '<p class="text-center text-on-surface-variant text-body-sm py-8">No check-ins yet today.</p>';
        } else {
          records.slice(0, 10).forEach(r => {
            const time = new Date(r.timestamp).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
            const initials = r.name.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2);
            const item = document.createElement('div');
            item.className = 'flex items-center gap-3 p-3 rounded-xl hover:bg-surface-container-low transition-colors cursor-pointer border-b border-outline-variant/10';
            item.innerHTML = '<div class="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center text-primary font-bold">' + initials + '</div>' +
              '<div class="flex-1"><p class="font-body-sm font-bold text-on-surface">' + r.name + '</p>' +
              '<p class="text-[10px] text-on-surface-variant uppercase tracking-tighter">' + (r.department || '') + ' \u2022 ' + time + '</p></div>' +
              '<div class="bg-success-green/10 p-1.5 rounded-full"><span class="material-symbols-outlined text-success-green text-[16px]" style="font-variation-settings: \\'FILL\\' 1;">check_circle</span></div>';
            list.appendChild(item);
          });
        }
      }
    } catch (err) {
      console.error('Failed to load attendance log:', err);
    }
  })();
</script>
'''
content, n = re.subn(
    r'(</script>\s*</body></html>)',
    new_script + r'\1', content)
changes['loader script inserted'] = n

with open('capture.html', 'w') as f:
    f.write(content)

print("=== Change report ===")
for k, v in changes.items():
    status = "✅" if v > 0 else "⚠️  ZERO MATCHES"
    print(f"{status} {k}: {v}")
