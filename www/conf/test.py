from conf.default import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '{{ project_code }}_test', # Or path to database file if using sqlite3.
        'USER': '{{ project_code}}_app', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for peer (local non-IP socket). Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    },
}

EMAIL_SUBJECT_PREFIX = '[{{ project_code }}][Test] '

LOGGING = create_logging_dict(location('../../logs/test'))
