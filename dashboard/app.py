import os
import subprocess
import sys
import time
import requests
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from collections import Counter, defaultdict
import sqlite3
import hashlib
import secrets

app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Configuration
DATA_DIR = "../data"
ATTACK_LOG = os.path.join(DATA_DIR, "attack_log.csv")
DEFENSE_LOG = os.path.join(DATA_DIR, "defense_log.csv")
USERNAMES_FILE = os.path.join(DATA_DIR, "usernames.txt")
PASSWORDS_FILE = os.path.join(DATA_DIR, "passwords.txt")
VALID_CREDS_FILE = os.path.join(DATA_DIR, "valid_creds.txt")
BLOCKED_FILE = os.path.join(DATA_DIR, "blocked.txt")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.txt")
DATABASE_FILE = os.path.join(DATA_DIR, "dashboard.db")

# Global variables
attack_speed = 1.0
processes = {
    "attacker": None,
    "defender": None
}

# Real-time data storage
real_time_data = {
    "threats": {"blocked": 0, "detected": 0, "quarantined": 0},
    "network": {"bandwidth": 0, "connections": 0, "latency": 0},
    "system": {"cpu": 0, "memory": 0, "disk": 0},
    "security": {"score": 85, "vulnerabilities": 0, "patches": 0}
}

# Notification system
notifications = []
max_notifications = 100

# Performance metrics
performance_metrics = {
    "uptime": time.time(),
    "requests_handled": 0,
    "errors_count": 0,
    "avg_response_time": 0
}

def init_database():
    """Initialize SQLite database for enhanced data storage"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attack_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            source_ip TEXT,
            target_user TEXT,
            attack_type TEXT,
            severity INTEGER,
            status TEXT,
            geolocation TEXT,
            user_agent TEXT,
            payload_size INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            network_in REAL,
            network_out REAL,
            active_connections INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER,
            event_type TEXT,
            severity TEXT,
            description TEXT,
            source TEXT,
            resolved BOOLEAN DEFAULT FALSE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            user_id TEXT,
            login_time INTEGER,
            last_activity INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    conn.close()

def add_notification(message, type="info", title=None):
    """Add notification to the global notifications list"""
    global notifications
    notification = {
        "id": f"notif_{int(time.time())}_{secrets.token_hex(4)}",
        "message": message,
        "type": type,
        "title": title,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    notifications.insert(0, notification)
    
    # Keep only the latest notifications
    if len(notifications) > max_notifications:
        notifications = notifications[:max_notifications]
    
    return notification

def update_real_time_metrics():
    """Update real-time metrics with simulated data"""
    import random
    import psutil
    
    try:
        # Get actual system metrics if psutil is available
        real_time_data["system"]["cpu"] = psutil.cpu_percent()
        real_time_data["system"]["memory"] = psutil.virtual_memory().percent
        real_time_data["system"]["disk"] = psutil.disk_usage('/').percent
    except ImportError:
        # Simulate system metrics
        real_time_data["system"]["cpu"] = random.randint(20, 80)
        real_time_data["system"]["memory"] = random.randint(40, 85)
        real_time_data["system"]["disk"] = random.randint(50, 90)
    
    # Simulate network metrics
    real_time_data["network"]["bandwidth"] = random.randint(100, 500)
    real_time_data["network"]["connections"] = random.randint(800, 2000)
    real_time_data["network"]["latency"] = random.randint(5, 50)
    
    # Update threat metrics based on logs
    if os.path.exists(ATTACK_LOG):
        recent_attacks = count_recent_attacks()
        real_time_data["threats"]["detected"] = recent_attacks
        real_time_data["threats"]["blocked"] = int(recent_attacks * 0.8)
        real_time_data["threats"]["quarantined"] = int(recent_attacks * 0.1)
    
    # Calculate security score
    cpu_score = max(0, 100 - real_time_data["system"]["cpu"])
    memory_score = max(0, 100 - real_time_data["system"]["memory"])
    threat_score = max(0, 100 - real_time_data["threats"]["detected"])
    real_time_data["security"]["score"] = int((cpu_score + memory_score + threat_score) / 3)

def count_recent_attacks(hours=1):
    """Count attacks in the last N hours"""
    if not os.path.exists(ATTACK_LOG):
        return 0
    
    cutoff_time = time.time() - (hours * 3600)
    count = 0
    
    try:
        with open(ATTACK_LOG, 'r') as f:
            for line in f:
                if line.startswith('#') or ',' not in line:
                    continue
                parts = line.strip().split(',')
                if len(parts) >= 1:
                    try:
                        timestamp = int(parts[0])
                        if timestamp > cutoff_time:
                            count += 1
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading attack log: {e}")
    
    return count

def launch_process(script_path, key):
    """Launch a subprocess for attack/defense modules"""
    if processes[key] and processes[key].poll() is None:
        return {"status": "already_running", "message": f"{key} is already running"}
    
    try:
        processes[key] = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(script_path)
        )
        print(f"[DASHBOARD] Started {key} (PID: {processes[key].pid})")
        add_notification(f"{key.title()} module started successfully", "success", "Module Started")
        return {"status": "started", "pid": processes[key].pid}
    except Exception as e:
        error_msg = f"Failed to start {key}: {str(e)}"
        print(f"[DASHBOARD] {error_msg}")
        add_notification(error_msg, "error", "Module Error")
        return {"status": "error", "message": error_msg}

def stop_process(key):
    """Stop a running subprocess"""
    proc = processes.get(key)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        processes[key] = None
        print(f"[DASHBOARD] Stopped {key}")
        add_notification(f"{key.title()} module stopped", "info", "Module Stopped")
        return {"status": "stopped"}
    else:
        return {"status": "not_running", "message": f"{key} was not running"}

def get_geoip(ip):
    """Get geolocation information for an IP address"""
    try:
        # Use a more reliable GeoIP service
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,city,lat,lon,timezone",
            timeout=3
        )
        data = response.json()
        
        if data.get("status") == "success":
            return {
                "country": data.get("country", "Unknown"),
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "timezone": data.get("timezone", "Unknown")
            }
    except Exception as e:
        print(f"GeoIP lookup failed for {ip}: {e}")
    
    return {
        "country": "Unknown",
        "city": "Unknown", 
        "region": "Unknown",
        "lat": 0,
        "lon": 0,
        "timezone": "Unknown"
    }

def analyze_attack_patterns():
    """Analyze attack patterns for threat intelligence"""
    patterns = {
        "top_sources": Counter(),
        "attack_types": Counter(),
        "time_distribution": defaultdict(int),
        "success_rate": {"total": 0, "successful": 0},
        "geographic_distribution": Counter()
    }
    
    if not os.path.exists(ATTACK_LOG):
        return patterns
    
    try:
        with open(ATTACK_LOG, 'r') as f:
            for line in f:
                if line.startswith('#') or ',' not in line:
                    continue
                
                parts = line.strip().split(',')
                if len(parts) >= 5:
                    timestamp, user, password, ip, status = parts[:5]
                    
                    try:
                        ts = int(timestamp)
                        hour = datetime.fromtimestamp(ts).hour
                        
                        patterns["top_sources"][ip] += 1
                        patterns["time_distribution"][hour] += 1
                        patterns["success_rate"]["total"] += 1
                        
                        if status == "SUCCESS":
                            patterns["success_rate"]["successful"] += 1
                        
                        # Determine attack type based on password patterns
                        if password.isdigit():
                            patterns["attack_types"]["Numeric Brute Force"] += 1
                        elif password.lower() in ['password', 'admin', '123456']:
                            patterns["attack_types"]["Common Password"] += 1
                        elif len(password) > 12:
                            patterns["attack_types"]["Complex Password"] += 1
                        else:
                            patterns["attack_types"]["Dictionary Attack"] += 1
                        
                        # Get geographic info (cached to avoid too many API calls)
                        geo_info = get_geoip(ip)
                        patterns["geographic_distribution"][geo_info["country"]] += 1
                        
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error analyzing attack patterns: {e}")
    
    return patterns

# Background thread for real-time updates
def background_updater():
    """Background thread to update metrics periodically"""
    while True:
        try:
            update_real_time_metrics()
            
            # Check for alerts
            if real_time_data["system"]["cpu"] > 90:
                add_notification(
                    f"High CPU usage detected: {real_time_data['system']['cpu']}%",
                    "warning",
                    "System Alert"
                )
            
            if real_time_data["threats"]["detected"] > 100:
                add_notification(
                    f"High threat activity: {real_time_data['threats']['detected']} threats detected",
                    "danger",
                    "Security Alert"
                )
            
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            print(f"Background updater error: {e}")
            time.sleep(10)

# Start background thread
threading.Thread(target=background_updater, daemon=True).start()

# Initialize database
init_database()

# ==================== ROUTES ====================

@app.before_request
def before_request():
    """Track request metrics"""
    request.start_time = time.time()
    performance_metrics["requests_handled"] += 1

@app.after_request
def after_request(response):
    """Update performance metrics after each request"""
    if hasattr(request, 'start_time'):
        response_time = time.time() - request.start_time
        performance_metrics["avg_response_time"] = (
            (performance_metrics["avg_response_time"] * 0.9) + (response_time * 0.1)
        )
    return response

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template("index.html")

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    uptime = time.time() - performance_metrics["uptime"]
    return jsonify({
        "status": "healthy",
        "uptime_seconds": int(uptime),
        "uptime_formatted": str(timedelta(seconds=int(uptime))),
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/real-time-data')
def get_real_time_data():
    """Get current real-time metrics"""
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "data": real_time_data,
        "performance": {
            "uptime": int(time.time() - performance_metrics["uptime"]),
            "requests_handled": performance_metrics["requests_handled"],
            "avg_response_time": round(performance_metrics["avg_response_time"] * 1000, 2)  # ms
        }
    })

@app.route('/api/notifications')
def get_notifications():
    """Get all notifications"""
    return jsonify({
        "notifications": notifications,
        "unread_count": len([n for n in notifications if not n["read"]])
    })

@app.route('/api/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    for notification in notifications:
        if notification["id"] == notification_id:
            notification["read"] = True
            return jsonify({"status": "marked_read"})
    return jsonify({"error": "Notification not found"}), 404

@app.route('/api/notifications/clear', methods=['POST'])
def clear_notifications():
    """Clear all notifications"""
    global notifications
    notifications = []
    return jsonify({"status": "cleared"})

@app.route('/start/<module>')
def start_module(module):
    """Start attack or defense module"""
    if module == "attacker":
        result = launch_process("../offensive/cracksim.py", "attacker")
    elif module == "defender":
        result = launch_process("../defensive/defendmonitor.py", "defender")
    else:
        return jsonify({"error": "Invalid module"}), 400
    
    return jsonify(result)

@app.route('/stop/<module>')
def stop_module(module):
    """Stop attack or defense module"""
    if module in processes:
        result = stop_process(module)
        return jsonify(result)
    return jsonify({"error": "Invalid module"}), 400

@app.route('/api/modules/status')
def get_module_status():
    """Get status of all modules"""
    status = {}
    for key, process in processes.items():
        if process and process.poll() is None:
            status[key] = {
                "running": True,
                "pid": process.pid,
                "uptime": "Unknown"  # Could be enhanced to track start time
            }
        else:
            status[key] = {"running": False, "pid": None, "uptime": None}
    
    return jsonify({"modules": status})

@app.route('/stats')
def api_stats():
    """Get comprehensive statistics"""
    total = success = fail = 0
    blocked_users = set()
    recent = []
    per_user = Counter()
    per_ip = Counter()
    per_pwd = Counter()
    per_hour = defaultdict(int)
    now = int(time.time())
    attempts_last_hour = 0
    
    # Process attack log
    if os.path.exists(ATTACK_LOG):
        with open(ATTACK_LOG) as f:
            for line in f:
                if "," not in line or line.startswith('#'):
                    continue
                parts = line.strip().split(",")
                if len(parts) < 5:
                    continue
                
                ts, user, pwd, ip, status = parts
                try:
                    ts = int(ts)
                except ValueError:
                    continue
                
                total += 1
                per_user[user] += 1
                per_ip[ip] += 1
                per_pwd[pwd] += 1
                per_hour[time.strftime("%H", time.localtime(ts))] += 1
                
                if now - ts < 3600:
                    attempts_last_hour += 1
                
                recent.append({
                    "time": time.strftime("%H:%M:%S", time.localtime(ts)),
                    "user": user,
                    "ip": ip,
                    "pwd": pwd,
                    "status": status,
                    "timestamp": ts
                })
                
                if status == "SUCCESS":
                    success += 1
                elif status == "FAIL":
                    fail += 1
    
    # Process defense log
    if os.path.exists(DEFENSE_LOG):
        with open(DEFENSE_LOG) as f:
            for line in f:
                if ",BLOCKED," in line:
                    blocked_users.add(line.split(",")[0])
                elif ",UNBLOCKED," in line:
                    blocked_users.discard(line.split(",")[0])
    
    # Get email statistics
    try:
        resp = requests.get("http://localhost:8025/api/v2/messages", timeout=2)
        emails_sent = resp.json().get("total", 0)
    except Exception:
        emails_sent = 0
    
    # Calculate derived statistics
    most_targeted_email = per_user.most_common(1)[0][0] if per_user else "N/A"
    most_used_pwd = per_pwd.most_common(1)[0][0] if per_pwd else "N/A"
    most_aggressive_ip = per_ip.most_common(1)[0][0] if per_ip else "N/A"
    
    # Get geolocation for most aggressive IP
    geo_info = get_geoip(most_aggressive_ip) if most_aggressive_ip != "N/A" else {}
    
    # Format hourly data
    per_hour_sorted = [per_hour.get(f"{h:02}", 0) for h in range(24)]
    
    # Get attack patterns
    patterns = analyze_attack_patterns()
    
    return jsonify({
        "attacks": total,
        "success": success,
        "fail": fail,
        "blocked": len(blocked_users),
        "emails_sent": emails_sent,
        "recent": recent[::-1][:20],  # Most recent first, limit to 20
        "most_targeted_email": most_targeted_email,
        "most_used_pwd": most_used_pwd,
        "most_aggressive_ip": most_aggressive_ip,
        "geoip": geo_info,
        "total_last_hour": attempts_last_hour,
        "hourly_attempts": per_hour_sorted,
        "per_ip": per_ip.most_common(10) if per_ip else [["No Data", 1]],
        "per_user": per_user.most_common(10) if per_user else [["No Data", 1]],
        "per_pwd": per_pwd.most_common(10) if per_pwd else [["No Data", 1]],
        "attack_patterns": {
            "top_sources": patterns["top_sources"].most_common(5),
            "attack_types": dict(patterns["attack_types"]),
            "time_distribution": dict(patterns["time_distribution"]),
            "success_rate": patterns["success_rate"],
            "geographic_distribution": patterns["geographic_distribution"].most_common(10)
        },
        "real_time_metrics": real_time_data
    })

@app.route('/api/threat-map')
def get_threat_map():
    """Get geographic threat data for world map"""
    threats = []
    
    if os.path.exists(ATTACK_LOG):
        recent_ips = set()
        cutoff_time = time.time() - 3600  # Last hour
        
        with open(ATTACK_LOG) as f:
            for line in f:
                if "," not in line or line.startswith('#'):
                    continue
                parts = line.strip().split(",")
                if len(parts) >= 5:
                    try:
                        ts = int(parts[0])
                        if ts > cutoff_time:
                            recent_ips.add(parts[3])  # IP address
                    except ValueError:
                        continue
        
        # Get geolocation for recent IPs
        for ip in list(recent_ips)[:20]:  # Limit to avoid API rate limits
            geo_info = get_geoip(ip)
            if geo_info["lat"] != 0 or geo_info["lon"] != 0:
                threats.append({
                    "ip": ip,
                    "lat": geo_info["lat"],
                    "lng": geo_info["lon"],
                    "country": geo_info["country"],
                    "city": geo_info["city"],
                    "severity": 1 + (hash(ip) % 3),  # Random severity 1-3
                    "timestamp": int(time.time())
                })
    
    return jsonify({"threats": threats})

@app.route('/mailhog')
def mailhog():
    """Get MailHog email data"""
    try:
        resp = requests.get("http://localhost:8025/api/v2/messages", timeout=2)
        items = resp.json().get("items", [])
        emails = []
        
        for item in items:
            try:
                to_addr = item['To'][0]['Mailbox'] + "@" + item['To'][0]['Domain']
                subject = item['Content']['Headers']['Subject'][0]
                created_time = item['Created']
                
                emails.append({
                    "time": created_time[11:19],
                    "to": to_addr,
                    "subject": subject,
                    "id": item.get('ID', ''),
                    "size": len(str(item.get('Content', {}))),
                    "timestamp": created_time
                })
            except (KeyError, IndexError):
                continue
        
        return jsonify({"emails": emails[:20]})  # Limit to 20 most recent
    except Exception as e:
        print(f"MailHog API error: {e}")
        return jsonify({"emails": []})

@app.route('/users')
def users():
    """Get list of usernames"""
    try:
        with open(USERNAMES_FILE) as f:
            users_list = [line.strip() for line in f if line.strip()]
        return jsonify({"users": users_list, "count": len(users_list)})
    except FileNotFoundError:
        return jsonify({"users": [], "count": 0})

@app.route('/passwords')
def passwords():
    """Get list of passwords"""
    try:
        with open(PASSWORDS_FILE) as f:
            pwd_list = [line.strip() for line in f if line.strip()]
        return jsonify({"passwords": pwd_list, "count": len(pwd_list)})
    except FileNotFoundError:
        return jsonify({"passwords": [], "count": 0})

@app.route('/blocked')
def api_blocked():
    """Get list of blocked users/IPs"""
    blocked = set()
    
    # Check defense log
    if os.path.exists(DEFENSE_LOG):
        with open(DEFENSE_LOG) as f:
            for line in f:
                if ",BLOCKED," in line:
                    blocked.add(line.split(",")[0])
                elif ",UNBLOCKED," in line:
                    blocked.discard(line.split(",")[0])
    
    # Check blocked file
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE) as f:
            for line in f:
                if line.strip():
                    blocked.add(line.strip())
    
    return jsonify({"blocked": list(blocked), "count": len(blocked)})

@app.route('/whitelist')
def api_whitelist():
    """Get list of whitelisted users/IPs"""
    whitelist = set()
    
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE) as f:
            for line in f:
                if line.strip():
                    whitelist.add(line.strip())
    
    return jsonify({"whitelist": list(whitelist), "count": len(whitelist)})

@app.route('/unblock')
def api_unblock():
    """Unblock a user"""
    user = request.args.get('user')
    if not user:
        return jsonify({"error": "User parameter required"}), 400
    
    # Log unblock action
    with open(DEFENSE_LOG, "a") as f:
        f.write(f"{user},UNBLOCKED,{int(time.time())}\n")
    
    # Remove from blocked file
    if os.path.exists(BLOCKED_FILE):
        with open(BLOCKED_FILE, "r") as f:
            lines = [l for l in f if l.strip() and l.strip() != user]
        with open(BLOCKED_FILE, "w") as f:
            f.writelines(lines)
    
    add_notification(f"User {user} has been unblocked", "info", "User Management")
    return jsonify({"status": "unblocked", "user": user})

@app.route('/block_user', methods=['POST'])
def block_user():
    """Block a user"""
    data = request.get_json()
    user = data.get('user') if data else None
    
    if not user:
        return jsonify({"error": "User required"}), 400
    
    # Log block action
    with open(DEFENSE_LOG, "a") as f:
        f.write(f"{user},BLOCKED,{int(time.time())}\n")
    
    # Add to blocked file
    with open(BLOCKED_FILE, "a") as f:
        f.write(user + "\n")
    
    add_notification(f"User {user} has been blocked", "warning", "User Management")
    return jsonify({"status": "blocked", "user": user})

@app.route('/whitelist_user', methods=['POST'])
def whitelist_user():
    """Add user to whitelist"""
    data = request.get_json()
    user = data.get('user') if data else None
    
    if not user:
        return jsonify({"error": "User required"}), 400
    
    with open(WHITELIST_FILE, "a") as f:
        f.write(user + "\n")
    
    add_notification(f"User {user} has been whitelisted", "success", "User Management")
    return jsonify({"status": "whitelisted", "user": user})

@app.route('/add_user', methods=['POST'])
def add_user():
    """Add new user credentials"""
    data = request.get_json()
    username = data.get('username') if data else None
    password = data.get('password') if data else None
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    # Add to respective files
    with open(USERNAMES_FILE, "a") as f:
        f.write(username + "\n")
    
    with open(PASSWORDS_FILE, "a") as f:
        f.write(password + "\n")
    
    with open(VALID_CREDS_FILE, "a") as f:
        f.write(f"{username}:{password}\n")
    
    add_notification(f"New user {username} added to system", "success", "User Management")
    return jsonify({"status": "added", "username": username})

@app.route('/add_password', methods=['POST'])
def add_password():
    """Add new password to dictionary"""
    data = request.get_json()
    password = data.get('password') if data else None
    
    if not password:
        return jsonify({"error": "Password required"}), 400
    
    with open(PASSWORDS_FILE, "a") as f:
        f.write(password + "\n")
    
    add_notification(f"New password added to dictionary", "info", "Password Management")
    return jsonify({"status": "added", "password": "***"})  # Don't return actual password

@app.route('/set_attack_speed', methods=['POST'])
def set_attack_speed():
    """Set attack simulation speed"""
    global attack_speed
    data = request.get_json()
    speed = data.get('speed') if data else None
    
    try:
        attack_speed = float(speed)
        add_notification(f"Attack speed set to {attack_speed}x", "info", "Configuration")
        return jsonify({"status": "ok", "speed": attack_speed})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid speed value"}), 400

@app.route('/upload_list', methods=['POST'])
def upload_list():
    """Upload email or password list"""
    list_type = request.form.get('type')
    uploaded_file = request.files.get('file')
    
    if not list_type or not uploaded_file:
        return jsonify({"error": "Type and file required"}), 400
    
    if list_type == "email":
        target_file = USERNAMES_FILE
    elif list_type == "password":
        target_file = PASSWORDS_FILE
    else:
        return jsonify({"error": "Invalid type"}), 400
    
    try:
        lines_added = 0
        with open(target_file, "a") as out:
            for line in uploaded_file:
                decoded_line = line.decode("utf-8").strip()
                if decoded_line:
                    out.write(decoded_line + "\n")
                    lines_added += 1
        
        add_notification(
            f"Uploaded {lines_added} {list_type} entries",
            "success",
            "File Upload"
        )
        return jsonify({"status": "ok", "lines_added": lines_added})
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/reset_stats', methods=['POST'])
def reset_stats():
    """Reset all statistics and logs"""
    try:
        # Reset log files
        with open(ATTACK_LOG, "w") as f:
            f.write("# Format: timestamp,user,password,ip,status\n")
        
        with open(DEFENSE_LOG, "w") as f:
            f.write("# Format: username,action,timestamp\n")
        
        # Clear notifications
        global notifications
        notifications = []
        
        # Reset real-time data
        global real_time_data
        real_time_data = {
            "threats": {"blocked": 0, "detected": 0, "quarantined": 0},
            "network": {"bandwidth": 0, "connections": 0, "latency": 0},
            "system": {"cpu": 0, "memory": 0, "disk": 0},
            "security": {"score": 85, "vulnerabilities": 0, "patches": 0}
        }
        
        add_notification("All statistics have been reset", "info", "System Reset")
        return jsonify({"status": "reset"})
    except Exception as e:
        return jsonify({"error": f"Reset failed: {str(e)}"}), 500

@app.route('/download_log')
def download_log():
    """Download log files"""
    log_type = request.args.get('type')
    
    if log_type == "attack" and os.path.exists(ATTACK_LOG):
        return send_file(ATTACK_LOG, as_attachment=True, download_name="attack_log.csv")
    elif log_type == "defense" and os.path.exists(DEFENSE_LOG):
        return send_file(DEFENSE_LOG, as_attachment=True, download_name="defense_log.csv")
    else:
        return jsonify({"error": "Invalid log type or file not found"}), 400

@app.route('/api/export', methods=['POST'])
def export_data():
    """Export dashboard data in various formats"""
    data = request.get_json()
    export_format = data.get('format', 'json')
    include_logs = data.get('include_logs', True)
    include_stats = data.get('include_stats', True)
    
    export_data = {
        "metadata": {
            "export_timestamp": datetime.now().isoformat(),
            "format": export_format,
            "version": "2.0.0"
        }
    }
    
    if include_stats:
        # Get current statistics
        stats_response = api_stats()
        export_data["statistics"] = stats_response.get_json()
    
    if include_logs:
        export_data["logs"] = {
            "attack_log": [],
            "defense_log": []
        }
        
        # Read attack log
        if os.path.exists(ATTACK_LOG):
            with open(ATTACK_LOG, 'r') as f:
                export_data["logs"]["attack_log"] = [
                    line.strip() for line in f if not line.startswith('#')
                ]
        
        # Read defense log
        if os.path.exists(DEFENSE_LOG):
            with open(DEFENSE_LOG, 'r') as f:
                export_data["logs"]["defense_log"] = [
                    line.strip() for line in f if not line.startswith('#')
                ]
    
    export_data["notifications"] = notifications
    export_data["real_time_data"] = real_time_data
    
    if export_format == 'json':
        return jsonify(export_data)
    elif export_format == 'csv':
        # Convert to CSV format (simplified)
        csv_data = "timestamp,type,data\n"
        for notification in notifications:
            csv_data += f"{notification['timestamp']},notification,\"{notification['message']}\"\n"
        return csv_data, 200, {'Content-Type': 'text/csv'}
    else:
        return jsonify({"error": "Unsupported format"}), 400

@app.route('/api/system-info')
def get_system_info():
    """Get detailed system information"""
    try:
        import psutil
        
        # Get system information
        cpu_info = {
            "usage": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        memory_info = psutil.virtual_memory()._asdict()
        disk_info = psutil.disk_usage('/')._asdict()
        
        # Get network information
        network_info = {
            "connections": len(psutil.net_connections()),
            "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
        }
        
        # Get process information
        processes_info = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes_info.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return jsonify({
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
            "processes": sorted(processes_info, key=lambda x: x['cpu_percent'], reverse=True)[:10],
            "timestamp": datetime.now().isoformat()
        })
    
    except ImportError:
        return jsonify({
            "error": "psutil not available",
            "message": "Install psutil for detailed system information"
        }), 503

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    performance_metrics["errors_count"] += 1
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    performance_metrics["errors_count"] += 1
    print(f"Unhandled exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create empty log files if they don't exist
    for log_file in [ATTACK_LOG, DEFENSE_LOG]:
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write(f"# Created: {datetime.now().isoformat()}\n")
    
    print("🚀 Starting CrackDefend Dashboard Server...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔧 API endpoints available at: http://localhost:5000/api/")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
