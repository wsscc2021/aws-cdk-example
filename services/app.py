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

# Import service stacks modules
from vpc.vpc_stack import VpcStack
from security.iam.iam_stack import IamStack
from security.kms.kms_stack import KmsStack
from s3.s3_stack import S3Stack
from lambda_.lambda_stack import LambdaStack
from security.security_group.security_group_stack import SecurityGroupStack
from security.nacl.nacl_stack import NaclStack
from eks.eks_stack import EksStack
from ec2.instance_stack import EC2InstanceStack
from elb.elb_stack import ElasticLoadBalancerStack
from ec2.asg_stack import AutoScalingGroupStack
from rds.rds_stack import RdsStack
from efs.efs_stack import EfsStack
from elasticache.elasticache_stack import ElasticacheStack
from cloudfront.cloudfront_stack import CloudFrontStack
from cicd.cicd_stack import CiCdStack

# Information of project
project = dict()
project['account'] = "242593025403"
project['region']  = "us-east-1"
project['env']     = "dev"
project['name']    = "cdkworkshop"
project['prefix']  = f"{project['env']}-{project['name']}"
project['keypair'] = "dev-useast1"

# Environment
cdk_environment = Environment(
    account=project['account'],
    region=project['region'])

# Construct
app = App()

# Service stack
vpc_stack = VpcStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}",
    project      = project)

iam_stack = IamStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-iam",
    project      = project)

kms_stack = KmsStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-kms",
    project      = project)

s3_stack = S3Stack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-s3",
    project      = project)

lambda_stack = LambdaStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-lambda",
    project      = project)

security_group_stack = SecurityGroupStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-security-group",
    project      = project,
    vpc          = vpc_stack.vpc)

nacl_stack = NaclStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-nacl",
    project      = project,
    vpc          = vpc_stack.vpc)

eks_stack = EksStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-eks",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

ec2_instance_stack = EC2InstanceStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-ec2-instance",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

elb_stack = ElasticLoadBalancerStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-elb",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

asg_stack = AutoScalingGroupStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-asg",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    target_group   = elb_stack.target_group)

rds_stack = RdsStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-rds",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

efs_stack = EfsStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-efs",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

elasticache_stack = ElasticacheStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-elasticache",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

cloudfront_stack = CloudFrontStack(
    scope        = app,
    env          = cdk_environment,
    construct_id = f"{project['prefix']}-cloudfront",
    project      = project,
    origin       = {
        's3': s3_stack.s3_bucket,
        'elb': None,
    })

cicd_stack = CiCdStack(
    scope          = app,
    env            = cdk_environment,
    construct_id   = f"{project['prefix']}-cicd",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group)

# app synth -> cloudformation template
app.synth()