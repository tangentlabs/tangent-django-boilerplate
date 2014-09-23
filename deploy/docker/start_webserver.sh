#!/bin/bash
#
# Webserver start-up script for Docker container
#
# The environmental variables parsed by this script are:
#
# ENV_FILE_URI (required)
#     The filepath to an env file. This will be copied to /var/www/.env

# Helper Functions

function error() {
    # Print an error message and exit with non-zero exit code
    printf "\n\nError: $1\n\n" 1>&2
    exit 1
}

set -e  # Fail fast

# Check that an env file URI was specified
[ -z "$ENV_FILE_URI" ] && error "A ENV_FILE_URI environmental variable must be specified"

# Ensure there is a folder to log to
[[ ! -d /host/logs ]] && mkdir -p /host/logs

# Copy all output to file
exec 1> >(tee -a /host/logs/docker.container_startup.log)
exec 2>&1

# When the container starts is useful audit information
printf "\n%s - Starting container with ENV_FILE_URI=%s\n\n" "$(date)" $ENV_FILE_URI

# Grab the envfile using the appropriate mechanism
echo "Copying $ENV_FILE_URI to /var/www/.env"
case $ENV_FILE_URI in
    s3://*|S3://*)
        REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')
        aws s3 cp --region=$REGION $ENV_FILE_URI /var/www/.env
        ;;
    /*)
        cp $ENV_FILE_URI /var/www/.env
        ;;
    *)
        error "Unrecognised ENV_FILE_URI '$ENV_FILE_URI'"
        ;;
esac

echo "Updating database schema"
cd /var/www/
./manage.py syncdb --noinput
./manage.py migrate

echo "Collecting static files"
./manage.py collectstatic --noinput

echo "Compressing"
./manage.py compress --force

# Ensure log files are writable by uwsgi process
[ ! -d /host/logs ] && mkdir /host/logs
chown www-data:www-data /host/logs/*.log

echo "Starting supervisord"
supervisord -n 
