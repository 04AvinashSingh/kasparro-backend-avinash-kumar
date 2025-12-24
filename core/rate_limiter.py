import time
from collections import defaultdict

REQUEST_LIMIT = 5        # max requests
WINDOW_SECONDS = 60      # per minute

_requests = defaultdict(list)

def is_rate_limited(client_ip: str) -> bool:
    now = time.time()

    # Remove old timestamps
    _requests[client_ip] = [
        t for t in _requests[client_ip]
        if now - t < WINDOW_SECONDS
    ]

    if len(_requests[client_ip]) >= REQUEST_LIMIT:
        return True

    _requests[client_ip].append(now)
    return False
