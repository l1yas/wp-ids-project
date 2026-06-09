import json
import time
from collections import Counter, deque

from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

log_file="logs.json"

console = Console()

recent_events = deque(maxlen=10)

def load_stats():
    attacks = Counter()
    ips = Counter()
    users = Counter()

    try :
        with open(log_file, "r") as f:
            for line in f :
                try:
                    event = json.loads(line)

                    attack = event.get("attack") or event.get("subtype")
                    ip = event.get("ip")
                    user = event.get("username")

                    if attack:
                        attacks[attack] += 1
                    if ip:
                        ips[ip] += 1
                    if user:
                        users[user] += 1

                    if isinstance(event, dict):
                        recent_events.append(event)

                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return attacks, ips, users

def make_table(title, counter, limit=5):
    table = Table(title=title)
    table.add_column("Key")
    table.add_column("Count")

    for k, v in counter.most_common(limit):
        table.add_row(str(k), str(v))
    return table


def make_recent():
    table = Table(title="Recent Alerts")
    table.add_column("Type")
    table.add_column("IP/User")

    for e in list(recent_events)[-10:]:
        table.add_row(
            str(e.get("subtype", e.get("attack", ""))),
            str(e.get("ip", e.get("username", "")))
        )
    return table


def build_dash():
    attacks, ips, users = load_stats()   
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=10),
    )

    layout["header"].update(
        Panel(
            f"IDS DASHBOARD",
            style="bold white on green"
        )
    )

    body = Layout()

    body.split_row(
        Layout(make_table("Attacks", attacks)),
        Layout(make_table("Top IPs", ips)),
        Layout(make_table("Top Users", users)),
    )

    layout["body"].update(body)

    layout["footer"].update(make_recent())

    return layout


with Live(build_dash(), refresh_per_second=1) as live:
    while True:
        time.sleep(2)
        live.update(build_dash())

