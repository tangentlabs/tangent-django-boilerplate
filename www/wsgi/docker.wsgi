import os
import sys

sys.stdout = sys.stderr

# Project root
root = '/var/www/'
sys.path.insert(0, root)

# Set environmental variable for Django and fire WSGI handler 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['DJANGO_CONF'] = 'conf.docker'
import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    return _application(environ, start_response)
