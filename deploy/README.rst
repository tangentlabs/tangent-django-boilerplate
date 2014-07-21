==============
AWS and Docker
==============

Stage 1 bootstrap
-----------------

File: ``deploy/aws/bootstrap/user-data.txt``

This bootstrap file is responsible for project-agnostic configuration of the
host EC2 instance. The content of this file need to be set as "user-data"
against the EC2 instance.

See the AWS docs on `Launching Instances with User Data`_. 

This bootstrap file is responsible for:

- Updating the OS
- Installing Python and Pip
- Installing Docker and NSEnter
- Installing AWS CLI tools
- Configuring the instance to talk to Tangent's Docker server
- Downloading the Stage 2 bootstrap file from S3 and executing it. Note, the URL of
  the Stage 2 file is stored the EC2 metadata for the instance.

.. _`Launching Instances with User Data`: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html

Stage 2 bootstrap
-----------------

File: ``deploy/aws/bootstrap/webserver.sh``

This bootstrap file is responsible for project-specific configuration of the
host EC2 instance. This file needs to be uploaded to S3 and have its S3 URL set
as a tag against the EC2 instance so the bootstrap 1 script can download and
execute it.

This script is responsible for:

- Creating folders for persistent storage (eg logs, data)
- Pulling the appropriate Docker image
- Running the Docker container, passing in all the appropriate env variables
- Installing nginx
- Configuring nginx to forward port 80 traffic to the appropriate port of the
  running Docker container
