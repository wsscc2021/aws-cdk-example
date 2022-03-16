
# Import service stack modules
from us_east_1.vpc import VPCStack
from us_east_1.vpc.private_link import PrivateLinkStack
from us_east_1.security.security_group import SecurityGroupStack
from us_east_1.ec2.instance import EC2InstanceStack
from us_east_1.ec2.auto_scaling_group import AutoScalingGroupStack
from us_east_1.elbv2 import ElasticLoadBalancerStack

class StackSet:

    def __init__(self, app, environment):
        self.vpcStack = VPCStack(
            scope        = app,
            env          = environment,
            construct_id = f"{environment.region}--vpc")

        self.securityGroupStack = SecurityGroupStack(
            scope        = app,
            env          = environment,
            construct_id = f"{environment.region}--security-group",
            vpc          = self.vpcStack.vpc)

        self.privateLinkStack = PrivateLinkStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{environment.region}--private-link",
            vpc             = self.vpcStack.vpc,
            subnets         = self.vpcStack.subnets,
            route_tables    = self.vpcStack.route_tables,
            security_groups = self.securityGroupStack.security_groups,)

        self.elasticLoadBalancerStack = ElasticLoadBalancerStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{environment.region}--elbv2",
            vpc             = self.vpcStack.vpc,
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,)

        self.ec2InstanceStack = EC2InstanceStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{environment.region}--ec2-instance",
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,)

        self.autoScalingGroupStack = AutoScalingGroupStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{environment.region}--ec2-asg",
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,
            target_groups   = self.elasticLoadBalancerStack.target_groups,)
