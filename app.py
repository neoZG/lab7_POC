from flask import Flask, request, jsonify, Response
import uuid, random

from data import users, content_db, chunks, cache, cache_usage, queue
from cache import enforce_storage_limit

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    user = request.json['user']
    pwd  = request.json['password']
    if users.get(user, {}).get("password") == pwd:
        token = str(uuid.uuid4())
        users[user]["token"] = token
        cache[user]["auth"] = token
        return jsonify({"token": token})
    return jsonify({"error": "Invalid"}), 401

@app.route('/content', methods=['GET'])
def list_content():
    return jsonify(content_db)

@app.route('/download/<file_id>', methods=['GET'])
def download(file_id):
    def generate():
        for idx, chunk in enumerate(chunks[file_id]):
            # simulate compression
            c = chunk[:len(chunk)//2]
            # simulate unreliable network
            if random.random() < 0.2:
                raise ConnectionError("Simulated drop")
            # cache it
            cache[file_id] = cache.setdefault(file_id, {})
            cache["alice"]["chunks"].setdefault(file_id, []).append(c)
            cache["alice"]["files"].append(file_id) if file_id not in cache["alice"]["files"] else None
            cache_usage["alice"] += len(c)
            enforce_storage_limit("alice")
            yield c
    return Response(generate(), mimetype='application/octet-stream')

@app.route('/sync-chunk', methods=['POST'])
def sync_chunk():
    data = request.get_json()
    queue.append((data['file_id'], data['index'], data['data']))
    return jsonify({"status": "queued"})

@app.route('/auth/sync', methods=['POST'])
def auth_sync():
    # stub: e.g. clear or update tokens
    return jsonify({"status": "auth synced"})

if __name__ == '__main__':
    app.run()
