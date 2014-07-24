==========================
Tangent Django Boilerplate
==========================

This is a boilerplate ``README.rst`` created from the `tangent-django-boilerplate`_ project.
This section should be deleted and the below sections completed when the project
is created.

.. _`tangent-django-boilerplate`: https://github.com/tangentlabs/tangent-django-boilerplate

Usage
-----

Use this project with Django's ``startproject`` command::

    $ django-admin.py startproject $PROJECT_NAME \
      --extension="py,rst,conf,wsgi" \
      --template=https://github.com/tangentlabs/tangent-django-boilerplate/zipball/master

Note that you need to specify a name for the project and pass the following variables:

* ``client`` - The client for this project

* ``project_code`` - The project code

* ``domain`` - The top-level domain for the test/stage sites and the alerts mailing list

* ``timezone`` - Which timezone to use in ``settings.py``

* ``language_code`` - Which timezone to use in ``settings.py``

Tangent developers can use the `tangent-kickstart`_ tool to simplify creation
of projects that conform to our conventions:

.. _`tangent-kickstart`: https://github.com/tangentlabs/tangent-kickstart

Once a new project is created, there are a number of details that need
completing. These are marked with `TODO` markers - find them like so::

    $ grep -rnH TODO .

TODO: Delete above section and complete details below

=============
Project title
=============

*<TODO: Describe the purpose of this project. What problem is it trying to solve.>*

*<TODO: Describe any third party integrations.>*

Status
------

*<TODO: Set project up on Travis to get the correct token for the below image>*

.. image:: https://magnum.travis-ci.com/tangentlabs/{{ client }}_{{ project_code }}.png?token=&branch=master   
   :target: https://magnum.travis-ci.com/tangentlabs/{{ client }}_{{ project_code }}

*<TODO: Set project up on Sentry and include URL here>*

Communication
-------------

*<TODO: Create project mailing lists and detail them here>*

For developers
--------------

Local set-up
~~~~~~~~~~~~

Clone the repo, create a virtualenv and run::

    $ make

This will:

- Install all Python dependencies (from ``www/deploy/requirements.txt``);

- Create your database schema

- Load sample data (stored in ``fixtures/*.json``)

Two sample users are loaded::

    username: superuser
    email: superuser@example.com
    password: testing

and::

    username: staff
    email: staff@example.com
    password: testing

Re-run this make target when switching branches to rebuild your database.

Testing
~~~~~~~

Run the test suite using either::

    $ make test

or::

    $ cd www
    $ py.test

See the `py.test docs`_ for info on how to run subsets of the test suite.

.. _`py.test docs`: http://pytest.org/latest/

Deployment
~~~~~~~~~~

Deployment uses Fabric_. There are helper scripts for each environment::

    $ ./deploy-to-test.sh
    $ ./deploy-to-stage.sh
    $ ./deploy-to-prod.sh

.. _Fabric: http://www.fabfile.org/

For testers
-----------

*<TODO: List information that testers will need to know such as testing bankcard
numbers.>*

Infrastructure
--------------

*<TODO: Describe the infrastructure for this project, covering webservers, databases
and other services (eg Solr, RabbitMQ). Include versions>*

*<TODO: List the IP addresses of each server used by this project and any HTTP basic
auth credentials>*

Notes
-----

*<TODO: Describe any gotchas or unusual parts of the codebase. Assume the person who
will take over this project from you is a serial killer who knows where you
live.>*

*<TODO: Describe the reasoning behind major design decisions>*
