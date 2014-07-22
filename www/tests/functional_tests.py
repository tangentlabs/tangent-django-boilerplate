def test_with_django_client(client):
    r = client.get('/')
    assert 'Hello' in r.content


def test_with_webtest(webtest):
    r = webtest.get('/')
    assert 'Hello' in r.content


def test_with_firefox(live_server, firefox):
    firefox.get(live_server.url + '/')
    assert 'Hello' in firefox.page_source


def test_with_splinter(live_server, browser):
    browser.visit(live_server.url + '/')
    assert browser.is_text_present("Hello")
