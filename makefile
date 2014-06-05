# Build a working version of the project
build: virtualenv database

# Update the virtualenv
virtualenv: remove_pyc update_virtualenv

# Create a database populated with data
database: remove_db create_db load_fixtures

# Run Django's server on a random port
run:
	www/manage.py runserver $$((RANDOM+1000))

remove_pyc:
	-find . -type f -name "*.pyc" -delete

update_virtualenv:
	pip install -r www/deploy/requirements.txt

remove_db:
	python www/manage.py reset_db --router=default --noinput

create_db:
	python www/manage.py syncdb --noinput
	python www/manage.py migrate

load_fixtures:
	python www/manage.py loaddata fixtures/*.json

test:
	www/runtests.sh

clean:
	-find . -type f -name "*.pyc" -delete

# On travis, run all tests and check the project can be built from scratch
travis: test database

.PHONY: build virtualenv database remove_pyc update_virtualenv remove_db create_db load_fixtures test run
