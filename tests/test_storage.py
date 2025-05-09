def test_storage_eviction():
    from data import cache, cache_usage, MAX_CACHE
    # artificially fill cache beyond limit
    cache_usage["alice"] = MAX_CACHE + 1
    cache["alice"]["files"] = ["file1","file2"]
    cache["alice"]["chunks"]["file1"] = [b"x"* (MAX_CACHE//2)]
    cache["alice"]["chunks"]["file2"] = [b"x"* (MAX_CACHE//2)]
    # enforce eviction
    from cache import enforce_storage_limit
    enforce_storage_limit("alice")
    assert cache_usage["alice"] <= MAX_CACHE
