from conf.default import *  # noqa

# The production database will be on RDS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{ project_code }}_prod',
        'USER': '{{ project_code}}_app',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][Prod] '

# Insert production hostname here!
ALLOWED_HOSTS = ['']

# Create a new project on Sentry to get the DSN value to put here.
RAVEN_CONFIG['dsn'] = ''
