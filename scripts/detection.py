#libraries
import re
import time
from collections import defaultdict
import subprocess
import json
from bruteforce import failed_logins, detect_bruteforce
import threading

# files
log_file= "access.log"
alert_file = "alerts.log"
json_output="logs.json"

# colors
rouge="\033[91m"
vert="\033[92m"
jaune="\033[93m"
bleu="\033[96m"
reset="\033[0m"
bold="\033[1m"

# patterns
patterns = {
    "SQLi": [
        r"(?i)(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"(?i)(union.*select)",
        r"(?i)(or\s+1=1)",
        r"(?i)(sleep\()"
    ],
    "LFI": [
        r"(\.\./\.\./)",
        r"/etc/passwd",
        r"wp-config\.php"
    ],
    "XSS": [
        r"(?i)<script>",
        r"(?i)javascript:",
        r"(?i)onerror="
    ],
}

#functions



def detection(line):
    for attack_type, PATTERNS in patterns.items():
        for pattern in PATTERNS:
            if re.search(pattern, line):
                return attack_type
    return None

def log_alert(message):
    with open(alert_file, "a") as f:
            f.write(message + "\n")

def docker_logs():
    cmd = ["docker", "logs", "-f","wordpress-wordpress-1"]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    for line in process.stdout:
        yield line

def is_failed_login(line):
    return "Failed to login" in line
            


def json_logs(data):
    with open(json_output, "a") as f:
    	f.write(json.dumps(data) + "\n")

# -- Extractions

def extract_url(line):
    try :
        return line.split('"')[1].split(" ")[1]
    except:
        return ""

def extract_ip(line):
    return line.split(" ")[0]

def extract_timestamp(line):
	return line.split("[")[1].split("]")[0]

def extract_username(line):
	match = re.search(r'username "([^"]+)"', line)
	return match.group(1) if match else None

# -- Threads 

def web_loop():
    for line in docker_logs():

        ip = extract_ip(line)
        url = extract_url(line)
        attack = detection(line)

        if attack:
            alert_text = f"{bold}{jaune}[Alert]{reset} {attack} from {ip}"
            print(alert_text)

            log_alert(alert_text)

            json_logs({
                "ip": ip,
                "attack": attack,
                "url": url,
                "log": line.strip()
            })

def auth_loop():
    seen = set()

    while True:

        process = subprocess.Popen(
            [
                "docker", "exec", "wordpress-wordpress-1",
                "wp", "simple-history", "list", "--allow-root"
            ],
            stdout=subprocess.PIPE,
            text=True
        )

        for line in process.stdout:

            if "Failed to login" not in line:
                continue

            username = extract_username(line)

            if not username:
                continue

            if line in seen:
                continue

            seen.add(line)

            failed_logins("unknown", username)

            brute = detect_bruteforce("unknown", username)

            if brute:
                print(f"{bold}{rouge}[ALERT]{reset} BRUTEFORCE user={username}")

        time.sleep(5)

if __name__ == "__main__":

    print("Script IDS démarré")

    t1 = threading.Thread(target=web_loop, daemon=True)
    t2 = threading.Thread(target=auth_loop, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
