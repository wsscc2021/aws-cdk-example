#!/usr/bin/env python3
'''
    Initial cdk project information
    1. Import CDK modules
    2. Import Services modules in this project
    3. Project information
    4. cdk Construct
'''
# Import CDK modules
from aws_cdk import App, Environment

# Import Services modules
from vpc.vpc_stack import VpcStack

# Information of project
project = dict()
project['account'] = "242593025403"
project['region']  = "us-east-1"
project['env']     = "dev"
project['name']    = "cdkworkshop"
project['prefix']  = f"{project['env']}-{project['name']}"

# cdk environment
cdk_environment = Environment(
    account=project['account'],
    region=project['region'])

# cdk construct
app = App()

# VPC
vpc_stack = VpcStack(
    scope        = app,
    construct_id = f"{project['prefix']}",
    env          = cdk_environment,
    project      = project)

# app synth -> cloudformation template
app.synth()