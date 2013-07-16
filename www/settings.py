import os

__import__(os.environ.get('DJANGO_CONF', 'conf.local'), globals(), locals(), ['*'])
