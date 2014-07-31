#!/bin/bash
#
# Push config files to S3

set -e  # Fail fast

PROD_BUCKET=
STAGE_BUCKET=

printf "\nPush configuration to stage or prod? [stage/prod]: "
read ENVIRONMENT

case $ENVIRONMENT in
    stage)
        if [ -z "$STAGE_BUCKET" ]; then
            printf "\nSTAGE_BUCKET variable not set. Exiting....\n\n"
            exit 1
        fi
        aws s3 cp stage/stage.py s3://${STAGE_BUCKET}/config/stage.py
        exit 0
    ;;

    prod)
        if [ -z "$PROD_BUCKET" ]; then
            printf "\nPROD_BUCKET variable not set. Exiting....\n\n"
            exit 1
        fi
        aws s3 cp /prod/prod.py s3://${STAGE_BUCKET}/config/prod.py
        exit 0
    ;;

    *)
       printf "\n\t$ENVIRONMENT != prod or stage. S3 configuration storage is for production or staging environments only.\n\n"
       exit 1
    ;;
esac

exit 0
