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
from security.kms.kms_stack import KmsStack
from security.iam.iam_stack import IamStack
from security.nacl.nacl_stack import NaclStack
from security.security_group.security_group_stack import SecurityGroupStack
from eks.eks_stack import EksStack
from ec2.instance_stack import EC2InstanceStack
from ec2.asg_stack import AutoScalingGroupStack
from elb.elb_stack import ElasticLoadBalancerStack
from rds.rds_stack import RdsStack
from efs.efs_stack import EfsStack
from elasticache.elasticache_stack import ElasticacheStack
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

iam_stack = IamStack(
    scope        = app,
    construct_id = f"{project['prefix']}-iam",
    project      = project,
    env          = cdk_environment)

kms_stack = KmsStack(
    scope        = app,
    construct_id = f"{project['prefix']}-kms",
    project      = project,
    env          = cdk_environment)

s3_stack = S3Stack(
    scope          = app,
    construct_id   = f"{project['prefix']}-s3",
    project        = project,
    env            = cdk_environment)

lambda_stack = LambdaStack(
    scope        = app,
    construct_id = f"{project['prefix']}-lambda",
    project      = project,
    env          = cdk_environment)

security_group_stack = SecurityGroupStack(
    scope        = app,
    construct_id = f"{project['prefix']}-security-group",
    project      = project,
    vpc          = vpc_stack.vpc,
    env          = cdk_environment)

eks_stack = EksStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-eks",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

nacl_stack = NaclStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-nacl",
    project        = project,
    vpc            = vpc_stack.vpc,
    env            = cdk_environment)

ec2_instance_stack = EC2InstanceStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-ec2-instance",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

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

rds_stack = RdsStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-rds",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

efs_stack = EfsStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-efs",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

elasticache_stack = ElasticacheStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-elasticache",
    project        = project,
    vpc            = vpc_stack.vpc,
    security_group = security_group_stack.security_group,
    env            = cdk_environment)

cloudfront_stack = CloudFrontStack(
    scope          = app,
    construct_id   = f"{project['prefix']}-cloudfront",
    project        = project,
    origin         = {
        's3': s3_stack.s3_bucket,
        'elb': None,
    },
    env            = cdk_environment)

# app synth -> cloudformation template
app.synth()