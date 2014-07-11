from conf.default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '{{ project_code }}_prod',
        'USER': '{{ project_code}}_prod',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}

EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][Prod] '

# Save logs to the docker containers /host/ mount 
# (bind-mounted to /containers/{container-name}/
# on the host machine
LOG_ROOT = '/host/logs'

# Insert production hostname here!
ALLOWED_HOSTS = ['']

# Create a new project on Sentry to get the DSN value to put here.
RAVEN_CONFIG['dsn'] = ''
