'''
    Dependency: vpc
    VPC Recommended Network ACL Rules
    -> https://docs.aws.amazon.com/ko_kr/vpc/latest/userguide/VPC_Scenario2.html#nacl-rules-scenario-2
'''
from aws_cdk import (
    core, aws_ec2
)

class NaclStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, project: dict, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Init
        self.vpc = vpc
        self.project = project
        self.nacl = dict()
        self.rule_number = dict()
        
        # Define NACL
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/NetworkAcl.html
        self.add_nacl(
            name='public',
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnet_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.PUBLIC))
        self.add_nacl(
            name='private',
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnet_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.PRIVATE))
        self.add_nacl(
            name='data',
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnet_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.ISOLATED))
        
        # Define NACL Rule
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/NetworkAclEntry.html
        '''
            private subnets nacl
        '''
        #Ingress
        self.add_ingress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(80,80),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_ingress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(443,443),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_ingress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        #Egress
        self.add_egress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(80,80),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_egress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(443,443),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_egress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_egress_rule(
            name='public',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(8080,8080),
            cidr_blocks=None,
            subnets=self.vpc.private_subnets)
        
        '''
            private subnets nacl
        '''
        #Ingress
        self.add_ingress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(8080,8080),
            cidr_blocks=None,
            subnets=self.vpc.public_subnets)
        self.add_ingress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        #Egress
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(80,80),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(443,443),
            cidr_blocks=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            subnets=None)
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            cidr_blocks=None,
            subnets=self.vpc.public_subnets)
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(2049,2049),
            cidr_blocks=None,
            subnets=self.vpc.isolated_subnets)
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(3306,3306),
            cidr_blocks=None,
            subnets=self.vpc.isolated_subnets)
        self.add_egress_rule(
            name='private',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(6379,6379),
            cidr_blocks=None,
            subnets=self.vpc.isolated_subnets)

        '''
            data subnets nacls
        '''
        #Ingress
        self.add_ingress_rule(
            name='data',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(2049,2049),
            cidr_blocks=None,
            subnets=self.vpc.private_subnets)
        self.add_ingress_rule(
            name='data',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(3306,3306),
            cidr_blocks=None,
            subnets=self.vpc.private_subnets)
        self.add_ingress_rule(
            name='data',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(6379,6379),
            cidr_blocks=None,
            subnets=self.vpc.private_subnets)
        #Egress
        self.add_egress_rule(
            name='data',
            tcp_port_range=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            cidr_blocks=None,
            subnets=self.vpc.private_subnets)

    def add_ingress_rule(self, name, tcp_port_range, cidr_blocks=None, subnets=None):
        if cidr_blocks:
            self.rule_number[name]+=5
            aws_ec2.NetworkAclEntry(self, f"nacl-{name}-ingress-{self.rule_number[name]}",
                network_acl=self.nacl[name],
                cidr=cidr_blocks,
                rule_number=self.rule_number[name],
                traffic=tcp_port_range,
                direction=aws_ec2.TrafficDirection.INGRESS,
                network_acl_entry_name=None,
                rule_action=aws_ec2.Action.ALLOW)
        if subnets:
            for subnet in subnets:
                self.rule_number[name]+=5
                aws_ec2.NetworkAclEntry(self, f"nacl-{name}-ingress-{self.rule_number[name]}",
                    network_acl=self.nacl[name],
                    cidr=aws_ec2.AclCidr.ipv4(subnet.ipv4_cidr_block),
                    rule_number=self.rule_number[name],
                    traffic=tcp_port_range,
                    direction=aws_ec2.TrafficDirection.INGRESS,
                    network_acl_entry_name=None,
                    rule_action=aws_ec2.Action.ALLOW)

    def add_egress_rule(self, name, tcp_port_range, cidr_blocks=None, subnets=None):
        if cidr_blocks:
            self.rule_number[name]+=5
            aws_ec2.NetworkAclEntry(self, f"nacl-{name}-ingress-{self.rule_number[name]}",
                network_acl=self.nacl[name],
                cidr=cidr_blocks,
                rule_number=self.rule_number[name],
                traffic=tcp_port_range,
                direction=aws_ec2.TrafficDirection.EGRESS,
                network_acl_entry_name=None,
                rule_action=aws_ec2.Action.ALLOW)
        if subnets:
            for subnet in subnets:
                self.rule_number[name]+=5
                aws_ec2.NetworkAclEntry(self, f"nacl-{name}-ingress-{self.rule_number[name]}",
                    network_acl=self.nacl[name],
                    cidr=aws_ec2.AclCidr.ipv4(subnet.ipv4_cidr_block),
                    rule_number=self.rule_number[name],
                    traffic=tcp_port_range,
                    direction=aws_ec2.TrafficDirection.EGRESS,
                    network_acl_entry_name=None,
                    rule_action=aws_ec2.Action.ALLOW)

    def add_nacl(self, name, subnet_selection):
        self.rule_number[name] = 0
        self.nacl[name] = aws_ec2.NetworkAcl(self, f"nacl-{name}",
            vpc=self.vpc,
            network_acl_name=f"{self.project['prefix']}-nacl-{name}",
            subnet_selection=subnet_selection)
        core.Tags.of(self.nacl[name]).add(
            "Name",
            f"{self.project['prefix']}-nacl-{name}")