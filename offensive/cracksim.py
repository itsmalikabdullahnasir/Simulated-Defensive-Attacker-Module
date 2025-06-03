
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
                f.write(f"{now},{user},{pwd},{ip},{status}\n")
            print(f"User {user} is blocked. Attempt BLOCKED.")
            time.sleep(get_attack_speed())
            continue
        is_valid = valid_creds.get(user) == pwd
        status = "SUCCESS" if is_valid else "FAIL"
        with open(ATTACK_LOG, "a") as f:
            f.write(f"{now},{user},{pwd},{ip},{status}\n")
        print(f"Trying {user} with {pwd} from {ip} ... {status}")
        if is_valid:
            send_mailhog_email(
                user,
                "Login Alert",
                f"Hi {user},\n\nYour account was logged into at {time.ctime(now)} from IP {ip}. If this wasn't you, please change your password!\n"
            )
        time.sleep(get_attack_speed())

if __name__ == "__main__":
    main()
