import os

from fabric.operations import put, prompt
from fabric.colors import green, red
from fabric.api import local, cd, sudo, abort
from fabric.contrib.files import exists
from fabric.contrib.console import confirm

from fabconfig import env
from fabconfig import test, stage, prod  # noqa


# Misc utils


def _get_commit_id():
    """
    Return the commit ID for the branch about to be deployed
    """
    return local('git rev-parse HEAD', capture=True)[:20]


def _get_current_branch_name():
    """
    Return name of current git branch
    """
    return local('git branch | grep "^*" | cut -d" " -f2', capture=True)


def notify(msg):
    bar = '+' + '-' * (len(msg) + 2) + '+'
    print green('')
    print green(bar)
    print green("| %s |" % msg)
    print green(bar)
    print green('')


# Targets


def init():
    """
    Create initial project/build folder structure on remote machine
    """
    notify('Setting up remote project structure for %(build_name)s build' % env)
    sudo('mkdir -p %(project_root)s' % env)
    with cd(env.project_root):
        sudo('mkdir -p builds')
        sudo('mkdir -p data/%(build_name)s' % env)
        sudo('mkdir -p logs/%(build_name)s' % env)
        sudo('mkdir -p media/%(build_name)s' % env)
        sudo('mkdir -p run/%(build_name)s' % env)

        # Change directory permissions so uwsgi and nginx don't trip over
        sudo('chown -R root.www-data logs/ media/ run/')
        sudo('chmod -R g+w logs/ media/ run/')

        # Check for virtualenv
        if not exists(env.virtualenv_root):
            sudo('mkdir -p %s' % env.virtualenv_root)
            with cd('%(project_root)s/virtualenvs/' % env):
                sudo('`which virtualenv` --no-site-packages %(build_name)s/' % env)
                sudo('echo "export DJANGO_CONF=\"conf.%(build_name)s\"" >> %(build_name)s/bin/activate' % env)

    with cd('%(project_root)s/builds/' % env):
        if not exists(env.build_name):
            # Create directory and symlink for "zero" build
            sudo('mkdir %(build_name)s-0' % env)
            sudo('ln -s %(build_name)s-0 %(build_name)s' % env)

    notify('Remote project structure created')


def prepare(remote='origin'):
    """
    Create a tarball of sourcecode ready to be uploaded
    """
    # Ensure codebase is in-sync with remote and select commit/tag to build
    # from.
    branch = _get_current_branch_name()
    _verify_codebase_status(branch, remote)
    env.pointer = _determine_pointer(branch)

    # Create a tarball ready to be pushed to the servers
    notify("Deploying codebase from pointer %(pointer)s to %(build_name)s" % env)
    env.tarball_filepath = '/tmp/build-%s.tar.gz' % env.pointer
    local('git archive --format tar %s %s | gzip > %s' % (
        env.pointer, env.web_folder, env.tarball_filepath))


def deploy():
    """
    Deploys the codebase
    """
    # Upload tarball and unpack into place
    _deploy_codebase(env.tarball_filepath)

    # Run processing scripts
    _update_virtualenv()
    _migrate_db_schema()
    _collect_static_files()
    _deploy_cronjobs()
    _deploy_nginx_config()
    _deploy_supervisord_config()

    # Make new codebase live
    _switch_symlink()
    _reload_python_code()
    _reload_nginx()
    _reload_supervisord()

    # Clean-up
    _delete_old_builds()
    _push_tags()
    _delete_tarball()

# Helpers

def _verify_codebase_status(branch, remote):
    """
    Look for differences between local checkout of the codebase and that on the
    remote.

    - If there commits locally that aren't pushed, then ensure these are
    pushed. This avoids a situation where the exact commit that was deployed
    from gets rewritten as part of a rebase.

    - If there are unmerged remote commits, then prompt to ensure it's ok to
    deploy. It's annoying if your build accidentally didn't include some remote
    that commits that it should have.
    """
    notify('Fetching commits from remote "%s"' % remote)
    local('git fetch %s' % remote)

    remote_branch = "%s/%s" % (remote, branch)
    notify('Looking for unmerged commits on this branch and its remote equivalent')
    num_remote_commits = int(local(
        'git rev-list HEAD..%s | wc -l' % remote_branch, capture=True))
    num_local_commits = int(local(
        'git rev-list %s..HEAD | wc -l' % remote_branch, capture=True))
    if num_remote_commits > 0:
        msg = (
            "Warning: There are %s commits on %s/%s that aren't merged into "
            "this branch. Do you still still want to deploy?") % (
                num_remote_commits, remote, branch)
        if not confirm(red(msg), default=False):
            abort("Deployment aborted!")

    # If there any un-pushed local commits, push them
    if num_local_commits:
        msg = (
            "Warning: There are %s local unpushed commits. Push them now?") % (
                num_local_commits,)
        if confirm(red(msg)):
            local('git push %s %s' % (remote, branch))


def _determine_pointer(branch):
    """
    Determine the pointer (tag or commit ID) to build from
    """
    notify("Determine the git pointer to deploy from")

    if not env.require_tag:
        return _prompt_for_pointer(branch)
    return _prompt_for_tag()


def _prompt_for_pointer(branch):
    """
    Return the pointer when building to test
    """
    if confirm(red('Tag this release?'), default=False):
        pointer = _create_tag()
    else:
        deploy_version = confirm(
            red('Build from a specific commit (useful for debugging)?'),
            default=False)
        print ''
        if deploy_version:
            pointer = prompt(red('Enter commit ID to build from: '))
        else:
            pointer = local('git describe --tags %s' % branch, capture=True).strip()
    return pointer


def _create_tag():
    # Create a tag
    notify("Showing latest tags for reference")
    local('git tag | sort -V | tail -5')
    tag = prompt(red('Tag name [in format x.x.x]? '))
    notify("Tagging version %s" % tag)
    # Adding a message to the tab allows "git describe" to pick up the tag.
    local('git tag %s -m "Tagging version %s in fabfile"' % (
        tag, tag))
    # Ensure any created tags are pushed to the remote.
    local('git push --tags')
    return pointer


def _prompt_for_tag():
    """
    Return a tag specified by the user
    """
    local('git fetch --tags')
    local('git tag | sort -V | tail -5')
    tag = prompt(red('Choose tag to build from: '))

    # Check this tag exists
    notify("Checking chosen tag exists")
    local('git tag | grep "%s"' % tag)
    return tag


def _set_ssh_user():
    """
    Ensure env.user is correctly set
    """
    if 'TANGENT_USER' in os.environ:
        env.user = os.environ['TANGENT_USER']
    else:
        env.user = prompt(red('Username for remote host? [default is current user] '))
    if not env.user:
        env.user = os.environ['USER']


def _deploy_codebase(tarball):
    """
    Upload a tarballand unpack into place
    """
    _set_ssh_user()
    _upload(tarball)
    _unpack(tarball)


def _upload(local_path, remote_path=None):
    """
    Uploads a file
    """
    if not remote_path:
        remote_path = local_path
    notify("Uploading %s to %s" % (local_path, remote_path))
    put(local_path, remote_path)


def _unpack(tarball_filepath):
    """
    Unpacks the tarball into the correct place but doesn't switch
    the symlink
    """
    # Ensure all folders are in place
    sudo('if [ ! -d "%(build_root)s" ]; then mkdir -p "%(build_root)s"; fi' % env)

    notify("Unpacking tarball into %(build_root)s" % env)
    with cd(env.builds_root):
        sudo('tar xzf %s' % tarball_filepath)

        # Create new build folder
        sudo('if [ -d "%(build_folder)s" ]; then rm -rf "%(build_folder)s"; fi' % env)
        sudo('mv %(web_folder)s %(build_folder)s' % env)

        # Symlink in media folder
        sudo('ln -s %(media_root)s %(build_folder)s/public/media' % env)

        # Insert release info to settings.py so it can be used within templates
        sudo("sed -i 's/UNVERSIONED/%(pointer)s/' %(build_folder)s/settings.py" % env)

        # Add file with build information (very useful for debugging)
        commit = _get_commit_id()
        sudo('echo -e "pointer: %s\ncommit: %s\nuser: %s" > %s/build-info' % (
            env.version, commit, env.user, env.build_folder))

        # Remove archive
        sudo('rm %s' % tarball_filepath)


def _update_virtualenv():
    """
    Install the dependencies in the requirements file
    """
    notify("Updating virtualenv")
    with cd(env.build_root):
        sudo('source %(virtualenv_root)s/bin/activate && pip install -r deploy/requirements.txt' % env)


def _migrate_db_schema():
    """
    Apply any schema alterations
    """
    notify("Applying database migrations")
    with cd(env.build_root):
        sudo('source %(virtualenv_root)s/bin/activate && ./manage.py syncdb --noinput > /dev/null' % env)
        sudo('source %(virtualenv_root)s/bin/activate && ./manage.py migrate' % env)


def _collect_static_files():
    notify("Collecting static files")
    with cd(env.build_root):
        sudo('source %(virtualenv_root)s/bin/activate && ./manage.py collectstatic --noinput > /dev/null' % env)
        sudo('chmod -R g+w public' % env)


def _deploy_nginx_config():
    notify('Moving nginx config into place')
    sudo('mv %(nginx_conf_filepath)s /etc/nginx/sites-enabled/' % env)


def _deploy_supervisord_config():
    notify('Moving supervisord config into place')
    sudo('mv %(supervisord_conf_filepath)s /etc/supervisor/conf.d/' % env)


def _deploy_cronjobs():
    """
    Deploy the app server cronjobs
    """
    notify('Deploying cronjobs')
    with cd(env.build_root):
        # Replace variables in cron files
        sudo("rename 's#BUILD#%(build_name)s#' deploy/cron.d/*" % env)
        sudo("sed -i 's#VIRTUALENV_ROOT#%(virtualenv_root)s#g' deploy/cron.d/*" % env)
        sudo("sed -i 's#BUILD_ROOT#%(build_root)s#g' deploy/cron.d/*" % env)
        # Ensure permissions are correct and move into /etc/cron.d
        sudo("chmod 600 deploy/cron.d/*" % env)
        sudo("mv deploy/cron.d/* /etc/cron.d" % env)


def _delete_old_builds():
    notify('Deleting old builds')
    with cd(env.builds_root):
        sudo('find . -maxdepth 1 -type d -name "%(build_name)s*" | sort -r | sed "1,9d" | xargs rm -rf' % env)


def _push_tags():
    notify("Pushing tags")
    local('git push --tags')


def _delete_tarball():
    notify("Removing tarball")
    local('rm %(tarball_filepath)s' % env)


def _switch_symlink():
    notify("Switching symlinks")
    with cd(env.builds_root):
        # Create new symlink for build folder
        sudo('if [ -h %(build_name)s ]; then unlink %(build_name)s; fi' % env)
        sudo('ln -s %(build_folder)s %(build_name)s' % env)


def _reload_python_code():
    notify('Touching WSGI file to reload python code')
    sudo('touch %(wsgi_filepath)s' % env)


def _reload_nginx():
    notify('Reloading nginx configuration')
    sudo('/etc/init.d/nginx force-reload')


def _reload_supervisord():
    notify('Reloading supervisord configuration')
    sudo('/usr/bin/supervisorctl reload')
