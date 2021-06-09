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
from vpc.vpc_stack import VpcStack
from security_group.security_group_stack import SecurityGroupStack
from elb.elb_stack import ElasticLoadBalancerStack
from ec2.asg_stack import AutoScalingGroupStack

# Information of project
project = dict()
project['account'] = "242593025403"
project['region']  = "us-east-1"
project['env']     = "dev"
project['name']    = "cdkworkshop"
project['prefix']  = f"{project['env']}-{project['name']}"
project['keypair'] = "dev-useast1"

# cdk environment
cdk_environment = core.Environment(
    account=project['account'],
    region=project['region'])

# cdk construct
app = core.App()

vpc_stack = VpcStack(
    scope        = app,
    construct_id = f"{project['prefix']}",
    project      = project,
    env          = cdk_environment)

security_group_stack = SecurityGroupStack(
    scope        = app,
    construct_id = f"{project['prefix']}-security-group",
    project      = project,
    vpc          = vpc_stack.vpc,
    env          = cdk_environment)

elb_stack = ElasticLoadBalancerStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-elb",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

asg_stack = AutoScalingGroupStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-asg",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    target_group   = elb_stack.target_group,
    env            = cdk_environment)

# app synth -> cloudformation template
app.synth()