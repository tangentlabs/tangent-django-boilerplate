from conf.default import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ project_code }}_test',
        'USER': '{{ project_code}}_app',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][Test] '

ALLOWED_HOSTS = ['{{ client }}-{{ project_code }}-test.tangentlabs.co.uk']

# Create a new project on Sentry to get the DSN value to put here.
RAVEN_CONFIG['dsn'] = ''
