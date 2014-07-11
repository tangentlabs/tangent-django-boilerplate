# Docker + AWS Deployment Guide

### Table of Contents

* [Preface](#Preface)
* [Technologies / Definitions](#Technologies)
    * [Docker Engine](#Docker Engine)
        * [Definitions](#Docker)
        * [Docker Image Inheritence](#Docker Image Inheritence)
        * [Development Images](#Development Images)
        * [Release Images](#Release Images)
        * [Data Persistence for Docker Containers](#Data Persistence for Docker Containers)
    * [Amazon Web Services](#Amazon Web Services)
    * [Custom Conventions](#Custom Conventions)
* [Anatomy of a AWS+Docker Project (Quick Start)](#Anatomy of a AWS+Docker Project (Quick Start)
* [Detailed Walkthrough for Starting a Project](#Detailed Walkthrough for Starting a Project)
    * [AWS Account Setup Steps](#AWS Account Setup Steps)
    * [AWS Landscape Setup](#AWS Landscape Setup)
        * [Security Groups](#Security Groups)
        * [S3 Buckets](#S3 Buckets)
        * [IAM Roles](#IAM Roles)
        * [RDS Instance(s)](#RDS Instance(s)
    * [Docker](#Docker)
        * [Initial Setup](#Initial Setup)
        * [Building an Image](#Building an Image)
        * [Publish Your Image](#Publish Your Image)
    * [Transferring Configuration to S3](#Transferring Configuration to S3)
    * [Deploying to EC2](#Deploying to EC2)
* [Overview of Automation](#Overview of Automation)
    * [Bootstrap-Stage #1 (EC2 User-data Script)](#Bootstrap Stage #1 (EC2 User-data Script)
    * [Bootstrap Stage #2 (S3 Bash Script)](#Bootstrap Stage #2 (S3 Bash Script))
    * [Bootstrap Stage #3 (Docker Start-scripts)](#Bootstrap Stage #3 (Docker Start-scripts)

##Preface
This document aims to outline the process and method by which applications/projects can be deployed to Amazon Web Services using Docker.


It can be broken down into the following steps:

* Preparation / Initial Setup
* Build
* Deploy

##Technologies

###Docker Engine
Docker is a platform that allows for entire applications to be wrapped into a single “image” and run on any Docker-capable host. In such situations, all software required to successfully run the application is installed within the container itself, making the only requirement of the host the ability to run Docker containers.


All documentation not specific to the deployment of projects can be found on the official Docker site (http://docs.docker.io)


**Base Image**

This is a Docker image that contains all the base requirements for the project to build off.

**Container**

An instance spawned from a Docker Image. Once started, it runs independently of the parent image (i.e. changes to the parent will not be copied forward into the running container).

**Docker Engine**

The software used to write, build and run LXC containers in a repeatable fashion.

**Image**

A package containing all the software, requirements and code required to run an application in an isolated environment.

**Dockerfile**

A script of commands and actions used to automate building of a Docker Image

**Start Script**

The term “start script” is used throughout this documentation to refer to a Bash embedded inside an image/container that configures and runs the application housed within said image. The start-script is signified in the Dockerfile with the CMD command.<p>
Examples include:

* running Django management commands (syncdb/migrate/collectstatic), or
* pre-configuring a database (mysql_installdb | pg_createcluster)

**Tangent Base Image (tangent-12.04)**

An image based on Ubuntu 12.04 with some basic scaffolding and key pieces of software and configuration embedded, such as nginx, supervisord, Github SSH keys for Tangent projects, python and python-pip.<p>

**Important**: Do not make any image based off of tangent-12.04:* publicly available. It contains a pub-key pair that allows read access to all Tangent Github repositories.


**Volume + Volume Map**

A directory inside a container that can be mapped to a directory on the host machine (e.g. /var/log on the container could be bound to /containers/{project}/logs on the host machine). Volumes are good for ensuring that data can be persisted outside of the running container should it stop, restart, die or be killed.<br><br>

A volume map is an explicit mapping of host-to-container directories.


####Docker Image Inheritence

To save space and help ensure dependencies are ubiquitous across images, it is best to build all “dev” and “release” images based on the projects “base” Docker image (built using deploy/base/Dockerfile). This drastically reduces the size of subsequent images when deploying to dev/test/stage/production (see example image hierarchy in Fig 1 below).

When starting a project it is a good idea to construct your base image and have it include requirements that exist across both development and stage/production environments minus the codebase itself (e.g. all python requirements, all basic software packages etc.). From then on, when you need to build and ship an image, you are only copying the differences between the base image and the modifications you make to the new dev or release image.

![Docker Image Inheritance](http://github.com/tangentlabs/tangent-django-boilerplate/docs/aws/img/docker_image_inheritance.png)
*Fig 1. An example of base-image inheritance.*

####Development Images

Development Docker images should aim to contain all software, configuration and requirements needed for testing/running an app from scratch. You want to be able to say “Pull docker container xyz:dev” to a new developer on the project and have them up and running in two commands.

A Dockerfile for a development image would:

 * Inherit the base image
 * Update the software stack (apt-get update && apt-get upgrade -y)
 * Install additional software packages that are needed to “isolate” the container, like
 * MySQL / Postgres software
 * RabbitMQ or Solr
 * Additional debug software that might be needed for development
 * Add the codebase to the container **

** This can be overridden using volume arguments at runtime to allow for exposing your own code to the container so you can test changes you make in real-time without having to rebuild an entire image (e.g. your local copy of www gets mounted into the container on /var/www).


####Release Images

Historically it has always been the practice that each environment (dev/test/stage/prod) get built-to separately. In order to allow quicker transition of builds through each environment (e.g. test -> stage -> prod), we are trying to work with the concept of a “release” image. 

A release image should be tagged with its version and should match 1:1 the tag in Git from which it was built (e.g. version 0.1.1 of a container might match up to a Git tag called release/0.1.1). The container should also be ready to run across all build environments (dev, test, stage and production). Any environment-specific configuration (e.g. database names, queue servers, DB hosts etc.) should be made dynamic and configurable, either through configuration files stored on a remote server/service (like Django settings stored in Amazon S3) or through Docker commandline arguments that can be parsed by the Docker start-script and acted upon accordingly. 

An example of this functionality would be to allow for Djagno configuration to exist in S3 and some additional RabbitMQ queue information passed in to the start-script. It could be called with the following docker command:

    docker run -d -p 80 -v /containers/{project}/:/host  \
               -e DJANGO_CONFIG_URI=s3://{project}/django.py \
               -e QUEUE_NAME=processing_queue \
               project-release:0.0.1


Processing of any Bash environment variables being passed in (e.g.  ``-e QUEUE_NAME=`` above) needs to be specifically handled in your containers own start-script. The example above, could be handled like so:


    if [ -n “$QUEUE_NAME ]; then
        rabbitmqctl create_queue $QUEUE_NAME
    else
        echo “QUEUE_NAME needs to be set. Exiting….”
        exit 1
    fi


The above code in the start-script would create a new AMQP queue called ``processing_queue``, or exit with an error, killing the container.

A Dockerfile for a release image should follow these steps:and

 * Inherit the base image
 * Update the software (apt-get update && apt-get upgrade -y)
 * Update the python environment with the latest requirements.txt
 * Add the codebase to the image (e.g. www -> /var/www inside the container)
 * Add the start-script and make it the CMD script
 * EXPOSE the ports required to serve the application

####Data Persistence for Docker Containers

It is assumed that some applications will need to persist data beyond the lifetime of the Docker container they run inside of. It is, therefore, a good idea to expose a directory on the host server to the container running the application. This should be done irregardless of whether the container is running on an EC2 instance, local dev machine or VPS.<p>

<i>*Tip*</i>: Another upside of using a persistent directory for logging information is the fact that it is no longer necessary to enter the container itself to read or debug information stored in application logs. You can simply browse to the directory that has been exposed to the container and read the logs from there.

Because there is no point in every container or project implementing it’s own way of doing things, this document assumes the following:


 * Each host machine will have a directory called /containers. In here will be separate directories for each running container on the system and is used for storing data outside of the container.
 * /containers/{container-role}/ will be exposed/mounted inside the container on /host (this is done via the -v argument to docker run).
 * Applications running inside of containers should be configured to store all persistent data inside of the /host directory.
 
It can become difficult to ensure all of an applications data ends up inside of the /host directory. A good example of this is the Postgres database server which, by default on Ubuntu servers, will store all of its data files inside of ``/var/lib/postgres/9.3/main/``. 

To work around this, you are able to use symlinks to redirect data to the /host partition (e.g. symlink ``/host/postgres/data`` -> ``/var/lib/postgres/9.3/main``). When you do this it is important to make sure that, should your application expect data inside of these directories, that it is populated accordingly. 

In the example above if ``/containers/myapp-postgres/postgres/data`` was empty, then Postgres would fail to start. Any pre-configuration like this should be handled in your containers startup-scripts.

###Amazon Web Services

Amazon Web Services (AWS) is a commercial platform that provides hosting services to external parties. They offer compute facilities (EC2), database storage (RDS), asset storage (S3 | EBS), archive storage (S3-Glacier) and data analytics platforms (EMR).

A few key definitions are outlined below.


**AMI**

An Amazon Machine Image. This is a templated server image that can be instantiated as an EC2 instance.


**Availability Zone**

An Availability Zone is the equivalent of a separate datacentre within an Amazon Region. Deployment in multiple AZs can provide a way of managing disaster recovery and high-availability.


**EC2**

This is the equivalent of a Virtual Machine on Amazon. It should be treated as an ephemeral object that could disappear at any moment, taking with it all data stored on the virtual hard disk. While this is not always the case (EBS backed instances, for example, will retain data across reboots), care should be taken to design infrastructure in a resilient way to avoid platform failures due to individual EC2 instance failure.

**EBS (Elastic Block Storage)**

Elastic Block Storage is a form of attaching a new virtual hard drive to an EC2 instance. It can be used to persist data, regardless of the EC2 instances lifecycle.<br><br>

When used as “backing” for an EC2 instances root device it provides significantly faster throughput as opposed to “instance store” backed EC2 instances. Additionally, when used to back an EC2 instances root device, you can toggle the “Delete on Termination” option so that the data will remain in an EBS volume after the instance terminates.


**IAM Roles**

Identity Access Management Roles are runtime credentials to allow access control to EC2 instances that may need to access other AWS services. An example of this is would be a webserver running on EC2 that needs to be able to save content to an S3 bucket. It would be possible to hard-code the AWS keys into the configuration, but this poses a security risk and should be avoided. IAM provides a mechanism to work around this by generating time-restricted AWS key-pair that has pre-configured policies applied to it, allowing the application to access the services it needs without having hard-coded credentials in it.


**Instance Storage**

A type of ephemeral storage that can be used to host the core operating system image of an AMI. This only exists for the life of a particular EC2 instance and is lost on reboot or instance failure.


**RDS**

Amazons Relational Database Service provides a managed way to run MySQL, Postgresql, Oracle and MS SQL database instances. RDS also offers automated snapshot/backup services (nightly for up to 31 days retention), Multi Availability-Zone deployments (think block-level replication across datacentres) and, depending on the SQL engine used, one-click Read-Only Slave/Replica servers.


**Region**

An Amazon Region is a geo-located group of datacentres around the world. Each Region has multiple Availability Zones to it (usually 3 per-region).


**S3**

Simple Storage Service is the AWS “bit-bucket” storage service that exposes near-infinite storage via REST API. This is used for storing and serving static content to end users or internal applications/services.


**User-Data**

Amazon EC2 instances allow a form of “bootstrap” script to be run on instantiation via the “user-data” parameter when you start an EC2 instance. This can be a Cloud-Init, BASH or Python script. The scaffolding documented bellow is written in BASH.



### Custom Conventions

**Bootstrap Stage #1**

Actions performed during the first stage of starting an Amazon EC2 instance. Controlled by the EC2 instances’ user-data.


**Bootstrap Stage #2**

Actions performed after an EC2 container has finished booting and has the base packages required


**Bootstrap Stage #3 / Docker Boot Script**

The “start_*.sh” scripts contained within a Docker image (specified by CMD)


**Production Docker Repository**

EC2 + S3 endpoint for storing Docker images. Use for production images.


**Internal Docker Repository**

Desktop/Workstation in the Tangent office running Docker Registry. Use for dev/test images.


## Anatomy of a AWS+Docker Project (Quick Start)

At its most basic the lifecycle of an application on AWS performs the following stages.

 1. Configure AWS

 In order to run in effectively on Amazon, some pre-deployment steps need to be taken. These include deploying EC2 security groups (firewalls), S3 storage buckets (for static content + configuration files), IAM roles (for access control) and, if required, DatabaseBootstrap Stage #3 / Docker Boot Script services on RDS

 2. Create Project + Code Repository
 This is a simple as forking the tangent-django-boilerplate Git repository and modifying it so that it fits your application. Depending on your project requirements, you may need to modify the Dockerfiles located in deploy/{base|dev|release}, along with any supporting files in deploy/shared/*.

 3. Build Docker Image
 When you are at a point where you can do a dev or release build, you need to build your docker images based on the Dockerfiles in your projects deploy/*/Dockerfile (with * being either base, dev or release)

 4. Push Docker Image<p>If you’re sharing your image between developers, push it to the internal Docker repository:
 
 ``docker push docker-internal.tangentuk.local/{image}:{tag}``
 
 Release images are pushed to the central production docker server on AWS:
 
 ``docker push docker.tangentlabs.co.uk/{image}:{tag}``

 5. Push Project Configuration Files to S3

 Depending on the project, you should store as much of the configuration in a single location and retrieve it via your start-script. This allows you to spawn multiple EC2 instances and scale out your application dynamically, without having to manually configure each new instance.

 6. Launch EC2 Instance

 This is the last of the manual stages of deployment. Here you spawn an EC2 instance (as of writing the preferred AMI is Ubuntu 14.04 LTS). This can be done through the web interface, the command line utilities (aws ec2 run-instances) or via the EC2 API.
 
 The key here is to ensure that the server knows how to build itself and deploy the relevant docker containers and start the application. This is achieved through the use of a Bash script loaded into the Amazon EC2 Instances’ user-data* (Stage #1 Bootstrap) which in turn pulls a second project-specific Bash script from S3 (Stage #2 Bootstrap). Finaly the Docker containers start-script prepares and runs the application.

##Detailed Walkthrough for Starting a Project

In order to deploy a project two broad actions need to be taken:

 1. Setup Amazon Web Services
 2. Create a working codebase with relevant “scaffolding” in place for deployment
 3. Setup Amazon Web Services
 For manageability and billing purposes, each client will have their own Amazon Web Services account assigned to them, under which all of their projects will run and be billed against.
 
 **Note**: Multiple projects for the same client will all go into a single account. Logical separation can be done either with separate Security Groups for each application deployment or, ideally, placed inside separate Virtual Private Clouds (VPC) under the same account.

###AWS Account Setup Steps

 1. Speak to a member of Operations about setting up an email address for the new AWS account. The format for AWS email accounts is ``{customer}.aws@tangentlabs.co.uk``
 
 Multi-Word Customers are concatenated with no separator (e.g. “Big Company” becomes bigcompany.aws@tangentlabs.co.uk)

 These addresses are usually aliases to sys@tangentlabs.co.uk so Operations can pick up the incoming mail and action it. It may be necessary in future to have each project team and its members also receive Amazon emails for the account, so making this a mailing list and subscribing developers is also an option.
 
 2. Navigate to http://aws.amazon.com

 3. Click the “Sign Up” button

 4. Use the following details for registration of the account:
 
 **Full Name**: {Customer} {Project} @ Tangent
 
 **Email Address**: {customer}.aws@tangentlabs.co.uk
 
 **Company Name**: Tangent Communications
 
 **Country**: United Kingdom
 
 **Address**: 84-86 Great Portland Street
 
 **City**: London
 
 **State**: London
 
 **Post Code**: W1W 7NR
 
 **Phone Number**: 442074626100

 5. Enter in valid company credit card details<p>Note: Must be a working card in order to “activate” services correctly (even though we use consolidated billing, initial setup requires it).

 6. Enter in our company VAT number:   757157994

 7. Perform the Phone Validation process

 8. Choose the “Basic” support package unless the customer is paying for additional AWS support packages.

 9. Once complete, sign out and back in as ``sys@tangentlabs.co.uk`` at http://aws.amazon.com/ and navigate to “Billing Management Console” (as of writing on the top right under the account name menu).

 10. Navigate to “Consolidated Billing”

 11. Send a new request to ``{customer}.aws@tangentlabs.co.uk`` requesting they join the billing consolidation system.

 12. Acknowledge/Accept the request to ``{customer}.aws@tangentlabs.co.uk`` when it comes through.

The account should be active and ready to use within 15 minutes. You will receive an email confirming account activation.

If you experience any issues, AWS support cases are free and they are very helpful. It can take up to 48hrs to get a response from them via email, but phone support is free and immediate (they’ll even auto-call you so we aren’t charged… so considerate).


##AWS Landscape Setup

Most projects will require some basic infrastructure in order to deploy a project. This includes EC2 Security Groups, RDS instances (if required), S3 Buckets and IAM Roles.

While each application may differ in its requirements, below is an example configuration for a simple web-application. The steps will guide you through creating a production environment and should be repeated for stage, replacing or appending names to reflect the different environment.


All steps are outlined as though we are working in the eu-west-1 AWS region. If you are deploying services elsewhere, make changes to the steps and policy-templates below to reflect this.

###Security Groups

It is a good idea to separate production and stage environments using Amazon Security Groups. You should also endeavour to place the backend and web-app layers of your application into separate security groups and control their access using defined rules.

 1. Navigate to https://console.aws.amazon.com/ec2/v2/home?region=eu-west-1#SecurityGroups:
 2. Click **Create Security Group**
 3. Enter in the details:
 **Security Group Name**: prod-web-sg
 
 **Description**: Production Webserver Security Group
 
 **VPC**: Leave it as the default unless deploying into a custom VPC (out of scope here)
 
 **Inbound Rules**: Add individual rules as required by your application.
 
 **Outbound Rules**: It may be advantageous to remove the “0.0.0.0/0 ALL” rule and limit outbound application traffic. Use your discretion when deciding if this is required for your application.
 
 4. Click **Create** once completed.

Repeat for ``prod-backend-sg``, ``stage-backend-sg`` and ``stage-web-sg`` as required.

**Note**: Tangent has two main IP address ranges that you may want to allow access To/From when configuring security groups. These are:

**217.205.197.194/32**

The Tangent Office IP/Gateway (used by all internal systems to access the outside world)

**87.83.25.0/24**

This is the range used by production servers on our internal vSphere platform

Once you have all required security-groups created, you need to ensure that they can intercommunicate where necessary. One example would be web-servers needing to publish to RabbitMQ, which can be added as follows:

 1. Select the target security group in EC2 console under Security Groups (in this example “prod-backend-sg”
 2. Under the “Inbound” tab, press “Edit”
 3. In the “Type” drop-down, select “Custom TCP Rule”
 4. Enter “5672” under “Port Range”
 5. Select “Custom IP” under the “Source” drop-down
 6. In the source IP edit-box type “sg-” and it will provide a drop-down of currently configured security group ID’s and their friendly names. Choose “prod-webserver-sg” and click “Save”

**Note**: Auto-completion of security group names isn’t available in the initial “Create Security Group” screen, thus adding interconnecting rules is easier done after the groups have been created.


###S3 Buckets
Create two Amazon S3 buckets called {PROJECT_NAME} and {PROJECT_NAME}-stage

 1. Navigate to https://console.aws.amazon.com/s3/home?region=eu-west-1#
 2. Click **Create Bucket**
 3. Enter in the bucket name, select the region for the bucket and click **Create**
 4. Select the bucket you’ve just created and click the “Properties” button on the top-right corner to reveal additional bucket options.
 5. Expand **Permissions** and click **Edit Bucket Policy**
 6. Enter in the policy JSON from https://github.com/tangentlabs/tangent-django-boilerplate/docs/aws/s3_policy_bucket.json

 **Note**: Replace ``{PROJECT_NAME}`` with the correct project name.

 7. Still under **Permissions** click **Edit CORS Policy** and enter in the XML contained in https://github.com/tangentlabs/tangent-django-boilerplate/docs/aws/s3_policy_cors.xml
 
 **Note**: The CORS policy specified is not necessarily the best one to use for all applications. It is what we’ve found is required for Django projects. It may be insecure and should be reviewed for your purposes.


###IAM Roles

We’ll create two sets of credentials, one for stage and one for production:

 1. Navigate to https://console.aws.amazon.com/iam/home?region=eu-west-1#roles
 2. Click **Create New Role**
 3. Enter in a Role Name (e.g. ``prod-webserver``) and click **Continue**
 4. Select **Amazon EC2** and click **Continue**
 5. Select **Custom Policy** and click **Continue**
 6. Enter a Policy Name of ``access-ec2-tags``
 7. Enter in the policy JSON from https://github.com/tangentlabs/tangent-django-boilerplate/docs/aws/iam_policy_ec2_tags.json
 
 **Note**: ``{CUSTOMER_ID}`` in the JSON needs to be replaced with the accounts own AWS Account ID. If you are working outside of the EU region, you will also need to adjust the region ID’s in the JSON text.
 
 8. Create the role
 9. Select the new role and click on “Attach Role Policy” in the bottom pane.
 10. Select “Custom Policy” and click “Select”
 11. Enter in “s3-prod-bucket” as the name
 12. Enter in the text found in https://github.com/tangentlabs/tangent-django-boilerplate/docs/aws/iam_policy_s3_bucket.json<p>**Note**: Replace ``{BUCKET_NAME}`` in the JSON with the name of the S3 bucket you’re granting access to.

###RDS Instance(s)
To setup a database instance on Amazon RDS:

 1. Navigate to https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1#dbinstances:
 2. Select **Launch DB Instance**
 3. Select **MySQL** or **Postgres** depending on your requirements.
 4. Select ``Yes`` or ``No`` for Multi-AZ deployment. 
 
 **Note**: Extra costs are associated, so know whether this is a requirement before provisioning, as it cannot be quickly added later on.
 5. Enter in the required configuration:
 
 **License Model**: postgres-license
 
 **DB Engine Version**: as-required
 
 **DB Instance Class**: usage-dependant (e.g. db.m1.small is 1 core 4GB RAM)
 
 **Multi-AZ Deployment**: usage-dependant
 
 **Allocated Storage**: Size of the disk to be configured (cannot easily be resized later on)
 
 **Use Provisioned IOPS**: No (unless needed)
 
 **DB Instance Identifier**: {project}-rds
 
 **Master Username**: postgres *
 
 **Master Password**: {PASSWORD}
 
 \* Remember to document it on **bastion** (192.168.125.67) under ``/aws/{aws_id}/RDS_{Instance_ID}.txt``
  
 Enter in the Advanced Settings

 **VPC**: default
 
 **DB Subnet Group**: default
 
 **Publicly Accessible**: Yes / No (usage dependant. You usually require this to perform initial setup remotely)
 
 **VPC Security Groups**: prod-backend-sg
 
 **Database Name**: project_db_prod<br>
 
 **Database Port**: 5432
 
 **Parameter Group**: default
 
 **Option Group**: default#
 
 **Backup Retention Period**: 1-35 days
 
 **Backup Window**: 00:00-00:30
 
 **Auto Minor Version**: Yes
 
 **Maintenance Window**: 01:00-01:30
 
 6. Click **Launch**

Once deployed, you will need to allow the Tangent gateway IP address to access the RDS instance remotely. This is done through the security group you configured in the previous steps.


When you have access, login via the ``psql`` command as the superuser you configured (e.g. ``postgres``) and create the databases and roles required.


##Docker

###Initial Setup

To get a basic Django Boilerplate up and running and ready for docker:

    git clone git@github.com:tangentlabs/tangent-django-boilerplate.git {project-name}
    cd {project-name}
    
    # Edit “PROJECT_NAME” variable in build_docker_image.sh
    vi build_docker_image.sh

###Building an Image

To build an image once you have a working configuration/codebase, follow these steps:

    # Building a developer image and tag it as version 0.0.1
    ./build_docker_image.sh dev 0.0.1
    
    # Build a release image and tag it as 1.0
    ./build_docker_image.sh release 1.0


###Publish Your Image

To share your image and/or get it ready for deployment, push it to a central docker repository:

    # To push a release image
    docker push docker.tangentlabs.co.uk/{PROJECT_NAME}-release:{TAG}

    # To share a developer image
    docker push docker-internal.tangentuk.local/{PROJECT_NAME}-dev:{TAG}

**Note**: In the above two examples there are two docker endpoints that you can push to. The first is on Amazon AWS and should only be used for production and staging images. The later is open to (ab)use and is a good way to share images amongst developers.

##Transferring Configuration to S3

The easiest method for this is to store the configuration in Amazon S3 and use the AWS Command Line tools to retrieve them from within your start-script.

In future, something like CoreOS’ etcd distributed key-value storage cluster can be used/queried for centralised configuration values. More information on etcd can be found here: https://coreos.com/docs/

You can upload files to S3 using the web interface (https://console.aws.amazon.com/s3/home) or via the command line.

    aws s3 put {file} s3://{bucket}/config/{file}

The standard boilerplate container assumes the django configuration file is stored and retrieved from S3 on startup. Some further examples of configuration files and their S3 locations are detailed in Table 1.
 
| Purpose                   | Template                       | S3 Location                        | Bash Variable     |
| ------------------------- | ------------------------------ | ---------------------------------- | ----------------- |
| Django Stage Config       | ``deploy/aws/config/stage.py`` | ``s3://{project}/config/stage.py`` | DJANGO_CONFIG_URI |
| Django Prod Config        | ``deploy/aws/config/prod.py``  | ``s3://{project}/config/prod.py``  | DJANGO_CONFIG_URI |
| Example CRM Tomcat Config | ``deploy/aws/config/crm.xml``  | ``s3://{project}/config/crm.xml``  | CRM_CONFIG_URI    |

*Table 1. Example Configuration Files and Their Suggested S3 Locations.*

**Note**: Templates should be left in template form when committed back to version-control without passwords or configuration data present. Passwords and configuration should not be hard-coded anywhere for security reasons.

It is important to note that simply placing these variables on the Docker run commandline or copying configuration to S3 *will not* have any effect. Your Docker images’ start-script needs to interpret them and act accordingly before handing control off to supervisor.

One such example of this would be collecting a Solr schema file from S3 before. This could be done in the following way:

Modify the ``deploy/aws/bootstrap.webserver.sh`` by including a new stanza that looks for your environment variable (e.g. ``SOLR_SCHEMA``) and pulls the relevant schema from S3:

    if [[ -n “$SOLR_SCHEMA” ]]; then
        s3cmd get $SOLR_SCHEMA /opt/solr/schema.xml
    fi

**Note:** The above assumes that ``SOLR_SCHEMA`` will be a valid S3 URL. You should take care to plan for failure and, if possible exit in a controlled fashion while writing a usable message to the logs for debugging purposes.

Before deploying an instance, we need to centralise our configuration so that any new instances can collect it on start-up. The three main things that need to be pushed to S3 are:

 * Django Site Configuration
 * Stage #2 Bootstrap Script
 * Any additional configuration needed (e.g. CRM configuration XML files, external configuration files etc.)

To do this:
 1. Login to S3 (https://console.aws.amazon.com/s3/home?region=eu-west-1)
 2. Under the relevant project bucket, add two folders ``config`` and ``deploy``
 3. Under ``deploy`` upload your stage #2 bootstrap script e.g.
 
 ``deploy/aws/bootstrap.webserver.sh`` -> ``s3://{project}/deploy/webserver.sh``
 
 4. Similarly, upload your Django configuration to the config directory e.g.
 
 ``deploy/config/stage/django.py`` -> ``s3://{project}/config/prod.py``

###Deploying to EC2

Once the image has been pushed to the remote repository it can then be deployed to a server on Amazon EC2.

 1. Navigate to https://console.aws.amazon.com/ec2/v2/home?region=eu-west-1#Instances:
 2. Click **Launch Instance**
 3. Select the latest Ubuntu 14.04 EBS-backed Paravirtualised AMI (``ami-896c96fe`` as of writing)
 4. Select the required instance type and click **Next: Configure Instance Details**
 5. Expand the section called **Advanced Details**
 6. Under “user-data” copy and paste your projects ``user-data.txt`` file (an example should be under ``deploy/aws/user-data.txt`` in your project tree).
 7. Configure the rest of the VM options available on this page and click **Next: Add Storage**.
 8. Add additional storage if needed and press **Next: Tag Instance**
 9. Add a **Name** tag and set an appropriate value so the instance can be identified
 10. Add a tag called ``Bootstrap`` and enter in the value pointing to the S3 location of your stage #2 bootstrap file uploaded previously (e.g. ``s3://{project}/deploy/webserver.sh``)
 11. Click **Next: Configure Security Groups** when ready.
 12. Adjust the security groups so that your instance will end up in the correct one and click **Review and Launch**
 13. Review your settings and the launch your instance when ready.

##Overview of Automation

The next phase of deployment is heavily automated though, depending on your specific deployment, some modifications to the deployment scripts may be required. This section aims to provide an overview of the steps that have been automated.

The automation scripts can be broken down into the following types:

 1. Bootstrap Stage #1 (EC2 + user-data.txt)
 2. Bootstrap Stage #2 (Bash script run on boot of the instance)
 3. Docker Container Startup

It should be noted here that all stages of the automation process are not fault-tolerant. If for example a command in any of the stages fails, the scripts will terminate (hopefully with some notice/logging). This is forced by having all of the relevant Bash scripts launch with the set -e command at the beginning.

###Bootstrap Stage #1 (EC2 User-data Script)

During first boot of an AMI the user-data script is called. It aims to take a bare Amazon Machine Image and configure it correctly to deploy a Tangent docker container. To do this it performs the following tasks:


 1. Apply server-wide security and package updates (``apt-get update && apt-get dist-upgrade -y``)
 2. Install Docker Engine (``wget -O - https://get.docker.io | bash``)
 3. Install Amazon CLI tools (``pip install s3cmd awscli``)
 4. Query the ``Bootstrap`` EC2 tag of the running instance, pull the indicated script from S3 and run it as root
 5. As a post-installation step the current script attempts to configure Zabbix agent on the server however, at the time of writing, this has largely been unsuccessful. As such, monitoring should be configured manually through Amazon SNS (Simple Notification Service) or Tangents own Zabbix installation.

This portion of the automation is likely not to change amongst projects. Any per-project specific Docker host configuration should happen as part of stage #2.

###Bootstrap Stage #2 (S3 Bash Script)

This script is in charge of a) making sure the host server is capable of running the project-specific Docker containers and b) pulling the Docker image, or images, and running them with all the required arguments for it to function correctly.

It should be assumed at this stage that all credentials and software required to pull and run a Tangent-hosted Docker container have been installed/configured. The main tasks that are run during this stage are:


 1. Create ``/containers/{container-name}/`` directories on the host for persistent storage
 2. Install any additional app-specific dependencies that may not have been handled by the generic Bootstrap Stage #1 script.
 3. Pull the application Docker image(s) from Tangents Docker repository
 4. Run the Docker image with all required arguments for the container to succeed.


###Bootstrap Stage #3 (Docker Start-scripts)

This is the Docker start-up script that is specified via the CMD entry in the Dockerfile used to build the image. For more information on Dockerfiles, please see the above section on “Release Images”.


