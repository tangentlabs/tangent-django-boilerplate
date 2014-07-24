from conf.default import *  # noqa

# TODO Configure an RDS database and enter details here
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

# TODO: Create a new project on Sentry and enter the DSN here
RAVEN_CONFIG['dsn'] = ''
