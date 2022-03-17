from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_ec2
)

class NaclStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, subnets, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # NACL
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnNetworkAcl.html
        nacl = dict()
        nacl["public"] = aws_ec2.CfnNetworkAcl(self, "nacl-public",
            vpc_id=vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="nacl-public"
                ),
            ])

        # NACL Entry
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnNetworkAclEntry.html
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i1",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=10,
            cidr_block="0.0.0.0/0",
            protocol=6, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            port_range=aws_ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=80,
                to=80),
            rule_action="allow", # allow , deny
            icmp=None,
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i2",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=20,
            cidr_block="0.0.0.0/0",
            protocol=6, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            port_range=aws_ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=22,
                to=22),
            rule_action="allow", # allow , deny
            icmp=None,
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i3",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=30,
            cidr_block="0.0.0.0/0",
            protocol=6, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            port_range=aws_ec2.CfnNetworkAclEntry.PortRangeProperty(
                from_=1024,
                to=65535),
            rule_action="allow", # allow , deny
            icmp=None,
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i4",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=40,
            cidr_block="0.0.0.0/0",
            protocol=1, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            rule_action="allow", # allow , deny
            icmp=aws_ec2.CfnNetworkAclEntry.IcmpProperty(
                # 0 (echo-reply) , 8 (echo) , 11 (TimeExceeded - traceroute reply)
                # 3 (Destination unreachable - traceroute-reply) , 30 (traceroute)
                type=0,
                code=-1,),
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i5",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=50,
            cidr_block="0.0.0.0/0",
            protocol=1, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            rule_action="allow", # allow , deny
            icmp=aws_ec2.CfnNetworkAclEntry.IcmpProperty(
                # 0 (echo-reply) , 8 (echo) , 11 (TimeExceeded - traceroute reply)
                # 3 (Destination unreachable - traceroute-reply) , 30 (traceroute)
                type=3,
                code=-1,),
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-i6",
            network_acl_id=nacl["public"].ref,
            egress=False,
            rule_number=60,
            cidr_block="0.0.0.0/0",
            protocol=1, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            rule_action="allow", # allow , deny
            icmp=aws_ec2.CfnNetworkAclEntry.IcmpProperty(
                # 0 (echo-reply) , 8 (echo) , 11 (TimeExceeded - traceroute reply)
                # 3 (Destination unreachable - traceroute-reply) , 30 (traceroute)
                type=11,
                code=-1,),
            ipv6_cidr_block=None,)
        aws_ec2.CfnNetworkAclEntry(self, "nacl-public-e1",
            network_acl_id=nacl["public"].ref,
            egress=True,
            rule_number=10,
            cidr_block="0.0.0.0/0",
            protocol=-1, # -1 (all) , 1 (ICMP) , 6 (TCP) , 17 (UDP) ...
            rule_action="allow", # allow , deny
            icmp=None,
            ipv6_cidr_block=None,)
        
        # Subnet NACL Association
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSubnetNetworkAclAssociation.html
        aws_ec2.CfnSubnetNetworkAclAssociation(self, "nacl-public-subnet1",
            network_acl_id=nacl["public"].ref,
            subnet_id=subnets["public-a"].ref)
        aws_ec2.CfnSubnetNetworkAclAssociation(self, "nacl-public-subnet2",
            network_acl_id=nacl["public"].ref,
            subnet_id=subnets["public-b"].ref)