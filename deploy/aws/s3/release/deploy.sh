#!/usr/bin/env bash

# Check the docker_image file on S3. If it has changed, then update the Docker
# container.

set -e  # Fail fast

exec 1> >(tee -a /var/log/docker.deploy.log)
exec 2>&1

# Grab S3 bucket URL
S3_BUCKET_URL=$(cat /etc/s3_bucket_url)

# Fetch region
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')

# Grab Docker image string on S3
TMP_FILE=$(mktemp)
aws s3 cp --region=$REGION $S3_BUCKET_URL/release/docker_image $TMP_FILE > /dev/null
S3_DOCKER_IMAGE=$(cat $TMP_FILE)

printf "%s - Docker image is %s\n" "$(date)" $S3_DOCKER_IMAGE

# Grab running Docker image (will be empty string if no docker container running)
CURRENT_DOCKER_IMAGE=$(docker ps | tail -n +2 | awk '{print $2}')

# Only deploy if the images differ
[ "$S3_DOCKER_IMAGE" == "$CURRENT_DOCKER_IMAGE" ] && exit

# Pull latest Docker image
echo "Pulling Docker image $S3_DOCKER_IMAGE"
docker pull $S3_DOCKER_IMAGE > /dev/null

# Fetch sensitive env variables from S3
aws s3 cp --region=$REGION $S3_BUCKET_URL/release/env /host/env > /dev/null

echo "Starting Docker container from image $S3_DOCKER_IMAGE"
DOCKER_CONTAINER_ID=$(docker run -d -p 80 -v /host:/host -e DJANGO_ENV_URI=/host/env $S3_DOCKER_IMAGE)

# Port 80 inside the container will be bound to a random
# port on the host. Find out what it is!
DOCKER_PORT=$(docker port $DOCKER_CONTAINER_ID 80 | cut -d":" -f2)

# Determine hostnames from a S3 file
aws s3 cp --region=$REGION $S3_BUCKET_URL/release/hostnames /tmp/hostnames > /dev/null
HOSTNAMES=$(cat /tmp/hostnames)
    
# Tweak nginx to talk to new container
echo "Pointing nginx to port $DOCKER_PORT"

cat > /etc/nginx/sites-enabled/002-docker << EOF
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

/etc/init.d/nginx configtest > /dev/null && /etc/init.d/nginx restart > /dev/null

echo "Deploy complete"
