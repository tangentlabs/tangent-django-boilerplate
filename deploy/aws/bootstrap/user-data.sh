#!/bin/bash
#
# Stage 1 (project agnostic) bootstrapping of an EC2 instance.
#
# The contents of this file need to be stored against the created EC2 instance as "user data".
# See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
#
# This script:
#   - updates the OS
#   - installs Python and PIP
#   - installs Docker and NSEnter
#   - installs AWS CLI tools
#   - configures the Docker config so this instance can talk to the Tangent Docker registry
#   - downloads runs the "stage 2 bootstrap" script from S3
#
# This script is intended to be fairly project agnostic. Project-specific stuff is generally held in the
# Stage 2 script.

set -x  # Debug mode
set -e  # Fail fast

# Keep all audit here
LOGFILE="/opt/bootstrap.stage1.log"

# Redirect STDOUT and STDERR to file
exec 1> >(tee -a $LOGFILE)
exec 2>&1

function notify {
    printf "\n\n==== $1 ====\n\n"
}

notify "Updating Apt"
apt-get update
apt-get dist-upgrade -y

notify "Installing Python Tools"
apt-get install -y python-dev python-pip
pip install -U pip

notify "Installing Docker"
wget -O - https://get.docker.io/ | bash

notify "Installing nsenter"
wget -O /usr/local/bin/nsenter https://github.com/tangentlabs/nsenter/raw/master/nsenter
chmod +x /usr/local/bin/nsenter

notify "Installing AWS CLI Tools"
pip install awscli s3cmd

# Pre-Populate the ~/.dockercfg for root and ubuntu so they can pull images
# from docker.tangentlabs.co.uk. Note, this value of the auth needs to be
# extracted from the Tangent Docs repo.

# DOCKER_REGISTRY_AUTH=
notify "Creating Docker Credentials Files"
[[ ! -z "$DOCKER_REGISTRY_AUTH" ]] && echo "Docker registry auth missing!" && exit 1 
echo '{"https://docker.tangentlabs.co.uk/v1/":{"auth":"' $DOCKER_REGISTRY_AUTH '","email":""}}' > /root/.dockercfg
echo '{"https://docker.tangentlabs.co.uk/v1/":{"auth":"' $DOCKER_REGISTRY_AUTH '","email":""}}' > /home/ubuntu/.dockercfg

# Query the EC2 Instance Metadata and find the "Bootstrap" tag.  This tag
# contains the 2nd-stage script required to continue the boot-automation
# process.
notify "Pulling Second-Stage Boot File from S3"
INSTANCE_ID=$(ec2metadata | awk '/^instance-id/ {print $2}')
BOOTSTRAP_SCRIPT=$(/usr/local/bin/aws ec2 describe-instances --region eu-west-1 --output text --instance-ids $INSTANCE_ID | awk '/Bootstrap/ {print $3}')
aws s3 cp --region eu-west-1 $BOOTSTRAP_SCRIPT /opt/boot_stage2.sh

# Run the 2nd-stage bootstrap script
notify "Running 2nd-Stage Boot Script"
chmod +x /opt/boot_stage2.sh
sudo -u root /bin/bash -lc "bash /opt/boot_stage2.sh"
