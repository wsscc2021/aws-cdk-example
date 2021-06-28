#!/usr/bin/env python3
'''
    Initial cdk project information
    1. Import CDK modules
    2. Import Services modules in this project
    3. Project information
    4. cdk Construct
'''
# Import CDK modules
from aws_cdk import core

# Import Services modules
from s3.s3_stack import S3Stack
from cloudfront.cloudfront_stack import CloudFrontStack
from lambda_.lambda_stack import LambdaStack

# Information of project
project = dict()
project['account'] = "242593025403"
project['region']  = "us-east-1"
project['env']     = "dev"
project['name']    = "cdkworkshop"
project['prefix']  = f"{project['env']}-{project['name']}"

# cdk environment
cdk_environment = core.Environment(
    account=project['account'],
    region=project['region'])

# cdk construct
app = core.App()

s3_stack = S3Stack(
    scope        = app,
    construct_id = f"{project['prefix']}-s3",
    project      = project,
    env          = cdk_environment)

lambda_stack = LambdaStack(
    scope        = app,
    construct_id = f"{project['prefix']}-lambda",
    project      = project,
    env          = cdk_environment)

cloudfront_stack = CloudFrontStack(
    scope        = app,
    construct_id = f"{project['prefix']}-cloudfront",
    project      = project,
    origin       = {
        's3': s3_stack.s3_bucket
    },
    function     = lambda_stack.function,
    env          = cdk_environment)


# app synth -> cloudformation template
app.synth()