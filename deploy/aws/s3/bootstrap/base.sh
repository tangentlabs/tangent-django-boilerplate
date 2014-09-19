#!/bin/bash
#
# Base bootstrapping script which should be applicable for all types of EC2
# instance.
#
# Note, the user-data script (which executes this one) exports the notify
# function as well as the S3_BUCKET_URL and REGION vars.

set -e  # Fail fast

# Create folder that we will mount into Docker containers
mkdir -p /host/

notify "Installing Docker"
wget -q -O - https://get.docker.io/ | bash

notify "Installing nsenter"
wget -q -O /usr/local/bin/nsenter https://github.com/tangentlabs/nsenter/raw/master/nsenter
chmod +x /usr/local/bin/nsenter

# Grab Docker auth from S3
S3_PATH="$S3_BUCKET_URL/bootstrap/dockercfg"
notify "Fetching Docker config from $S3_PATH"
aws s3 cp --region=$REGION $S3_PATH /home/ubuntu/.dockercfg
cp /home/ubuntu/.dockercfg /root/.dockercfg
