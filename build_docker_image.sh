#!/bin/bash
# 
# Build the docker image ready for deployment

# Immediately exit if a command exits with a non-zero status
set -e

# Ensure the Dockerfile symlink is removed if an EXIT signal is raised
trap "[[ -h Dockerfile ]] && unlink Dockerfile" EXIT

# Set project name
PROJECT_NAME=boilerplate

# Ensure script is called correctly
usage() {
    echo "Usage: $0 [base|dev|release] [TAG|VERSION]"
    exit 1
}
[[ -z $PROJECT_NAME ]] && usage "Missing project name"
[[ -z $1 ]] && usage "Missing image type"
[[ -z $2 ]] && usage "Missing tag"

IMAGETYPE=$1
TAG=${2:-latest}

case $IMAGETYPE in
    base|dev|release)
        DOCKERFILE="deploy/$IMAGETYPE/Dockerfile"
        if [ ! -f "$DOCKERFILE" ]; then
            echo "Missing $ROLE Dockerfile ($DOCKERFILE)"
            exit 1
        else 
            # Symlink the appropriate Dockerfile into place and run 'docker build'
            ln -sf $DOCKERFILE Dockerfile
            DOCKER_TAG="$PROJECT_NAME-$IMAGETYPE-$ROLE:$TAG"
            printf "Building Docker image $DOCKER_TAG\n\n"
            docker build -t $DOCKER_TAG .
        fi
    ;;
    *)
        usage
    ;;
esac
