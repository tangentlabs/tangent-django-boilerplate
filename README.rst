==========================
Tangent Django Boilerplate
==========================

This is a boilerplate ``README.rst`` created from the `tangent-django-boilerplate`_ project.
This section should be deleted and the below sections completed when the project
is created.

.. _`tangent-django-boilerplate`: https://github.com/tangentlabs/tangent-django-boilerplate

Use this project with Django's ``startproject`` command::

    $ django-admin.py startproject $PROJECT_NAME \
      --extension="py,rst,conf,wsgi" \
      --template=https://github.com/tangentlabs/tangent-django-boilerplate/zipball/master

Note that you need to specify a name for the project and pass the following variables:

* ``client`` - The client for this project

* ``project_code`` - The project code

* ``domain`` - The top-level domain for the test/stage sites and the alerts mailing list

* ``timezone`` - Which timezone to use in ``settings.py``

Tangent developers can use the `tangent-kickstart`_ tool to simplify creation
of projects that conform to our conventions:

.. _`tangent-kickstart`: https://github.com/tangentlabs/tangent-kickstart

The below copy contains template variables - it gets merged with a context
when a new boilerplate project is created.

=============
Project title
=============

*<Describe the purpose of this project. What problem is it trying to solve.>*

Status
------

*<Set project up on Travis to get the correct token for the below image>*

.. image:: https://magnum.travis-ci.com/tangentlabs/{{ client }}_{{ project_code }}.png?token=&branch=master   
   :target: https://magnum.travis-ci.com/tangentlabs/{{ client }}_{{ project_code }}

*<Set project up on Sentry and include URL here>*

Communication
-------------

*<List mailing lists and any other channels for project communication>*

For developers
--------------

*<Explain how to set-up the project locally and run the tests>*

*<Explain how to deploy the project>*

Two sample users are available in the local build::

    username: superuser
    email: superuser@example.com
    password: testing

and::

    username: staff
    email: staff@example.com
    password: testing

For testers
-----------

*<List information that testers will need to know such as testing bankcard
numbers.>*

Infrastructure
--------------

*<Describe the infrastructure for this project, covering webservers, databases
and other services (eg Solr, RabbitMQ). Include versions>*

*<List the IP addresses of each server used by this project and any HTTP basic
auth credentials>*

Notes
-----

*<Describe any gotchas or unusual parts of the codebase. Assume the person who
will take over this project from you is a serial killer who knows where you
live.>*

*<Describe the reasoning behind major design decisions>*

Handover
--------

*<Describe any ongoing pieces of work. Cover the history of the feature and
what development has been done to date. Highlight any potential risks.>*
