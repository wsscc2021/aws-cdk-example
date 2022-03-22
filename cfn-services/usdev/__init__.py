
# Import service stack modules
from usdev.vpc import VPCStack
from usdev.vpc.private_link import PrivateLinkStack
from usdev.security.security_group import SecurityGroupStack
from usdev.ec2.instance import EC2InstanceStack
from usdev.ec2.auto_scaling_group import AutoScalingGroupStack
from usdev.elbv2 import ElasticLoadBalancerStack
from usdev.security.nacl import NaclStack
from usdev.route53 import Route53Stack
from usdev.cloudfront import CloudfrontStack

class StackSet:

    def __init__(self, app, construct_prefix, environment):
        self.vpcStack = VPCStack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--vpc")

        self.route53Stack = Route53Stack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--route53",
            vpc          = self.vpcStack.vpc)

        self.securityGroupStack = SecurityGroupStack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--security-group",
            vpc          = self.vpcStack.vpc)
        
        self.naclStack = NaclStack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--nacl",
            vpc          = self.vpcStack.vpc,
            subnets      = self.vpcStack.subnets,)

        self.privateLinkStack = PrivateLinkStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{construct_prefix}--private-link",
            vpc             = self.vpcStack.vpc,
            subnets         = self.vpcStack.subnets,
            route_tables    = self.vpcStack.route_tables,
            security_groups = self.securityGroupStack.security_groups,)

        self.elasticLoadBalancerStack = ElasticLoadBalancerStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{construct_prefix}--elbv2",
            vpc             = self.vpcStack.vpc,
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,)

        self.ec2InstanceStack = EC2InstanceStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{construct_prefix}--ec2-instance",
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,)

        self.autoScalingGroupStack = AutoScalingGroupStack(
            scope           = app,
            env             = environment,
            construct_id    = f"{construct_prefix}--ec2-asg",
            subnets         = self.vpcStack.subnets,
            security_groups = self.securityGroupStack.security_groups,
            target_groups   = self.elasticLoadBalancerStack.target_groups,)
        
        self.cloudfrontStack = CloudfrontStack(
            scope        = app,
            env          = environment,
            construct_id = f"{construct_prefix}--cloudfront",
            elb          = self.elasticLoadBalancerStack.elb,)
