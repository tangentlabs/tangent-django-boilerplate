def test_with_django_client(client):
    r = client.get('/')
    assert 'Hello' in r.content
