#libraries
import re
import time
from collections import defaultdict
import subprocess
import json
from bruteforce import failed_logins, detect_bruteforce
from parsers.wp_simple_history import get_failed_logins_events
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
        r"(?i)(\%27|')\s*(or|and)\s*\d+=\d+",
        r"(?i)(union(\s+all)?\s+select)",
        r"(?i)(or\s+1\s*=\s*1)",
        r"(?i)(--|#|/\*)",
        r"(?i)sleep\s*\(",
        r"(?i)benchmark\s*\(",
        r"(?i)information_schema",
        r"(?i)load_file\s*\(",
        r"(?i)into\s+outfile",
        r"(?i)extractvalue\s*\(",
        r"(?i)updatexml\s*\("
    ],

    "LFI": [
        r"(\.\./|\.\.\\)+",
        r"(?i)/etc/passwd",
        r"(?i)/proc/self/environ",
        r"(?i)boot\.ini",
        r"(?i)wp-config\.php",
        r"(?i)php://filter",
        r"(?i)php://input",
        r"(?i)file://",
        r"(?i)expect://",
        r"(%2e%2e%2f|%2e%2e%5c)"
    ],

    "XSS": [
    r"(?i)<\s*script",
    r"(?i)javascript\s*:",
    r"(?i)on\w+\s*=",
    r"(?i)<img[^>]+onerror",
    r"(?i)<svg[^>]+onload",
    r"(?i)document\.cookie",
    r"(?i)alert\s*\(",
    r"(?i)eval\s*\(",
    r"(?i)src\s*=\s*javascript:"
    ],

    "CommandInjection": [
    r"(?i)(;|\||&&)\s*(cat|ls|id|whoami|wget|curl)",
    r"(?i)`.*`",
    r"(?i)\$\(",
    r"(?i)/bin/(sh|bash)",
    r"(?i)nc\s+-e"
    ],

    "FileDisclosure": [
    r"(?i)/etc/shadow",
    r"(?i)/etc/hosts",
    r"(?i)\.env",
    r"(?i)id_rsa",
    r"(?i)config\.php",
    ],

    "WebShell": [
    r"(?i)cmd=",
    r"(?i)exec\(",
    r"(?i)system\(",
    r"(?i)passthru\(",
    r"(?i)shell_exec\("
    ]
}

#functions

severity_map = {
    "SQLi": 5,
    "LFI": 4,
    "XSS": 3,
    "CommandInjection": 5,
    "FileDisclosure": 4,
    "WebShell": 5,
    "SSRF": 4,
    "BRUTEFORCE": 2
}

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

# -- Threads 

def web_loop():
    for line in docker_logs():

        ip = extract_ip(line)
        url = extract_url(line)
        attack = detection(line)

        if attack:
            severity = severity_map.get(attack, 1)
            alert_text = f"{bold}{jaune}[Alert]{reset} {attack} from {ip}"
            print(alert_text)

            log_alert(alert_text)

            json_logs({
                "timestamp": extract_timestamp(line),
                "source": "nginx",
                "type": "web",
                "subtype": attack,
                "severity": severity,
                "ip": ip,
                "username": None,
                "url": url, 
                "log": line.strip()
            })

def auth_loop():
    seen = set()

    while True:

        events = get_failed_logins_events()

        for event in events:

            key = event["raw"]

            if key in seen:
                continue

            seen.add(key)

            username = event["username"]

            failed_logins("unknown", username)

            brute = detect_bruteforce("unknown", username)

            if brute:

                alert_text = (
                    f"{bold}{rouge}[ALERT]{reset} "
                    f"BRUTEFORCE user={username}"
                )

                print(alert_text)

                log_alert(alert_text)

            json_logs({
                "timestamp": event.get("date"),
                "source": "wordpress",
                "type": "auth",
                "subtype": "bruteforce",
                "ip": "unknown",
                "username": username,
                "url": None, 
                "log": event["raw"]
            })

        time.sleep(5)
        
if __name__ == "__main__":

    print("Script IDS démarré")

    t1 = threading.Thread(target=web_loop, daemon=True)
    t2 = threading.Thread(target=auth_loop, daemon=True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
