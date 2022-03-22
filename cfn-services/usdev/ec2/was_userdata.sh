#!/bin/bash
sudo mkdir -p /opt/app
sudo aws s3 cp s3://useast1-artifact-bucket/product-app /opt/app
sudo chmod +x /opt/app/product-app
sudo /opt/app/product-app us-east-1