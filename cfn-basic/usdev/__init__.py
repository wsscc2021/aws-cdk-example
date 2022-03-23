
# Import service stack modules
from usdev.vpc import VPCStack


class StackSet:

    def __init__(self, app, construct_prefix, environment):
        self.vpcStack = VPCStack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--vpc")