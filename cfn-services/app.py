#!/usr/bin/env python3
from aws_cdk import (
    App, Environment
)
import usdev
import apdev
import uswsi

# CDK App
app = App()

# Stacks per region
usdev.StackSet(app, "usdev", Environment(region="us-east-1"))
uswsi.StackSet(app, "uswsi", Environment(region="us-east-1"))
apdev.StackSet(app, "apdev", Environment(region="ap-northeast-2"))

# Synthesize
app.synth()
