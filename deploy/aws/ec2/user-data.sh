#!/usr/bin/env bash
#
# Initial bootstrap script for an EC2 instance.
#
# The contents of this file need to be stored against the created EC2 instance
# as "user data". See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

set -e

export S3_BUCKET_URL="{{ s3_bucket_url }}"

# Pretty printing function (so user data output is easier to spot in the system logs)
function notify() {
    local len=$((${#1}+2))
    printf "\n+"
    printf -- "-%.0s" $(seq 1 $len)
    printf "+\n| $1 |\n+"
    printf -- "-%.0s" $(seq 1 $len)
    printf "+\n\n"
}

notify "Bootstrapping starting using $S3_BUCKET_URL"

# Allow child processes to use this function
export -f notify

notify "Installing AWS CLI"
apt-get update
apt-get install -y awscli

# Download and execute each bootstrap file (note they must sort to the correct order)
BOOTSTRAP_URL="$S3_BUCKET_URL/bootstrap/"  # trailing slash matters!
notify "Executing all bootstrap scripts within $BOOTSTRAP_URL"
BOOTSTRAP_SCRIPTS=$(aws s3 ls $BOOTSTRAP_URL | awk '/\.sh/ {print $4}' | sort)
export REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')
for FILENAME in $BOOTSTRAP_SCRIPTS
do
    LOCAL_PATH=/tmp/$FILENAME
    S3_PATH=$BOOTSTRAP_URL$FILENAME
    notify "Downloading $S3_PATH to $LOCAL_PATH"
    aws s3 cp --region=$REGION $S3_PATH $LOCAL_PATH
    chmod +x $LOCAL_PATH
    notify "Executing $LOCAL_PATH"
    $LOCAL_PATH
    notify "Finished executing $LOCAL_PATH"
    rm $LOCAL_PATH
done

notify "Bootstrapping complete"
