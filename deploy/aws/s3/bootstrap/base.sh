#!/bin/bash
#
# Base bootstrapping script which should be applicable for all types of EC2
# instance
#
# This script installs
#   - Docker
#   - NSEnter

set -e  # Fail fast

# Keep all audit here
LOGFILE="/var/log/bootstrap.base.log"

# Redirect STDOUT and STDERR to file
exec 1> >(tee -a $LOGFILE)
exec 2>&1

function notify {
    printf "\n\n==== $1 ====\n\n"
}

notify "Installing Docker"
wget -O - https://get.docker.io/ | bash

notify "Installing nsenter"
wget -O /usr/local/bin/nsenter https://github.com/tangentlabs/nsenter/raw/master/nsenter
chmod +x /usr/local/bin/nsenter

# TODO Set the auth key here
# DOCKER_REGISTRY_AUTH=
notify "Creating Docker credentials Files"
[[ ! -z "$DOCKER_REGISTRY_AUTH" ]] && echo "Docker registry auth missing!" && exit 1 
echo '{"https://docker.tangentlabs.co.uk/v1/":{"auth":"' $DOCKER_REGISTRY_AUTH '","email":""}}' > /root/.dockercfg
echo '{"https://docker.tangentlabs.co.uk/v1/":{"auth":"' $DOCKER_REGISTRY_AUTH '","email":""}}' > /home/ubuntu/.dockercfg
