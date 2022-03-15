#!/usr/bin/env python3
# Import CDK modules
from aws_cdk import (
    App
)

# Import service stack modules
from vpc import VPCStack
from security.security_group import SecurityGroupStack

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

# Synthesize
app.synth()
