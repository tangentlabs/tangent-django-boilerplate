# -*- coding: utf-8 -*-

# The same settings file is used across all environments, only alternative
# configurations are specified by using environmental variables.
#
# See http://bruno.im/2013/may/18/django-stop-writing-settings-files/
#
# TODO Ensure all instances of {{ project_code }} are replaced.

# Default settings are secure/production-ready.  Debug settings need to be
# enabled locally in conf/local.py

import os
import sys

# Helper function to determine the absolute path of a file
location = lambda *path: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), *path)

# Helper function for accessing env variables
env = lambda key, default: os.environ.get(key, default)

# The "name" of the current environment. Usually one of "dev", "test", "stage"
# or "prod".
ENVIRONMENT = env('ENVIRONMENT', 'local').lower()

DEBUG = bool(env('DEBUG', False))
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Alerts', 'alerts.{{ project_code }}@{{ domain }}'),
)
EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][%s] ' % ENVIRONMENT
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MANAGERS = ADMINS

# The default database is defined by the DATABASE_URL env variable
import dj_database_url
DATABASES = {'default': dj_database_url.config()}

ATOMIC_REQUESTS = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = '{{ language_code }}'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Use timezone support
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = location('public/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
PRIVATE_MEDIA_URL = '/media/private/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = location('public/static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    location('static/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '{{ secret_key }}'

# Use cached template loading by default
if bool(os.environ.get('CACHED_TEMPLATE_LOADER', True)):
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )
else:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    location('templates'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'south',
    'django_extensions',
    'debug_toolbar',
    'compressor',
]

# Use cached sessions by default
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_COOKIE_HTTPONLY = True

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Disabled for local but enabled in real envs
COMPRESS_ENABLED = bool(env('COMPRESS_ENABLED', True))
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_CACHE_KEY_FUNCTION = 'compressor.cache.socket_cachekey'
COMPRESS_OFFLINE = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


def create_logging_dict(root):
    """
    Create a logging dict using the passed root for log files

    Note the file handlers don't rotate their files.  This should be handled by
    logrotate (there is a sample conf file in www/deploy/logrotate.d).
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            }
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'django.utils.log.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'filters': ['require_debug_true'],
                'stream': sys.stdout,
            },
            'error_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(root, 'errors.log'),
                'filters': ['require_debug_false'],
                'formatter': 'verbose'
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
            # Log errors to console only when DEBUG=True but to both file and
            # admins when DEBUG=False
            'django.request': {
                'handlers': ['console', 'error_file', 'mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            # Enable this logger to see SQL queries
            'django.db.backends': {
                'handlers': ['null'],
                'level': 'INFO',
                'propagate': False,
            },
        }
    }

# Aside from local development, we run within a Docker container which has a
# volume mounted at /host/. We default to logging within there.
LOGGING = create_logging_dict(env('LOG_ROOT', '/host/logs'))

# Debug toolbar settings
DEBUG_TOOLBAR_PATCH_SETTINGS = False
INTERNAL_IPS = ('127.0.0.1',)

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split()

# Raven settings (for Sentry)
RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', ''),
    'timeout': 5,
}
