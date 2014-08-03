#!/bin/bash
#
# Initial bootstrap script for an EC2 instance.
#
# The contents of this file need to be stored against the created EC2 instance
# as "user data". See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

BUCKET=tangent-boilerplate
ITEMS=(
    bootstrap/base.sh
    bootstrap/webserver.sh
)

# Install AWS CLI
apt-get update
apt-get install -y python-pip
pip install -U pip
pip install awscli

# Fetch and run each bootstrap file
for ITEM in "${ITEMS[@]}"
do
    aws s3 cp s3://$BUCKET/$ITEM /tmp/bootstrap.sh
    chmod +x /tmp/bootstrap.sh
    /tmp/bootstrap.sh
done
