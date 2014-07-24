from conf.default import *  # noqa

# TODO Configure a database and enter details here
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

# TODO: Create a new project on Sentry and enter the DSN here
RAVEN_CONFIG['dsn'] = ''
