import os

from fabric.colors import green, red
from fabric.api import local, env, abort

# Config
# ------

# TODO Set the client and project for your project
env.client = 'tangent'
env.project = 'boilerplate'

# Utils
# -----


def notify(msg):
    bar = '+' + '-' * (len(msg) + 2) + '+'
    print green('')
    print green(bar)
    print green("| %s |" % msg)
    print green(bar)
    print green('')


def fail(msg):
    abort(red(msg))


# Docker tasks
# ------------

def build_docker_image(image_type=None, tag="latest"):
    """
    Build a Docker image
    """
    if image_type not in ('base', 'dev', 'release'):
        fail("Choose one of base, dev or release")

    # Check Dockerfile exists
    dockerfile = "deploy/docker/Dockerfile-%s" % image_type
    if not os.path.exists(dockerfile):
        fail("Dockerfile %s does not exist!" % dockerfile)

    # Remove the www/.env file (if it exists) as we don't want it in the image
    envfile = "www/.env"
    if os.path.exists(envfile) and os.path.islink(envfile):
        local("unlink %s" % envfile)

    # Symlink in the dockerfile and build the container
    notify("Building Docker image '%s' from %s" % (
        tag, dockerfile))
    dockerlink = "Dockerfile"
    if os.path.islink(dockerlink):
        local("unlink %s" % dockerlink)
    local("ln -s %s %s" % (dockerfile, dockerlink))
    local("docker build -t %s ." % tag)
    local("unlink %s" % dockerlink)


# Deployment/AWS tasks
# --------------------


env.build_name = None


def _configure(build_name):
    env.build_name = build_name
    env.s3_bucket_name = '%s-%s-%s' % (
        env.client, env.project, build_name)
    env.s3_bucket_url = 's3://%s' % env.s3_bucket_name
    env.docker_image = 'docker.tangentlabs.co.uk/%s-%s' % (
        env.client, env.project)


def test():
    _configure('test')


def stage():
    _configure('stage')


def prod():
    _configure('prod')


def deploy(tag):
    """
    Deploy a Docker tag

    This uploads a "release/docker_image" file to S3 which specifies which
    Docker image to deploy.
    """
    if env.build_name not in ('test', 'stage', 'prod'):
        fail("Choose one of test, stage or prod")
    notify("Deploying tag %s" % tag)
    init_s3()

    folder = local("mktemp -d", capture=True)
    filepath = os.path.join(folder, 'docker_image')
    local("echo %s:%s > %s" % (env.docker_image, tag, filepath))
    local("aws s3 cp %s %s/release/docker_image" % (
        filepath, env.s3_bucket_url))


def init_s3():
    """
    Ensure the appropriate bucket is created and populated.
    """
    notify("Ensuring the %(s3_bucket_url)s bucket is created" % env)
    local("aws s3 mb %(s3_bucket_url)s" % env)


def sync_s3():
    """
    Sync all bootstrap/release files onto S3
    """
    init_s3()
    sync_s3_bootstrap_files()
    sync_s3_release_files()


def sync_s3_bootstrap_files():
    """
    Sync bootstrap files onto S3
    """
    init_s3()
    notify("Syncing bootstrap files")
    files = local("find deploy/aws/s3/bootstrap -type f", capture=True).split()
    for file in files:
        filename = os.path.basename(file)
        local("aws s3 cp %s %s/bootstrap/%s" % (
            file, env.s3_bucket_url, filename))


def sync_s3_release_files():
    """
    Sync release files onto S3
    """
    init_s3()
    notify("Syncing release files")
    # Some files in the release folder should not be in source control if they
    # contain sensitive variables.
    files = local("find deploy/aws/s3/release -type f", capture=True).split()
    for file in files:
        filename = os.path.basename(file)
        local("aws s3 cp %s %s/release/%s" % (file, env.s3_bucket_url, filename))
