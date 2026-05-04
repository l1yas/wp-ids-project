from collections import defaultdict
import time

request_by_ip = defaultdict(list)

window = 10
treshold= 10

def detect_bruteforce(ip, url):
        now = time.time()

        request_by_ip[ip].append(now)
        recent_requests = []
        for t in request_by_ip[ip]:
            if now - t < window:
                recent_requests.append(t)
        request_by_ip[ip]= recent_requests

        if len(recent_requests)>treshold:
            return True
        return False
