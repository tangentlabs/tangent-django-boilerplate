#!/usr/bin/env bash
#
# Initial bootstrap script for an EC2 instance.
#
# The contents of this file need to be stored against the created EC2 instance
# as "user data". See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

set -e

# TODO Set the S3 bucket for this instance
export S3_BUCKET_URL=s3://tangent-boilerplate-test

echo "Installing AWS CLI"
apt-get update
apt-get install -y awscli

# Download and execute each bootstrap file (note they must sort to the correct order)
BOOTSTRAP_URL="$S3_BUCKET_URL/bootstrap/"  # trailing slash matters!
echo "Executing all bootstrap scripts within $BOOTSTRAP_URL"
BOOTSTRAP_SCRIPTS=$(aws s3 ls $BOOTSTRAP_URL | awk '/\.sh/ {print $4}' | sort)
for FILENAME in "${BOOTSTRAP_SCRIPTS[@]}"
do
    LOCAL_PATH=/tmp/$FILENAME
    S3_PATH=$BOOTSTRAP_URL$FILENAME
    echo "Downloading $S3_PATH to $LOCAL_PATH"
    aws s3 cp $S3_PATH $LOCAL_PATH
    chmod +x $LOCAL_PATH
    echo "Executing $LOCAL_PATH"
    $LOCAL_PATH
    rm $LOCAL_PATH
done

echo "Bootstrapping complete"
