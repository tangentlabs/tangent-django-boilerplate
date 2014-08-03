#!/bin/bash
#
# Webserver start-up script for Docker container
#
# The environmental variables parsed by this script are:
#
# DJANGO_ENV_URI (required)
#     An S3/HTTP/HTTPS URI or a file that has been
#     exposed to the container through the /host/ mount
#     point. Parsed by get_file() function below.

# Helper Functions

function error() {
    # Print an error message and exit with non-zero exit code
    printf "Error: $1\n" 1>&2
    exit 1
}

function get_file() {
    # Fetch a file from a (possibly remote) location
    #
    # get_file [variable-name] [variable-contents] [destination-file]
    #
    #         get_file MY_BASH_VARIABLE $MY_BASH_VARIABLE /opt/myfile
    #
    ENV_VAR=$1
    URI=$2
    DEST=$3

    if [[ -z "$ENV_VAR" ]] || [[ -z "$URI" ]] || [[ -z "$DEST" ]]; then
        printf "get_file() Error:\n\n"
        printf "Could not get file specified in $ENV_VAR\n"
        printf "\tSrc URI: ${URI:-UNDEFINED}\n"
        printf "\tDst Path:${DEST:-UNDEFINED}\n\n"
        printf "Exiting..\n\n"
        exit 1
    fi

    case $URI in
        s3://*|S3://*)
            OUTPUT=$(s3 cmd cp --force $URI $DEST) || error "Error retrieving $URI from S3\n\n$OUTPUT\n\n\nExiting\n" && exit 1
        ;;
        http://*|https://*)
            OUTPUT=$(wget -O $DEST $URI) || error "Error retrieving file from $URI\n\n$OUTPUT\n\nExiting\n\n"
        ;;
        /*)
            OUTPUT=$(cp $URI $DEST) || error "Error copying file from $URI\n\n$OUTPUT\n\nExiting\n\n"
        ;;
        *)
            printf "\n\"$URI\" is not a valid URI\n\n"
            printf "Please specify one of the following:\n"
            printf "\t- A file from the host (e.g. /host/myfile1)\n"
            printf "\t- An HTTP/HTTPS URL (e.g. http://example.com/file1\n"
            printf "\t- An S3 URL (e.g. s3://my-bucket/file1\n\n"
            printf "Exiting....\n\n"
            exit 1
        ;;
    esac
}


set -e  # Fail fast

# Ensure there is a folder to log to
[[ ! -d /host/logs ]] && mkdir -p /host/logs

# Copy all output to file
exec 1> >(tee -a /host/logs/container_startup.log)
exec 2>&1

# When the container starts is useful audit information
echo
echo "Starting container: `date`"

# Check that an env file was specified
[ -z "${DJANGO_ENV_URI}" ] && error "A DJANGO_ENV_URI env variable must be specified"

# Fetch env conf
get_file DJANGO_ENV_URI $DJANGO_ENV_URI /var/www/.env

echo "Updating database schema"
cd /var/www/
./manage.py syncdb --noinput
./manage.py migrate

echo "Collecting static files"
./manage.py collectstatic --noinput

echo "Starting supervisord"
supervisord -n 
