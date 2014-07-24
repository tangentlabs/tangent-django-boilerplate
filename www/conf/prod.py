from conf.default import *  # noqa

# TODO Configure an RDS database and enter details here
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

# TODO: Insert production hostname here!
ALLOWED_HOSTS = ['']

# TODO: Create a new project on Sentry and enter the DSN here
RAVEN_CONFIG['dsn'] = ''
