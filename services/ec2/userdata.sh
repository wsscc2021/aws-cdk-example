#!/bin/bash
S3_BUCKET="apnortheast2-application-artifact-z01k3m2oaks"
S3_KEY="flask/helloworld.zip"
APPLICATION="helloworld.zip"

# create application directory
mkdir -p /opt/my-app/

# working directory
cd /opt/my-app

# download application binary file
aws s3 cp s3://${S3_BUCKET}/${S3_KEY} /opt/my-app/${APPLICATION}

# tar
tar zxf /opt/my-app/${APPLICATION}

# virtual environment
python3 -m venv .venv
.venv/bin/pip3 install -r /opt/my-app/requirements.txt

# run
nohup .venv/bin/python3 /opt/my-app/app.py > /opt/my-app/app.log 2>&1 &