from data import cache, users

def test_offline_login(client):
    # 1) online login
    res = client.post('/login', json={"user":"alice","password":"secret"})
    token = res.get_json()['token']
    # 2) go offline: rely on cache alone
    assert cache["alice"]["auth"] == token
    assert users["alice"]["token"] == token
