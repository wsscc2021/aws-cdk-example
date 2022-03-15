#!/bin/bash
sudo mkdir -p /opt/app
sudo aws s3 cp s3://usdev-artifacts-bucket/main /opt/app
sudo chmod +x /opt/app/main
sudo /opt/app/main us-east-1