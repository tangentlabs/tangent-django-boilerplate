import pytest
from selenium import webdriver
from django_webtest import DjangoTestApp, WebTestMixin


@pytest.fixture(scope='function')
def webtest(request):
    """
    Provide the "app" object from WebTest as a fixture

    Taken and adapted from https://gist.github.com/magopian/6673250
    """
    # Patch settings on startup
    wtm = WebTestMixin()
    wtm._patch_settings()

    # Unpatch settings on teardown
    request.addfinalizer(wtm._unpatch_settings)

    return DjangoTestApp()


@pytest.fixture(scope='session')
def firefox(request):
    browser = webdriver.Firefox()
    request.addfinalizer(browser.quit)
    return browser


# You may need to install the Chrome webdriver for this fixture to work. See
# this article for more info:
# http://damien.co/resources/how-to-install-chromedriver-mac-os-x-selenium-python-7406
@pytest.fixture(scope='session')
def chrome(request):
    browser = webdriver.Chrome()
    request.addfinalizer(browser.quit)
    return browser
