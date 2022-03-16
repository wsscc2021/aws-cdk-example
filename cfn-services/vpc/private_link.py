
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2
)

class PrivateLinkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,  vpc, subnets, 
                       route_tables, security_groups, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # vpc endpoint
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnVPCEndpoint.html
        # !! tag is not working !!
        vpc_endpoint = dict()
        vpc_endpoint['dynamodb'] = aws_ec2.CfnVPCEndpoint(self, "VPCEndpointDynamoDB",
            service_name="com.amazonaws.us-east-1.dynamodb",
            vpc_id=vpc.ref,
            policy_document=None,
            route_table_ids=[
                route_tables["public"].ref,
                route_tables["private-a"].ref,
                route_tables["private-b"].ref
            ],
            vpc_endpoint_type="Gateway")
        vpc_endpoint['s3'] = aws_ec2.CfnVPCEndpoint(self, "VPCEndpointS3",
            service_name="com.amazonaws.us-east-1.s3",
            vpc_id=vpc.ref,
            policy_document=None,
            private_dns_enabled=None, # s3 can not support private dns enabled.
            subnet_ids=[
                subnets["private-a"].ref,
                subnets["private-b"].ref,
            ],
            security_group_ids=[
                security_groups["privatelink"].ref,
            ],
            vpc_endpoint_type="Interface")