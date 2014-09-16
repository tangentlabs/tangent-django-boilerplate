#!/bin/bash
#
# Bootstrap script for a webserver EC2 instance

set -e  # Fail fast

exec 1> >(tee -a /var/log/bootstrap.webserver.log)
exec 2>&1

# Ensure nginx is installed and serving 404s by default
notify "Installing nginx"
apt-get install -y nginx
find /etc/nginx/sites-enabled/ -type f -delete

cat > /etc/nginx/sites-enabled/001-default << EOF
# Default server
server {
    return 404;
}
EOF

/etc/init.d/nginx restart

# Grab deploy script
notify "Installing deployment cronjob"
DEPLOY_FILE=/opt/deploy.sh
aws s3 cp --region=$REGION $S3_BUCKET_URL/release/deploy.sh $DEPLOY_FILE
chmod +x $DEPLOY_FILE

# Create cronjob to call deploy script every 5 minutes
echo "*/5 * * * * root $DEPLOY_FILE > /dev/null" > /etc/cron.d/deploy
