#!/bin/bash
S3_BUCKET="useast1-artifact"
S3_KEY="sample-app-foo-v2.3.jar"
APPLICATION="sample-app-foo-v2.3.jar"

# create application directory
mkdir -p /opt/my-app/

# download application binary file
aws s3 cp s3://${S3_BUCKET}/${S3_KEY} /opt/my-app/${APPLICATION}

# run
nohup java -jar /opt/my-app/${APPLICATION} > /opt/my-app/app.log 2> /opt/my-app/error.log &