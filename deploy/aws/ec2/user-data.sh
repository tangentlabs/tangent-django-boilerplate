#!/usr/bin/env bash
#
# Initial bootstrap script for an EC2 instance.
#
# The contents of this file need to be stored against the created EC2 instance
# as "user data". See http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html
# 
# This EC2 instance should have a "bucket" tag which specifies the S3 bucket
# URL. This script will download and execute any bootstrap files in the
# bootstrap/ folder in the bucket.

set -e

echo "Installing AWS CLI"
apt-get update
apt-get install -y awscli

# Determine S3 bucket URL for bootstrapping scripts from tag with key 'bucket'.
# This is *way* harder than it should be.  We need to determine the instance ID
# and region in order to get the tags for the instance. For some reason,
# ec2metadata doesn't return the region (only the AZ) and so we have to take a
# convoluted route to find it.
#
# See http://stackoverflow.com/questions/4249488/find-region-from-within-ec2-instance
TAG="bucket"  
INSTANCE_ID=$(ec2metadata --instance-id)
REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')
echo "Fetching S3 bucket URL (from tag $TAG) for instance $INSTANCE_ID in region $REGION"
export BUCKET_URL=$(aws ec2 describe-tags --filters "Name=resource-id,Values=$INSTANCE_ID" "Name=key,Values=$TAG" --region=$REGION --output=text | cut -f5)
if [[ -z "$BUCKET_URL" ]]; then
    echo "No tag '$TAG' is defined - unable to bootstrap"
    exit 1
fi

# Download and execute each bootstrap file (note they must sort to the correct order)
BOOTSTRAP_URL="$BUCKET_URL/bootstrap/"  # trailing slash matters!
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
