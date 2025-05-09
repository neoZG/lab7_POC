def test_chunked_download(client):
    # download file1
    resp = client.get('/download/file1', stream=True)
    data = b"".join(resp.iter_bytes())
    # expect sum of compressed chunks length
    from data import chunks
    expected = sum(len(c)//2 for c in chunks["file1"])
    assert len(data) == expected
