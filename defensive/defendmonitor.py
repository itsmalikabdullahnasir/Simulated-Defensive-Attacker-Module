
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
        f.write(f"{user},BLOCKED,{int(time.time())}\n")
    with open(BLOCKED_FILE, "a") as f:
        f.write(user + "\n")

def unblock_user(user):
    print(f"[UNBLOCK] User {user} is now unblocked")
    with open(DEFENSE_LOG, "a") as f:
        f.write(f"{user},UNBLOCKED,{int(time.time())}\n")

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
