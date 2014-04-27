==========================
Tangent Django Boilerplate
==========================

This is a boilerplate ``README.rst`` created from the `tangent-django-boilerplate`_ project.
This section should be deleted and the below sections completed when the project
is created.

.. _`tangent-django-boilerplate`: https://github.com/tangentlabs/tangent-django-boilerplate

Use this project with Django's ``startproject`` command::

    django-admin.py startproject $PROJECT_NAME --extension="py,rst,conf,wsgi" --template=https://github.com/tangentlabs/tangent-django-boilerplate/zipball/master

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

=======================================
{{ client|title }} / {{ project_code }}
=======================================

Communication
-------------

[List mailing lists for projects]

For developers
--------------

[Explain how to set-up the project and run the unit tests]

For testers
-----------

[Add information useful for testing (eg magic bankcard numbers)]

Environments
------------

[List IP addresses and auth details for the various environments]
