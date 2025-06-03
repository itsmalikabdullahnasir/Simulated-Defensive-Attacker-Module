import time
import os
import smtplib
import json
import sqlite3
import threading
import hashlib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, Counter
import ipaddress
import re

# Configuration
LOG_FILE = "../data/attack_log.csv"
DEFENSE_LOG = "../data/defense_log.csv"
BLOCKED_FILE = "../data/blocked.txt"
WHITELIST_FILE = "../data/whitelist.txt"
DATABASE_FILE = "../data/dashboard.db"
CONFIG_FILE = "../data/defense_config.json"

# Enhanced thresholds and settings
DEFAULT_CONFIG = {
    "ban_threshold": 5,
    "unblock_time": 2 * 60,  # 2 minutes
    "monitoring_interval": 5,
    "email_notifications": True,
    "adaptive_thresholds": True,
    "geo_blocking": False,
    "honeypot_detection": True,
    "rate_limiting": True,
    "threat_intelligence": True,
    "auto_whitelist_trusted": True,
    "escalation_levels": {
        "low": {"threshold": 3, "action": "log"},
        "medium": {"threshold": 5, "action": "block"},
        "high": {"threshold": 10, "action": "block_ip"},
        "critical": {"threshold": 20, "action": "escalate"}
    },
    "blocked_countries": [],
    "trusted_networks": ["127.0.0.0/8", "10.0.0.0/8", "192.168.0.0/16"],
    "honeypot_users": ["admin", "root", "administrator", "test", "guest"],
    "suspicious_patterns": [
        r".*[<>\"'&].*",  # XSS attempts
        r".*union.*select.*",  # SQL injection
        r".*\.\./.*",  # Directory traversal
        r".*script.*",  # Script injection
    ]
}

class ThreatIntelligence:
    """Advanced threat intelligence and pattern recognition"""
    
    def __init__(self):
        self.known_bad_ips = set()
        self.suspicious_patterns = []
        self.attack_signatures = {}
        self.load_threat_feeds()
    
    def load_threat_feeds(self):
        """Load threat intelligence from various sources"""
        try:
            # Load local threat intelligence
            threat_file = "../data/threat_intelligence.json"
            if os.path.exists(threat_file):
                with open(threat_file, 'r') as f:
                    data = json.load(f)
                    self.known_bad_ips.update(data.get('bad_ips', []))
                    self.suspicious_patterns.extend(data.get('patterns', []))
        except Exception as e:
            print(f"[THREAT_INTEL] Error loading threat feeds: {e}")
    
    def is_known_bad_ip(self, ip):
        """Check if IP is in known bad IP list"""
        return ip in self.known_bad_ips
    
    def analyze_attack_pattern(self, user, password, ip):
        """Analyze attack patterns for threat classification"""
        threat_score = 0
        indicators = []
        
        # Check for suspicious patterns in username/password
        for pattern in self.suspicious_patterns:
            if re.search(pattern, user, re.IGNORECASE) or re.search(pattern, password, re.IGNORECASE):
                threat_score += 10
                indicators.append(f"Suspicious pattern detected: {pattern}")
        
        # Check for known bad IP
        if self.is_known_bad_ip(ip):
            threat_score += 20
            indicators.append("Known malicious IP")
        
        # Check for common attack patterns
        if user.lower() in ['admin', 'root', 'administrator']:
            threat_score += 5
            indicators.append("High-value target username")
        
        if password in ['password', '123456', 'admin', 'root']:
            threat_score += 5
            indicators.append("Common password attempt")
        
        return {
            "threat_score": threat_score,
            "classification": self.classify_threat(threat_score),
            "indicators": indicators
        }
    
    def classify_threat(self, score):
        """Classify threat based on score"""
        if score >= 30:
            return "CRITICAL"
        elif score >= 20:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "LOW"

class GeoIPAnalyzer:
    """Geographic IP analysis and blocking"""
    
    def __init__(self, config):
        self.config = config
        self.geo_cache = {}
        self.blocked_countries = set(config.get('blocked_countries', []))
    
    def get_country(self, ip):
        """Get country for IP address with caching"""
        if ip in self.geo_cache:
            return self.geo_cache[ip]
        
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,country,countryCode",
                timeout=3
            )
            data = response.json()
            
            if data.get("status") == "success":
                country = data.get("countryCode", "Unknown")
                self.geo_cache[ip] = country
                return country
        except Exception as e:
            print(f"[GEO] Error getting country for {ip}: {e}")
        
        self.geo_cache[ip] = "Unknown"
        return "Unknown"
    
    def is_blocked_country(self, ip):
        """Check if IP is from a blocked country"""
        if not self.config.get('geo_blocking', False):
            return False
        
        country = self.get_country(ip)
        return country in self.blocked_countries

class RateLimiter:
    """Advanced rate limiting with sliding window"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_until = {}
    
    def is_rate_limited(self, ip, max_requests=10, window_seconds=60):
        """Check if IP is rate limited"""
        now = time.time()
        
        # Check if IP is currently blocked
        if ip in self.blocked_until and now < self.blocked_until[ip]:
            return True
        
        # Clean old requests
        cutoff = now - window_seconds
        self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > cutoff]
        
        # Check rate limit
        if len(self.requests[ip]) >= max_requests:
            # Block for 5 minutes
            self.blocked_until[ip] = now + 300
            return True
        
        # Add current request
        self.requests[ip].append(now)
        return False

class EnhancedDefenseMonitor:
    """Enhanced defense monitoring system with advanced threat detection"""
    
    def __init__(self):
        self.config = self.load_config()
        self.threat_intel = ThreatIntelligence()
        self.geo_analyzer = GeoIPAnalyzer(self.config)
        self.rate_limiter = RateLimiter()
        self.banned_users = {}
        self.banned_ips = {}
        self.attack_stats = defaultdict(int)
        self.honeypot_hits = defaultdict(int)
        self.running = True
        
        # Initialize database
        self.init_database()
        
        # Start background threads
        self.start_background_tasks()
    
    def load_config(self):
        """Load configuration from file or use defaults"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    merged_config = DEFAULT_CONFIG.copy()
                    merged_config.update(config)
                    return merged_config
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}")
        
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[CONFIG] Error saving config: {e}")
    
    def init_database(self):
        """Initialize SQLite database for enhanced logging"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defense_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    event_type TEXT,
                    target TEXT,
                    source_ip TEXT,
                    action_taken TEXT,
                    threat_score INTEGER,
                    classification TEXT,
                    indicators TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocked_entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_type TEXT,
                    entity_value TEXT,
                    blocked_at INTEGER,
                    unblock_at INTEGER,
                    reason TEXT,
                    threat_score INTEGER,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DATABASE] Error initializing database: {e}")
    
    def log_defense_event(self, event_type, target, source_ip, action, threat_analysis=None):
        """Log defense event to database"""
        try:
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            
            threat_score = threat_analysis.get('threat_score', 0) if threat_analysis else 0
            classification = threat_analysis.get('classification', 'UNKNOWN') if threat_analysis else 'UNKNOWN'
            indicators = json.dumps(threat_analysis.get('indicators', [])) if threat_analysis else '[]'
            
            cursor.execute('''
                INSERT INTO defense_events 
                (timestamp, event_type, target, source_ip, action_taken, threat_score, classification, indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(time.time()), event_type, target, source_ip, action,
                threat_score, classification, indicators
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DATABASE] Error logging defense event: {e}")
    
    def send_enhanced_email(self, to_addr, subject, body, priority="normal", threat_data=None):
        """Send enhanced email notifications with threat intelligence"""
        if not self.config.get('email_notifications', True):
            return
        
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"[CrackDefend] {subject}"
            msg['From'] = 'defense@crackdefend.local'
            msg['To'] = to_addr
            msg['X-Priority'] = '1' if priority == "high" else '3'
            
            # Create enhanced email body
            enhanced_body = f"""
CrackDefend Security Alert
========================

{body}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Priority: {priority.upper()}

"""
            
            if threat_data:
                enhanced_body += f"""
Threat Analysis:
- Threat Score: {threat_data.get('threat_score', 'N/A')}
- Classification: {threat_data.get('classification', 'N/A')}
- Indicators: {', '.join(threat_data.get('indicators', []))}

"""
            
            enhanced_body += """
This is an automated message from CrackDefend Defense Monitor.
For more information, check the dashboard at http://localhost:5000

Best regards,
CrackDefend Security Team
"""
            
            msg.attach(MIMEText(enhanced_body, 'plain'))
            
            with smtplib.SMTP('localhost', 1025, timeout=5) as server:
                server.sendmail(msg['From'], [msg['To']], msg.as_string())
                
            print(f"[EMAIL] Sent notification: {subject}")
            
        except Exception as e:
            print(f"[EMAIL] Error sending notification: {e}")
    
    def load_failed_attempts(self):
        """Load and analyze failed login attempts"""
        fails = defaultdict(list)
        ip_fails = defaultdict(list)
        
        if not os.path.exists(LOG_FILE):
            return fails, ip_fails
        
        try:
            with open(LOG_FILE) as f:
                for line in f:
                    if not line.strip() or line.strip().startswith("#"):
                        continue
                    
                    parts = line.strip().split(",")
                    if len(parts) != 5:
                        continue
                    
                    ts, user, pwd, ip, status = parts
                    
                    try:
                        timestamp = int(ts)
                    except ValueError:
                        continue
                    
                    if status == "FAIL":
                        fails[user].append({
                            'timestamp': timestamp,
                            'password': pwd,
                            'ip': ip
                        })
                        ip_fails[ip].append({
                            'timestamp': timestamp,
                            'user': user,
                            'password': pwd
                        })
                    
                    # Check for honeypot hits
                    if user.lower() in self.config.get('honeypot_users', []):
                        self.honeypot_hits[ip] += 1
                        
        except Exception as e:
            print(f"[ANALYSIS] Error loading failed attempts: {e}")
        
        return fails, ip_fails
    
    def is_trusted_network(self, ip):
        """Check if IP is from a trusted network"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            for network in self.config.get('trusted_networks', []):
                if ip_obj in ipaddress.ip_network(network):
                    return True
        except Exception:
            pass
        return False
    
    def analyze_attack_velocity(self, attempts):
        """Analyze attack velocity and patterns"""
        if len(attempts) < 2:
            return {"velocity": 0, "pattern": "single"}
        
        # Sort by timestamp
        sorted_attempts = sorted(attempts, key=lambda x: x['timestamp'])
        
        # Calculate velocity (attempts per minute)
        time_span = sorted_attempts[-1]['timestamp'] - sorted_attempts[0]['timestamp']
        if time_span == 0:
            velocity = len(attempts)
        else:
            velocity = len(attempts) / (time_span / 60)  # attempts per minute
        
        # Detect patterns
        passwords = [attempt['password'] for attempt in sorted_attempts]
        unique_passwords = len(set(passwords))
        
        if unique_passwords == 1:
            pattern = "single_password"
        elif unique_passwords == len(passwords):
            pattern = "dictionary_attack"
        else:
            pattern = "mixed_attack"
        
        return {
            "velocity": velocity,
            "pattern": pattern,
            "unique_passwords": unique_passwords,
            "time_span": time_span
        }
    
    def adaptive_threshold_calculation(self, user, base_threshold):
        """Calculate adaptive threshold based on user behavior"""
        if not self.config.get('adaptive_thresholds', True):
            return base_threshold
        
        # Check if user is in honeypot list
        if user.lower() in self.config.get('honeypot_users', []):
            return 1  # Immediate action for honeypot users
        
        # Check historical behavior
        # This could be enhanced with machine learning
        return base_threshold
    
    def ban_user(self, user, reason="Brute force attack", threat_analysis=None):
        """Ban user with enhanced logging and notifications"""
        print(f"[BAN] User {user} blocked - Reason: {reason}")
        
        # Log to traditional defense log
        with open(DEFENSE_LOG, "a") as f:
            f.write(f"{user},BLOCKED,{int(time.time())}\n")
        
        # Log to blocked file
        with open(BLOCKED_FILE, "a") as f:
            f.write(user + "\n")
        
        # Log to database
        self.log_defense_event("USER_BLOCKED", user, "N/A", "BLOCKED", threat_analysis)
        
        # Add to banned users with timestamp
        self.banned_users[user] = time.time()
        
        # Send enhanced email notification
        priority = "high" if threat_analysis and threat_analysis.get('threat_score', 0) > 20 else "normal"
        self.send_enhanced_email(
            "admin@crackdefend.local",
            f"User Blocked: {user}",
            f"User {user} has been blocked due to {reason}.\n\nImmediate action may be required.",
            priority,
            threat_analysis
        )
        
        # Update attack statistics
        self.attack_stats['users_blocked'] += 1
    
    def ban_ip(self, ip, reason="Malicious activity", threat_analysis=None):
        """Ban IP address with enhanced logging"""
        print(f"[BAN] IP {ip} blocked - Reason: {reason}")
        
        # Log to database
        self.log_defense_event("IP_BLOCKED", ip, ip, "BLOCKED", threat_analysis)
        
        # Add to banned IPs
        self.banned_ips[ip] = time.time()
        
        # Send notification
        priority = "high" if threat_analysis and threat_analysis.get('threat_score', 0) > 20 else "normal"
        self.send_enhanced_email(
            "admin@crackdefend.local",
            f"IP Address Blocked: {ip}",
            f"IP address {ip} has been blocked due to {reason}.\n\nThis may indicate a coordinated attack.",
            priority,
            threat_analysis
        )
        
        # Update attack statistics
        self.attack_stats['ips_blocked'] += 1
    
    def unblock_user(self, user):
        """Unblock user with logging"""
        print(f"[UNBLOCK] User {user} unblocked")
        
        # Log to defense log
        with open(DEFENSE_LOG, "a") as f:
            f.write(f"{user},UNBLOCKED,{int(time.time())}\n")
        
        # Remove from blocked file
        if os.path.exists(BLOCKED_FILE):
            try:
                with open(BLOCKED_FILE, "r") as f:
                    lines = [line for line in f if line.strip() != user]
                with open(BLOCKED_FILE, "w") as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"[UNBLOCK] Error updating blocked file: {e}")
        
        # Log to database
        self.log_defense_event("USER_UNBLOCKED", user, "N/A", "UNBLOCKED")
        
        # Remove from banned users
        if user in self.banned_users:
            del self.banned_users[user]
    
    def unblock_ip(self, ip):
        """Unblock IP address"""
        print(f"[UNBLOCK] IP {ip} unblocked")
        
        # Log to database
        self.log_defense_event("IP_UNBLOCKED", ip, ip, "UNBLOCKED")
        
        # Remove from banned IPs
        if ip in self.banned_ips:
            del self.banned_ips[ip]
    
    def check_escalation_needed(self, threat_analysis, user, ip):
        """Check if threat requires escalation"""
        threat_score = threat_analysis.get('threat_score', 0)
        classification = threat_analysis.get('classification', 'LOW')
        
        escalation_levels = self.config.get('escalation_levels', {})
        
        if classification == "CRITICAL" or threat_score >= 30:
            # Critical threat - immediate escalation
            self.escalate_threat(user, ip, threat_analysis, "CRITICAL")
            return True
        elif classification == "HIGH" or threat_score >= 20:
            # High threat - escalate if multiple indicators
            if len(threat_analysis.get('indicators', [])) >= 3:
                self.escalate_threat(user, ip, threat_analysis, "HIGH")
                return True
        
        return False
    
    def escalate_threat(self, user, ip, threat_analysis, level):
        """Escalate threat to security team"""
        print(f"[ESCALATION] {level} threat escalated - User: {user}, IP: {ip}")
        
        # Log escalation
        self.log_defense_event("THREAT_ESCALATED", user, ip, f"ESCALATED_{level}", threat_analysis)
        
        # Send high-priority notification
        self.send_enhanced_email(
            "security@crackdefend.local",
            f"URGENT: {level} Threat Detected",
            f"""
IMMEDIATE ATTENTION REQUIRED

A {level} level threat has been detected and requires immediate investigation.

Target User: {user}
Source IP: {ip}
Threat Score: {threat_analysis.get('threat_score', 'N/A')}
Classification: {threat_analysis.get('classification', 'N/A')}

Threat Indicators:
{chr(10).join('- ' + indicator for indicator in threat_analysis.get('indicators', []))}

Please investigate immediately and take appropriate action.
""",
            "high",
            threat_analysis
        )
        
        # Update statistics
        self.attack_stats['threats_escalated'] += 1
    
    def generate_defense_report(self):
        """Generate periodic defense report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "period": "Last monitoring cycle",
            "statistics": dict(self.attack_stats),
            "active_bans": {
                "users": len(self.banned_users),
                "ips": len(self.banned_ips)
            },
            "honeypot_activity": dict(self.honeypot_hits),
            "top_attacking_ips": [],
            "threat_summary": {
                "total_events": sum(self.attack_stats.values()),
                "high_priority": self.attack_stats.get('threats_escalated', 0)
            }
        }
        
        return report
    
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        # Start report generation thread
        def report_generator():
            while self.running:
                try:
                    time.sleep(300)  # Generate report every 5 minutes
                    report = self.generate_defense_report()
                    
                    # Save report to file
                    report_file = f"../data/defense_report_{int(time.time())}.json"
                    with open(report_file, 'w') as f:
                        json.dump(report, f, indent=2)
                    
                    # Clean old reports (keep last 24 hours)
                    self.cleanup_old_reports()
                    
                except Exception as e:
                    print(f"[REPORT] Error generating report: {e}")
        
        threading.Thread(target=report_generator, daemon=True).start()
    
    def cleanup_old_reports(self):
        """Clean up old report files"""
        try:
            data_dir = "../data"
            cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
            
            for filename in os.listdir(data_dir):
                if filename.startswith("defense_report_") and filename.endswith(".json"):
                    file_path = os.path.join(data_dir, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        
        except Exception as e:
            print(f"[CLEANUP] Error cleaning old reports: {e}")
    
    def monitor(self):
        """Main monitoring loop with enhanced threat detection"""
        print("🛡️  Enhanced DefendMonitor: Advanced threat detection active...")
        print(f"📊 Configuration: {json.dumps(self.config, indent=2)}")
        
        while self.running:
            try:
                # Load failed attempts
                user_fails, ip_fails = self.load_failed_attempts()
                
                # Process user-based attacks
                for user, attempts in user_fails.items():
                    if user in self.banned_users:
                        continue
                    
                    # Calculate adaptive threshold
                    threshold = self.adaptive_threshold_calculation(
                        user, 
                        self.config['ban_threshold']
                    )
                    
                    if len(attempts) >= threshold:
                        # Analyze the most recent attempt for threat intelligence
                        latest_attempt = max(attempts, key=lambda x: x['timestamp'])
                        
                        threat_analysis = self.threat_intel.analyze_attack_pattern(
                            user, 
                            latest_attempt['password'], 
                            latest_attempt['ip']
                        )
                        
                        # Analyze attack velocity
                        velocity_analysis = self.analyze_attack_velocity(attempts)
                        threat_analysis['velocity'] = velocity_analysis
                        
                        # Check for escalation
                        if not self.check_escalation_needed(threat_analysis, user, latest_attempt['ip']):
                            # Standard ban
                            reason = f"Brute force attack ({len(attempts)} attempts)"
                            self.ban_user(user, reason, threat_analysis)
                
                # Process IP-based attacks
                for ip, attempts in ip_fails.items():
                    if ip in self.banned_ips or self.is_trusted_network(ip):
                        continue
                    
                    # Check rate limiting
                    if self.rate_limiter.is_rate_limited(ip):
                        continue
                    
                    # Check geographic blocking
                    if self.geo_analyzer.is_blocked_country(ip):
                        threat_analysis = {
                            "threat_score": 15,
                            "classification": "MEDIUM",
                            "indicators": ["Blocked country"]
                        }
                        self.ban_ip(ip, "Geographic blocking", threat_analysis)
                        continue
                    
                    # Check for distributed attacks from single IP
                    unique_users = len(set(attempt['user'] for attempt in attempts))
                    if unique_users >= 5:  # Attacking multiple users
                        threat_analysis = {
                            "threat_score": 25,
                            "classification": "HIGH",
                            "indicators": [f"Distributed attack on {unique_users} users"]
                        }
                        self.ban_ip(ip, "Distributed brute force attack", threat_analysis)
                        continue
                    
                    # Check honeypot hits
                    if self.honeypot_hits[ip] >= 1:
                        threat_analysis = {
                            "threat_score": 30,
                            "classification": "CRITICAL",
                            "indicators": ["Honeypot interaction"]
                        }
                        self.ban_ip(ip, "Honeypot interaction", threat_analysis)
                
                # Process unblocking
                current_time = time.time()
                unblock_time = self.config['unblock_time']
                
                # Unblock users
                for user in list(self.banned_users.keys()):
                    if current_time - self.banned_users[user] > unblock_time:
                        self.unblock_user(user)
                
                # Unblock IPs (longer timeout for IPs)
                ip_unblock_time = unblock_time * 3  # 3x longer for IPs
                for ip in list(self.banned_ips.keys()):
                    if current_time - self.banned_ips[ip] > ip_unblock_time:
                        self.unblock_ip(ip)
                
                # Update statistics
                self.attack_stats['monitoring_cycles'] += 1
                
                # Sleep until next monitoring cycle
                time.sleep(self.config['monitoring_interval'])
                
            except KeyboardInterrupt:
                print("\n[MONITOR] Shutting down gracefully...")
                self.running = False
                break
            except Exception as e:
                print(f"[MONITOR] Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def shutdown(self):
        """Graceful shutdown"""
        print("[MONITOR] Shutting down Enhanced Defense Monitor...")
        self.running = False
        
        # Generate final report
        final_report = self.generate_defense_report()
        with open("../data/final_defense_report.json", 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print("[MONITOR] Shutdown complete.")

def main():
    """Main entry point"""
    monitor = EnhancedDefenseMonitor()
    
    try:
        monitor.monitor()
    except KeyboardInterrupt:
        monitor.shutdown()
    except Exception as e:
        print(f"[MAIN] Fatal error: {e}")
        monitor.shutdown()

if __name__ == "__main__":
    main()
