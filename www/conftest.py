import pytest

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
