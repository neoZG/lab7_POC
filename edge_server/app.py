from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# Dummy User Database (edge cache) – initially contains only a subset of users
user_db = {
    "user1": "pass1"   # user2 is missing initially; will be added via sync
}

# Dummy Content Database (edge cache) – initially only some content
content_db = {
    1: {"title": "Video1.mp4", "data": b"x" * (10 * 1024)},  # same 10 KB content as central
    2: {"title": "Video2.mp4", "data": b"x" * (5 * 1024)}    # same 5 KB content as central
}
# Note: content 3 is not present initially on edge. It will be pulled from central on sync.

@app.route('/login', methods=['POST'])
def login():
    """Authenticate user against edge's local user DB."""
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
    """List content available on the edge (that has been synced)."""
    content_list = []
    for cid, info in content_db.items():
        content_list.append({
            "id": cid,
            "title": info["title"],
            "size": len(info["data"])
        })
    return jsonify(content_list)

@app.route('/download/<int:content_id>', methods=['GET'])
def download_content(content_id):
    """Download a content file from the edge."""
    if content_id in content_db:
        data = content_db[content_id]["data"]
        return Response(data, mimetype='application/octet-stream')
    else:
        return jsonify({"message": "Content not found"}), 404

if __name__ == '__main__':
    # Run edge server on port 5001
    app.run(host='0.0.0.0', port=5001, debug=False)
