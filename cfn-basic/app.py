#!/usr/bin/env python3
from aws_cdk import (
    App, Environment
)
import usdev

# CDK App
app = App()

# Stacks per vpc
usdev.StackSet(app, "usdev", Environment(region="us-east-1"))

# Synthesize
app.synth()
