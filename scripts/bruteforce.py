from collections import defaultdict, deque
import time

failed_by_ip =defaultdict(deque)
failed_by_user = defaultdict(deque)

window = 60
treshold_ip= 7
treshold_user=7

def failed_logins(ip, username):
    now = time.time()
    failed_by_ip[ip].append(now)
    while failed_by_ip[ip] and now - failed_by_ip[ip][0] > window:
        failed_by_ip[ip].popleft()
    failed_by_user[username].append(now)

    while failed_by_user[username].append(now) and now - failed_by_user[username][0] > window:
        failed_by_user[username].popleft()

def detect_bruteforce(ip, username):
    ip_hits = len(failed_by_ip[ip])
    user_hits = len(failed_by_user[username])

    if ip_hits >= treshold_ip:
        return {
            "type": "bruteforce_ip",
            "ip": ip,
            "score": ip_hits
        }
    if user_hits >= treshold_user:
        return {
            "type": "password_spraying",
            "username": username,
            "score": user_hits
        }
    return None          
