
# Import service stack modules
from ap_northeast_2.vpc import VPCStack
class StackSet:

    def __init__(self, app, environment):
        self.vpcStack = VPCStack(
            scope        = app,
            env          = environment,
            construct_id = f"{environment.region}--vpc")