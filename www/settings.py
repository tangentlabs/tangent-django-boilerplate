import os

# Import default settings for the project
from conf.default import *

# We use an environmental variable to indicate the, erm, environment
# This block writes all settings to the local namespace
module_path = os.environ.get('DJANGO_CONF', 'conf.local')
try:
    module = __import__(module_path, globals(), locals(), ['*'])
except ImportError:
    import sys
    print "You need to create a file conf/local.py to contain your local settings"
    sys.exit(1)

for k in dir(module):
    if not k.startswith("__"):
        locals()[k] = getattr(module, k)

# Add any additional apps only required locally
if 'EXTRA_APPS' in locals():
    INSTALLED_APPS = INSTALLED_APPS + EXTRA_APPS

# Adjust settings based on the DISABLED_APPS setting
if 'DISABLED_APPS' in locals():
    # Redefine INSTALLED_APPS
    INSTALLED_APPS = [k for k in INSTALLED_APPS if k not in DISABLED_APPS]
    for app_name in DISABLED_APPS:
        # Remove any offending MIDDLEWARE, TEMPLATE_CONTEXT_PROCESSORS or
        # DATABASE_ROUTERS
        MIDDLEWARE_CLASSES = [
            path for path in MIDDLEWARE_CLASSES
            if not path.startswith(app_name)]
        TEMPLATE_CONTEXT_PROCESSORS = [
            path for path in TEMPLATE_CONTEXT_PROCESSORS
            if not path.startswith(app_name)]
        if 'DATABASE_ROUTERS' in locals():
            DATABASE_ROUTERS = [
                path for path in DATABASE_ROUTERS
                if not path.startswith(app_name)]

# Keep version number here - this is generally overwritten as
# part of deployment to be the build name
VERSION = 'UNVERSIONED'
