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
from security.security_group.security_group_stack import SecurityGroupStack
from eks.eks_stack import EksStack
from ecr.ecr_stack import EcrStack

# Information of project
project = dict()
project['account'] = "242593025403"
project['region']  = "us-east-1"
project['keypair'] = "dev-useast1"
project['env']     = "eks"
project['name']    = "workshop"
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

security_group_stack = SecurityGroupStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-security-group",
    project      = project,
    vpc          = vpc_stack.vpc)

eks_stack = EksStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-eks",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

ecr_stack = EcrStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-ecr",
    env            = cdk_environment)

# app synth -> cloudformation template
app.synth()