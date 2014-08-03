#!/bin/bash
# 
# Build a docker image
#
# This script symlinks in the appropriate Dockerfile then builds the image.

# TODO Set project name
PROJECT_NAME=boilerplate

set -e  # Fail fast

# Ensure the Dockerfile symlink is removed if an EXIT signal is raised
trap "[[ -h Dockerfile ]] && unlink Dockerfile" EXIT

usage() {
    echo $1
    echo "Usage: $0 [base|dev|release] [TAG]"
    exit 1
}

# Ensure script is called correctly
[[ -z $1 ]] && usage "Missing image type"

# Remove symlink of env variables
[[ -h www/.env ]] && unlink www/.env

IMAGETYPE=$1
TAG=${2:-latest}

case $IMAGETYPE in
    base|dev|release)
        DOCKERFILE="deploy/docker/Dockerfile-$IMAGETYPE"
        if [ ! -f "$DOCKERFILE" ]; then
            echo "Missing $IMAGETYPE Dockerfile ($DOCKERFILE)"
            exit 1
        else 
            # Symlink the appropriate Dockerfile into place and run 'docker
            # build'
            ln -sf $DOCKERFILE Dockerfile
            DOCKER_TAG="$PROJECT_NAME-$IMAGETYPE:$TAG"
            printf "Building Docker image $DOCKER_TAG\n\n"
            docker build -t $DOCKER_TAG .
        fi
    ;;
    *)
        usage "Unknown image type '$IMAGETYPE'"
    ;;
esac
