#!/usr/bin/env bash
#
# Synchronise bootstrap files with S3 for a given build
#
# This script takes an environment name as a required parameter, then ensures
# the appropriate bucket is created and uploads the bootstrap scripts
#
# Note, for this script to work you need to have set your AWS access and secret keys
# as environmental variables. The best way to do this is to have them set in the 
# post-activate script of your virtual env - that lets you have different credentials
# for different projects.
#
# Further reading:
# - http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html

set -e  # Fail fast

# TODO Set client and project name
CLIENT=tangent
PROJECT=boilerplate

if [[ -z "$1" ]]; then
    echo "Usage: $0 [test|stage|prod]"
    exit 1
fi

# Create bucket (if it doesn't exist already) and upload files in bootstrap/
# folder
BUCKET_URL=s3://$CLIENT-$PROJECT-$1
aws s3 mb $BUCKET_URL
for FILEPATH in $(find bootstrap -type f)
do
    aws s3 cp $FILEPATH $BUCKET_URL/$FILEPATH
done
