import os
import sys

sys.stdout = sys.stderr

# Project root
root = '/var/www/'
sys.path.insert(0, root)

# Read environmental variables from a local file (.env)
# See https://github.com/jacobian/django-dotenv
import dotenv
envfile = os.path.join(os.path.dirname(__file__), '../.env')
dotenv.read_dotenv(envfile)

# Set environmental variable for Django and fire WSGI handler 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    return _application(environ, start_response)
