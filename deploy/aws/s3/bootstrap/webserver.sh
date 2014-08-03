#!/bin/bash
#
# Bootstrap script for a webserver
#
# This file is just an example - it is intended to be customised for your project.
# TODO Customise this file for your project
# 
# When ready, this file should be uploaded to S3 so it can be downloaded and
# executed by the Stage 1 bootstrap script. Its S3 location will need to be set
# as a tag against the EC2 instance.

# ===================================================================

# Set your project name here
PROJECT=boilerplate

# Role of this container (eg webserver, search, queue)
ROLE=webserver

# This is the Docker Image Tag you want to pull
TAG=latest

# What is the address to configure the nginx vhost on to listen
# for?
HOSTNAMES=

# Docker Repository to pull the image from
DOCKER_IMAGE_NAME=docker.tangentlabs.co.uk/${PROJECT}-release-${ROLE}:${TAG}

# S3 URI for htaccess file should it be needed. Leave empty to ignore password
# protection for the site.
HTACCESS_FILE=

# ===================================================================

set -e  # Fail fast

exec 1> >(tee -a /var/log/bootstrap.webserver.log)
exec 2>&1

# Create a /containers/ subdirectory to act as a bridge
# between the host and the container
HOST_SHARED_FOLDER="/containers/${PROJECT}-${ROLE}"
echo "Creating $HOST_SHARED_FOLDER"
mkdir -p "$HOST_SHARED_FOLDER"

# Fetch and run the docker image, passing in the S3 location of the
# production settings file.
echo "Pulling docker image '$DOCKER_IMAGE_NAME'"
docker pull ${DOCKER_IMAGE_NAME}
DOCKER_CONTAINER_NAME="$PROJECT-$ROLE-$TAG"

echo "Running docker container"
docker run -d -p 80 --name $DOCKER_CONTAINER_NAME \
           -v $HOST_SHARED_FOLDER:/host \
           -e DJANGO_ENV_URI=s3://${PROJECT}/env/prod \
           ${DOCKER_IMAGE_NAME}

# Port 80 inside the container will be bound to a random
# port on the host. Find out what it is!
DOCKER_PORT=$(docker port $DOCKER_CONTAINER_NAME 80)

# Ensure nginx is installed
apt-get install -y nginx
find /etc/nginx/sites-enabled/ -type f -delete
[ -n "$HTACCESS_FILE" ] && aws s3 cp $HTACCESS_FILE /etc/nginx/htpasswd

cat > /etc/nginx/sites-enabled/docker.conf << EOF
upstream docker {
    server 127.0.0.1:$DOCKER_PORT;
}

server {
    listen 80;
    server_name ${HOSTNAMES};

    location / {
        $([[ -n $HTACCESS_FILE ]] && printf "auth_basic \"Restricted\";")
        $([[ -n $HTACCESS_FILE ]] && printf "auth_basic_user_file /etc/nginx/htpasswd;")
        include uwsgi_params;
        uwsgi_pass docker;
    }
}
EOF

/etc/init.d/nginx restart
