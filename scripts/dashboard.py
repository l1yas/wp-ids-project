import json
import time
from collections import Counter

from rich.console import Console
from rich.table import Table
from rich.live import Live

log_file="logs.json"

console = Console()

def load_stats():
    attacks = Counter()
    ips = Counter()
    users = Counter()

    try : 
        with open(log_file, "r") as f:
            for line in f :
                try:
                    event = json.loads(line)
                    if "attack" in event:
                        attacks[event["attack"]] += 1
                    if "ip" in event:
                        ips[event["ip"]] += 1
                    if "username" in event:
                        users[event["username"]] += 1
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return attacks, ips, users

def build_dash():
    attacks, ips, users = load_stats()   
    table = Table(title="IDS Dashboard")

    table.add_column("Category")
    table.add_column("Value")
    table.add_column("Count")

    for attack, count in attacks.most_common():
        table.add_row("Attack", attack, str(count))
    
    for ip, count in ips.most_common(5):
        table.add_row("IP", ip, str(count))

    for user, count in users.most_common(5):
        table.add_row("User", user, str(count))
    return table

with Live(build_dash(), refresh_per_second=1) as live:
    while True:
        live.update(build_dash())
        time.sleep(2)
