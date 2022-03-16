#!/usr/bin/env python3
from aws_cdk import (
    App, Environment
)
import us_east_1
import ap_northeast_2

# CDK App
app = App()

# Stacks per region
us_east_1.StackSet(app, Environment(region="us-east-1"))
ap_northeast_2.StackSet(app, Environment(region="ap-northeast-2"))

# Synthesize
app.synth()
