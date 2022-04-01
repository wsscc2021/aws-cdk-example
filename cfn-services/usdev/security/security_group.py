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
        self.security_groups["example"] = aws_ec2.CfnSecurityGroup(self,
            "example-sg",
            group_name="example-sg",
            group_description="description",
            security_group_egress=None,
            security_group_ingress=None,
            vpc_id=vpc.ref,
            tags=[
                CfnTag(
                    key="Name",
                    value="example-sg"
                )
            ])
        
        # security group ingress
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSecurityGroupIngress.html
        # security group egress
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnSecurityGroupEgress.html
        aws_ec2.CfnSecurityGroupIngress(self, "example-sg-r1",
            group_id=self.security_groups["example"].ref,
            ip_protocol="-1", # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip="0.0.0.0/0",
            from_port=None, # -1 (all)
            to_port=None, # -1 (all)
            source_prefix_list_id=None,
            source_security_group_id=None,
            source_security_group_name=None,
            source_security_group_owner_id=None,)
        
        aws_ec2.CfnSecurityGroupEgress(self, "example-sg-r2",
            group_id=self.security_groups["example"].ref,
            ip_protocol="-1",  # tcp , udp , icmp , icmpv6 , -1 (all)
            cidr_ip="0.0.0.0/0",
            from_port=None, # -1 (all)
            to_port=None, # -1 (all)
            destination_prefix_list_id=None,
            destination_security_group_id=None,)