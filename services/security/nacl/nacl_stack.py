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
        
        # Define NACL
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/NetworkAcl.html
        self.nacl['public'] = self.add_nacl(
            name='public',
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnet_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.PUBLIC))
        self.nacl['private'] = self.add_nacl(
            name='private',
            subnet_selection=aws_ec2.SubnetSelection(
                availability_zones=None,
                one_per_az=None,
                subnet_filters=None,
                subnet_group_name=None,
                subnet_name=None,
                subnets=None,
                subnet_type=aws_ec2.SubnetType.PRIVATE))
        self.nacl['data'] = self.add_nacl(
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
        self.public_ingress()
        self.public_egress()
        self.private_ingress()
        self.private_egress()
        self.data_ingress()
        self.data_egress()

    def public_ingress(self):
        rule_number=0
        rule_number+=5
        aws_ec2.NetworkAclEntry(self, f"nacl-public-ingress-{rule_number}",
            network_acl=self.nacl['public'],
            cidr=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            rule_number=rule_number,
            traffic=aws_ec2.AclTraffic.tcp_port_range(443,443),
            direction=aws_ec2.TrafficDirection.INGRESS,
            network_acl_entry_name=None,
            rule_action=aws_ec2.Action.ALLOW)
        
        rule_number+=5
        aws_ec2.NetworkAclEntry(self, f"nacl-public-ingress-{rule_number}",
            network_acl=self.nacl['public'],
            cidr=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            rule_number=rule_number,
            traffic=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            direction=aws_ec2.TrafficDirection.INGRESS,
            network_acl_entry_name=None,
            rule_action=aws_ec2.Action.ALLOW)

        for subnet in self.vpc.public_subnets:
            rule_number+=5
            aws_ec2.NetworkAclEntry(self, f"nacl-public-ingress-{rule_number}",
                network_acl=self.nacl['public'],
                cidr=aws_ec2.AclCidr.ipv4(subnet.ipv4_cidr_block),
                rule_number=rule_number,
                traffic=aws_ec2.AclTraffic.tcp_port_range(80,80),
                direction=aws_ec2.TrafficDirection.INGRESS,
                network_acl_entry_name=None,
                rule_action=aws_ec2.Action.ALLOW)

    def public_egress(self):
        rule_number=0
        rule_number+=5
        aws_ec2.NetworkAclEntry(self, f"nacl-public-egress-{rule_number}",
            network_acl=self.nacl['public'],
            cidr=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            rule_number=rule_number,
            traffic=aws_ec2.AclTraffic.tcp_port_range(80,80),
            direction=aws_ec2.TrafficDirection.EGRESS,
            network_acl_entry_name=None,
            rule_action=aws_ec2.Action.ALLOW)
        
        rule_number+=5
        aws_ec2.NetworkAclEntry(self, f"nacl-public-egress-{rule_number}",
            network_acl=self.nacl['public'],
            cidr=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            rule_number=rule_number,
            traffic=aws_ec2.AclTraffic.tcp_port_range(443,443),
            direction=aws_ec2.TrafficDirection.EGRESS,
            network_acl_entry_name=None,
            rule_action=aws_ec2.Action.ALLOW)
        
        rule_number+=5
        aws_ec2.NetworkAclEntry(self, f"nacl-public-egress-{rule_number}",
            network_acl=self.nacl['public'],
            cidr=aws_ec2.AclCidr.ipv4('0.0.0.0/0'),
            rule_number=rule_number,
            traffic=aws_ec2.AclTraffic.tcp_port_range(1024,65535),
            direction=aws_ec2.TrafficDirection.EGRESS,
            network_acl_entry_name=None,
            rule_action=aws_ec2.Action.ALLOW)

    def private_ingress(self):
        rule_number=0

    def private_egress(self):
        rule_number=0

    def data_ingress(self):
        rule_number=0

    def data_egress(self):
        rule_number=0

    def add_nacl(self, name, subnet_selection):
        nacl = aws_ec2.NetworkAcl(self, f"nacl-{name}",
            vpc=self.vpc,
            network_acl_name=f"{self.project['prefix']}-nacl-{name}",
            subnet_selection=subnet_selection)
        core.Tags.of(nacl).add(
            "Name",
            f"{self.project['prefix']}-nacl-{name}")
        return nacl