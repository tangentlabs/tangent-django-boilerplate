from conf.default import *  # noqa

# All debugging activated
DEBUG = TEMPLATE_DEBUG = True

# Output emails to STDOUT
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': location('db.sqlite3'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

# Use a folder outside of www for logs
LOGGING = create_logging_dict(location('../logs'))

# Don't use cached templates in development
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# Use in-process cache by default
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Don't compress assets
COMPRESS_ENABLED = False
