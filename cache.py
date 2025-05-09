from data import cache, cache_usage, MAX_CACHE

def enforce_storage_limit(user):
    """Evict oldest files until cache_usage[user] ≤ MAX_CACHE."""
    used = cache_usage[user]
    while used > MAX_CACHE and cache[user]["files"]:
        oldest = cache[user]["files"].pop(0)
        for c in cache[user]["chunks"].pop(oldest, []):
            used -= len(c)
        cache_usage[user] = used
