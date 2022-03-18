from constructs import Construct
from aws_cdk import (
    Stack,
    aws_route53
)

class Route53Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Hosted Zone
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_route53/CfnHostedZone.html
        aws_route53.CfnHostedZone(self, "hosted-zone-",
            hosted_zone_config=aws_route53.CfnHostedZone.HostedZoneConfigProperty(
                comment="comment"),
            hosted_zone_tags=[
                aws_route53.CfnHostedZone.HostedZoneTagProperty(
                    key="Name",
                    value=""),
            ],
            name="example.com",
            query_logging_config=None,
            vpcs=[
                aws_route53.CfnHostedZone.VPCProperty(
                    vpc_id=vpc.ref,
                    vpc_region="us-east-1")
            ])