def test_retry_logic():
    # actually relying on our download endpoint’s retry logic
    # we trigger /download multiple times until all chunks are retrieved
    from data import chunks, cache
    cnt=0
    while len(cache["alice"]["chunks"].get("file1", [])) < len(chunks["file1"]):
        try:
            _ = client.get('/download/file1', stream=True).data
        except:
            pass
        cnt += 1
        if cnt > 10: break
    assert len(cache["alice"]["chunks"]["file1"]) == len(chunks["file1"])
