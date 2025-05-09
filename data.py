import uuid

# 1) Users
users = {
    "alice": {"password": "secret", "token": None}
}

# 2) Content DB
content_db = {
    "file1": {"size": 5000, "chunks": 5},
    "file2": {"size": 8000, "chunks": 8}
}

# 3) Chunks Store
chunks = {
    "file1": [b"A"*1000 for _ in range(5)],
    "file2": [b"B"*1000 for _ in range(8)]
}

# 4) Local Cache per user
cache = {
    "alice": {"auth": None, "files": [], "chunks": {}}
}
cache_usage = {"alice": 0}

# 5) Message Queue
queue = []

# Config
MAX_CACHE = 10 * 1024**3  # 10 GB
