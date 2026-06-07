import subprocess
import re

failed_login_pattern = re.compile(r'username "([^"]+)"')

def fetch_logs():
        result = subprocess.run(
                ["docker", "exec", "wordpress-wordpress-1", "wp", "simple-history", "list", "--allow-root"],
                capture_output=True,
                text=True
        )
        return result.stdout

def parse_line(line):
        parts = line.split("\t")
        if len(parts)<4:
                return None
        return {
                "id": parts[0],
                "date": parts[1],
                "initiator": parts[2],
                "description": parts[3],
                "level": parts[-2] if len(parts)>2 else None,
                "raw": line
        }

def failed_logins(raw):
        events=[]
        for line in raw.split("\n"):
                if "Failed to login" not in line:
                        continue

                parsed = parse_line(line)
                if not parsed:
                        continue

                match = failed_login_pattern.search(parsed["description"])
                username = match.group(1) if match else None

                events.append({
                        "source": "wordpress",
                        "type": "failed_login",
                        "username": username,
                        "date" : parsed["date"],
                        "level": parsed["level"],
                        "raw": line
                })
        return events

def get_failed_logins_events():
        raw = fetch_logs()
        return failed_logins(raw)


def debug():
        raw = fetch_logs()
        print("=== RAW LOGS ===")
        print(raw)
        events = failed_logins(raw)
        print("\n=== EVENTS ===")
        print(events)

