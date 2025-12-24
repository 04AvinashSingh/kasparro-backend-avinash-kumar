import time

_cache = {}
_cache_expiry = {}

def get_cache(key):
    if key in _cache and time.time() < _cache_expiry[key]:
        return _cache[key]
    return None

def set_cache(key, value, ttl_seconds=30):
    _cache[key] = value
    _cache_expiry[key] = time.time() + ttl_seconds
