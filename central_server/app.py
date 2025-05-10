from flask import Flask, request, jsonify, Response
import base64

app = Flask(__name__)

# Dummy User Database (central authority)
# In practice, passwords would be hashed; here plaintext for simplicity.
user_db = {
    "user1": "pass1",
    "user2": "pass2"
}

# Dummy Content Database (central repository)
# Each content has an ID, title, and binary data. Using small byte strings as dummy content.
def generate_content_bytes(size_kb):
    """Generate dummy content bytes of given size (KB)."""
    return b"x" * (size_kb * 1024)  # 'x' repeated to desired size

content_db = {
    1: {"title": "Video1.mp4", "data": generate_content_bytes(10)},  # 10 KB content
    2: {"title": "Video2.mp4", "data": generate_content_bytes(5)},   # 5 KB content
    3: {"title": "Video3.mp4", "data": generate_content_bytes(20)}   # 20 KB content (new content not on edge yet)
}

CHUNK_SIZE = 1024  # bytes per chunk for sync

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user against central user DB (if needed)."""
    creds = request.get_json()
    if not creds or 'username' not in creds or 'password' not in creds:
        return jsonify({"message": "Missing credentials"}), 400
    username = creds['username']
    password = creds['password']
    if username in user_db and user_db[username] == password:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/content', methods=['GET'])
def list_content():
    """List all content available on the central server."""
    content_list = []
    for cid, info in content_db.items():
        content_list.append({
            "id": cid,
            "title": info["title"],
            "size": len(info["data"])
        })
    # Return as JSON array
    return jsonify(content_list)

@app.route('/download/<int:content_id>', methods=['GET'])
def download_content(content_id):
    """Download a full content file by ID from central."""
    if content_id in content_db:
        data = content_db[content_id]["data"]
        # Return raw bytes with binary content type
        return Response(data, mimetype='application/octet-stream')
    else:
        return jsonify({"message": "Content not found"}), 404

@app.route('/sync-chunk', methods=['POST'])
def sync_chunk():
    """
    Provide a chunk of a content file for edge synchronization.
    Expects JSON: {"content_id": <id>, "chunk_index": <n>}.
    Responds with base64-encoded chunk and whether more chunks remain.
    """
    req = request.get_json()
    if not req or "content_id" not in req or "chunk_index" not in req:
        return jsonify({"message": "Invalid request"}), 400
    cid = req["content_id"]
    chunk_idx = req["chunk_index"]
    if cid not in content_db:
        return jsonify({"message": "Content not found"}), 404

    data = content_db[cid]["data"]
    start = chunk_idx * CHUNK_SIZE
    if start >= len(data):
        # No more data to send
        return jsonify({"content_id": cid, "chunk_index": chunk_idx, "data": "", "more": False})
    end = start + CHUNK_SIZE
    chunk_bytes = data[start:end]
    # Encode chunk in base64 so it can be sent as text in JSON
    encoded_chunk = base64.b64encode(chunk_bytes).decode('utf-8')
    more = True if end < len(data) else False
    response = {
        "content_id": cid,
        "chunk_index": chunk_idx,
        "data": encoded_chunk,
        "more": more
    }
    return jsonify(response)

@app.route('/auth/sync', methods=['POST'])
def auth_sync():
    """
    Provide user credential data for synchronization.
    In a real scenario, could accept a last sync timestamp to send only diffs.
    Here, we simply return the full user list.
    """
    users_list = []
    for username, pwd in user_db.items():
        users_list.append({"username": username, "password": pwd})
    return jsonify({"users": users_list})

if __name__ == '__main__':
    # Run central server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
