#!/usr/bin/env python3
# Import CDK modules
from aws_cdk import (
    App
)

# Import service stack modules
from vpc import VPCStack

# CDK App
app = App()

# Service Stack
vpcStack = VPCStack(
    scope        = app,
    construct_id = "vpc")

# Synthesize
app.synth()
