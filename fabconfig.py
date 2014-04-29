"""
Project-specific environment information.

This module provides configuration for the fabfile to run with.  The idea is
that the fabfile is project-agnostic and all configuration takes place within
this file.  In reality, this won't be entirely true as each project will evolve
specific deployment needs.  Nevertheless, this still provides a good starting
point.
"""
import datetime

from fabric.api import env

# Many things are configured using the client name and project code
env.client = '{{ client }}'
env.project_code = '{{ project_code }}'

# This is the name of the folder within the repo which houses all code
# to be deployed.
env.web_folder = 'www'


def _configure(build_name):
    env.build_name = build_name
    env.project_root = '/var/www/%(client)s/%(project_code)s' % env
    env.virtualenv_root = '%(project_root)s/virtualenvs/%(build)s/' % env
    env.builds_root = '%(project_root)s/builds' % env

    # Default to requiring a tag to build from
    env.require_tag = True

    # Determine filepath to final
    # Set timestamp now so it is the same on all servers after deployment
    now = datetime.datetime.now()
    env.build_folder = '%s-%s' % (build_name, now.strftime('%Y-%m-%d-%H-%M'))
    env.build_root = '%s/%s' % (env.builds_root, env.build_folder)
    env.media_root = '%(project_root)s/media/%(build_name)s' % env

    env.nginx_conf_filepath = '%(build_root)s/deploy/nginx/%(build_name)s.conf' % env
    env.supervisord_conf_filepath = '%(build_root)s/deploy/supervisord/%(build_name)s.conf' % env
    env.wsgi_filepath = '%(build_root)s/deploy/wsgi/%(build_name)s.wsgi' % env

    env.hosts = ['%(client)s-%(project_code)s-%(build_name)s.tangentlabs.co.uk' % env]


def test():
    _configure('test')
    env.require_tag = False


def stage():
    _configure('stage')


def prod():
    _configure('prod')
