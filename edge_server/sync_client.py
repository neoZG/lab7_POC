import time
import base64
import requests

# Define the base URLs for central and edge servers (assuming local host simulation)
CENTRAL_BASE = "http://localhost:5000"
EDGE_BASE    = "http://localhost:5001"

def sync_from_central():
    """
    Simulate the edge's cron job: synchronize users and content from central server.
    """
    # 1. Sync User Credentials
    try:
        resp = requests.post(f"{CENTRAL_BASE}/auth/sync")
    except requests.RequestException as e:
        print(f"[Sync] Failed to reach central /auth/sync: {e}")
        return
    if resp.status_code == 200:
        central_users = resp.json().get("users", [])
        # Update edge's user_db
        # (Directly importing edge_server.app to modify the in-memory DB in this simulation)
        try:
            from edge_server import app as edge_app
        except ImportError:
            edge_app = None
        if edge_app:
            for user in central_users:
                username = user["username"]
                password = user["password"]
                edge_app.user_db[username] = password
            print(f"[Sync] Updated edge user DB with {len(central_users)} users.")
        else:
            # In a real scenario, write to a shared database or file that edge server reads.
            print("[Sync] Warning: Edge app module not found. Cannot update users in memory.")
    else:
        print(f"[Sync] auth/sync failed with status {resp.status_code}")

    # 2. Sync Content
    try:
        resp2 = requests.get(f"{CENTRAL_BASE}/content")
    except requests.RequestException as e:
        print(f"[Sync] Failed to reach central /content: {e}")
        return
    if resp2.status_code == 200:
        central_content_list = resp2.json()
        # Determine which content IDs are new to the edge
        try:
            from edge_server import app as edge_app
        except ImportError:
            edge_app = None
        if edge_app:
            existing_ids = set(edge_app.content_db.keys())
        else:
            existing_ids = set()
        new_ids = [item["id"] for item in central_content_list if item["id"] not in existing_ids]
        for cid in new_ids:
            print(f"[Sync] Fetching new content ID {cid} in chunks...")
            chunk_index = 0
            content_bytes = b""
            # Fetch chunks until 'more' is False
            while True:
                try:
                    resp_chunk = requests.post(f"{CENTRAL_BASE}/sync-chunk",
                                               json={"content_id": cid, "chunk_index": chunk_index})
                except requests.RequestException as e:
                    print(f"[Sync] Failed to fetch chunk {chunk_index} for content {cid}: {e}")
                    break
                if resp_chunk.status_code != 200:
                    print(f"[Sync] /sync-chunk returned status {resp_chunk.status_code} (chunk {chunk_index}, content {cid})")
                    break
                data = resp_chunk.json()
                # Decode the chunk data
                chunk_b64 = data.get("data", "")
                if chunk_b64:
                    chunk = base64.b64decode(chunk_b64)
                else:
                    chunk = b""
                content_bytes += chunk
                more = data.get("more", False)
                if not more:
                    # Last chunk received
                    break
                chunk_index += 1
            if content_bytes:
                # Store the new content in edge content DB
                if edge_app:
                    title = next((item["title"] for item in central_content_list if item["id"] == cid), f"Content {cid}")
                    edge_app.content_db[cid] = {"title": title, "data": content_bytes}
                    print(f"[Sync] Content {cid} synced to edge (size={len(content_bytes)} bytes).")
                else:
                    # In a real setup, save to file or database
                    print(f"[Sync] Retrieved content {cid} (size {len(content_bytes)} bytes).")
            else:
                print(f"[Sync] No data received for content {cid}.")
    else:
        print(f"[Sync] content list fetch failed with status {resp2.status_code}")

if __name__ == "__main__":
    # If run directly, perform a sync (this would be triggered by cron in production)
    start_time = time.time()
    print("[Sync] Starting sync job...")
    sync_from_central()
    elapsed = time.time() - start_time
    print(f"[Sync] Sync job completed in {elapsed:.2f} seconds.")
