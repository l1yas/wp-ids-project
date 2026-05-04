#libraries
import re
import time
from collections import defaultdict
import subprocess
import json
from bruteforce import detect_bruteforce

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

def extract_url(line):
    try :
        return line.split('"')[1].split(" ")[1]
    except:
        return ""

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
def extract_ip(line):
	return line.split(" ")[0]

def extract_timestamp(line):
	return line.split("[")[1].split("]")[0]

def json_logs(data):
    with open(json_output, "a") as f:
    	f.write(json.dumps(data) + "\n")


def run():
    print("Script IDS démarré")

    for line in docker_logs():
        ip= extract_ip(line)        
        url = extract_url(line)
        attack = detection(line)
        brute= detect_bruteforce(ip,url)

        if brute:
            alert_text = f"{bold}{rouge}[Alert] {vert}BRUTEFORCE{reset} from {bold}{ip}{reset}"
            print(alert_text)
            log_alert(alert_text)
            alert_json = {
                "ip": ip,
                "attack": "BRUTEFORCE",
                "url": url,
                "log": line.strip()
            }
            json_logs(alert_json)
            continue
        if attack:
            alert_text = f"{bold}{jaune}[Alert] {vert}{attack}{reset} in {bold}{line.strip()}{reset}"
            print(alert_text)
            log_alert(alert_text)

            alert_json = {
                "ip": ip,
                "attack": attack,
                "url": url,
                "log": line.strip()
            }

            json_logs(alert_json)

 
if __name__ == "__main__":
    run()
