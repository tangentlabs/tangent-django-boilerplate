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
        aws s3 cp bootstrap/base.sh s3://${STAGE_BUCKET}/bootstrap/base.sh
        aws s3 cp bootstrap/webserver.sh s3://${STAGE_BUCKET}/bootstrap/webserver.sh
        aws s3 cp conf/stage.py s3://${STAGE_BUCKET}/conf/stage.py
        exit 0
    ;;

    prod)
        if [ -z "$PROD_BUCKET" ]; then
            printf "\nPROD_BUCKET variable not set. Exiting....\n\n"
            exit 1
        fi
        aws s3 cp bootstrap/base.sh s3://${STAGE_BUCKET}/bootstrap/base.sh
        aws s3 cp bootstrap/webserver.sh s3://${STAGE_BUCKET}/bootstrap/webserver.sh
        aws s3 cp conf/prod.py s3://${STAGE_BUCKET}/conf/prod.py
        exit 0
    ;;

    *)
       printf "\n\t$ENVIRONMENT != prod or stage. S3 configuration storage is for production or staging environments only.\n\n"
       exit 1
    ;;
esac

exit 0
