"""
Project-specific environment information.

This module provides configuration for the fabfile to run with.  The idea is
that the fabfile is project-agnostic and all configuration takes place within
this file.

In reality, this won't be entirely true as each project will evolve specific
deployment needs.  Nevertheless, this still provides a good starting point.
"""
from fabric.api import env

# Many things are configured using the client and project code
env.client = '{{ client }}'
env.project_code = '{{ project_code }}'
env.domain = '{{ domain }}'

# This is the name of the folder within the repo which houses all code
# to be deployed.
env.web_dir = 'www'

# Environment-agnostic folders
env.project_dir = '/var/www/%(client)s/%(project_code)s' % env
env.static_dir = '/mnt/static/%(client)s/%(project_code)s' % env
env.builds_dir = '%(project_dir)s/builds' % env

def _configure(build_name):
    env.build = build_name
    env.virtualenv = '%(project_dir)s/virtualenvs/%(build)s/' % env
    env.code_dir = '%(project_dir)s/builds/%(build)s/' % env
    env.data_dir = '%(project_dir)s/data/%(build)s/' % env
    env.apache_conf = 'deploy/apache2/%(build)s.conf' % env
    env.nginx_conf = 'deploy/nginx/%(build)s.conf' % env
    env.supervisord_conf = 'deploy/supervisord/%(build)s.conf' % env
    env.wsgi = 'deploy/wsgi/%(build)s.wsgi' % env

def test():
    _configure('test')
    env.hosts = ['test-%(project_code)s-%(client)s.%(domain)s'] % env

def stage():
    _configure('stage')
    env.hosts = ['stage-%(project_code)s-%(client)s.%(domain)s'] % env

def prod():
    _configure('prod')
    # Production hosts needs filling in
    env.hosts = []
