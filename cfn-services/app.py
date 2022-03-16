#!/usr/bin/env python3
# Import CDK modules
from aws_cdk import (
    App
)

# Import service stack modules
from vpc import VPCStack
from vpc.private_link import PrivateLinkStack
from security.security_group import SecurityGroupStack
from ec2.instance import EC2InstanceStack
from ec2.auto_scaling_group import AutoScalingGroupStack
from elbv2 import ElasticLoadBalancerStack

# CDK App
app = App()

# Service Stack
vpcStack = VPCStack(
    scope        = app,
    construct_id = "vpc")

securityGroupStack = SecurityGroupStack(
    scope        = app,
    construct_id = "security-group",
    vpc          = vpcStack.vpc)

privateLinkStack = PrivateLinkStack(
    scope           = app,
    construct_id    = "private-link",
    vpc             = vpcStack.vpc,
    subnets         = vpcStack.subnets,
    route_tables    = vpcStack.route_tables,
    security_groups = securityGroupStack.security_groups,)

elasticLoadBalancerStack = ElasticLoadBalancerStack(
    scope           = app,
    construct_id    = "elbv2",
    vpc             = vpcStack.vpc,
    subnets         = vpcStack.subnets,
    security_groups = securityGroupStack.security_groups,)

ec2InstanceStack = EC2InstanceStack(
    scope           = app,
    construct_id    = "ec2-instance",
    subnets         = vpcStack.subnets,
    security_groups = securityGroupStack.security_groups,)

autoScalingGroupStack = AutoScalingGroupStack(
    scope           = app,
    construct_id    = "ec2-asg",
    subnets         = vpcStack.subnets,
    security_groups = securityGroupStack.security_groups,
    target_groups   = elasticLoadBalancerStack.target_groups,)

# Synthesize
app.synth()
