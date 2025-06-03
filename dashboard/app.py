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
    # Always provide fallback arrays to frontend
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
        "hourly_attempts": per_hour_sorted if len(per_hour_sorted)==24 else [0]*24,
        "per_ip": per_ip.most_common(10) if per_ip else [["No Data", 1]],
        "per_user": per_user.most_common(10) if per_user else [["No Data", 1]],
        "per_pwd": per_pwd.most_common(10) if per_pwd else [["No Data", 1]]
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
        # Remove user from blocked.txt
        if os.path.exists(BLOCKED_FILE):
            with open(BLOCKED_FILE, "r") as f:
                lines = [l for l in f if l.strip() and l.strip() != user]
            with open(BLOCKED_FILE, "w") as f:
                f.writelines(lines)
    return jsonify({"status": "unblocked", "user": user})

@app.route('/block_user', methods=['POST'])
def block_user():
    user = request.json.get('user')
    if user:
        with open(DEFENSE_LOG, "a") as f:
            f.write(f"{user},BLOCKED,{int(time.time())}\n")
        with open(BLOCKED_FILE, "a") as f:
            f.write(user + "\n")
    return jsonify({"status": "blocked", "user": user})

@app.route('/whitelist_user', methods=['POST'])
def whitelist_user():
    user = request.json.get('user')
    if user:
        with open(WHITELIST_FILE, "a") as f:
            f.write(user + "\n")
    return jsonify({"status": "whitelisted", "user": user})

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username and password:
        with open(USERNAMES_FILE, "a") as f:
            f.write(username + "\n")
        with open(PASSWORDS_FILE, "a") as f:
            f.write(password + "\n")
        with open(VALID_CREDS_FILE, "a") as f:
            f.write(f"{username}:{password}\n")
        return jsonify({'status': 'added'})
    return jsonify({'status': 'error'}), 400

@app.route('/add_password', methods=['POST'])
def add_password():
    password = request.json.get('password')
    if password:
        with open(PASSWORDS_FILE, "a") as f:
            f.write(password + "\n")
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
        f.write("# Format: time,user,password,ip,status\n")
    with open(DEFENSE_LOG, "w") as f:
        f.write("# Format: username,action,timestamp\n")
    return jsonify({"status": "reset"})

@app.route('/download_log')
def download_log():
    log_type = request.args.get('type')
    if log_type == "attack":
        return send_file(ATTACK_LOG, as_attachment=True)
    elif log_type == "defense":
        return send_file(DEFENSE_LOG, as_attachment=True)
    return "Invalid log type", 400

@app.route('/add_whitelist_ip', methods=['POST'])
def add_whitelist_ip():
    ip = request.json.get('ip')
    if ip:
        with open(WHITELIST_FILE, "a") as f:
            f.write(ip + "\n")
        return jsonify({'status': 'added', 'ip': ip})
    return jsonify({'status': 'error'}), 400

@app.route('/remove_whitelist_ip', methods=['POST'])
def remove_whitelist_ip():
    ip = request.json.get('ip')
    if ip and os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            lines = [l for l in f if l.strip() and l.strip() != ip]
        with open(WHITELIST_FILE, "w") as f:
            f.writelines(lines)
        return jsonify({'status': 'removed', 'ip': ip})
    return jsonify({'status': 'error'}), 400

if __name__ == "__main__":
    app.run(debug=True)
