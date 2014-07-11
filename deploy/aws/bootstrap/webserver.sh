#!/bin/bash
#
# EXAMPLE: Stage Webserver Bootstrap file
#
# NOTE: You need to enter in a valid HTAccess file S3 location if
#       you want the site password protected!!!
#

# This is the Docker Image Tag you want to pull
RELEASE_VERSION=latest

# Set your project name here
PROJECT=

# What is the address to configure the nginx vhost on to listen
# for?
URLS=

# Docker Repository to pull the image from
DOCKER_IMAGE=docker.tangentlabs.co.uk/${PROJECT}-release-webserver:${RELEASE_VERSION}

# S3 URI for HTAccess file should it be needed. Leave empty to
# ignore password protection for the site.
HTACCESS_FILE=

# Log output of this script too /opt/boot_stage2.log
set -e
exec 1> >(tee -a /opt/boot_stage2.log)
exec 2>&1

# Create a /containers/ subdirectory to act as a bridge
# between the host and the container
mkdir -p /containers/${PROJECT}-webserver/logs
docker pull ${DOCKER_IMAGE}
docker run -d -p 80 --name webserver-$RELEASE_VERSION \
           -v /containers/${PROJET}-webserver:/host \
           -e UWSGI_INI_URI=s3://${PROJECT}/config/uwsgi.ini \
           -e DJANGO_CONFIG_URI=s3://${PROJECT}/config/prod.py \
           ${DOCKER_IMAGE}

# Port 80 inside the container will be bound to a random
# port on the host. Find out what it is!
DOCKER_PORT=$(docker port webserver-$RELEASE_VERSION 80)

#
# This may be redundant, but it will ensure nginx is installed
#
apt-get install -y nginx
[ -e /etc/nginx/sites-enabled/default ] && rm /etc/nginx/sites-enabled/default
find /etc/nginx/sites-enabled/ -type f -delete
[ -n "$HTACCESS_FILE" ] && aws s3 cp $HTACCESS_FILE /etc/nginx/htpasswd

cat > /etc/nginx/sites-enabled/docker.conf << EOF
upstream docker {
    server 127.0.0.1:$DOCKER_PORT;
}

server {
    listen 80;#
    server_name ${URLS};

    location / {
        $([[ -n $HTACCESS_FILE ]] && printf "auth_basic \"Restricted\";")
        $([[ -n $HTACCESS_FILE ]] && printf "auth_basic_user_file /etc/nginx/htpasswd;")
        include uwsgi_params;
        uwsgi_pass docker;
    }
}
EOF

#
# If you want to automate the restart of Nginx, uncomment this
#

#/etc/init.d/nginx restart
