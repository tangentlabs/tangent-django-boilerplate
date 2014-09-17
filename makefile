# Build a working version of the project
build: clean virtualenv env database

# Update the virtualenv
virtualenv: install_dependencies

# Create a database populated with data
database: remove_db create_db load_fixtures

# Ensure there is a .env file in place
env:
	-[[ ! -L www/.env ]] && ln -s env/local www/.env

# Run Django's server on a random port
run:
	www/manage.py runserver $$((RANDOM+1000))

# Delete all temporary or untracked files
clean: remove_pyc remove_media

remove_pyc:
	-find . -type f -name "*.pyc" -delete

remove_media:
	# Temporarily move the placeholder folder to /tmp/ so we can delete 
	# everything else in the MEDIA_ROOT.
	mv www/public/media/placeholder /tmp/_placeholder
	-rm -rf www/public/media/*
	mv /tmp/_placeholder www/public/media/placeholder

install_dependencies:
	# We need to install the setup.py in www so py.test runs with the right 
	# python path.
	pip install -e www
	pip install -r deploy/requirements/local.txt

remove_db:
	python www/manage.py reset_db --router=default --noinput

create_db:
	python www/manage.py syncdb --noinput
	python www/manage.py migrate

load_fixtures:
	python www/manage.py loaddata fixtures/*.json

test:
	cd www && py.test

# On travis, run all tests and check the project can be built from scratch
travis: test database

.PHONY: build virtualenv database run clean remove_pyc remove_media removeinstall_dependencies remove_db create_db load_fixtures test
