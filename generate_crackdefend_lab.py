import os
import shutil

# Clean up previous run (optional, for repeatability)
for folder in ["offensive", "defensive", "dashboard", "data", "scripts"]:
    if os.path.exists(folder):
        shutil.rmtree(folder)
os.makedirs("offensive", exist_ok=True)
os.makedirs("defensive", exist_ok=True)
os.makedirs("dashboard/templates", exist_ok=True)
os.makedirs("dashboard/static", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("scripts", exist_ok=True)

# --- DATA FILES ---
data_files = [
    ("data/usernames.txt", "ali_khan\nabdullah@gmail.com\nzainab@gmail.com\nhassan@gmail.com\n"),
    ("data/passwords.txt", "password\nletmein\nqwerty\n123456\nadmin\n"),
    ("data/valid_creds.txt", "ali_khan:password\nabdullah@gmail.com:letmein\nzainab@gmail.com:qwerty\nhassan@gmail.com:admin\n"),
    ("data/hashes.txt", "password:5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8\nletmein:0d107d09f5bbe40cade3de5c71e9e9b7\nqwerty:d8578edf8458ce06fbc5bb76a58c5ca4\n123456:e10adc3949ba59abbe56e057f20f883e\nadmin:21232f297a57a5a743894a0e4a801fc3\n"),
    ("data/attack_log.csv", "# Format: time,user,password,ip,status\n"),
    ("data/defense_log.csv", "# Format: username,action,timestamp\n"),
    ("data/blocked.txt", ""),
    ("data/whitelist.txt", ""),
]
for path, content in data_files:
    with open(path, "w") as f:
        f.write(content)

# --- SCRIPTS ---
with open("scripts/cron_unblock.sh", "w") as f:
    f.write('#!/bin/bash\necho "All users unblocked at $(date)" >> ../data/defense_log.csv\n')

# --- README ---
with open("README.md", "w") as f:
    f.write('''\
# CrackDefend Lab

- All required folders and files are created automatically.
- Start MailHog (`MailHog` or `docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog`)
- Start dashboard: `cd dashboard && python3 app.py`
- Open http://localhost:5000 in your browser.
- Use the dashboard to control attacker/defender modules, monitor logs, and send emails.

Enjoy!
''')

# --- DASHBOARD HTML/JS/CSS ---
with open("dashboard/templates/index.html", "w") as f:
    f.write('''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CrackDefend Lab Dashboard</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-light">
<div class="container py-4">
  <h1 class="text-center mb-4">CrackDefend Lab Dashboard</h1>
  <div class="mb-4 text-end">
    <button class="btn btn-success me-2" onclick="startModule('attacker')">Start Attacker</button>
    <button class="btn btn-danger me-2" onclick="stopModule('attacker')">Stop Attacker</button>
    <button class="btn btn-success me-2" onclick="startModule('defender')">Start Defender</button>
    <button class="btn btn-danger me-2" onclick="stopModule('defender')">Stop Defender</button>
    <button class="btn btn-outline-dark ms-3" onclick="toggleDarkMode()">🌓 Dark Mode</button>
    <button class="btn btn-outline-danger ms-3" onclick="resetStats()">Reset All Statistics</button>
  </div>
  <div class="row mb-2">
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Attacks</h6><h3 id="stat-attacks">0</h3></div></div></div>
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Success</h6><h3 id="stat-success">0</h3></div></div></div>
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Blocked</h6><h3 id="stat-blocked">0</h3></div></div></div>
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Emails Sent</h6><h3 id="stat-emails">0</h3></div></div></div>
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Most Targeted</h6><div id="stat-most-email"></div></div></div></div>
    <div class="col-md-2"><div class="card text-center"><div class="card-body"><h6>Most Used Pwd</h6><div id="stat-most-pwd"></div></div></div></div>
  </div>
  <div class="row mb-4">
    <div class="col-md-3"><div class="card text-center"><div class="card-body"><h6>Most Aggressive IP</h6><div id="stat-most-ip"></div><div id="stat-most-ip-geo"></div></div></div></div>
    <div class="col-md-3"><div class="card text-center"><div class="card-body"><h6>Attempts (Last Hour)</h6><div id="stat-last-hour"></div></div></div></div>
    <div class="col-md-6">
      <div class="card">
        <div class="card-body">
          <canvas id="hourChart" height="80"></canvas>
        </div>
      </div>
    </div>
  </div>
  <div class="row mb-4">
    <div class="col-md-6"><div class="card"><div class="card-body"><canvas id="ipPie" height="120"></canvas></div></div></div>
    <div class="col-md-6"><div class="card"><div class="card-body"><canvas id="attackChart"></canvas></div></div></div>
  </div>
  <div class="card mb-3">
    <div class="card-header">Live Control Panel</div>
    <div class="card-body">
      <label>Attack Speed (sec): <input type="number" id="attackSpeed" min="0.1" step="0.1" value="1"></label>
      <button class="btn btn-primary btn-sm ms-2" onclick="setAttackSpeed()">Update Speed</button>
      <form id="uploadListForm" class="d-inline ms-4" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <select name="type"><option value="email">Email</option><option value="password">Password</option></select>
        <button class="btn btn-secondary btn-sm" type="submit">Upload List</button>
      </form>
    </div>
  </div>
  <div class="row mt-3">
    <div class="col-md-6">
      <div class="card mb-3">
        <div class="card-header bg-info text-white">Recent Attacks</div>
        <div class="card-body p-0">
          <table class="table table-sm table-hover mb-0">
            <thead><tr><th>Time</th><th>User</th><th>IP</th><th>Password</th><th>Status</th></tr></thead>
            <tbody id="attack-table"></tbody>
          </table>
        </div>
      </div>
      <div class="card mb-3">
        <div class="card-header bg-info text-white">User List</div>
        <div class="card-body">
          <ul id="users-list" class="list-group"></ul>
          <form id="addUserForm" class="mt-3">
            <h6>Add New User/Email:</h6>
            <input name="username" class="form-control mb-2" placeholder="Username or Email" required>
            <input name="password" class="form-control mb-2" placeholder="Password" required id="newPwd">
            <small id="pwdStrength" style="font-weight:bold;"></small>
            <button class="btn btn-primary" type="submit">Add User</button>
          </form>
          <form id="addPasswordForm" class="mt-3">
            <h6>Add New Password:</h6>
            <input name="password" class="form-control mb-2" placeholder="Password" required>
            <button class="btn btn-secondary" type="submit">Add Password</button>
          </form>
        </div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="card mb-3">
        <div class="card-header bg-warning text-dark">Recent Emails (MailHog)</div>
        <div class="card-body p-0">
          <table class="table table-sm table-hover mb-0">
            <thead><tr><th>Time</th><th>To</th><th>Subject</th></tr></thead>
            <tbody id="email-table"></tbody>
          </table>
        </div>
      </div>
      <div class="card mb-3">
        <div class="card-header bg-secondary text-white">Password List</div>
        <div class="card-body">
          <ul id="passwords-list" class="list-group"></ul>
        </div>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="col">
      <div class="card border-danger">
        <div class="card-header bg-danger text-white">Blocked Users/IPs</div>
        <div class="card-body">
          <ul id="blocked-list" class="list-group"></ul>
          <button class="btn btn-secondary mt-2" onclick="refreshBlocked()">Refresh</button>
        </div>
      </div>
      <div class="card border-success mt-2">
        <div class="card-header bg-success text-white">Whitelisted Users/IPs</div>
        <div class="card-body">
          <ul id="whitelist-list" class="list-group"></ul>
        </div>
      </div>
    </div>
  </div>
</div>
<script src="{{ url_for('static', filename='dashboard.js') }}"></script>
</body>
</html>
''')

with open("dashboard/static/style.css", "w") as f:
    f.write('''\
body { background: #f8fafc; }
body.dark { background: #18191a !important; color: #f9f9f9 !important;}
body.dark .card { background: #242526; color: #eee; }
body.dark .table { color: #eee; }
h1 { color: #1a237e; letter-spacing: 1px;}
.card { box-shadow: 0 2px 10px rgba(60,60,60,0.07); }
pre.logbox { background: #18191a; color: #f9f9f9; padding: 10px; height: 160px; overflow: auto; border-radius: 5px; font-size: 0.95em;}
.badge { font-size: 1em; padding: 0.5em 1em; }
footer { margin-top: 30px; }
''')

with open("dashboard/static/dashboard.js", "w") as f:
    f.write('''\
function startModule(mod) { fetch('/start/' + mod).then(() => {}); }
function stopModule(mod) { fetch('/stop/' + mod).then(() => {}); }
function updateStatsAndCharts() {
  fetch('/stats').then(r => r.json()).then(data => {
    document.getElementById("stat-attacks").textContent = data.attacks;
    document.getElementById("stat-success").textContent = data.success;
    document.getElementById("stat-blocked").textContent = data.blocked;
    document.getElementById("stat-emails").textContent = data.emails_sent;
    document.getElementById("stat-most-email").textContent = data.most_targeted_email;
    document.getElementById("stat-most-pwd").textContent = data.most_used_pwd;
    document.getElementById("stat-most-ip").textContent = data.most_aggressive_ip;
    document.getElementById("stat-most-ip-geo").textContent = data.geoip_country + ", " + data.geoip_city;
    document.getElementById("stat-last-hour").textContent = data.total_last_hour;
    let tbody = document.getElementById("attack-table");
    tbody.innerHTML = "";
    data.recent.forEach(row => {
      let tr = `<tr>
        <td>${row.time}</td><td>${row.user}</td><td>${row.ip}</td><td>${row.pwd||""}</td>
        <td><span class="badge ${row.status === 'SUCCESS' ? 'bg-success' : (row.status === 'BLOCKED' ? 'bg-secondary' : 'bg-danger')}">${row.status}</span></td>
      </tr>`;
      tbody.innerHTML += tr;
    });
    // Historical hourly line chart
    if (!window.hourChart) {
      window.hourChart = new Chart(document.getElementById('hourChart'), {
        type: 'line',
        data: {
          labels: Array.from({length:24},(_,i)=>i+":00"),
          datasets: [{data:data.hourly_attempts, label:'Attempts/Hour', borderColor:'#007bff', fill:false}]
        }
      });
    } else {
      window.hourChart.data.datasets[0].data = data.hourly_attempts;
      window.hourChart.update();
    }
    // IP distribution pie
    if (!window.ipPie) {
      window.ipPie = new Chart(document.getElementById('ipPie'), {
        type:'pie',
        data:{
          labels:data.per_ip.map(i=>i[0]),
          datasets:[{data:data.per_ip.map(i=>i[1]), backgroundColor:["#9ae6b4","#f6ad55","#f56565","#4299e1","#ecc94b","#ed64a6"]}]
        }
      });
    } else {
      window.ipPie.data.labels = data.per_ip.map(i=>i[0]);
      window.ipPie.data.datasets[0].data = data.per_ip.map(i=>i[1]);
      window.ipPie.update();
    }
    // Overall attack donut
    if (!window.attackChart) {
      window.attackChart = new Chart(document.getElementById('attackChart'), {
        type: 'doughnut',
        data: { labels: ['Success','Fail'], datasets: [{ data: [data.success, data.fail], backgroundColor: ['#28a745','#dc3545'] }] }
      });
    } else {
      window.attackChart.data.datasets[0].data = [data.success, data.fail];
      window.attackChart.update();
    }
  });
}
function fetchMailhogEmails() {
  fetch('/mailhog')
    .then(resp => resp.json())
    .then(data => {
      let table = document.getElementById('email-table');
      table.innerHTML = "";
      data.emails.forEach(msg => {
        let tr = `<tr>
          <td>${msg.time}</td>
          <td>${msg.to}</td>
          <td>${msg.subject}</td>
        </tr>`;
        table.innerHTML += tr;
      });
    });
}
function refreshBlocked() {
  fetch('/blocked').then(r => r.json()).then(data => {
    let ul = document.getElementById('blocked-list');
    ul.innerHTML = "";
    data.blocked.forEach(item => {
      let li = document.createElement('li');
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.textContent = item;
      let btn = document.createElement('button');
      btn.className = "btn btn-sm btn-outline-success";
      btn.textContent = "Unblock";
      btn.onclick = () => fetch('/unblock?user=' + encodeURIComponent(item)).then(refreshBlocked);
      li.appendChild(btn);
      ul.appendChild(li);
    });
  });
  fetch('/whitelist').then(r=>r.json()).then(data=>{
    let ul = document.getElementById('whitelist-list');
    ul.innerHTML = "";
    data.whitelist.forEach(item=>{
      let li = document.createElement('li');
      li.className = "list-group-item";
      li.textContent = item;
      ul.appendChild(li);
    });
  });
}
function refreshUsers() {
  fetch('/users').then(r => r.json()).then(data => {
    let ul = document.getElementById('users-list');
    ul.innerHTML = "";
    data.users.forEach(user => {
      let li = document.createElement('li');
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.textContent = user;
      let btn = document.createElement('button');
      btn.className = "btn btn-sm btn-outline-danger";
      btn.textContent = "Block";
      btn.onclick = () => blockUser(user);
      li.appendChild(btn);
      ul.appendChild(li);
    });
  });
}
function blockUser(user) {
  fetch('/block_user', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({user})
  }).then(()=>{refreshBlocked();});
}
function refreshPasswords() {
  fetch('/passwords').then(r => r.json()).then(data => {
    let ul = document.getElementById('passwords-list');
    ul.innerHTML = "";
    data.passwords.forEach(pwd => {
      let li = document.createElement('li');
      li.className = "list-group-item";
      li.textContent = pwd;
      ul.appendChild(li);
    });
  });
}
document.getElementById('addUserForm').onsubmit = function(e) {
  e.preventDefault();
  fetch('/add_user', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      username: e.target.username.value,
      password: e.target.password.value
    })
  }).then(()=>{refreshUsers();});
};
document.getElementById('addPasswordForm').onsubmit = function(e) {
  e.preventDefault();
  fetch('/add_password', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({password: e.target.password.value})
  }).then(()=>{refreshPasswords();});
};
function setAttackSpeed() {
  fetch('/set_attack_speed', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({speed:document.getElementById('attackSpeed').value})
  });
}
document.getElementById('uploadListForm').onsubmit = function(e){
  e.preventDefault();
  const formData = new FormData(this);
  fetch('/upload_list', {method:'POST', body:formData}).then(()=>{});
};
function resetStats() {
  if (!confirm("Are you sure you want to reset all statistics?")) return;
  fetch('/reset_stats', {method: 'POST'}).then(r => r.json()).then(data => {
    if(data.status==="reset") {
      alert("Statistics reset.");
      updateStatsAndCharts();
      refreshBlocked();
    }
  });
}
function toggleDarkMode() {
  document.body.classList.toggle('dark');
  localStorage.setItem('darkmode', document.body.classList.contains('dark'));
}
document.getElementById('newPwd').oninput = function() {
  const val = this.value;
  let score = 0;
  if(val.length>=8) score++;
  if(/[A-Z]/.test(val)) score++;
  if(/[0-9]/.test(val)) score++;
  if(/[^A-Za-z0-9]/.test(val)) score++;
  let msg = ["Very Weak","Weak","Medium","Strong","Very Strong"];
  document.getElementById('pwdStrength').textContent = msg[score];
  document.getElementById('pwdStrength').style.color = ["#c00","#e90","#d9d900","#0c0","#090"][score];
};
setInterval(updateStatsAndCharts, 1500);
setInterval(fetchMailhogEmails, 2500);
setInterval(refreshBlocked, 4000);
setInterval(refreshUsers, 4000);
setInterval(refreshPasswords, 4000);
window.onload = function() {
  if(localStorage.getItem('darkmode')==='true') document.body.classList.add('dark');
  updateStatsAndCharts();
  fetchMailhogEmails();
  refreshBlocked();
  refreshUsers();
  refreshPasswords();
};
''')

# --- DASHBOARD BACKEND ---
with open("dashboard/app.py", "w") as f:
    f.write("""\
import os
import subprocess
import sys
import time
import requests
from flask import Flask, render_template, request, jsonify, send_file
from collections import Counter, defaultdict

app = Flask(__name__)
DATA_DIR = "../data"
ATTACK_LOG = os.path.join(DATA_DIR, "attack_log.csv")
DEFENSE_LOG = os.path.join(DATA_DIR, "defense_log.csv")
USERNAMES_FILE = os.path.join(DATA_DIR, "usernames.txt")
PASSWORDS_FILE = os.path.join(DATA_DIR, "passwords.txt")
VALID_CREDS_FILE = os.path.join(DATA_DIR, "valid_creds.txt")
BLOCKED_FILE = os.path.join(DATA_DIR, "blocked.txt")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.txt")

attack_speed = 1.0
processes = {
    "attacker": None,
    "defender": None
}

def launch_process(script_path, key):
    if processes[key] and processes[key].poll() is None:
        return
    try:
        processes[key] = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=os.path.dirname(script_path)
        )
        print(f"[DASHBOARD] Started {key}.")
    except Exception as e:
        print(f"[DASHBOARD] Failed to start {key}: {e}")

def stop_process(key):
    proc = processes.get(key)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        processes[key] = None
        print(f"[DASHBOARD] Stopped {key}.")

def get_geoip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=city,country", timeout=2)
        js = r.json()
        return js.get("country", "N/A"), js.get("city", "N/A")
    except Exception:
        return "N/A", "N/A"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start/<module>')
def start_module(module):
    if module == "attacker":
        launch_process("../offensive/cracksim.py", "attacker")
    elif module == "defender":
        launch_process("../defensive/defendmonitor.py", "defender")
    return jsonify({"status": "started", "module": module})

@app.route('/stop/<module>')
def stop_module(module):
    if module in processes:
        stop_process(module)
    return jsonify({"status": "stopped", "module": module})

@app.route('/stats')
def api_stats():
    total = 0
    success = fail = 0
    blocked_users = set()
    recent = []
    per_user = Counter()
    per_ip = Counter()
    per_pwd = Counter()
    per_hour = defaultdict(int)
    now = int(time.time())
    attempts_last_hour = 0
    log_data = []
    if os.path.exists(ATTACK_LOG):
        with open(ATTACK_LOG) as f:
            for line in f:
                if "," not in line or line.startswith('#'): continue
                parts = line.strip().split(",")
                if len(parts) < 5: continue
                ts, user, pwd, ip, status = parts
                ts = int(ts)
                total += 1
                log_data.append((ts, user, pwd, ip, status))
                per_user[user] += 1
                per_ip[ip] += 1
                per_pwd[pwd] += 1
                per_hour[time.strftime("%H", time.localtime(ts))] += 1
                if now - ts < 3600:
                    attempts_last_hour += 1
                recent.append({
                    "time": time.strftime("%H:%M:%S", time.localtime(ts)),
                    "user": user, "ip": ip, "pwd": pwd, "status": status
                })
                if status == "SUCCESS":
                    success += 1
                elif status == "FAIL":
                    fail += 1
    if os.path.exists(DEFENSE_LOG):
        with open(DEFENSE_LOG) as f:
            for line in f:
                if ",BLOCKED," in line:
                    blocked_users.add(line.split(",")[0])
                elif ",UNBLOCKED," in line:
                    blocked_users.discard(line.split(",")[0])
    try:
        resp = requests.get("http://localhost:8025/api/v2/messages", timeout=2)
        emails_sent = resp.json().get("total", 0)
    except Exception:
        emails_sent = 0
    most_targeted_email = per_user.most_common(1)[0][0] if per_user else ""
    most_used_pwd = per_pwd.most_common(1)[0][0] if per_pwd else ""
    most_aggressive_ip = per_ip.most_common(1)[0][0] if per_ip else ""
    geo_country, geo_city = get_geoip(most_aggressive_ip) if most_aggressive_ip else ("N/A", "N/A")
    per_hour_sorted = [per_hour.get(f"{h:02}", 0) for h in range(24)]
    return jsonify({
        "attacks": total, "success": success, "fail": fail,
        "blocked": len(blocked_users),
        "emails_sent": emails_sent,
        "recent": recent[::-1][:20],
        "most_targeted_email": most_targeted_email,
        "most_used_pwd": most_used_pwd,
        "most_aggressive_ip": most_aggressive_ip,
        "geoip_country": geo_country,
        "geoip_city": geo_city,
        "total_last_hour": attempts_last_hour,
        "hourly_attempts": per_hour_sorted,
        "per_ip": per_ip.most_common(10),
        "per_user": per_user.most_common(10),
        "per_pwd": per_pwd.most_common(10)
    })

@app.route('/mailhog')
def mailhog():
    try:
        resp = requests.get("http://localhost:8025/api/v2/messages", timeout=2)
        items = resp.json().get("items", [])
        emails = []
        for item in items:
            to = item['To'][0]['Mailbox'] + "@" + item['To'][0]['Domain']
            subject = item['Content']['Headers']['Subject'][0]
            t = item['Created']
            emails.append({"time": t[11:19], "to": to, "subject": subject})
        return jsonify(emails=emails[:10])
    except Exception:
        return jsonify(emails=[])

@app.route('/users')
def users():
    with open(USERNAMES_FILE) as f:
        users = [line.strip() for line in f if line.strip()]
    return jsonify(users=users)

@app.route('/passwords')
def passwords():
    with open(PASSWORDS_FILE) as f:
        pwds = [line.strip() for line in f if line.strip()]
    return jsonify(passwords=pwds)

@app.route('/blocked')
def api_blocked():
    blocked = set()
    if os.path.exists(DEFENSE_LOG):
        with open(DEFENSE_LOG) as f:
            for line in f:
                if ",BLOCKED," in line:
                    blocked.add(line.split(",")[0])
                elif ",UNBLOCKED," in line:
                    blocked.discard(line.split(",")[0])
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE) as f:
            for line in f:
                if line.strip():
                    blocked.add(line.strip())
    return jsonify({"blocked": list(blocked)})

@app.route('/whitelist')
def api_whitelist():
    whitelist = set()
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE) as f:
            for line in f:
                if line.strip():
                    whitelist.add(line.strip())
    return jsonify({"whitelist": list(whitelist)})

@app.route('/unblock')
def api_unblock():
    user = request.args.get('user')
    if user:
        with open(DEFENSE_LOG, "a") as f:
            f.write(f"{user},UNBLOCKED,{int(time.time())}\n")
    return jsonify({"status": "unblocked", "user": user})

@app.route('/block_user', methods=['POST'])
def block_user():
    user = request.json.get('user')
    if user:
        with open(DEFENSE_LOG, "a") as f:
            f.write(f"{user},BLOCKED,{int(time.time())}\n")
        with open(BLOCKED_FILE, "a") as f:
            f.write(user + "\\n")
    return jsonify({"status": "blocked", "user": user})

@app.route('/whitelist_user', methods=['POST'])
def whitelist_user():
    user = request.json.get('user')
    if user:
        with open(WHITELIST_FILE, "a") as f:
            f.write(user + "\\n")
    return jsonify({"status": "whitelisted", "user": user})

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username and password:
        with open(USERNAMES_FILE, "a") as f:
            f.write(username + "\\n")
        with open(PASSWORDS_FILE, "a") as f:
            f.write(password + "\\n")
        with open(VALID_CREDS_FILE, "a") as f:
            f.write(f"{username}:{password}\\n")
        return jsonify({'status': 'added'})
    return jsonify({'status': 'error'}), 400

@app.route('/add_password', methods=['POST'])
def add_password():
    password = request.json.get('password')
    if password:
        with open(PASSWORDS_FILE, "a") as f:
            f.write(password + "\\n")
        return jsonify({'status': 'added'})
    return jsonify({'status': 'error'}), 400

@app.route('/set_attack_speed', methods=['POST'])
def set_attack_speed():
    global attack_speed
    speed = request.json.get('speed')
    try:
        attack_speed = float(speed)
    except Exception:
        pass
    return jsonify({'status':'ok','speed':attack_speed})

@app.route('/upload_list', methods=['POST'])
def upload_list():
    t = request.form['type']
    f = request.files['file']
    if t == "email":
        path = USERNAMES_FILE
    elif t == "password":
        path = PASSWORDS_FILE
    else:
        return jsonify({'status':'error'}), 400
    with open(path, "a") as out:
        for line in f:
            out.write(line.decode("utf-8"))
    return jsonify({'status':'ok'})

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    with open(ATTACK_LOG, "w") as f:
        f.write("# Format: time,user,password,ip,status\\n")
    with open(DEFENSE_LOG, "w") as f:
        f.write("# Format: username,action,timestamp\\n")
    return jsonify({"status": "reset"})

@app.route('/download_log')
def download_log():
    log_type = request.args.get('type')
    if log_type == "attack":
        return send_file(ATTACK_LOG, as_attachment=True)
    elif log_type == "defense":
        return send_file(DEFENSE_LOG, as_attachment=True)
    return "Invalid log type", 400

if __name__ == "__main__":
    app.run(debug=True)
""")

# ---- OFFENSIVE MODULE (ADVANCED) ----
with open("offensive/cracksim.py", "w") as f:
    f.write("""
import random
import time
import os
import smtplib
from email.mime.text import MIMEText

DATA_DIR = "../data"
USERNAMES_FILE = os.path.join(DATA_DIR, "usernames.txt")
PASSWORDS_FILE = os.path.join(DATA_DIR, "passwords.txt")
VALID_CREDS_FILE = os.path.join(DATA_DIR, "valid_creds.txt")
ATTACK_LOG = os.path.join(DATA_DIR, "attack_log.csv")
DEFENSE_LOG = os.path.join(DATA_DIR, "defense_log.csv")
BLOCKED_FILE = os.path.join(DATA_DIR, "blocked.txt")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.txt")
CONFIG_FILE = os.path.join(DATA_DIR, "attack_speed.cfg")

def send_mailhog_email(to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'lab@crackdefend.local'
    msg['To'] = to_addr
    try:
        with smtplib.SMTP('localhost', 1025, timeout=3) as server:
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        print(f"[MailHog ERROR] Could not send mail: {e}")

def load_list(path):
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]

def load_valid_creds(path):
    valid = {}
    with open(path) as f:
        for line in f:
            if ":" in line:
                email, pwd = line.strip().split(":", 1)
                valid[email] = pwd
    return valid

def is_blocked(user):
    blocked = set()
    if os.path.exists(DEFENSE_LOG):
        with open(DEFENSE_LOG) as f:
            for line in f:
                if ",BLOCKED," in line:
                    blocked.add(line.split(",")[0])
                elif ",UNBLOCKED," in line:
                    blocked.discard(line.split(",")[0])
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE) as f:
            for line in f:
                blocked.add(line.strip())
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE) as f:
            for line in f:
                if line.strip() in blocked:
                    blocked.discard(line.strip())
    return user in blocked

def generate_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

def get_attack_speed():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                return float(f.read().strip())
    except Exception:
        pass
    return 1.0

def main():
    print("CrackSim: Starting brute-force simulation. Press Ctrl+C to stop.")
    # Try to use rockyou.txt for dictionary attacks if exists
    rockyou_path = os.path.join(DATA_DIR, "rockyou.txt")
    use_dict = os.path.exists(rockyou_path)
    dict_pwds = []
    if use_dict:
        with open(rockyou_path, encoding='latin-1') as f:
            dict_pwds = [line.strip() for line in f if line.strip()]
    dict_idx = 0
    while True:
        usernames = load_list(USERNAMES_FILE)
        passwords = load_list(PASSWORDS_FILE)
        valid_creds = load_valid_creds(VALID_CREDS_FILE)
        if not usernames or not passwords:
            print("No usernames or passwords to test. Waiting...")
            time.sleep(2)
            continue
        user = random.choice(usernames)
        # Dictionary attack: try rockyou.txt first
        if use_dict and dict_idx < len(dict_pwds):
            pwd = dict_pwds[dict_idx]
            dict_idx += 1
        else:
            pwd = random.choice(passwords)
        ip = generate_ip()
        now = int(time.time())
        if is_blocked(user):
            status = "BLOCKED"
            with open(ATTACK_LOG, "a") as f:
                f.write(f"{now},{user},{pwd},{ip},{status}\\n")
            print(f"User {user} is blocked. Attempt BLOCKED.")
            time.sleep(get_attack_speed())
            continue
        is_valid = valid_creds.get(user) == pwd
        status = "SUCCESS" if is_valid else "FAIL"
        with open(ATTACK_LOG, "a") as f:
            f.write(f"{now},{user},{pwd},{ip},{status}\\n")
        print(f"Trying {user} with {pwd} from {ip} ... {status}")
        if is_valid:
            send_mailhog_email(
                user,
                "Login Alert",
                f"Hi {user},\\n\\nYour account was logged into at {time.ctime(now)} from IP {ip}. If this wasn't you, please change your password!\\n"
            )
        time.sleep(get_attack_speed())

if __name__ == "__main__":
    main()
""")

# ---- DEFENSIVE MODULE (ADVANCED) ----
with open("defensive/defendmonitor.py", "w") as f:
    f.write("""
import time
import os
import smtplib
from email.mime.text import MIMEText

LOG_FILE = "../data/attack_log.csv"
DEFENSE_LOG = "../data/defense_log.csv"
BLOCKED_FILE = "../data/blocked.txt"
WHITELIST_FILE = "../data/whitelist.txt"
BAN_THRESHOLD = 5
UNBLOCK_TIME = 2 * 60  # 2 minutes

def send_mailhog_email(to_addr, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'admin@crackdefend.local'
    msg['To'] = to_addr
    try:
        with smtplib.SMTP('localhost', 1025, timeout=3) as server:
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        print(f"[MailHog ERROR] Could not send mail: {e}")

def load_failed():
    fails = {}
    if not os.path.exists(LOG_FILE):
        return fails
    with open(LOG_FILE) as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue
            parts = line.strip().split(",")
            if len(parts) != 5:
                continue
            ts, user, pwd, ip, status = parts
            if status == "FAIL":
                fails[user] = fails.get(user, 0) + 1
    return fails

def ban_user(user):
    print(f"[BAN] User {user} is now blocked")
    send_mailhog_email(
        "admin@crackdefend.local",
        f"User Blocked: {user}",
        f"User {user} has been blocked due to repeated brute-force attempts."
    )
    with open(DEFENSE_LOG, "a") as f:
        f.write(f"{user},BLOCKED,{int(time.time())}\\n")
    with open(BLOCKED_FILE, "a") as f:
        f.write(user + "\\n")

def unblock_user(user):
    print(f"[UNBLOCK] User {user} is now unblocked")
    with open(DEFENSE_LOG, "a") as f:
        f.write(f"{user},UNBLOCKED,{int(time.time())}\\n")

def monitor():
    print("DefendMonitor: Watching for brute-force attacks...")
    banned = {}
    while True:
        fails = load_failed()
        for user, count in fails.items():
            if count >= BAN_THRESHOLD and user not in banned:
                ban_user(user)
                banned[user] = time.time()
        for user in list(banned):
            if time.time() - banned[user] > UNBLOCK_TIME:
                unblock_user(user)
                del banned[user]
        time.sleep(5)

if __name__ == "__main__":
    monitor()
""")

# ---- rockyou.txt (optional, demo) ----
with open("data/rockyou.txt", "w") as f:
    f.write("123456\npassword\n123456789\nqwerty\nabc123\npassword1\n")

print("CrackDefend Lab: All files and folders created! Now run:\n  cd dashboard\n  python3 app.py")
