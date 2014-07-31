#!/bin/bash
#
# Webserver setup/start script for Docker
#
# This script takes arguments via BASH environment variables and
# is capable of extension to include other customer functionality
# on a per-project basis.
#
# The BASH variables currently parsed by this script are:
#
#     DJANGO_CONFIG_URI (required)
#         An S3/HTTP/HTTPS URI or a file that has been
#         exposed to the container through the /host/ mount
#         point. Parsed by get_file() function bellow.
#
#         Examples:
#             ./deploy/aws/config/stage/stage.py
#             ./deploy/aws/config/prod/prod.py
#
#     UWSGI_INI_URI (optional)
#         S3/HTTP/HTTPS or /host/ reference to a custom
#         Uwsgi ini file used for booting your application
#
#         Example:
#             ./deploy/aws/config/stage/uwsgi.ini
#
#     CRON_INI_URI (optional)
#         S3/HTTP/HTTPS or /host/ reference to a custom cron
#         INI file. Cron is performed using the Uwsgi
#         "unique-cron" function, so the INI file needs to
#         be in Uwsgi INI format.
#
#         Example:
#             ./deploy/aws/config/stage/cron.ini
#
#     SUPERVISOR_CONFIG_URI (optional)
#         S3/HTTP/HTTPS or /host/ reference to a customer
#         supervisor configuration file. Can be used to
#         overwrite the default behaviour configured in
#         /etc/supervisor/conf.d/app.conf
#
#         Example:
#             ./deploy/shared/supervisor.app.conf


# Helper Functions

function error() {
    # Print an error message and exit with error (1)
    printf "$1\n\nExiting.....\n\n"
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

echo
echo "Starting container: `date`"

# Check that DJANGO_URI was specified or exit with error
[ -z "${DJANGO_CONFIG_URI}" ] && error "DJANGO_CONFIG_URI cannot be empty"

# Retrieve Django conf and save it to a known location
get_file DJANGO_CONFIG_URI $DJANGO_CONFIG_URI /var/www/conf/docker.py

echo "Updating database schema"
cd /var/www/
DJANGO_CONF=conf.docker ./manage.py syncdb --noinput
DJANGO_CONF=conf.docker ./manage.py migrate

echo "Collecting static files"
DJANGO_CONF=conf.docker ./manage.py collectstatic --noinput

supervisord -n 
