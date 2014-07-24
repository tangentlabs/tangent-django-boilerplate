from conf.default import *  # noqa

# The stage database will be on RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ project_code }}_stage',
        'USER': '{{ project_code}}_app',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][Stage] '

ALLOWED_HOSTS = ['{{ client }}-{{ project_code }}-stage.tangentlabs.co.uk']

# Create a new project on Sentry to get the DSN value to put here.
RAVEN_CONFIG['dsn'] = ''
