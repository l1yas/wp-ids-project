import subprocess
import re

def fetch_logs():
        result = subprocess.run(
                ["wp", "simple-history", "list", "--allow-root"],
                capture_output=True,
                text=True
        )
        return result.stdout

def failed_logins(raw):
        events=[]
        for line in raw.split("\n"):
                if "Failed to login" in line:
                        user_match = re.search(r'user name "[(^"]+)"', line)
                        username = user_match.group(1) if user_match else None
                        events.append({
                                "type": "failed_login",
                                "username": username,
                                "ip": None,
                                "raw": line.strip()
                        })
        return events

def get_failed_logins_events():
        raw = fetch_logs()
        return failed_logins(raw)
