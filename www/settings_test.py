# Read environmental variables from a local file (.env)
# See https://github.com/jacobian/django-dotenv
import dotenv
dotenv.read_dotenv()

from settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

DEBUG_PROPAGATE_EXCEPTIONS = True

# Use syncdb rather than applying migrations
SOUTH_TESTS_MIGRATE = False

# Disable logging
import logging
logging.disable(logging.CRITICAL)
