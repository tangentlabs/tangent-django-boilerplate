#!/bin/bash
#
# Webserver start-up script for Docker container
#
# The environmental variables parsed by this script are:
#
# DJANGO_ENV_URI (required)
#     The filepath to an env file. This will be copied to /var/www/.env

# Helper Functions

function error() {
    # Print an error message and exit with non-zero exit code
    printf "\n\nError: $1\n\n" 1>&2
    exit 1
}

set -e  # Fail fast

# Check that an env file was specified
[ -z "$DJANGO_ENV_URI" ] && error "A DJANGO_ENV_URI env variable must be specified"
[ ! -f "$DJANGO_ENV_URI" ] && error "$DJANGO_ENV_URI does not exist"

# Copy all output to file
exec 1> >(tee -a /host/logs/docker.container_startup.log)
exec 2>&1

# When the container starts is useful audit information
printf "\n%s - Starting container with DJANGO_ENV_URI=%s\n\n" "$(date)" $DJANGO_ENV_URI

# Ensure there is a folder to log to
[[ ! -d /host/logs ]] && mkdir -p /host/logs

echo "Linking /var/www/.env to $DJANGO_ENV_URI"
ln -s $DJANGO_ENV_URI /var/www/.env

echo "Updating database schema"
cd /var/www/
./manage.py syncdb --noinput
./manage.py migrate

echo "Collecting static files"
./manage.py collectstatic --noinput

# Ensure log files are writable by uwsgi process
chown www-data:www-data /host/logs/*.log

echo "Starting supervisord"
supervisord -n 
