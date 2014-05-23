def test_with_django_client(client):
    r = client.get('/')
    assert 'Hello' in r.content


def test_with_webtest(webtest):
    r = webtest.get('/')
    assert 'Hello' in r.content
