# This is required purely so the www folder is added to the python path for
# py.test. It's a bit of a kludge as we don't really need to update the version
# here.

from distutils.core import setup

# Change the name to be something more meaningful
setup(name='project', version='0')
