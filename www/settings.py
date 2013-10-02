import os

# Use an env variable to determine which settings file to import.  Then copy
# all variables into the local namespace.
__import__(os.environ.get('DJANGO_CONF', 'conf.local'), globals(), locals(), ['*'])
module = __import__(os.environ.get('DJANGO_CONF', 'conf.local'), globals(), locals(), ['*'])
for k in dir(module):
    if not k.startswith("__"):
        locals()[k] = getattr(module, k)
