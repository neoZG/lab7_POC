import threading, time, requests
from werkzeug.serving import make_server
import pytest

# Import the Flask apps
from central_server.app import app as central_app
from edge_server.app import app as edge_app

# Global server objects
central_server = None
edge_server = None
central_thread = None
edge_thread = None

def setup_module(module):
    """Setup test servers (runs once for all tests)."""
    global central_server, edge_server, central_thread, edge_thread
    # Start central and edge Flask apps on separate threads
    central_server = make_server('127.0.0.1', 5000, central_app)
    edge_server = make_server('127.0.0.1', 5001, edge_app)
    central_thread = threading.Thread(target=central_server.serve_forever)
    edge_thread = threading.Thread(target=edge_server.serve_forever)
    central_thread.daemon = True
    edge_thread.daemon = True
    central_thread.start()
    edge_thread.start()
    # Give servers a moment to start
    time.sleep(0.5)

def teardown_module(module):
    """Teardown servers after tests."""
    global central_server, edge_server, central_thread, edge_thread
    if central_server:
        central_server.shutdown()
    if edge_server:
        edge_server.shutdown()
    if central_thread:
        central_thread.join(timeout=1)
    if edge_thread:
        edge_thread.join(timeout=1)

def test_availability():
    """
    Availability fitness test:
    Simulate 100 user requests (mix of content fetch and login).
    Check that ≥90% succeed.
    """
    total_requests = 100
    success_count = 0
    for i in range(total_requests):
        try:
            if i % 2 == 0:
                # Every other request: fetch content list
                resp = requests.get("http://localhost:5001/content")
            else:
                # Alternate requests: attempt login
                resp = requests.post("http://localhost:5001/login",
                                     json={"username": "user1", "password": "pass1"})
        except requests.RequestException as e:
            # If a request fails to connect or similar, count as failure
            print(f"Request {i} failed: {e}")
            continue
        # Count HTTP 200 responses as success
        if resp.status_code == 200:
            success_count += 1
    availability = (success_count / total_requests) * 100
    print(f"Availability: {availability:.2f}% success rate")
    assert success_count >= 90, "Availability below 90%"

def test_performance():
    """
    Performance fitness test:
    Simulate 10 concurrent users fetching content.
    Measure average Queries Per Second (QPS).
    """
    concurrent_users = 10
    requests_per_user = 10
    total_requests = concurrent_users * requests_per_user

    def user_session(requests_to_make, success_counter):
        count = 0
        for _ in range(requests_to_make):
            try:
                r = requests.get("http://localhost:5001/content")
            except requests.RequestException:
                continue
            if r.status_code == 200:
                count += 1
        success_counter.append(count)

    threads = []
    success_counts = []
    start_time = time.time()
    # Launch 10 threads simulating concurrent user activity
    for _ in range(concurrent_users):
        t = threading.Thread(target=user_session, args=(requests_per_user, success_counts))
        threads.append(t)
        t.start()
    # Wait for all threads to finish
    for t in threads:
        t.join()
    duration = time.time() - start_time
    total_success = sum(success_counts)
    qps = total_success / duration
    print(f"Performed {total_success} requests in {duration:.2f}s, approx {qps:.2f} QPS")
    # We expect some reasonable QPS on local; ensure > 5 for this POC
    assert qps > 5, "Average QPS is too low"

def test_content_update_time():
    """
    Content Update Time fitness test:
    Measure time from initiating sync to content availability at edge.
    Also verify that new content and user data appear on edge after sync.
    """
    # Before sync: content ID 3 and user2 should not be available on edge
    resp1 = requests.get("http://localhost:5001/content")
    edge_content = {item["id"] for item in resp1.json()}
    assert 3 not in edge_content, "Content ID 3 should not be present before sync"
    # Also check user2 login fails before sync
    resp_login = requests.post("http://localhost:5001/login",
                               json={"username": "user2", "password": "pass2"})
    assert resp_login.status_code == 401, "User2 should not authenticate before sync"

    # Initiate sync and measure time
    import edge_server.sync_client as sync_client
    start = time.time()
    sync_client.sync_from_central()
    elapsed = time.time() - start

    # After sync: content ID 3 should be available on edge
    resp2 = requests.get("http://localhost:5001/content")
    edge_content_after = {item["id"] for item in resp2.json()}
    # Check that content 3 is now present
    assert 3 in edge_content_after, "Content ID 3 was not synced to edge"
    # Check that user2 can now log in on edge
    resp_login2 = requests.post("http://localhost:5001/login",
                                json={"username": "user2", "password": "pass2"})
    assert resp_login2.status_code == 200, "User2 was not synced to edge"

    print(f"Content sync completed in {elapsed:.2f} seconds")
    # (We do not set a strict threshold for time, but it should be reasonably low for the POC.)
