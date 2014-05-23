def test_with_django_client(client):
    r = client.get('/')
    assert 'Hello' in r.content


def test_with_webtest(webtest):
    r = webtest.get('/')
    assert 'Hello' in r.content


def test_with_firefox(live_server, firefox):
    firefox.get(live_server.url + '/')
    assert 'Hello' in firefox.page_source
