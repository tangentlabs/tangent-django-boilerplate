FROM ubuntu

# Install a load of packages
RUN apt-get update -qq
RUN apt-get install -y python-dev python-pip nginx supervisor 

# Copy code into container
ADD ./ /code

# Install python deps and build the database
RUN cd /code && make

# Set-up nginx and supervisor
RUN sed -i -e 's/{{ project_code }}/bp/' -e 's/{{ client }}/tangent/' -e 's/{{ domain }}/tangentlabs.co.uk/' /code/www/deploy/nginx/prod.conf
RUN cp /code/www/deploy/nginx/prod.conf /etc/nginx/sites-enabled
RUN cp /code/www/deploy/supervisord/docker.conf /etc/supervisor/conf.d

# Ensure folders are created with correct ownership
RUN mkdir -p /var/www/tangent/bp/builds /var/www/tangent/bp/run/prod /var/www/tangent/bp/logs/prod
RUN ln -s /code/www /var/www/tangent/bp/builds/prod
RUN chown -R www-data:www-data /var/www/tangent/bp/logs /var/www/tangent/bp/run /code/www

# Ensure nginx runs as a standalone process
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

EXPOSE 80

## Run supervisor once the container is built
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
