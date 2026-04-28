import re
import time
from collections import defaultdict
import subprocess

log_file= "access.log"
alert_file = "alerts.log"

rouge="\033[91m"
vert="\033[92m"
jaune="\033[93m"
bleu="\033[96m"
reset="\033[0m"
bold="\033[1m"

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

def extract_ip(line):
    return line.split(" ")[0]

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

def run():
    print("Script IDS démarré")
    for line in docker_logs():
        attack = detection(line)
        if attack:
            alert = f"{bold}{vert}[Alerte]{jaune} {attack}{reset} in {bold}{line.strip()}{reset}"
            print(alert)
            log_alert(alert)

if __name__ == "__main__":
    run()
