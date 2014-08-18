import os

from fabric.api import local, env, abort

env.client = 'tangent'
env.project = 'boilerplate'
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


def deploy(tag):
    """
    Deploy a Docker tag

    This uploads a "release/docker_image" file to S3 which specifies which
    Docker image to deploy.
    """
    if env.build_name not in ('test', 'stage', 'prod'):
        abort("Choose one of test, stage or prod")
    print("Deploying tag %s" % tag)
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
    local("aws s3 mb %(s3_bucket_url)s" % env)


def sync_s3_bootstrap_files():
    init_s3()
    files = local("find aws/s3/bootstrap -type f", capture=True).split()
    for file in files:
        local("aws s3 cp %s %s/%s" % (file, env.s3_bucket_url, file))


def sync_s3_release_files():
    init_s3()
    # Some files in the release folder should not be in source control if they
    # contain sensitive variables.
    files = local("find aws/s3/release -type f", capture=True).split()
    for file in files:
        local("aws s3 cp %s %s/%s" % (file, env.s3_bucket_url, file))
