from conf.default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': ':memory:',
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DEBUG_PROPAGATE_EXCEPTIONS = True

# Use syncdb rather than applying migrations
SOUTH_TESTS_MIGRATE = False

# Disable logging
import logging
logging.disable(logging.CRITICAL)
