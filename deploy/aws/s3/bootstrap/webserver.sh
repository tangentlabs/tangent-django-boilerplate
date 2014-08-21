#!/bin/bash
#
# Bootstrap script for a webserver
#
# This script is intended to be called by the user data script from an EC2
# instance (as it requires the S3_BUCKET_URL env variable to be set). This script
# fetches 3 things that it needs to run the appropriate docker container:
#
# s3://$bucket/release/docker_image  -  A text file whose contents are a Docker
# registry URL.
#
# s3://$bucket/release/hostnames  -  A text file whose contents are the
# hostnames that nginx should respond to.
#
# s3://$bucket/release/env  -  A text file (not in source control) which is
# downloaded so it can be passed into the Docker container


set -e  # Fail fast

exec 1> >(tee -a /var/log/bootstrap.webserver.log)
exec 2>&1

# Determine docker image name from a S3 file
IMAGE_S3_PATH="$S3_BUCKET_URL/release/docker_image"
notify "Fetching $IMAGE_S3_PATH"
aws s3 cp --region=$REGION $IMAGE_S3_PATH /tmp/docker_image
DOCKER_IMAGE=$(cat /tmp/docker_image)

# Determine hostnames from a S3 file
HOSTNAMES_S3_PATH="$S3_BUCKET_URL/release/hostnames"
notify "Fetching $HOSTNAMES_S3_PATH"
aws s3 cp --region=$REGION $HOSTNAMES_S3_PATH /tmp/hostnames
HOSTNAMES=$(cat /tmp/hostnames)

# Fetch sensitive env variables from S3
ENV_S3_PATH="$S3_BUCKET_URL/release/env"
notify "Fetching $ENV_S3_PATH"
aws s3 cp --region=$REGION $ENV_S3_PATH /host/env

# Fetch and run the docker image, passing in the S3 location of the
# production settings file.
notify "Pulling docker image '$DOCKER_IMAGE'"
docker pull $DOCKER_IMAGE

notify "Running docker container"
docker run -d -p 80 --name webserver \
           -v /host:/host \
           -e DJANGO_ENV_URI=/host/env \
           $DOCKER_IMAGE_NAME

# Port 80 inside the container will be bound to a random
# port on the host. Find out what it is!
DOCKER_PORT=$(docker port $DOCKER_CONTAINER_NAME 80)

# Ensure nginx is installed
echo "Installing nginx to proxy to port $DOCKER_PORT of container"
apt-get install -y nginx
find /etc/nginx/sites-enabled/ -type f -delete

cat > /etc/nginx/sites-enabled/docker.conf << EOF
# Default server
server {
    return 404;
}

upstream docker {
    server 127.0.0.1:$DOCKER_PORT;
}

server {
    listen 80;
    server_name $HOSTNAMES;

    location / {
        include uwsgi_params;
        uwsgi_pass docker;
    }
}
EOF

/etc/init.d/nginx restart
