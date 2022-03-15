'''
    Dependncy: VpcStack
'''
from constructs import Construct
from aws_cdk import Stack, Tags, aws_ec2

class SecurityGroupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, project: dict, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Init
        self.vpc = vpc
        self.project = project
        self.security_group = dict()
        # Security Group
        self.add_security_group(
            name = "eks-cluster-controlplane",
            description = "",
            allow_all_outbound = False)
        self.add_security_group(
            name = "eks-nodegroup",
            description = "",
            allow_all_outbound = True)
        '''
            Security Group Rules
            1. Ingress
            1-1. TCP, Chained Security Group
            1-2. All Traffic, IPv4 CIDR
            2. Egress
            2-1. TCP, Chained Security Group
            2-2. All Traffic, IPv4 CIDR for Specific address
        '''
        # eks-cluster-controlplane
        self.security_group['eks-cluster-controlplane'].add_ingress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-cluster-controlplane-1",
                from_port=443,
                to_port=443),
            description = "")
        self.security_group['eks-cluster-controlplane'].add_egress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-cluster-controlplane-2",
                from_port=1025,
                to_port=65535),
            description = "")
        # eks nodegroup
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-nodegroup'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.ALL,
                string_representation="eks-nodegroup-1",
                from_port=None,
                to_port=None),
            description = "")
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-cluster-controlplane'],
            connection = aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-nodegroup-2",
                from_port=443,
                to_port=443),
            description = "")
        self.security_group['eks-nodegroup'].add_ingress_rule(
            peer = self.security_group['eks-cluster-controlplane'],
            connection=aws_ec2.Port(
                protocol=aws_ec2.Protocol.TCP,
                string_representation="eks-nodegroup-3",
                from_port=1025,
                to_port=65535),
            description = "",)

    '''
        This function create security group, It also tagging for operate efficient.
    '''
    def add_security_group(self, name: str, description: str, allow_all_outbound: bool):
        self.security_group[name] = aws_ec2.SecurityGroup(self, name,
            vpc                 = self.vpc,
            security_group_name = f"{self.project['prefix']}-{name}-sg",
            description         = description,
            allow_all_outbound  = allow_all_outbound)
        Tags.of(self.security_group[name]).add(
            "Name",
            f"{self.project['prefix']}-{name}-sg")