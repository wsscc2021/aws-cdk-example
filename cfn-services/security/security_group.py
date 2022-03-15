from constructs import Construct
from aws_cdk import (
    Stack,
    CfnTag,
    aws_ec2
)

class SecurityGroupStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # security group
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSecurityGroup.html
        self.security_groups = dict()
        self.security_groups["product-ext"] = aws_ec2.CfnSecurityGroup(self,
            "product-ext-sg",
            group_name="product-ext-sg",
            group_description="description",
            security_group_egress=None,
            security_group_ingress=None,
            vpc_id=vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="product-ext-sg"
                )
            ])
        self.security_groups["product-api"] = aws_ec2.CfnSecurityGroup(self,
            "product-api-sg",
            group_name="product-api-sg",
            group_description="description",
            security_group_egress=None,
            security_group_ingress=None,
            vpc_id=vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="product-api-sg"
                )
            ])
        self.security_groups["bastion"] = aws_ec2.CfnSecurityGroup(self,
            "bastion-sg",
            group_name="bastion-sg",
            group_description="description",
            security_group_egress=None,
            security_group_ingress=None,
            vpc_id=vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="bastion-sg"
                )
            ])
        
        # security group ingress
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSecurityGroupIngress.html
        # security group egress
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSecurityGroupEgress.html
        aws_ec2.CfnSecurityGroupIngress(self, "product-ext-sg-r1",
            ip_protocol="tcp", # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip="0.0.0.0/0",
            from_port=80, # -1 (all)
            to_port=80, # -1 (all)
            group_id=self.security_groups["product-ext"].ref,
            group_name=None,
            source_prefix_list_id=None,
            source_security_group_id=None,
            source_security_group_name=None,
            source_security_group_owner_id=None,)
        
        aws_ec2.CfnSecurityGroupEgress(self, "product-ext-sg-r2",
            ip_protocol="tcp",  # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip=None,
            from_port=8080, # -1 (all)
            to_port=8080, # -1 (all)
            group_id=self.security_groups["product-ext"].ref,
            destination_prefix_list_id=None,
            destination_security_group_id=self.security_groups["product-api"].ref,)

        aws_ec2.CfnSecurityGroupIngress(self, "product-api-sg-r1",
            ip_protocol="tcp", # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip=None,
            from_port=8080, # -1 (all)
            to_port=8080, # -1 (all)
            group_id=self.security_groups["product-api"].ref,
            group_name=None,
            source_prefix_list_id=None,
            source_security_group_id=self.security_groups["product-ext"].ref,
            source_security_group_name=None,
            source_security_group_owner_id=None,)
        
        aws_ec2.CfnSecurityGroupIngress(self, "product-api-sg-r2",
            ip_protocol="tcp", # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip=None,
            from_port=22, # -1 (all)
            to_port=22, # -1 (all)
            group_id=self.security_groups["product-api"].ref,
            group_name=None,
            source_prefix_list_id=None,
            source_security_group_id=self.security_groups["bastion"].ref,
            source_security_group_name=None,
            source_security_group_owner_id=None,)
        
        aws_ec2.CfnSecurityGroupIngress(self, "bastion-sg-r1",
            ip_protocol="tcp", # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip="175.195.57.38/32",
            from_port=22, # -1 (all)
            to_port=22, # -1 (all)
            group_id=self.security_groups["bastion"].ref,
            group_name=None,
            source_prefix_list_id=None,
            source_security_group_id=None,
            source_security_group_name=None,
            source_security_group_owner_id=None,)