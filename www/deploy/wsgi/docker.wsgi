import os
import sys
import site

sys.stdout = sys.stderr

# Project root
root = '/var/www/tangent/bp/builds/prod/'
sys.path.insert(0, root)

# Set environmental variable for Django and fire WSGI handler 
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['DJANGO_CONF'] = 'conf.docker'
import django.core.handlers.wsgi
_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    # Check for custom header from load balancer, and use it
    # to manually set the url_scheme variable
    environ['wsgi.url_scheme'] = environ.get('HTTP_X_FORWARDED_PROTO', 'http')
    if environ['wsgi.url_scheme'] == 'https':
        environ['HTTPS'] = 'on'
    return _application(environ, start_response)
