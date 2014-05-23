# Build a working version of the project
build: virtualenv database

# Update the virtualenv
virtualenv: remove_pyc update_virtualenv

# Create a database populated with data
database: remove_db create_db load_fixtures

remove_pyc:
	-find . -type f -name "*.pyc" -delete

update_virtualenv:
	pip install -e www
	pip install -r www/deploy/requirements.txt

remove_db:
	python www/manage.py reset_db --router=default --noinput

create_db:
	python www/manage.py syncdb --noinput
	python www/manage.py migrate

load_fixtures:

test:
	www/runtests.sh

clean:
	-find . -type f -name "*.pyc" -delete

# On travis, run all tests and check the project can be built from scratch
travis: test database

.PHONY: build virtualenv database remove_pyc update_virtualenv remove_db create_db load_fixtures test
