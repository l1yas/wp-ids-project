import json
from collections import Counter

log_file="logs.json"

attacks = Counter()
ips = Counter()
users = Counter()

with open(log_file, "r") as f:
    for line in f:
        try:
            event = json.loads(line)
            if "attack" in event:
                attacks[event["attack"]] += 1
            if "ip" in event:
                ips[event["ip"]] += 1

            if "username" in event:
                users[event["username"]] += 1
        except Exception:
            continue

print("=" * 50)
print("IDS DASHBOARD")
print("=" * 50)

print("\nAttack types:")
for attack, count in attacks.most_common():
    print(f"  {attack:<15} {count}")

print("\nTop IPs:")
for ip, count in ips.most_common(5):
    print(f"  {ip:<20} {count}")

print("\nTop usernames:")
for user, count in users.most_common(5):
    print(f"  {user:<20} {count}")

print("\nTotal events:", sum(attacks.values()))