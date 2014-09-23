import os

from fabric.colors import green, red, blue
from fabric.api import local, env, abort

# Config
# ------

# TODO Set the client and project for your project
env.client = 'tangent'
env.project = 'boilerplate'

# Utils
# -----


def _notify(msg):
    bar = '+' + '-' * (len(msg) + 2) + '+'
    print green('')
    print green(bar)
    print green("| %s |" % msg)
    print green(bar)
    print green('')


def _fail(msg):
    abort(red(msg))


# Docker tasks
# ------------

def build_docker_image(image_type=None, tag="latest"):
    """
    Build a Docker image
    """
    if image_type not in ('base', 'dev', 'release'):
        _fail("Choose one of base, dev or release")

    # Check Dockerfile exists
    dockerfile = "deploy/docker/Dockerfile-%s" % image_type
    if not os.path.exists(dockerfile):
        _fail("Dockerfile %s does not exist!" % dockerfile)

    # Remove the www/.env file (if it exists) as we don't want it in the image
    envfile = "www/.env"
    if os.path.exists(envfile) and os.path.islink(envfile):
        local("unlink %s" % envfile)

    # Symlink in the dockerfile and build the container
    build_tag = "%s-%s-%s:%s" % (env.client, env.project, image_type, tag)
    if image_type == 'release':
        # Prepend registry when creating a release image
        build_tag = "docker.tangentlabs.co.uk/%s" % build_tag

    _notify("Building Docker image '%s' from %s" % (
        build_tag, dockerfile))
    dockerlink = "Dockerfile"
    if os.path.islink(dockerlink):
        local("unlink %s" % dockerlink)
    local("ln -s %s %s" % (dockerfile, dockerlink))
    local("docker build -t %s ." % build_tag)
    local("unlink %s" % dockerlink)

    _notify("Docker image built")

    # Show useful information for release image types
    if image_type == 'release':
        image_id = local("docker images | sed -n 2p | awk '{print $3}'",
                         capture=True)
        print "Test this container locally by running:\n"
        print blue(("$ docker run -it -v /tmp:/host -e "
                    "ENV_FILE_URI=/var/www/env/local %s") % image_id)
        print "\nTo push this image to the registory, run:\n"
        print blue("$ docker push %s" % build_tag)


# Deployment/AWS tasks
# --------------------


env.build_name = None


def _configure(build_name):
    env.build_name = build_name
    env.s3_bucket_name = '%s-%s-%s' % (
        env.client, env.project, build_name)
    env.s3_bucket_url = 's3://%s' % env.s3_bucket_name
    env.docker_image = 'docker.tangentlabs.co.uk/%s-%s-release' % (
        env.client, env.project)


# Environments


def test():
    _configure('test')


def stage():
    _configure('stage')


def prod():
    _configure('prod')


# Actions


def deploy(tag):
    """
    Deploy a Docker tag

    This uploads a "release/docker_image" file to S3 which specifies which
    Docker image to deploy.
    """
    if env.build_name not in ('test', 'stage', 'prod'):
        _fail("Choose one of test, stage or prod")
    _notify("Deploying tag %s" % tag)
    init_s3()

    folder = local("mktemp -d", capture=True)
    filepath = os.path.join(folder, 'docker_image')
    local("echo %s:%s > %s" % (env.docker_image, tag, filepath))
    local("aws s3 cp %s %s/release/docker_image" % (
        filepath, env.s3_bucket_url))


def user_data():
    """
    Print the EC2 user data for a given environment
    """
    filepath = 'deploy/aws/ec2/user-data.sh'
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace('{{ s3_bucket_url }}', env.s3_bucket_url)
    print content


def init_s3():
    """
    Ensure the appropriate bucket is created and populated.
    """
    _notify("Ensuring the %(s3_bucket_url)s bucket is created" % env)
    local("aws s3 mb %(s3_bucket_url)s" % env)


def sync_s3():
    """
    Sync ALL bootstrap/release files onto S3
    """
    init_s3()
    sync_s3_bootstrap_files()
    sync_s3_release_files()


def sync_s3_bootstrap_files():
    """
    Sync bootstrap files onto S3
    """
    _notify("Syncing bootstrap files")
    files = local("find deploy/aws/s3/bootstrap -type f", capture=True).split()
    for file in files:
        filename = os.path.basename(file)
        local("aws s3 cp %s %s/bootstrap/%s" % (
            file, env.s3_bucket_url, filename))


def sync_s3_release_files():
    """
    Sync release files onto S3
    """
    _notify("Syncing release files")
    # Some files in the release folder should not be in source control if they
    # contain sensitive variables.
    files = local("find deploy/aws/s3/release -type f", capture=True).split()
    for file in files:
        filename = os.path.basename(file)
        local(
            "aws s3 cp %s %s/release/%s" % (file, env.s3_bucket_url, filename))
