#!/bin/bash
set -e
trap "[[ -f Dockerfile ]] && rm Dockerfile" EXIT

PROJECT_NAME=tangent-django-boilerplate
REPO_NAME=${PROJECT_NAME}

usage() {
    [ -n "$1" ] && echo $1
    printf "Ensure you have set the PROJECT_NAME variable in $0\n\nUsage: $0 [base|dev|release] [TAG | version]\n\n"
    exit 1
}

[ -z $PROJECT_NAME ] && usage
[[ -z $1 ]] && usage "Missing image-type (base|dev|release)"
[[ -z $2 ]] && usage "Missing TAG"

case $1 in
    base|local|dev|release)
        if [ ! -f "deploy/${1}/Dockerfile" ]; then
            printf "Missing $1 Dockerfile.\n\n"
            exit 1
        else 
            ln -sf deploy/${1}/Dockerfile Dockerfile
            printf "Building ${REPO_NAME}-${1}:${2} from \"${2}\" files....\n\n"
            docker build -t ${REPO_NAME}-${1}:${2} .
        fi
    ;;
    *)
        usage
    ;;
esac
