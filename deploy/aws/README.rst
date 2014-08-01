===
AWS
===

This folder houses the appropriate files needs for AWS.

IAM
---

Each EC2 instance needs an IAM role to define which other services it can
access. Policy JSON files are defined in ``iam/`` for help.

Bootstrapping
-------------

An EC2 instance is bootstrapped by using its user-data to fetch bootstrap files
from S3.  

- Sample user-data files are found in the ``ec2/`` folder.  
- Sample bootstrap files are found in the ``s3/bootstrap`` folder - these need
  to be uploaded to S3 prior to launching the EC2 instance. There is a script
  ``s3/push.sh`` for doing this.

The bootstrap scripts are as follows:

- ``s3/bootstrap/base.sh`` : installs Docker and NSEnter.
- ``s3/bootstrap/webserver.sh`` : creates the folders to share then pulls the
  docker container and configures nginx to proxy to it.
