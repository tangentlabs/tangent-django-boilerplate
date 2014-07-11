FROM tangent-django-boilerplate-base:latest
MAINTAINER david.dyball@tangentlabs.co.uk

# Add our codebase
ADD www /var/www

# Add a supervisor script that will run our app and supporting
# services
ADD deploy/shared/supervisor.app.conf /etc/supervisor/conf.d/app.conf

# Add our Docker start-up script and make it executable
ADD deploy/shared/bash.start_webserver.sh /opt/start_webserver.sh
RUN chmod +x /opt/start_webserver.sh

# UWSGI is configured to talk WSGI protocol and bind to port
# 80 by default. Nginx should use "uwsgi_pass" to send traffic
# to it.
EXPOSE 80

# The default command to run if nothing is specified on the CLI
CMD ['/opt/start_webserver.sh']
